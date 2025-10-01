"""
AI智能分析服务
实现情感分析、趋势预测、个性化推荐等AI增强功能
"""

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sqlalchemy.orm import Session
from ..data.models.database import get_db
from ..core.redis_client import redis_client
from ..core.config import settings

logger = logging.getLogger(__name__)

class SentimentType(Enum):
    """情感类型"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class TrendDirection(Enum):
    """趋势方向"""
    UPWARD = "upward"
    DOWNWARD = "downward"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class SentimentResult:
    """情感分析结果"""
    sentiment: SentimentType
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float
    emotions: Dict[str, float]

@dataclass
class TrendPrediction:
    """趋势预测结果"""
    direction: TrendDirection
    confidence: float
    predicted_values: List[float]
    time_horizon: int
    factors: List[str]
    accuracy_score: float

@dataclass
class RecommendationItem:
    """推荐项目"""
    item_id: str
    title: str
    description: str
    score: float
    reason: str
    category: str
    metadata: Dict[str, Any]

@dataclass
class PersonalizedRecommendations:
    """个性化推荐结果"""
    user_id: str
    recommendations: List[RecommendationItem]
    total_score: float
    diversity_score: float
    novelty_score: float
    explanation: str

class AIAnalysisService:
    """AI智能分析服务"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.emotion_classifier = None
        self.trend_model = None
        self.recommendation_model = None
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.scaler = StandardScaler()
        
        # 初始化模型
        self._initialize_models()
        
        # 缓存配置
        self.cache_ttl = 3600  # 1小时
        
    def _initialize_models(self):
        """初始化AI模型"""
        try:
            # 初始化NLTK情感分析器
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                except Exception as e:
                    logger.warning(f"Failed to download NLTK vader_lexicon: {e}")
                    # 继续运行，不阻止服务启动
            
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # 暂时跳过Transformers情感分析模型以避免网络问题
            logger.warning("Skipping Hugging Face model loading due to network issues")
            self.emotion_classifier = None
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
    
    async def analyze_sentiment(self, text: str, use_advanced: bool = True) -> SentimentResult:
        """
        分析文本情感
        
        Args:
            text: 待分析的文本
            use_advanced: 是否使用高级模型
            
        Returns:
            情感分析结果
        """
        try:
            # 检查缓存
            cache_key = f"sentiment:{hash(text)}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return SentimentResult(**json.loads(cached_result))
            
            # VADER情感分析
            vader_scores = self.sentiment_analyzer.polarity_scores(text)
            
            # TextBlob情感分析
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # 情感分类
            if vader_scores['compound'] >= 0.05:
                sentiment = SentimentType.POSITIVE
            elif vader_scores['compound'] <= -0.05:
                sentiment = SentimentType.NEGATIVE
            else:
                sentiment = SentimentType.NEUTRAL
            
            # 置信度计算
            confidence = abs(vader_scores['compound'])
            
            # 情绪分析（如果可用）
            emotions = {}
            if use_advanced and self.emotion_classifier:
                try:
                    emotion_results = self.emotion_classifier(text[:512])  # 限制长度
                    emotions = {result['label']: result['score'] for result in emotion_results[0]}
                except Exception as e:
                    logger.warning(f"Emotion classification failed: {e}")
            
            result = SentimentResult(
                sentiment=sentiment,
                confidence=confidence,
                positive_score=vader_scores['pos'],
                negative_score=vader_scores['neg'],
                neutral_score=vader_scores['neu'],
                compound_score=vader_scores['compound'],
                emotions=emotions
            )
            
            # 缓存结果
            await redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result.__dict__, default=str)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentResult(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0,
                compound_score=0.0,
                emotions={}
            )
    
    async def predict_trends(
        self,
        data: List[Dict[str, Any]],
        target_column: str,
        time_horizon: int = 30
    ) -> TrendPrediction:
        """
        预测趋势
        
        Args:
            data: 历史数据
            target_column: 目标列名
            time_horizon: 预测时间范围（天）
            
        Returns:
            趋势预测结果
        """
        try:
            # 检查缓存
            cache_key = f"trend:{hash(str(data))}{target_column}{time_horizon}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return TrendPrediction(**json.loads(cached_result))
            
            # 数据预处理
            df = pd.DataFrame(data)
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")
            
            # 时间序列特征工程
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['hour'] = df['timestamp'].dt.hour
                df['month'] = df['timestamp'].dt.month
            
            # 创建滞后特征
            for lag in [1, 3, 7]:
                df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
            
            # 移动平均特征
            for window in [3, 7, 14]:
                df[f'{target_column}_ma_{window}'] = df[target_column].rolling(window=window).mean()
            
            # 删除包含NaN的行
            df = df.dropna()
            
            if len(df) < 10:
                raise ValueError("Insufficient data for trend prediction")
            
            # 准备特征和目标
            feature_columns = [col for col in df.columns if col not in [target_column, 'timestamp']]
            X = df[feature_columns]
            y = df[target_column]
            
            # 训练模型
            if len(X) > 50:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            else:
                X_train, X_test, y_train, y_test = X, X, y, y
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 计算准确性
            accuracy_score = model.score(X_test, y_test)
            
            # 预测未来值
            last_row = df.iloc[-1:][feature_columns]
            predicted_values = []
            
            for i in range(time_horizon):
                pred = model.predict(last_row)[0]
                predicted_values.append(pred)
                
                # 更新特征用于下一次预测
                # 这里简化处理，实际应用中需要更复杂的逻辑
                last_row = last_row.copy()
                for col in last_row.columns:
                    if 'lag_1' in col:
                        last_row[col] = pred
            
            # 确定趋势方向
            current_value = df[target_column].iloc[-1]
            future_value = np.mean(predicted_values[-7:])  # 最后一周的平均值
            
            change_ratio = (future_value - current_value) / current_value if current_value != 0 else 0
            
            if change_ratio > 0.05:
                direction = TrendDirection.UPWARD
            elif change_ratio < -0.05:
                direction = TrendDirection.DOWNWARD
            else:
                direction = TrendDirection.STABLE
            
            # 计算波动性
            volatility = np.std(predicted_values) / np.mean(predicted_values) if np.mean(predicted_values) != 0 else 0
            if volatility > 0.2:
                direction = TrendDirection.VOLATILE
            
            # 特征重要性
            feature_importance = model.feature_importances_
            important_factors = [
                feature_columns[i] for i in np.argsort(feature_importance)[-5:][::-1]
            ]
            
            result = TrendPrediction(
                direction=direction,
                confidence=min(accuracy_score, 1.0),
                predicted_values=predicted_values,
                time_horizon=time_horizon,
                factors=important_factors,
                accuracy_score=accuracy_score
            )
            
            # 缓存结果
            await redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result.__dict__, default=str)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting trends: {e}")
            return TrendPrediction(
                direction=TrendDirection.STABLE,
                confidence=0.0,
                predicted_values=[],
                time_horizon=time_horizon,
                factors=[],
                accuracy_score=0.0
            )
    
    async def generate_personalized_recommendations(
        self,
        user_id: str,
        user_profile: Dict[str, Any],
        items: List[Dict[str, Any]],
        num_recommendations: int = 10
    ) -> PersonalizedRecommendations:
        """
        生成个性化推荐
        
        Args:
            user_id: 用户ID
            user_profile: 用户画像
            items: 候选项目列表
            num_recommendations: 推荐数量
            
        Returns:
            个性化推荐结果
        """
        try:
            # 检查缓存
            cache_key = f"recommendations:{user_id}:{hash(str(user_profile))}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return PersonalizedRecommendations(**json.loads(cached_result))
            
            if not items:
                return PersonalizedRecommendations(
                    user_id=user_id,
                    recommendations=[],
                    total_score=0.0,
                    diversity_score=0.0,
                    novelty_score=0.0,
                    explanation="No items available for recommendation"
                )
            
            # 用户兴趣向量化
            user_interests = user_profile.get('interests', [])
            user_categories = user_profile.get('preferred_categories', [])
            user_history = user_profile.get('interaction_history', [])
            
            # 计算推荐分数
            recommendations = []
            
            for item in items:
                score = await self._calculate_recommendation_score(
                    user_profile, item, user_history
                )
                
                if score > 0.1:  # 最低阈值
                    recommendations.append(RecommendationItem(
                        item_id=item.get('id', str(hash(str(item)))),
                        title=item.get('title', 'Unknown'),
                        description=item.get('description', ''),
                        score=score,
                        reason=self._generate_recommendation_reason(user_profile, item, score),
                        category=item.get('category', 'general'),
                        metadata=item.get('metadata', {})
                    ))
            
            # 排序并选择top N
            recommendations.sort(key=lambda x: x.score, reverse=True)
            top_recommendations = recommendations[:num_recommendations]
            
            # 多样性优化
            if len(top_recommendations) > 5:
                top_recommendations = self._optimize_diversity(top_recommendations)
            
            # 计算指标
            total_score = sum(rec.score for rec in top_recommendations)
            diversity_score = self._calculate_diversity_score(top_recommendations)
            novelty_score = self._calculate_novelty_score(top_recommendations, user_history)
            
            result = PersonalizedRecommendations(
                user_id=user_id,
                recommendations=top_recommendations,
                total_score=total_score,
                diversity_score=diversity_score,
                novelty_score=novelty_score,
                explanation=self._generate_recommendation_explanation(
                    user_profile, top_recommendations
                )
            )
            
            # 缓存结果
            await redis_client.setex(
                cache_key,
                self.cache_ttl // 2,  # 推荐结果缓存时间较短
                json.dumps(result.__dict__, default=str)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return PersonalizedRecommendations(
                user_id=user_id,
                recommendations=[],
                total_score=0.0,
                diversity_score=0.0,
                novelty_score=0.0,
                explanation=f"Error generating recommendations: {str(e)}"
            )
    
    async def analyze_text_insights(self, texts: List[str]) -> Dict[str, Any]:
        """
        分析文本洞察
        
        Args:
            texts: 文本列表
            
        Returns:
            文本洞察分析结果
        """
        try:
            if not texts:
                return {"error": "No texts provided"}
            
            # 情感分析
            sentiment_results = []
            for text in texts:
                sentiment = await self.analyze_sentiment(text)
                sentiment_results.append(sentiment)
            
            # 聚合情感统计
            positive_count = sum(1 for s in sentiment_results if s.sentiment == SentimentType.POSITIVE)
            negative_count = sum(1 for s in sentiment_results if s.sentiment == SentimentType.NEGATIVE)
            neutral_count = sum(1 for s in sentiment_results if s.sentiment == SentimentType.NEUTRAL)
            
            avg_compound = np.mean([s.compound_score for s in sentiment_results])
            
            # 关键词提取
            combined_text = " ".join(texts)
            keywords = self._extract_keywords(combined_text)
            
            # 主题聚类
            topics = await self._extract_topics(texts)
            
            # 情绪分布
            emotion_distribution = {}
            for sentiment in sentiment_results:
                for emotion, score in sentiment.emotions.items():
                    if emotion not in emotion_distribution:
                        emotion_distribution[emotion] = []
                    emotion_distribution[emotion].append(score)
            
            # 计算平均情绪分数
            avg_emotions = {
                emotion: np.mean(scores) 
                for emotion, scores in emotion_distribution.items()
            }
            
            return {
                "total_texts": len(texts),
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "positive_ratio": positive_count / len(texts),
                    "negative_ratio": negative_count / len(texts),
                    "neutral_ratio": neutral_count / len(texts)
                },
                "average_sentiment_score": avg_compound,
                "keywords": keywords,
                "topics": topics,
                "emotion_distribution": avg_emotions,
                "insights": self._generate_text_insights(
                    sentiment_results, keywords, topics, avg_emotions
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text insights: {e}")
            return {"error": str(e)}
    
    # 私有方法
    
    async def _calculate_recommendation_score(
        self,
        user_profile: Dict[str, Any],
        item: Dict[str, Any],
        user_history: List[str]
    ) -> float:
        """计算推荐分数"""
        score = 0.0
        
        # 兴趣匹配
        user_interests = user_profile.get('interests', [])
        item_tags = item.get('tags', [])
        
        if user_interests and item_tags:
            interest_match = len(set(user_interests) & set(item_tags)) / len(set(user_interests) | set(item_tags))
            score += interest_match * 0.4
        
        # 类别偏好
        user_categories = user_profile.get('preferred_categories', [])
        item_category = item.get('category', '')
        
        if item_category in user_categories:
            score += 0.3
        
        # 流行度
        item_popularity = item.get('popularity_score', 0.5)
        score += item_popularity * 0.2
        
        # 新颖性（避免推荐用户已经见过的内容）
        item_id = item.get('id', '')
        if item_id not in user_history:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendation_reason(
        self,
        user_profile: Dict[str, Any],
        item: Dict[str, Any],
        score: float
    ) -> str:
        """生成推荐理由"""
        reasons = []
        
        user_interests = user_profile.get('interests', [])
        item_tags = item.get('tags', [])
        common_interests = set(user_interests) & set(item_tags)
        
        if common_interests:
            reasons.append(f"匹配您的兴趣: {', '.join(list(common_interests)[:3])}")
        
        if item.get('category') in user_profile.get('preferred_categories', []):
            reasons.append(f"属于您偏好的类别: {item.get('category')}")
        
        if score > 0.8:
            reasons.append("高度推荐")
        elif score > 0.6:
            reasons.append("推荐")
        
        return "; ".join(reasons) if reasons else "基于您的个人偏好"
    
    def _optimize_diversity(self, recommendations: List[RecommendationItem]) -> List[RecommendationItem]:
        """优化推荐多样性"""
        if len(recommendations) <= 5:
            return recommendations
        
        # 按类别分组
        category_groups = {}
        for rec in recommendations:
            category = rec.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(rec)
        
        # 从每个类别选择最佳项目
        diverse_recommendations = []
        max_per_category = max(1, len(recommendations) // len(category_groups))
        
        for category, items in category_groups.items():
            diverse_recommendations.extend(items[:max_per_category])
        
        # 按分数排序
        diverse_recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return diverse_recommendations[:len(recommendations)]
    
    def _calculate_diversity_score(self, recommendations: List[RecommendationItem]) -> float:
        """计算多样性分数"""
        if not recommendations:
            return 0.0
        
        categories = [rec.category for rec in recommendations]
        unique_categories = len(set(categories))
        total_categories = len(categories)
        
        return unique_categories / total_categories if total_categories > 0 else 0.0
    
    def _calculate_novelty_score(
        self,
        recommendations: List[RecommendationItem],
        user_history: List[str]
    ) -> float:
        """计算新颖性分数"""
        if not recommendations:
            return 0.0
        
        novel_items = sum(1 for rec in recommendations if rec.item_id not in user_history)
        return novel_items / len(recommendations)
    
    def _generate_recommendation_explanation(
        self,
        user_profile: Dict[str, Any],
        recommendations: List[RecommendationItem]
    ) -> str:
        """生成推荐解释"""
        if not recommendations:
            return "暂无推荐内容"
        
        explanations = []
        
        # 分析推荐的主要类别
        categories = [rec.category for rec in recommendations]
        main_category = max(set(categories), key=categories.count)
        explanations.append(f"主要推荐{main_category}类别的内容")
        
        # 分析用户兴趣匹配
        user_interests = user_profile.get('interests', [])
        if user_interests:
            explanations.append(f"基于您对{', '.join(user_interests[:3])}的兴趣")
        
        # 分析推荐质量
        avg_score = np.mean([rec.score for rec in recommendations])
        if avg_score > 0.8:
            explanations.append("推荐质量很高")
        elif avg_score > 0.6:
            explanations.append("推荐质量良好")
        
        return "，".join(explanations)
    
    def _extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        try:
            # 使用TF-IDF提取关键词
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # 获取top-k关键词
            top_indices = np.argsort(tfidf_scores)[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def _extract_topics(self, texts: List[str], num_topics: int = 5) -> List[Dict[str, Any]]:
        """提取主题"""
        try:
            if len(texts) < 2:
                return []
            
            # 向量化文本
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # K-means聚类
            kmeans = KMeans(n_clusters=min(num_topics, len(texts)), random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # 提取每个主题的关键词
            feature_names = self.vectorizer.get_feature_names_out()
            topics = []
            
            for i in range(kmeans.n_clusters):
                # 获取聚类中心
                center = kmeans.cluster_centers_[i]
                top_indices = np.argsort(center)[-10:][::-1]
                keywords = [feature_names[idx] for idx in top_indices if center[idx] > 0]
                
                # 统计该主题的文档数量
                doc_count = np.sum(cluster_labels == i)
                
                topics.append({
                    "topic_id": i,
                    "keywords": keywords[:5],
                    "document_count": int(doc_count),
                    "weight": float(doc_count / len(texts))
                })
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def _generate_text_insights(
        self,
        sentiment_results: List[SentimentResult],
        keywords: List[str],
        topics: List[Dict[str, Any]],
        emotions: Dict[str, float]
    ) -> List[str]:
        """生成文本洞察"""
        insights = []
        
        # 情感洞察
        positive_ratio = sum(1 for s in sentiment_results if s.sentiment == SentimentType.POSITIVE) / len(sentiment_results)
        if positive_ratio > 0.7:
            insights.append("整体情感倾向积极正面")
        elif positive_ratio < 0.3:
            insights.append("整体情感倾向消极负面")
        else:
            insights.append("情感倾向相对中性")
        
        # 关键词洞察
        if keywords:
            insights.append(f"主要讨论话题包括: {', '.join(keywords[:5])}")
        
        # 主题洞察
        if topics:
            main_topic = max(topics, key=lambda x: x['weight'])
            insights.append(f"主要主题: {', '.join(main_topic['keywords'][:3])}")
        
        # 情绪洞察
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            if dominant_emotion[1] > 0.3:
                insights.append(f"主导情绪: {dominant_emotion[0]}")
        
        return insights

# 创建全局实例
ai_analysis_service = AIAnalysisService()