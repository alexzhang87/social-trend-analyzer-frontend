"""
增强文本分析服务
集成多种免费开源文本分析库：VADER、TextBlob、NLTK
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime
from collections import Counter, defaultdict

# 导入文本分析库
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist

# 导入MonkeyLearn服务（可选）
try:
    from .monkeylearn_service import monkeylearn_service
    MONKEYLEARN_AVAILABLE = True
except ImportError:
    MONKEYLEARN_AVAILABLE = False
    monkeylearn_service = None

logger = logging.getLogger("trend-analyzer")

class EnhancedTextAnalysisService:
    """增强文本分析服务"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        
        # 下载必要的NLTK数据
        self._download_nltk_data()
        
        # 加载停用词
        self._load_stopwords()
        
        logger.info("EnhancedTextAnalysisService 已初始化")
    
    def _download_nltk_data(self):
        """下载必要的NLTK数据包 - 暂时跳过以避免网络问题"""
        nltk_downloads = [
            'punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger',
            'averaged_perceptron_tagger_eng', 'maxent_ne_chunker', 'words', 'wordnet', 'vader_lexicon'
        ]
        
        # 检查已存在的数据，跳过下载
        for item in nltk_downloads:
            try:
                # 尝试查找已存在的数据
                if item == 'punkt':
                    nltk.data.find('tokenizers/punkt')
                elif item == 'stopwords':
                    nltk.data.find('corpora/stopwords')
                elif item == 'vader_lexicon':
                    nltk.data.find('vader_lexicon')
                # 其他数据包也可以类似检查，但为了简化暂时跳过
            except LookupError:
                logger.warning(f"NLTK数据 {item} 未找到，跳过下载以避免网络问题")
                # 继续运行，不阻止服务启动
    
    def _load_stopwords(self):
        """加载停用词"""
        try:
            self.english_stopwords = set(stopwords.words('english'))
            # 添加自定义停用词
            custom_stopwords = {
                'rt', 'via', 'http', 'https', 'www', 'com', 'org',
                'amp', 'get', 'go', 'new', 'now', 'see', 'way', 'well',
                'also', 'would', 'could', 'should', 'one', 'two', 'like'
            }
            self.english_stopwords.update(custom_stopwords)
            
            # 中文停用词（基础版）
            self.chinese_stopwords = {
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                '你', '会', '着', '没有', '看', '好', '自己', '这'
            }
            
        except Exception as e:
            logger.warning(f"停用词加载失败: {e}")
            self.english_stopwords = set()
            self.chinese_stopwords = set()
    
    def analyze_sentiment_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        综合情感分析 - 使用多种方法
        
        Args:
            text: 待分析文本
            
        Returns:
            综合分析结果
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {},
                'methods': {}
            }
        
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # VADER情感分析
        vader_result = self._analyze_with_vader(cleaned_text)
        
        # TextBlob情感分析
        textblob_result = self._analyze_with_textblob(cleaned_text)
        
        # 综合判断
        final_sentiment, confidence = self._combine_sentiment_results(
            vader_result, textblob_result
        )
        
        return {
            'sentiment': final_sentiment,
            'confidence': confidence,
            'scores': {
                'vader': vader_result,
                'textblob': textblob_result
            },
            'methods': {
                'vader_weight': 0.6,  # VADER对社交媒体文本更准确
                'textblob_weight': 0.4
            },
            'text_length': len(cleaned_text),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """使用VADER进行情感分析"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # VADER返回compound分数来判断整体情感
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'compound': compound,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'confidence': abs(compound)
            }
            
        except Exception as e:
            logger.error(f"VADER分析失败: {e}")
            return {
                'sentiment': 'neutral',
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0
            }
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """使用TextBlob进行情感分析"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # TextBlob极性范围：-1(负面)到1(正面)
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"TextBlob分析失败: {e}")
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'confidence': 0.0
            }
    
    def _combine_sentiment_results(self, vader_result: Dict, textblob_result: Dict) -> Tuple[str, float]:
        """综合多种情感分析结果"""
        vader_sentiment = vader_result.get('sentiment', 'neutral')
        textblob_sentiment = textblob_result.get('sentiment', 'neutral')
        
        vader_confidence = vader_result.get('confidence', 0.0)
        textblob_confidence = textblob_result.get('confidence', 0.0)
        
        # 权重配置
        vader_weight = 0.6
        textblob_weight = 0.4
        
        # 如果两个方法一致，增加置信度
        if vader_sentiment == textblob_sentiment:
            final_sentiment = vader_sentiment
            final_confidence = (vader_confidence * vader_weight + 
                              textblob_confidence * textblob_weight) * 1.2
        else:
            # 不一致时，选择置信度更高的
            if vader_confidence > textblob_confidence:
                final_sentiment = vader_sentiment
                final_confidence = vader_confidence * 0.8
            else:
                final_sentiment = textblob_sentiment
                final_confidence = textblob_confidence * 0.8
        
        # 确保置信度在合理范围内
        final_confidence = min(final_confidence, 1.0)
        
        return final_sentiment, final_confidence
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """
        关键词提取
        
        Args:
            text: 文本内容
            max_keywords: 最大关键词数量
            
        Returns:
            关键词列表，包含词频和重要性分数
        """
        if not text or not text.strip():
            return []
        
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            # 分词
            try:
                tokens = word_tokenize(cleaned_text.lower())
            except LookupError:
                # 如果NLTK数据缺失，使用简单分词
                tokens = cleaned_text.lower().split()
            
            # 过滤停用词和短词
            filtered_tokens = [
                token for token in tokens 
                if (token.isalpha() and 
                    len(token) > 2 and 
                    token not in self.english_stopwords)
            ]
            
            # 词性标注，只保留名词、形容词、动词
            try:
                pos_tags = pos_tag(filtered_tokens)
                important_words = [
                    word for word, pos in pos_tags 
                    if pos.startswith(('NN', 'JJ', 'VB'))
                ]
            except LookupError:
                # 如果词性标注失败，直接使用过滤后的tokens
                important_words = filtered_tokens
            
            # 词干提取
            try:
                lemmatized_words = [
                    self.lemmatizer.lemmatize(word) for word in important_words
                ]
            except LookupError:
                # 如果词干提取失败，直接使用原词
                lemmatized_words = important_words
            
            # 计算词频
            freq_dist = FreqDist(lemmatized_words)
            
            # 生成关键词列表
            keywords = []
            for word, frequency in freq_dist.most_common(max_keywords):
                # 计算重要性分数（词频 + 长度奖励）
                importance_score = frequency + (len(word) - 3) * 0.1
                
                keywords.append({
                    'word': word,
                    'frequency': frequency,
                    'importance_score': round(importance_score, 2),
                    'normalized_score': round(frequency / freq_dist.N(), 3) if freq_dist.N() > 0 else 0
                })
            
            logger.info(f"提取了 {len(keywords)} 个关键词")
            return keywords
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        命名实体识别
        
        Args:
            text: 文本内容
            
        Returns:
            实体列表
        """
        if not text or not text.strip():
            return []
        
        try:
            # 分词和词性标注
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # 命名实体识别
            tree = ne_chunk(pos_tags)
            
            entities = []
            current_entity = []
            current_label = None
            
            for item in tree:
                if hasattr(item, 'label'):
                    # 这是一个实体
                    if current_label == item.label():
                        # 同一个实体的延续
                        current_entity.extend([word for word, tag in item])
                    else:
                        # 新实体开始，保存之前的实体
                        if current_entity:
                            entities.append({
                                'entity': ' '.join(current_entity),
                                'type': current_label,
                                'confidence': 0.8  # NER的基础置信度
                            })
                        current_entity = [word for word, tag in item]
                        current_label = item.label()
                else:
                    # 不是实体，保存之前的实体
                    if current_entity:
                        entities.append({
                            'entity': ' '.join(current_entity),
                            'type': current_label,
                            'confidence': 0.8
                        })
                        current_entity = []
                        current_label = None
            
            # 处理最后一个实体
            if current_entity:
                entities.append({
                    'entity': ' '.join(current_entity),
                    'type': current_label,
                    'confidence': 0.8
                })
            
            logger.info(f"识别了 {len(entities)} 个命名实体")
            return entities
            
        except Exception as e:
            logger.error(f"实体识别失败: {e}")
            return []
    
    def analyze_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        文本统计分析
        
        Args:
            text: 文本内容
            
        Returns:
            文本统计信息
        """
        if not text or not text.strip():
            return {}
        
        try:
            # 基础统计
            char_count = len(text)
            word_count = len(text.split())
            
            # 使用NLTK进行更精确的分析
            try:
                sentences = sent_tokenize(text)
                sentence_count = len(sentences)
            except LookupError:
                # 如果NLTK数据缺失，使用简单方法
                sentence_count = text.count('.') + text.count('!') + text.count('?') + 1
                sentence_count = max(1, sentence_count)  # 至少一句
            
            try:
                tokens = word_tokenize(text)
                unique_words = len(set(token.lower() for token in tokens if token.isalpha()))
            except LookupError:
                # 简单分词
                tokens = text.split()
                unique_words = len(set(token.lower() for token in tokens if token.isalpha()))
            
            # 平均句子长度
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # 词汇丰富度（类型/词型比）
            lexical_diversity = unique_words / word_count if word_count > 0 else 0
            
            # 可读性评分（简化版）
            if sentence_count > 0 and word_count > 0:
                # Flesch Reading Ease的简化版本
                avg_words_per_sentence = word_count / sentence_count
                avg_syllables_per_word = self._estimate_syllables(text) / word_count
                
                readability_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
                readability_score = max(0, min(100, readability_score))  # 限制在0-100范围
            else:
                readability_score = 50  # 默认中等难度
            
            return {
                'character_count': char_count,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'unique_words': unique_words,
                'avg_sentence_length': round(avg_sentence_length, 2),
                'lexical_diversity': round(lexical_diversity, 3),
                'readability_score': round(readability_score, 1),
                'estimated_reading_time': round(word_count / 200, 1)  # 假设每分钟200词
            }
            
        except Exception as e:
            logger.error(f"文本统计分析失败: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 移除@用户名
        text = re.sub(r'@\w+', '', text)
        
        # 移除#标签
        text = re.sub(r'#\w+', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _estimate_syllables(self, text: str) -> int:
        """估算音节数（用于可读性计算）"""
        words = text.split()
        total_syllables = 0
        
        for word in words:
            word = word.lower().strip(".,!?;:")
            if word:
                # 简单的音节估算规则
                syllables = max(1, len(re.findall(r'[aeiouAEIOU]', word)))
                if word.endswith('e'):
                    syllables -= 1
                if syllables == 0:
                    syllables = 1
                total_syllables += syllables
        
        return total_syllables
    
    def batch_analyze_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量文本分析
        
        Args:
            texts: 文本列表
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = {
                    'index': i,
                    'text_preview': text[:100] + '...' if len(text) > 100 else text,
                    'sentiment': self.analyze_sentiment_comprehensive(text),
                    'keywords': self.extract_keywords(text, max_keywords=10),
                    'entities': self.extract_entities(text),
                    'statistics': self.analyze_text_statistics(text)
                }
                results.append(result)
                
            except Exception as e:
                logger.error(f"批量分析第{i}个文本失败: {e}")
                results.append({
                    'index': i,
                    'error': str(e),
                    'text_preview': text[:100] + '...' if len(text) > 100 else text
                })
        
        logger.info(f"批量分析完成，处理了 {len(texts)} 个文本")
        return results
    
    async def analyze_with_monkeylearn(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        使用MonkeyLearn进行高级文本分析
        
        Args:
            texts: 文本列表
            
        Returns:
            包含MonkeyLearn分析结果的列表
        """
        if not MONKEYLEARN_AVAILABLE or not monkeylearn_service.available:
            logger.warning("MonkeyLearn服务不可用，跳过高级分析")
            return []
        
        try:
            return await monkeylearn_service.comprehensive_analysis(texts)
        except Exception as e:
            logger.error(f"MonkeyLearn分析失败: {e}")
            return []
    
    async def comprehensive_analysis_with_monkeylearn(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        综合分析（本地VADER/TextBlob + MonkeyLearn）
        
        Args:
            texts: 文本列表
            
        Returns:
            综合分析结果列表
        """
        # 执行本地分析
        local_results = self.batch_analyze_texts(texts)
        
        # 执行MonkeyLearn分析（如果可用）
        monkeylearn_results = await self.analyze_with_monkeylearn(texts)
        
        # 合并结果
        comprehensive_results = []
        for i, text in enumerate(texts):
            local_result = local_results[i] if i < len(local_results) else {}
            ml_result = monkeylearn_results[i] if i < len(monkeylearn_results) else {}
            
            # 合并分析结果
            comprehensive_result = {
                'text': text,
                'index': i,
                'local_analysis': {
                    'sentiment': local_result.get('sentiment', {}),
                    'keywords': local_result.get('keywords', []),
                    'entities': local_result.get('entities', []),
                    'statistics': local_result.get('statistics', {})
                },
                'monkeylearn_analysis': ml_result.get('monkeylearn_analysis', None),
                'combined_insights': self._generate_combined_insights(
                    local_result.get('sentiment', {}),
                    ml_result.get('monkeylearn_analysis', {})
                )
            }
            
            comprehensive_results.append(comprehensive_result)
        
        logger.info(f"综合分析完成，处理了 {len(texts)} 个文本")
        return comprehensive_results
    
    def _generate_combined_insights(self, local_sentiment: Dict, ml_analysis: Dict) -> Dict[str, Any]:
        """生成综合洞察"""
        insights = {
            'confidence_boost': False,
            'sentiment_consensus': False,
            'enhanced_analysis': False,
            'notes': []
        }
        
        if not ml_analysis or not ml_analysis.get('api_available'):
            insights['notes'].append('仅使用本地分析（VADER/TextBlob）')
            return insights
        
        # 检查情感一致性
        local_sentiment_label = local_sentiment.get('sentiment', 'neutral')
        ml_sentiment = ml_analysis.get('sentiment', {})
        
        if ml_sentiment and ml_sentiment.get('sentiment'):
            ml_sentiment_label = ml_sentiment.get('sentiment', 'neutral')
            
            if local_sentiment_label == ml_sentiment_label:
                insights['sentiment_consensus'] = True
                insights['confidence_boost'] = True
                insights['notes'].append(f'情感分析一致：{local_sentiment_label}')
            else:
                insights['notes'].append(f'情感分析差异：本地={local_sentiment_label}, ML={ml_sentiment_label}')
        
        # 检查高级功能
        if ml_analysis.get('topics'):
            insights['enhanced_analysis'] = True
            topics = ml_analysis['topics'].get('topics', [])
            if topics:
                insights['notes'].append(f'主题分类：{topics[:3]}')
        
        if ml_analysis.get('intent'):
            intent = ml_analysis['intent'].get('intent', 'unknown')
            if intent != 'unknown':
                insights['notes'].append(f'意图识别：{intent}')
        
        return insights

# 全局实例
enhanced_text_analysis_service = EnhancedTextAnalysisService()