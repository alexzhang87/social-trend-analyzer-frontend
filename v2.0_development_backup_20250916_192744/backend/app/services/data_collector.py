import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from urllib.parse import quote

from ..core.config import settings

logger = logging.getLogger(__name__)

class DataCollector:
    """数据收集服务"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def collect_posts(
        self, 
        platform: str, 
        keyword: str, 
        time_range: str = "7d"
    ) -> List[Dict[str, Any]]:
        """收集指定平台的帖子数据"""
        try:
            if platform == "twitter":
                return await self._collect_twitter_data(keyword, time_range)
            elif platform == "reddit":
                return await self._collect_reddit_data(keyword, time_range)
            elif platform == "google_trends":
                return await self._collect_google_trends_data(keyword, time_range)
            else:
                logger.warning(f"不支持的平台: {platform}")
                return []
        except Exception as e:
            logger.error(f"收集{platform}数据失败: {str(e)}")
            return []
    
    async def _collect_twitter_data(self, keyword: str, time_range: str) -> List[Dict[str, Any]]:
        """收集Twitter数据"""
        try:
            # 模拟Twitter数据收集
            # 在实际实现中，这里会调用Twitter API或使用爬虫
            mock_posts = [
                {
                    "id": f"twitter_{i}",
                    "content": f"这是关于{keyword}的Twitter帖子 #{i}",
                    "author": f"user_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=i),
                    "metrics": {
                        "likes": 10 + i * 5,
                        "retweets": 2 + i,
                        "replies": 1 + i
                    },
                    "platform": "twitter"
                }
                for i in range(1, 11)
            ]
            
            logger.info(f"收集到{len(mock_posts)}条Twitter数据")
            return mock_posts
            
        except Exception as e:
            logger.error(f"Twitter数据收集失败: {str(e)}")
            return []
    
    async def _collect_reddit_data(self, keyword: str, time_range: str) -> List[Dict[str, Any]]:
        """收集Reddit数据"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Reddit搜索API
            search_url = f"https://www.reddit.com/search.json"
            params = {
                "q": keyword,
                "sort": "relevance",
                "t": "week" if time_range == "7d" else "month",
                "limit": 25
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for item in data.get("data", {}).get("children", []):
                        post_data = item.get("data", {})
                        posts.append({
                            "id": post_data.get("id"),
                            "content": post_data.get("title", "") + " " + post_data.get("selftext", ""),
                            "author": post_data.get("author"),
                            "created_at": datetime.fromtimestamp(post_data.get("created_utc", 0)),
                            "metrics": {
                                "score": post_data.get("score", 0),
                                "comments": post_data.get("num_comments", 0),
                                "upvote_ratio": post_data.get("upvote_ratio", 0)
                            },
                            "platform": "reddit",
                            "subreddit": post_data.get("subreddit")
                        })
                    
                    logger.info(f"收集到{len(posts)}条Reddit数据")
                    return posts
                else:
                    logger.error(f"Reddit API请求失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Reddit数据收集失败: {str(e)}")
            return []
    
    async def _collect_google_trends_data(self, keyword: str, time_range: str) -> List[Dict[str, Any]]:
        """收集Google Trends数据"""
        try:
            # 模拟Google Trends数据
            # 在实际实现中，这里会调用Google Trends API
            trend_data = [
                {
                    "id": f"trends_{i}",
                    "content": f"Google Trends显示{keyword}的搜索趋势数据点{i}",
                    "author": "Google Trends",
                    "created_at": datetime.utcnow() - timedelta(days=i),
                    "metrics": {
                        "search_volume": 100 - i * 5,
                        "interest_score": 80 + i * 2
                    },
                    "platform": "google_trends"
                }
                for i in range(1, 8)
            ]
            
            logger.info(f"收集到{len(trend_data)}条Google Trends数据")
            return trend_data
            
        except Exception as e:
            logger.error(f"Google Trends数据收集失败: {str(e)}")
            return []
    
    async def get_popular_topics(
        self, 
        platform: str = "all", 
        category: str = "general"
    ) -> Dict[str, Any]:
        """获取热门话题"""
        try:
            popular_data = {
                "topics": [
                    {"name": "人工智能", "score": 95, "growth": "+15%"},
                    {"name": "区块链", "score": 88, "growth": "+8%"},
                    {"name": "元宇宙", "score": 82, "growth": "+12%"},
                    {"name": "新能源汽车", "score": 79, "growth": "+6%"},
                    {"name": "量子计算", "score": 75, "growth": "+20%"}
                ],
                "hashtags": ["#AI", "#blockchain", "#metaverse", "#EV", "#quantum"],
                "viral_content": [
                    {
                        "title": "ChatGPT最新更新引发热议",
                        "engagement": 15000,
                        "platform": "twitter"
                    },
                    {
                        "title": "特斯拉新车型发布",
                        "engagement": 12000,
                        "platform": "reddit"
                    }
                ]
            }
            
            return popular_data
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {str(e)}")
            return {"topics": [], "hashtags": [], "viral_content": []}
    
    async def search_news(self, keyword: str, time_range: str = "7d") -> List[Dict[str, Any]]:
        """搜索新闻数据"""
        try:
            if not settings.NEWS_API_KEY:
                logger.warning("News API密钥未配置")
                return []
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            # News API搜索
            news_url = "https://newsapi.org/v2/everything"
            params = {
                "q": keyword,
                "apiKey": settings.NEWS_API_KEY,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "zh"
            }
            
            # 设置时间范围
            if time_range == "1d":
                from_date = datetime.utcnow() - timedelta(days=1)
            elif time_range == "7d":
                from_date = datetime.utcnow() - timedelta(days=7)
            else:
                from_date = datetime.utcnow() - timedelta(days=30)
            
            params["from"] = from_date.strftime("%Y-%m-%d")
            
            async with self.session.get(news_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = []
                    
                    for article in data.get("articles", []):
                        articles.append({
                            "id": f"news_{hash(article.get('url', ''))}",
                            "content": article.get("title", "") + " " + (article.get("description", "") or ""),
                            "author": article.get("source", {}).get("name", "Unknown"),
                            "created_at": datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00")),
                            "metrics": {
                                "source_authority": 80,  # 模拟权威性评分
                                "relevance": 90
                            },
                            "platform": "news",
                            "url": article.get("url")
                        })
                    
                    logger.info(f"收集到{len(articles)}条新闻数据")
                    return articles
                else:
                    logger.error(f"News API请求失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"新闻数据收集失败: {str(e)}")
            return []