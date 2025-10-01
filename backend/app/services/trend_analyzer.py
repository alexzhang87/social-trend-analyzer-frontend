import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from collections import Counter, defaultdict
import statistics

from ..core.config import settings

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """趋势分析服务"""
    
    def __init__(self):
        # 情感词典（简化版）
        self.positive_words = {
            "好", "棒", "优秀", "完美", "喜欢", "爱", "赞", "支持", "推荐", "满意",
            "amazing", "great", "excellent", "perfect", "love", "like", "awesome", "fantastic"
        }
        
        self.negative_words = {
            "差", "烂", "糟糕", "失望", "讨厌", "恨", "反对", "不满", "问题", "错误",
            "bad", "terrible", "awful", "hate", "dislike", "disappointed", "problem", "issue"
        }
    
    async def analyze(
        self, 
        posts_data: List[Dict[str, Any]], 
        analysis_type: str = "sentiment"
    ) -> Dict[str, Any]:
        """分析帖子数据"""
        try:
            if not posts_data:
                return self._empty_analysis_result()
            
            result = {
                "total_posts": len(posts_data),
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if analysis_type == "sentiment" or analysis_type == "comprehensive":
                sentiment_result = await self._analyze_sentiment(posts_data)
                result.update(sentiment_result)
            
            if analysis_type == "volume" or analysis_type == "comprehensive":
                volume_result = await self._analyze_volume(posts_data)
                result.update(volume_result)
            
            if analysis_type == "engagement" or analysis_type == "comprehensive":
                engagement_result = await self._analyze_engagement(posts_data)
                result.update(engagement_result)
            
            # 计算综合趋势评分
            result["trending_score"] = self._calculate_trending_score(result)
            
            # 生成分析摘要
            result["summary"] = self._generate_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"趋势分析失败: {str(e)}")
            return self._empty_analysis_result()
    
    async def _analyze_sentiment(self, posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """情感分析"""
        try:
            sentiment_scores = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for post in posts_data:
                content = post.get("content", "").lower()
                score = self._calculate_sentiment_score(content)
                sentiment_scores.append(score)
                
                if score > 0.1:
                    positive_count += 1
                elif score < -0.1:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0
            
            return {
                "sentiment_score": round(avg_sentiment, 3),
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "sentiment_trend": self._calculate_sentiment_trend(posts_data)
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {str(e)}")
            return {"sentiment_score": 0, "sentiment_distribution": {}, "sentiment_trend": []}
    
    def _calculate_sentiment_score(self, content: str) -> float:
        """计算单条内容的情感分数"""
        words = re.findall(r'\b\w+\b', content.lower())
        positive_score = sum(1 for word in words if word in self.positive_words)
        negative_score = sum(1 for word in words if word in self.negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0
        
        # 归一化分数到 [-1, 1] 范围
        score = (positive_score - negative_score) / total_words
        return max(-1, min(1, score * 5))  # 放大并限制范围
    
    def _calculate_sentiment_trend(self, posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """计算情感趋势"""
        try:
            # 按时间分组计算情感趋势
            daily_sentiment = defaultdict(list)
            
            for post in posts_data:
                created_at = post.get("created_at")
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                elif not isinstance(created_at, datetime):
                    continue
                
                date_key = created_at.strftime("%Y-%m-%d")
                content = post.get("content", "")
                sentiment = self._calculate_sentiment_score(content)
                daily_sentiment[date_key].append(sentiment)
            
            trend_data = []
            for date, sentiments in sorted(daily_sentiment.items()):
                avg_sentiment = statistics.mean(sentiments) if sentiments else 0
                trend_data.append({
                    "date": date,
                    "sentiment": round(avg_sentiment, 3),
                    "post_count": len(sentiments)
                })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"情感趋势计算失败: {str(e)}")
            return []
    
    async def _analyze_volume(self, posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """音量分析（讨论热度）"""
        try:
            total_volume = len(posts_data)
            
            # 按平台分组
            platform_volume = Counter(post.get("platform", "unknown") for post in posts_data)
            
            # 按时间分组计算音量趋势
            daily_volume = defaultdict(int)
            for post in posts_data:
                created_at = post.get("created_at")
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                elif not isinstance(created_at, datetime):
                    continue
                
                date_key = created_at.strftime("%Y-%m-%d")
                daily_volume[date_key] += 1
            
            volume_trend = [
                {"date": date, "volume": count}
                for date, count in sorted(daily_volume.items())
            ]
            
            return {
                "volume": total_volume,
                "platform_distribution": dict(platform_volume),
                "volume_trend": volume_trend,
                "peak_day": max(daily_volume.items(), key=lambda x: x[1])[0] if daily_volume else None
            }
            
        except Exception as e:
            logger.error(f"音量分析失败: {str(e)}")
            return {"volume": 0, "platform_distribution": {}, "volume_trend": []}
    
    async def _analyze_engagement(self, posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """参与度分析"""
        try:
            engagement_scores = []
            total_likes = 0
            total_shares = 0
            total_comments = 0
            
            for post in posts_data:
                metrics = post.get("metrics", {})
                
                # 不同平台的参与度指标
                if post.get("platform") == "twitter":
                    likes = metrics.get("likes", 0)
                    retweets = metrics.get("retweets", 0)
                    replies = metrics.get("replies", 0)
                    engagement = likes + retweets * 2 + replies * 3
                elif post.get("platform") == "reddit":
                    score = metrics.get("score", 0)
                    comments = metrics.get("comments", 0)
                    engagement = score + comments * 2
                else:
                    engagement = sum(metrics.values()) if metrics else 0
                
                engagement_scores.append(engagement)
                total_likes += metrics.get("likes", metrics.get("score", 0))
                total_shares += metrics.get("retweets", 0)
                total_comments += metrics.get("replies", metrics.get("comments", 0))
            
            avg_engagement = statistics.mean(engagement_scores) if engagement_scores else 0
            engagement_rate = avg_engagement / len(posts_data) if posts_data else 0
            
            return {
                "engagement_rate": round(engagement_rate, 2),
                "total_engagement": sum(engagement_scores),
                "avg_engagement": round(avg_engagement, 2),
                "engagement_breakdown": {
                    "likes": total_likes,
                    "shares": total_shares,
                    "comments": total_comments
                }
            }
            
        except Exception as e:
            logger.error(f"参与度分析失败: {str(e)}")
            return {"engagement_rate": 0, "total_engagement": 0, "avg_engagement": 0}
    
    def _calculate_trending_score(self, analysis_result: Dict[str, Any]) -> float:
        """计算综合趋势评分"""
        try:
            # 基础分数
            base_score = 50
            
            # 音量权重 (0-30分)
            volume = analysis_result.get("volume", 0)
            volume_score = min(30, volume * 2)
            
            # 情感权重 (0-25分)
            sentiment = analysis_result.get("sentiment_score", 0)
            sentiment_score = max(0, (sentiment + 1) * 12.5)  # 转换到0-25范围
            
            # 参与度权重 (0-25分)
            engagement_rate = analysis_result.get("engagement_rate", 0)
            engagement_score = min(25, engagement_rate / 4)
            
            # 时间衰减因子
            time_factor = 1.0  # 可以根据数据新鲜度调整
            
            trending_score = (base_score + volume_score + sentiment_score + engagement_score) * time_factor
            return round(min(100, max(0, trending_score)), 2)
            
        except Exception as e:
            logger.error(f"趋势评分计算失败: {str(e)}")
            return 50.0
    
    def _generate_summary(self, analysis_result: Dict[str, Any]) -> str:
        """生成分析摘要"""
        try:
            volume = analysis_result.get("volume", 0)
            sentiment_score = analysis_result.get("sentiment_score", 0)
            engagement_rate = analysis_result.get("engagement_rate", 0)
            trending_score = analysis_result.get("trending_score", 0)
            
            # 情感描述
            if sentiment_score > 0.3:
                sentiment_desc = "积极"
            elif sentiment_score < -0.3:
                sentiment_desc = "消极"
            else:
                sentiment_desc = "中性"
            
            # 热度描述
            if trending_score > 80:
                trend_desc = "非常热门"
            elif trending_score > 60:
                trend_desc = "较为热门"
            elif trending_score > 40:
                trend_desc = "一般热度"
            else:
                trend_desc = "热度较低"
            
            summary = f"共分析{volume}条数据，整体情感倾向{sentiment_desc}（{sentiment_score:.2f}），" \
                     f"平均参与度{engagement_rate:.1f}，综合趋势评分{trending_score:.1f}分，" \
                     f"当前热度状态：{trend_desc}。"
            
            return summary
            
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            return "分析摘要生成失败"
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """返回空的分析结果"""
        return {
            "sentiment_score": 0,
            "volume": 0,
            "engagement_rate": 0,
            "trending_score": 0,
            "summary": "暂无数据可供分析",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def analyze_popular_content(self, popular_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析热门内容"""
        try:
            return {
                "topics": popular_data.get("topics", []),
                "hashtags": popular_data.get("hashtags", []),
                "viral_content": popular_data.get("viral_content", []),
                "analysis_summary": "热门内容分析完成"
            }
        except Exception as e:
            logger.error(f"热门内容分析失败: {str(e)}")
            return {"topics": [], "hashtags": [], "viral_content": []}
    
    async def analyze_historical_trends(
        self, 
        posts: List[Any], 
        keyword: str, 
        days: int
    ) -> Dict[str, Any]:
        """分析历史趋势"""
        try:
            # 转换数据格式
            posts_data = []
            for post in posts:
                posts_data.append({
                    "content": post.content,
                    "created_at": post.created_at,
                    "platform": post.platform,
                    "metrics": json.loads(post.engagement_metrics) if post.engagement_metrics else {}
                })
            
            # 按日期分组分析
            daily_analysis = defaultdict(list)
            for post_data in posts_data:
                date_key = post_data["created_at"].strftime("%Y-%m-%d")
                daily_analysis[date_key].append(post_data)
            
            trend_data = []
            sentiment_evolution = []
            volume_evolution = []
            
            for date, day_posts in sorted(daily_analysis.items()):
                day_result = await self.analyze(day_posts, "comprehensive")
                
                trend_data.append({
                    "date": date,
                    "trending_score": day_result.get("trending_score", 0),
                    "post_count": len(day_posts)
                })
                
                sentiment_evolution.append({
                    "date": date,
                    "sentiment": day_result.get("sentiment_score", 0)
                })
                
                volume_evolution.append({
                    "date": date,
                    "volume": len(day_posts)
                })
            
            # 生成洞察
            insights = self._generate_historical_insights(trend_data, sentiment_evolution, volume_evolution)
            
            return {
                "trend_data": trend_data,
                "sentiment_evolution": sentiment_evolution,
                "volume_evolution": volume_evolution,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"历史趋势分析失败: {str(e)}")
            return {"trend_data": [], "sentiment_evolution": [], "volume_evolution": [], "insights": []}
    
    def _generate_historical_insights(self, trend_data, sentiment_evolution, volume_evolution) -> List[str]:
        """生成历史趋势洞察"""
        insights = []
        
        try:
            if trend_data:
                # 趋势变化分析
                scores = [item["trending_score"] for item in trend_data]
                if len(scores) > 1:
                    if scores[-1] > scores[0]:
                        insights.append("整体趋势呈上升态势")
                    elif scores[-1] < scores[0]:
                        insights.append("整体趋势呈下降态势")
                    else:
                        insights.append("整体趋势保持稳定")
            
            if volume_evolution:
                # 音量变化分析
                volumes = [item["volume"] for item in volume_evolution]
                peak_day = max(volume_evolution, key=lambda x: x["volume"])
                insights.append(f"讨论高峰出现在{peak_day['date']}，共{peak_day['volume']}条讨论")
            
            if sentiment_evolution:
                # 情感变化分析
                sentiments = [item["sentiment"] for item in sentiment_evolution]
                avg_sentiment = statistics.mean(sentiments) if sentiments else 0
                if avg_sentiment > 0.2:
                    insights.append("整体情感倾向积极")
                elif avg_sentiment < -0.2:
                    insights.append("整体情感倾向消极")
                else:
                    insights.append("整体情感倾向中性")
            
        except Exception as e:
            logger.error(f"洞察生成失败: {str(e)}")
        
        return insights if insights else ["暂无足够数据生成洞察"]
    
    async def compare_keywords(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """比较关键词分析"""
        try:
            if not comparison_results:
                return {"summary": "无数据可比较"}
            
            # 找出最热门的关键词
            best_keyword = max(comparison_results, key=lambda x: x["metrics"].get("trending_score", 0))
            
            # 找出情感最积极的关键词
            most_positive = max(comparison_results, key=lambda x: x["metrics"].get("sentiment_score", 0))
            
            # 找出讨论量最大的关键词
            most_discussed = max(comparison_results, key=lambda x: x["metrics"].get("volume", 0))
            
            comparison_summary = {
                "best_performing": best_keyword["keyword"],
                "most_positive_sentiment": most_positive["keyword"],
                "most_discussed": most_discussed["keyword"],
                "summary": f"在比较的关键词中，'{best_keyword['keyword']}'表现最佳，" \
                          f"'{most_positive['keyword']}'情感最积极，" \
                          f"'{most_discussed['keyword']}'讨论量最大。"
            }
            
            return comparison_summary
            
        except Exception as e:
            logger.error(f"关键词比较分析失败: {str(e)}")
            return {"summary": "比较分析失败"}