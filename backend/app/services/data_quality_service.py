"""
数据质量控制服务
实现数据去重、清洗、验证和异常检测功能
"""

import re
import hashlib
import logging
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import textblob
import emoji
import langdetect
from sqlalchemy.orm import Session
from ..data.models.database import get_db
from ..core.redis_client import redis_client

logger = logging.getLogger(__name__)

class DataQualityLevel(Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class QualityMetrics:
    """数据质量指标"""
    completeness: float  # 完整性 (0-1)
    accuracy: float      # 准确性 (0-1)
    consistency: float   # 一致性 (0-1)
    validity: float      # 有效性 (0-1)
    uniqueness: float    # 唯一性 (0-1)
    relevance: float     # 相关性 (0-1)
    overall_score: float # 总体质量分数 (0-1)
    level: DataQualityLevel

@dataclass
class DuplicationResult:
    """去重结果"""
    is_duplicate: bool
    similarity_score: float
    duplicate_id: Optional[str]
    duplicate_type: str  # exact, semantic, fuzzy

@dataclass
class AnomalyResult:
    """异常检测结果"""
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    description: str

class DataQualityService:
    """数据质量控制服务"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        
        # 缓存已处理的数据指纹
        self.processed_hashes: Set[str] = set()
        
        # 质量检查规则
        self.quality_rules = {
            'min_length': 10,
            'max_length': 5000,
            'min_words': 3,
            'max_words': 1000,
            'min_sentences': 1,
            'max_sentences': 50,
            'allowed_languages': ['en', 'zh', 'zh-cn'],
            'spam_keywords': ['spam', 'advertisement', 'promotion'],
            'profanity_threshold': 0.1
        }
        
        # 下载必要的NLTK数据
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        """下载NLTK数据 - 暂时跳过以避免网络问题"""
        try:
            # 尝试查找已存在的数据
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            logger.info("NLTK data found locally")
        except LookupError:
            # 跳过下载，使用基础功能
            logger.warning("NLTK data not found, skipping download due to network issues. Some text analysis features may be limited.")
    
    async def assess_data_quality(self, data: Dict[str, Any]) -> QualityMetrics:
        """
        评估数据质量
        
        Args:
            data: 待评估的数据
            
        Returns:
            质量指标
        """
        try:
            # 提取文本内容
            text_content = self._extract_text_content(data)
            
            # 计算各项质量指标
            completeness = self._calculate_completeness(data)
            accuracy = self._calculate_accuracy(text_content)
            consistency = self._calculate_consistency(data)
            validity = self._calculate_validity(text_content)
            uniqueness = await self._calculate_uniqueness(text_content)
            relevance = self._calculate_relevance(text_content, data.get('domain', ''))
            
            # 计算总体质量分数
            weights = {
                'completeness': 0.2,
                'accuracy': 0.2,
                'consistency': 0.15,
                'validity': 0.15,
                'uniqueness': 0.15,
                'relevance': 0.15
            }
            
            overall_score = (
                completeness * weights['completeness'] +
                accuracy * weights['accuracy'] +
                consistency * weights['consistency'] +
                validity * weights['validity'] +
                uniqueness * weights['uniqueness'] +
                relevance * weights['relevance']
            )
            
            # 确定质量等级
            level = self._determine_quality_level(overall_score)
            
            return QualityMetrics(
                completeness=completeness,
                accuracy=accuracy,
                consistency=consistency,
                validity=validity,
                uniqueness=uniqueness,
                relevance=relevance,
                overall_score=overall_score,
                level=level
            )
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return QualityMetrics(
                completeness=0.0,
                accuracy=0.0,
                consistency=0.0,
                validity=0.0,
                uniqueness=0.0,
                relevance=0.0,
                overall_score=0.0,
                level=DataQualityLevel.INVALID
            )
    
    async def check_duplication(self, text: str, data_id: Optional[str] = None) -> DuplicationResult:
        """
        检查数据重复
        
        Args:
            text: 待检查的文本
            data_id: 数据ID（可选）
            
        Returns:
            去重结果
        """
        try:
            # 1. 精确匹配检查
            exact_hash = self._calculate_text_hash(text)
            if exact_hash in self.processed_hashes:
                return DuplicationResult(
                    is_duplicate=True,
                    similarity_score=1.0,
                    duplicate_id=exact_hash,
                    duplicate_type="exact"
                )
            
            # 2. 语义相似度检查
            semantic_result = await self._check_semantic_similarity(text)
            if semantic_result['is_duplicate']:
                return DuplicationResult(
                    is_duplicate=True,
                    similarity_score=semantic_result['similarity'],
                    duplicate_id=semantic_result['duplicate_id'],
                    duplicate_type="semantic"
                )
            
            # 3. 模糊匹配检查
            fuzzy_result = await self._check_fuzzy_similarity(text)
            if fuzzy_result['is_duplicate']:
                return DuplicationResult(
                    is_duplicate=True,
                    similarity_score=fuzzy_result['similarity'],
                    duplicate_id=fuzzy_result['duplicate_id'],
                    duplicate_type="fuzzy"
                )
            
            # 记录新的数据指纹
            self.processed_hashes.add(exact_hash)
            
            return DuplicationResult(
                is_duplicate=False,
                similarity_score=0.0,
                duplicate_id=None,
                duplicate_type="none"
            )
            
        except Exception as e:
            logger.error(f"Error checking duplication: {e}")
            return DuplicationResult(
                is_duplicate=False,
                similarity_score=0.0,
                duplicate_id=None,
                duplicate_type="error"
            )
    
    async def clean_text_data(self, text: str) -> str:
        """
        清洗文本数据
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        try:
            # 1. 基础清理
            cleaned_text = self._basic_text_cleaning(text)
            
            # 2. 语言检测和标准化
            cleaned_text = self._normalize_language(cleaned_text)
            
            # 3. 表情符号处理
            cleaned_text = self._normalize_emojis(cleaned_text)
            
            # 4. 特殊字符处理
            cleaned_text = self._normalize_special_characters(cleaned_text)
            
            # 5. 空白字符标准化
            cleaned_text = self._normalize_whitespace(cleaned_text)
            
            # 6. 长度检查
            if len(cleaned_text) < self.quality_rules['min_length']:
                return ""
            
            return cleaned_text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text data: {e}")
            return text
    
    async def detect_anomalies(self, data: Dict[str, Any]) -> List[AnomalyResult]:
        """
        检测数据异常
        
        Args:
            data: 待检测的数据
            
        Returns:
            异常检测结果列表
        """
        anomalies = []
        
        try:
            text_content = self._extract_text_content(data)
            
            # 1. 长度异常检测
            length_anomaly = self._detect_length_anomaly(text_content)
            if length_anomaly:
                anomalies.append(length_anomaly)
            
            # 2. 语言异常检测
            language_anomaly = self._detect_language_anomaly(text_content)
            if language_anomaly:
                anomalies.append(language_anomaly)
            
            # 3. 内容质量异常检测
            quality_anomaly = self._detect_quality_anomaly(text_content)
            if quality_anomaly:
                anomalies.append(quality_anomaly)
            
            # 4. 格式异常检测
            format_anomaly = self._detect_format_anomaly(data)
            if format_anomaly:
                anomalies.append(format_anomaly)
            
            # 5. 统计异常检测
            statistical_anomaly = await self._detect_statistical_anomaly(text_content)
            if statistical_anomaly:
                anomalies.append(statistical_anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return [AnomalyResult(
                is_anomaly=True,
                anomaly_score=1.0,
                anomaly_type="processing_error",
                description=f"Error during anomaly detection: {str(e)}"
            )]
    
    async def batch_quality_check(self, data_batch: List[Dict[str, Any]]) -> List[QualityMetrics]:
        """
        批量质量检查
        
        Args:
            data_batch: 数据批次
            
        Returns:
            质量指标列表
        """
        tasks = [self.assess_data_quality(data) for data in data_batch]
        return await asyncio.gather(*tasks)
    
    async def generate_quality_report(self, data_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成数据质量报告
        
        Args:
            data_batch: 数据批次
            
        Returns:
            质量报告
        """
        try:
            quality_metrics = await self.batch_quality_check(data_batch)
            
            # 统计分析
            total_count = len(quality_metrics)
            excellent_count = sum(1 for m in quality_metrics if m.level == DataQualityLevel.EXCELLENT)
            good_count = sum(1 for m in quality_metrics if m.level == DataQualityLevel.GOOD)
            fair_count = sum(1 for m in quality_metrics if m.level == DataQualityLevel.FAIR)
            poor_count = sum(1 for m in quality_metrics if m.level == DataQualityLevel.POOR)
            invalid_count = sum(1 for m in quality_metrics if m.level == DataQualityLevel.INVALID)
            
            # 平均质量分数
            avg_scores = {
                'completeness': np.mean([m.completeness for m in quality_metrics]),
                'accuracy': np.mean([m.accuracy for m in quality_metrics]),
                'consistency': np.mean([m.consistency for m in quality_metrics]),
                'validity': np.mean([m.validity for m in quality_metrics]),
                'uniqueness': np.mean([m.uniqueness for m in quality_metrics]),
                'relevance': np.mean([m.relevance for m in quality_metrics]),
                'overall': np.mean([m.overall_score for m in quality_metrics])
            }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_records': total_count,
                'quality_distribution': {
                    'excellent': {'count': excellent_count, 'percentage': excellent_count / total_count * 100},
                    'good': {'count': good_count, 'percentage': good_count / total_count * 100},
                    'fair': {'count': fair_count, 'percentage': fair_count / total_count * 100},
                    'poor': {'count': poor_count, 'percentage': poor_count / total_count * 100},
                    'invalid': {'count': invalid_count, 'percentage': invalid_count / total_count * 100}
                },
                'average_scores': avg_scores,
                'recommendations': self._generate_recommendations(avg_scores)
            }
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'total_records': 0
            }
    
    # 私有方法实现
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """提取文本内容"""
        text_fields = ['content', 'text', 'message', 'description', 'instruction', 'response']
        for field in text_fields:
            if field in data and data[field]:
                return str(data[field])
        return ""
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """计算完整性"""
        required_fields = ['content', 'timestamp']
        optional_fields = ['domain', 'source', 'metadata']
        
        required_score = sum(1 for field in required_fields if field in data and data[field]) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if field in data and data[field]) / len(optional_fields)
        
        return required_score * 0.8 + optional_score * 0.2
    
    def _calculate_accuracy(self, text: str) -> float:
        """计算准确性"""
        if not text:
            return 0.0
        
        try:
            # 语法检查
            blob = textblob.TextBlob(text)
            grammar_score = 1.0 - (len(blob.correct().raw) - len(text)) / len(text)
            grammar_score = max(0.0, min(1.0, grammar_score))
            
            # 拼写检查
            words = word_tokenize(text.lower())
            misspelled = sum(1 for word in words if not word.isalpha() or len(word) < 2)
            spelling_score = 1.0 - (misspelled / len(words)) if words else 0.0
            
            return (grammar_score + spelling_score) / 2
            
        except Exception:
            return 0.5  # 默认中等分数
    
    def _calculate_consistency(self, data: Dict[str, Any]) -> float:
        """计算一致性"""
        # 检查数据格式一致性
        consistency_score = 1.0
        
        # 时间戳格式检查
        if 'timestamp' in data:
            try:
                datetime.fromisoformat(str(data['timestamp']))
            except ValueError:
                consistency_score -= 0.2
        
        # 域名格式检查
        if 'domain' in data:
            valid_domains = ['technology', 'business', 'finance', 'marketing', 'general']
            if data['domain'] not in valid_domains:
                consistency_score -= 0.2
        
        return max(0.0, consistency_score)
    
    def _calculate_validity(self, text: str) -> float:
        """计算有效性"""
        if not text:
            return 0.0
        
        validity_score = 1.0
        
        # 长度检查
        if len(text) < self.quality_rules['min_length']:
            validity_score -= 0.3
        elif len(text) > self.quality_rules['max_length']:
            validity_score -= 0.2
        
        # 单词数检查
        words = word_tokenize(text)
        if len(words) < self.quality_rules['min_words']:
            validity_score -= 0.2
        elif len(words) > self.quality_rules['max_words']:
            validity_score -= 0.1
        
        # 语言检查
        try:
            detected_lang = langdetect.detect(text)
            if detected_lang not in self.quality_rules['allowed_languages']:
                validity_score -= 0.3
        except Exception:
            validity_score -= 0.1
        
        return max(0.0, validity_score)
    
    async def _calculate_uniqueness(self, text: str) -> float:
        """计算唯一性"""
        duplication_result = await self.check_duplication(text)
        return 1.0 - duplication_result.similarity_score
    
    def _calculate_relevance(self, text: str, domain: str) -> float:
        """计算相关性"""
        if not text or not domain:
            return 0.5
        
        # 领域关键词
        domain_keywords = {
            'technology': ['tech', 'software', 'digital', 'innovation', 'AI', 'machine learning'],
            'business': ['business', 'strategy', 'market', 'customer', 'revenue', 'growth'],
            'finance': ['finance', 'investment', 'money', 'profit', 'cost', 'budget'],
            'marketing': ['marketing', 'brand', 'campaign', 'advertising', 'promotion', 'social media']
        }
        
        if domain not in domain_keywords:
            return 0.5
        
        keywords = domain_keywords[domain]
        text_lower = text.lower()
        
        keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
        relevance_score = min(1.0, keyword_count / len(keywords) * 2)
        
        return relevance_score
    
    def _determine_quality_level(self, overall_score: float) -> DataQualityLevel:
        """确定质量等级"""
        if overall_score >= 0.9:
            return DataQualityLevel.EXCELLENT
        elif overall_score >= 0.7:
            return DataQualityLevel.GOOD
        elif overall_score >= 0.5:
            return DataQualityLevel.FAIR
        elif overall_score >= 0.3:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.INVALID
    
    def _calculate_text_hash(self, text: str) -> str:
        """计算文本哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    async def _check_semantic_similarity(self, text: str) -> Dict[str, Any]:
        """检查语义相似度"""
        # 这里可以实现更复杂的语义相似度检查
        # 暂时返回简单的结果
        return {
            'is_duplicate': False,
            'similarity': 0.0,
            'duplicate_id': None
        }
    
    async def _check_fuzzy_similarity(self, text: str) -> Dict[str, Any]:
        """检查模糊相似度"""
        # 这里可以实现模糊匹配算法
        return {
            'is_duplicate': False,
            'similarity': 0.0,
            'duplicate_id': None
        }
    
    def _basic_text_cleaning(self, text: str) -> str:
        """基础文本清理"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # 移除电话号码
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        return text.strip()
    
    def _normalize_language(self, text: str) -> str:
        """语言标准化"""
        # 这里可以添加语言特定的标准化逻辑
        return text
    
    def _normalize_emojis(self, text: str) -> str:
        """表情符号标准化"""
        # 将表情符号转换为文本描述
        return emoji.demojize(text)
    
    def _normalize_special_characters(self, text: str) -> str:
        """特殊字符标准化"""
        # 标准化引号
        text = re.sub(r'[""''`]', '"', text)
        
        # 标准化破折号
        text = re.sub(r'[—–]', '-', text)
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """空白字符标准化"""
        # 将所有空白字符转换为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除行首行尾空白
        text = text.strip()
        
        return text
    
    def _detect_length_anomaly(self, text: str) -> Optional[AnomalyResult]:
        """检测长度异常"""
        if len(text) < 5:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=1.0,
                anomaly_type="too_short",
                description="Text is too short"
            )
        elif len(text) > 10000:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=0.8,
                anomaly_type="too_long",
                description="Text is unusually long"
            )
        return None
    
    def _detect_language_anomaly(self, text: str) -> Optional[AnomalyResult]:
        """检测语言异常"""
        try:
            detected_lang = langdetect.detect(text)
            if detected_lang not in self.quality_rules['allowed_languages']:
                return AnomalyResult(
                    is_anomaly=True,
                    anomaly_score=0.9,
                    anomaly_type="unsupported_language",
                    description=f"Detected language: {detected_lang}"
                )
        except Exception:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=0.7,
                anomaly_type="language_detection_failed",
                description="Could not detect language"
            )
        return None
    
    def _detect_quality_anomaly(self, text: str) -> Optional[AnomalyResult]:
        """检测内容质量异常"""
        # 检查垃圾内容
        spam_score = sum(1 for keyword in self.quality_rules['spam_keywords'] if keyword in text.lower())
        if spam_score > 0:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=0.8,
                anomaly_type="spam_content",
                description="Content contains spam keywords"
            )
        
        # 检查重复字符
        repeated_chars = re.findall(r'(.)\1{5,}', text)
        if repeated_chars:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=0.6,
                anomaly_type="repeated_characters",
                description="Content contains excessive repeated characters"
            )
        
        return None
    
    def _detect_format_anomaly(self, data: Dict[str, Any]) -> Optional[AnomalyResult]:
        """检测格式异常"""
        # 检查必需字段
        required_fields = ['content']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=1.0,
                anomaly_type="missing_required_fields",
                description=f"Missing required fields: {missing_fields}"
            )
        
        return None
    
    async def _detect_statistical_anomaly(self, text: str) -> Optional[AnomalyResult]:
        """检测统计异常"""
        # 这里可以实现基于统计的异常检测
        # 例如：字符分布异常、词频异常等
        return None
    
    def _generate_recommendations(self, avg_scores: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if avg_scores['completeness'] < 0.7:
            recommendations.append("Improve data completeness by ensuring all required fields are filled")
        
        if avg_scores['accuracy'] < 0.7:
            recommendations.append("Enhance data accuracy through better validation and spell checking")
        
        if avg_scores['consistency'] < 0.7:
            recommendations.append("Standardize data formats and enforce consistency rules")
        
        if avg_scores['validity'] < 0.7:
            recommendations.append("Implement stricter validation rules for data input")
        
        if avg_scores['uniqueness'] < 0.7:
            recommendations.append("Strengthen deduplication processes to improve data uniqueness")
        
        if avg_scores['relevance'] < 0.7:
            recommendations.append("Improve data relevance by better domain classification and filtering")
        
        return recommendations

# 创建全局实例
data_quality_service = DataQualityService()