"""
综合分析服务
整合所有数据源（Twitter、Reddit、Product Hunt、Google Trends）进行全面分析
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from .working_twitter_service import WorkingTwitterService
from .reddit_official_service import RedditOfficialService
from .product_hunt_service import ProductHuntOfficialService
from .google_trends_service import GoogleTrendsService
from .enhanced_text_analysis_service import enhanced_text_analysis_service

logger = logging.getLogger("trend-analyzer")

class ComprehensiveAnalysisService:
    """综合分析服务"""
    
    def __init__(self):
        self.twitter_service = WorkingTwitterService()
        self.reddit_service = RedditOfficialService()
        self.product_hunt_service = ProductHuntOfficialService()
        self.google_trends_service = GoogleTrendsService()
        
        logger.info("ComprehensiveAnalysisService 已初始化")
    
    async def analyze_trends_comprehensive(
        self, 
        keywords: List[str], 
        platforms: Optional[List[str]] = None,
        time_filter: str = "week",
        limit_per_platform: int = 50
    ) -> Dict[str, Any]:
        """
        综合趋势分析
        
        Args:
            keywords: 关键词列表
            platforms: 指定平台列表，如果为None则使用所有平台
            time_filter: 时间过滤器
            limit_per_platform: 每个平台的数据限制
            
        Returns:
            综合分析结果
        """
        start_time = datetime.now()
        
        if platforms is None:
            platforms = ['twitter', 'reddit', 'product_hunt', 'google_trends']
        
        logger.info(f"开始综合趋势分析: keywords={keywords}, platforms={platforms}")
        
        # 并行获取各平台数据
        platform_data = {}
        
        # 创建异步任务
        tasks = []
        
        if 'twitter' in platforms:
            tasks.append(self._get_twitter_data(keywords, limit_per_platform))
        if 'reddit' in platforms:
            tasks.append(self._get_reddit_data(keywords, time_filter, limit_per_platform))
        if 'product_hunt' in platforms:
            tasks.append(self._get_product_hunt_data(keywords, limit_per_platform))
        if 'google_trends' in platforms:
            tasks.append(self._get_google_trends_data(keywords, time_filter))
        
        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        platform_keys = [p for p in platforms if p in ['twitter', 'reddit', 'product_hunt', 'google_trends']]
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"平台 {platform_keys[i]} 数据获取失败: {result}")
                platform_data[platform_keys[i]] = []
            else:
                platform_data[platform_keys[i]] = result
        
        # 进行综合分析
        analysis_result = self._perform_comprehensive_analysis(
            platform_data, keywords, time_filter
        )
        
        analysis_result['processing_time'] = (datetime.now() - start_time).total_seconds()
        analysis_result['analyzed_at'] = datetime.now().isoformat()
        
        logger.info(f"综合趋势分析完成，用时 {analysis_result['processing_time']:.2f} 秒")
        return analysis_result
    
    async def _get_twitter_data(self, keywords: List[str], limit: int) -> List[Dict[str, Any]]:
        """获取Twitter数据"""
        try:
            query = " OR ".join(keywords)
            return self.twitter_service.search_tweets_enhanced(query, limit)
        except Exception as e:
            logger.error(f"获取Twitter数据失败: {e}")
            return []
    
    async def _get_reddit_data(self, keywords: List[str], time_filter: str, limit: int) -> List[Dict[str, Any]]:
        """获取Reddit数据"""
        try:
            return await self.reddit_service.search_posts_enhanced(keywords, limit, time_filter)
        except Exception as e:
            logger.error(f"获取Reddit数据失败: {e}")
            return []
    
    async def _get_product_hunt_data(self, keywords: List[str], limit: int) -> List[Dict[str, Any]]:
        """获取Product Hunt数据"""
        try:
            # 获取今日产品
            products = await self.product_hunt_service.get_daily_products_enhanced(limit=limit)
            
            # 基于关键词过滤
            relevant_products = []
            for product in products:
                content_lower = product.get('content', '').lower()
                if any(keyword.lower() in content_lower for keyword in keywords):
                    relevant_products.append(product)
            
            return relevant_products
        except Exception as e:
            logger.error(f"获取Product Hunt数据失败: {e}")
            return []
    
    async def _get_google_trends_data(self, keywords: List[str], time_filter: str) -> Dict[str, Any]:
        """获取Google Trends数据"""
        try:
            # 转换时间过滤器格式
            timeframe_map = {
                'hour': 'now 1-H',
                'day': 'today 1-d',
                'week': 'today 7-d',
                'month': 'today 1-m',
                'year': 'today 12-m'
            }
            timeframe = timeframe_map.get(time_filter, 'today 7-d')
            
            # 获取时间趋势数据
            trends_data = self.google_trends_service.get_interest_over_time(
                keywords[:5], timeframe  # Google Trends限制最多5个关键词
            )
            
            return trends_data
        except Exception as e:
            logger.error(f"获取Google Trends数据失败: {e}")
            return {}
    
    def _perform_comprehensive_analysis(
        self, 
        platform_data: Dict[str, Any], 
        keywords: List[str], 
        time_filter: str
    ) -> Dict[str, Any]:
        """执行综合分析"""
        
        # 统计各平台数据量
        platform_stats = {}
        total_posts = 0
        
        for platform, data in platform_data.items():
            if platform == 'google_trends':
                platform_stats[platform] = {
                    'data_points': len(data.get('data', [])),
                    'keywords_covered': len(data.get('keywords', []))
                }
            else:
                count = len(data) if isinstance(data, list) else 0
                platform_stats[platform] = {'posts_count': count}
                total_posts += count
        
        # 综合情感分析
        sentiment_analysis = self._analyze_cross_platform_sentiment(platform_data)
        
        # 热门关键词分析
        keyword_analysis = self._analyze_cross_platform_keywords(platform_data)
        
        # 平台对比分析
        platform_comparison = self._compare_platforms(platform_data)
        
        # 趋势评分
        trend_score = self._calculate_comprehensive_trend_score(platform_data, keywords)
        
        # 生成洞察
        insights = self._generate_comprehensive_insights(
            platform_data, sentiment_analysis, keyword_analysis, trend_score
        )
        
        return {
            'keywords': keywords,
            'time_filter': time_filter,
            'platform_stats': platform_stats,
            'total_posts_analyzed': total_posts,
            'sentiment_analysis': sentiment_analysis,
            'keyword_analysis': keyword_analysis,
            'platform_comparison': platform_comparison,
            'trend_score': trend_score,
            'insights': insights,
            'google_trends_data': platform_data.get('google_trends', {}),
            'detailed_platform_data': {
                platform: data[:5] if isinstance(data, list) else data 
                for platform, data in platform_data.items()
            }
        }
    
    def _analyze_cross_platform_sentiment(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """跨平台情感分析"""
        all_sentiments = []
        platform_sentiments = {}
        
        for platform, data in platform_data.items():
            if platform == 'google_trends' or not isinstance(data, list):
                continue
            
            sentiments = []
            for item in data:
                text_analysis = item.get('text_analysis', {})
                sentiment_data = text_analysis.get('sentiment', {})
                if sentiment_data:
                    sentiment = sentiment_data.get('sentiment', 'neutral')
                    confidence = sentiment_data.get('confidence', 0)
                    sentiments.append((sentiment, confidence))
                    all_sentiments.append((sentiment, confidence))
            
            # 平台情感统计
            if sentiments:
                sentiment_counts = Counter([s[0] for s in sentiments])
                avg_confidence = statistics.mean([s[1] for s in sentiments])
                
                platform_sentiments[platform] = {
                    'sentiment_distribution': dict(sentiment_counts),
                    'total_analyzed': len(sentiments),
                    'average_confidence': round(avg_confidence, 3),
                    'dominant_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral'
                }
        
        # 整体情感分析
        if all_sentiments:
            overall_sentiment_counts = Counter([s[0] for s in all_sentiments])
            overall_confidence = statistics.mean([s[1] for s in all_sentiments])
            
            return {
                'overall_sentiment': overall_sentiment_counts.most_common(1)[0][0],
                'overall_confidence': round(overall_confidence, 3),
                'sentiment_distribution': dict(overall_sentiment_counts),
                'platform_breakdown': platform_sentiments,
                'total_analyzed': len(all_sentiments)
            }
        
        return {
            'overall_sentiment': 'neutral',
            'overall_confidence': 0.0,
            'sentiment_distribution': {'neutral': 1},
            'platform_breakdown': platform_sentiments,
            'total_analyzed': 0
        }
    
    def _analyze_cross_platform_keywords(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """跨平台关键词分析"""
        all_keywords = Counter()
        platform_keywords = {}
        
        for platform, data in platform_data.items():
            if platform == 'google_trends' or not isinstance(data, list):
                continue
            
            platform_keyword_counter = Counter()
            
            for item in data:
                text_analysis = item.get('text_analysis', {})
                keywords_data = text_analysis.get('keywords', [])
                
                for keyword_info in keywords_data:
                    word = keyword_info.get('word', '').lower()
                    frequency = keyword_info.get('frequency', 1)
                    
                    if word and len(word) > 2:  # 过滤太短的词
                        all_keywords[word] += frequency
                        platform_keyword_counter[word] += frequency
            
            # 平台关键词统计
            if platform_keyword_counter:
                platform_keywords[platform] = {
                    'top_keywords': [{
                        'word': word,
                        'frequency': freq
                    } for word, freq in platform_keyword_counter.most_common(10)],
                    'unique_keywords': len(platform_keyword_counter)
                }
        
        # 整体关键词分析
        top_keywords = [{
            'word': word,
            'frequency': freq,
            'platforms': [p for p, data in platform_keywords.items() 
                         if any(kw['word'] == word for kw in data['top_keywords'])]
        } for word, freq in all_keywords.most_common(20)]
        
        return {
            'top_keywords': top_keywords,
            'total_unique_keywords': len(all_keywords),
            'platform_breakdown': platform_keywords
        }
    
    def _compare_platforms(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """平台对比分析"""
        comparison = {}
        
        for platform, data in platform_data.items():
            if platform == 'google_trends':
                # Google Trends特殊处理
                trends_data = data.get('data', [])
                if trends_data:
                    values = []
                    for point in trends_data:
                        for keyword in data.get('keywords', []):
                            if keyword in point:
                                values.append(point[keyword])
                    
                    comparison[platform] = {
                        'data_points': len(trends_data),
                        'average_interest': round(statistics.mean(values), 2) if values else 0,
                        'peak_interest': max(values) if values else 0,
                        'trend_direction': 'stable'  # 简化的趋势方向
                    }
                continue
            
            if not isinstance(data, list) or not data:
                comparison[platform] = {
                    'posts_count': 0,
                    'average_score': 0,
                    'engagement_rate': 0
                }
                continue
            
            # 计算平台指标
            scores = [item.get('score', 0) for item in data]
            engagement_scores = []
            
            for item in data:
                platform_specific = item.get('platform_specific', {})
                if platform == 'reddit':
                    engagement = platform_specific.get('num_comments', 0) + platform_specific.get('awards', 0)
                elif platform == 'product_hunt':
                    engagement = platform_specific.get('comments_count', 0)
                elif platform == 'twitter':
                    engagement = platform_specific.get('retweet_count', 0) + platform_specific.get('favorite_count', 0)
                else:
                    engagement = 0
                
                engagement_scores.append(engagement)
            
            comparison[platform] = {
                'posts_count': len(data),
                'average_score': round(statistics.mean(scores), 2) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'average_engagement': round(statistics.mean(engagement_scores), 2) if engagement_scores else 0,
                'total_engagement': sum(engagement_scores)
            }
        
        return comparison
    
    def _calculate_comprehensive_trend_score(self, platform_data: Dict[str, Any], keywords: List[str]) -> float:
        """计算综合趋势评分"""
        score = 0.0
        weight_sum = 0.0
        
        # 平台权重配置
        platform_weights = {
            'google_trends': 0.3,
            'twitter': 0.25,
            'reddit': 0.25,
            'product_hunt': 0.2
        }
        
        for platform, data in platform_data.items():
            weight = platform_weights.get(platform, 0.1)
            platform_score = 0.0
            
            if platform == 'google_trends':
                # Google Trends评分基于搜索兴趣
                trends_data = data.get('data', [])
                if trends_data:
                    values = []
                    for point in trends_data:
                        for keyword in data.get('keywords', []):
                            if keyword in point:
                                values.append(point[keyword])
                    
                    if values:
                        platform_score = statistics.mean(values) / 100.0  # 归一化到0-1
            
            elif isinstance(data, list) and data:
                # 其他平台基于内容量和参与度
                content_score = min(len(data) / 50.0, 1.0)  # 50个帖子为满分
                
                # 情感加权
                positive_count = sum(1 for item in data 
                                   if item.get('text_analysis', {})
                                       .get('sentiment', {})
                                       .get('sentiment') == 'positive')
                sentiment_score = positive_count / len(data) if data else 0
                
                platform_score = (content_score * 0.7 + sentiment_score * 0.3)
            
            score += platform_score * weight
            weight_sum += weight
        
        # 归一化评分
        final_score = (score / weight_sum) if weight_sum > 0 else 0.0
        return round(final_score * 100, 2)  # 转换为0-100分
    
    def _generate_comprehensive_insights(self, platform_data: Dict[str, Any], 
                                        sentiment_analysis: Dict[str, Any],
                                        keyword_analysis: Dict[str, Any],
                                        trend_score: float) -> List[str]:
        """生成综合洞察"""
        insights = []
        
        # 趋势强度洞察
        if trend_score >= 80:
            insights.append(f"🔥 趋势热度极高（{trend_score}分），建议重点关注")
        elif trend_score >= 60:
            insights.append(f"📈 趋势热度较高（{trend_score}分），具有潜力")
        elif trend_score >= 40:
            insights.append(f"📊 趋势热度中等（{trend_score}分），需要观察")
        else:
            insights.append(f"📉 趋势热度较低（{trend_score}分），关注度有限")
        
        # 情感洞察
        overall_sentiment = sentiment_analysis.get('overall_sentiment', 'neutral')
        sentiment_confidence = sentiment_analysis.get('overall_confidence', 0)
        
        if overall_sentiment == 'positive' and sentiment_confidence > 0.6:
            insights.append("😊 整体情感偏向积极，公众反应良好")
        elif overall_sentiment == 'negative' and sentiment_confidence > 0.6:
            insights.append("😟 整体情感偏向消极，需要关注负面反馈")
        else:
            insights.append("😐 整体情感中性，公众态度相对平静")
        
        # 平台对比洞察
        total_posts = sum(
            len(data) for data in platform_data.values() 
            if isinstance(data, list)
        )
        
        if total_posts > 100:
            insights.append(f"📢 跨平台讨论活跃，共分析了{total_posts}条相关内容")
        elif total_posts > 50:
            insights.append(f"💬 有一定讨论热度，共分析了{total_posts}条相关内容")
        else:
            insights.append(f"🔍 讨论相对较少，共分析了{total_posts}条相关内容")
        
        # 关键词洞察
        top_keywords = keyword_analysis.get('top_keywords', [])[:5]
        if top_keywords:
            keyword_names = [kw['word'] for kw in top_keywords]
            insights.append(f"🏷️ 热门关键词：{', '.join(keyword_names)}")
        
        # Google Trends洞察
        google_trends_data = platform_data.get('google_trends', {})
        if google_trends_data.get('data'):
            insights.append("📊 Google搜索趋势数据已整合，提供搜索热度参考")
        
        return insights

# 全局实例
comprehensive_analysis_service = ComprehensiveAnalysisService()