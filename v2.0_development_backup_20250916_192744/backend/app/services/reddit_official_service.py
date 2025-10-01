"""
Reddit 官方API服务

使用Reddit官方API获取高质量数据，完全免费且稳定。

API文档：https://www.reddit.com/dev/api/
速率限制：每分钟60次请求（足够使用）
认证方式：OAuth2 或用户名密码认证

优势：
- 完全免费
- 数据质量高
- 官方支持，稳定可靠
- 丰富的搜索和过滤选项
"""

import aiohttp
import asyncio
import base64
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from ..services.enhanced_text_analysis_service import enhanced_text_analysis_service

logger = logging.getLogger(__name__)


class RedditOfficialService:
    """Reddit 官方API服务"""
    
    def __init__(self):
        # 从环境变量获取认证信息
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = "trend-analyzer:v1.0.0 (by /u/your_username)"
        
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://oauth.reddit.com"
        
        # API配置
        self.rate_limit_delay = 1.1  # 确保不超过60次/分钟
        
    async def _get_access_token(self) -> str:
        """获取或刷新访问令牌"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            logger.error("Reddit API认证信息不完整")
            raise ValueError("请配置Reddit API认证信息：REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
        
        # 构建认证
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://www.reddit.com/api/v1/access_token', 
                                      headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data['access_token']
                        expires_in = token_data.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("Reddit访问令牌获取成功")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Reddit认证失败: {response.status} - {error_text}")
                        raise Exception(f"Reddit认证失败: {response.status}")
        
        except Exception as e:
            logger.error(f"获取Reddit访问令牌失败: {e}")
            raise
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发起API请求"""
        token = await self._get_access_token()
        
        headers = {
            'Authorization': f'bearer {token}',
            'User-Agent': self.user_agent
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            await asyncio.sleep(self.rate_limit_delay)  # 速率限制
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        logger.warning("Reddit API速率限制，等待重试...")
                        await asyncio.sleep(60)  # 等待1分钟
                        return await self._make_api_request(endpoint, params)
                    else:
                        error_text = await response.text()
                        logger.error(f"Reddit API请求失败: {response.status} - {error_text}")
                        return {"data": {"children": []}}
        
        except Exception as e:
            logger.error(f"Reddit API请求异常: {e}")
            return {"data": {"children": []}}
    
    async def search_posts(self, keywords: List[str], limit: int = 100, 
                          time_filter: str = "week", sort: str = "relevance") -> List[Dict[str, Any]]:
        """
        搜索Reddit帖子
        
        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制
            time_filter: 时间过滤器 (hour, day, week, month, year, all)
            sort: 排序方式 (relevance, hot, top, new, comments)
            
        Returns:
            Reddit帖子列表
        """
        query = " OR ".join(f'"{keyword}"' for keyword in keywords)
        
        params = {
            'q': query,
            'limit': min(limit, 100),  # Reddit API单次最多100条
            't': time_filter,
            'sort': sort,
            'type': 'link',
            'include_over_18': 'false'  # 转换为字符串格式
        }
        
        logger.info(f"搜索Reddit帖子: query='{query}', limit={limit}")
        
        try:
            response = await self._make_api_request("/search", params)
            posts = []
            
            for item in response.get("data", {}).get("children", []):
                post_data = item.get("data", {})
                
                # 转换为统一格式
                post = {
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "content": f"{post_data.get('title', '')} {post_data.get('selftext', '')}".strip(),
                    "author": post_data.get('author', 'unknown'),
                    "source": "reddit",
                    "published_at": datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    "score": post_data.get('score', 0),
                    "comments_count": post_data.get('num_comments', 0),
                    "subreddit": post_data.get('subreddit', ''),
                    "upvote_ratio": post_data.get('upvote_ratio', 0.5),
                    "platform_specific": {
                        "reddit_id": post_data.get('id'),
                        "subreddit_subscribers": post_data.get('subreddit_subscribers', 0),
                        "is_video": post_data.get('is_video', False),
                        "domain": post_data.get('domain', ''),
                        "flair_text": post_data.get('link_flair_text')
                    }
                }
                
                # 过滤相关性（确保至少包含一个关键词）
                content_lower = post["content"].lower()
                if any(keyword.lower() in content_lower for keyword in keywords):
                    posts.append(post)
            
            logger.info(f"从Reddit获取到 {len(posts)} 条相关帖子")
            return posts
        
        except Exception as e:
            logger.error(f"Reddit搜索失败: {e}")
            return []
    
    async def search_posts_enhanced(self, keywords: List[str], limit: int = 100, 
                                   time_filter: str = "week") -> List[Dict[str, Any]]:
        """
        增强搜索Reddit帖子（包含文本分析）
        
        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制
            time_filter: 时间过滤器
            
        Returns:
            包含文本分析的Reddit帖子列表
        """
        # 首先获取基础数据
        posts = await self.search_posts(keywords, limit, time_filter)
        
        # 为每个帖子添加文本分析
        enhanced_posts = []
        for post in posts:
            try:
                content = post.get('content', '')
                if content.strip():
                    # 执行文本分析
                    sentiment_result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(content)
                    keywords_result = enhanced_text_analysis_service.extract_keywords(content, max_keywords=10)
                    stats_result = enhanced_text_analysis_service.analyze_text_statistics(content)
                    
                    # 添加分析结果
                    post['text_analysis'] = {
                        'sentiment': sentiment_result,
                        'keywords': keywords_result,
                        'statistics': stats_result
                    }
                else:
                    # 无内容的默认分析
                    post['text_analysis'] = {
                        'sentiment': {'sentiment': 'neutral', 'confidence': 0.0},
                        'keywords': [],
                        'statistics': {}
                    }
                
                enhanced_posts.append(post)
                
            except Exception as e:
                logger.warning(f"Reddit帖子文本分析失败: {e}")
                # 即使分析失败，也保留原始帖子数据
                post['text_analysis'] = {
                    'sentiment': {'sentiment': 'neutral', 'confidence': 0.0},
                    'keywords': [],
                    'statistics': {}
                }
                enhanced_posts.append(post)
        
        logger.info(f"Reddit增强搜索完成，返回 {len(enhanced_posts)} 条分析过的帖子")
        return enhanced_posts
            
    async def get_trending_posts(self, subreddit: str = "all", time_filter: str = "day", limit: int = 25) -> List[Dict[str, Any]]:
        """
        获取热门帖子
        
        Args:
            subreddit: 子版块名称，默认"all"
            time_filter: 时间过滤器
            limit: 返回结果数量限制
            
        Returns:
            热门帖子列表
        """
        logger.info(f"获取Reddit热门帖子: r/{subreddit}, 时间: {time_filter}")
        
        try:
            endpoint = f"{self.base_url}/r/{subreddit}/hot"
            params = {
                'limit': limit,
                't': time_filter
            }
            
            response = await self._make_authenticated_request('GET', endpoint, params=params)
            
            if not response:
                return []
            
            posts_data = response.get('data', {}).get('children', [])
            trending_posts = []
            
            for post_item in posts_data:
                post = post_item.get('data', {})
                
                trending_post = {
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "content": post.get('title', ''),
                    "author": post.get('author', 'unknown'),
                    "source": "reddit",
                    "published_at": datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                    "score": post.get('score', 0),
                    "platform_specific": {
                        "subreddit": post.get('subreddit', ''),
                        "num_comments": post.get('num_comments', 0),
                        "upvote_ratio": post.get('upvote_ratio', 0),
                        "awards": post.get('total_awards_received', 0),
                        "post_id": post.get('id', ''),
                        "thumbnail": post.get('thumbnail', ''),
                        "flair": post.get('link_flair_text', '')
                    }
                }
                trending_posts.append(trending_post)
            
            logger.info(f"获取了 {len(trending_posts)} 个热门帖子")
            return trending_posts
            
        except Exception as e:
            logger.error(f"获取热门帖子失败: {e}")
            return []
    
    async def get_subreddit_posts(self, subreddit: str, keywords: List[str] = None,
                                 limit: int = 50, sort: str = "hot") -> List[Dict[str, Any]]:
        """
        获取特定子版块的帖子
        
        Args:
            subreddit: 子版块名称
            keywords: 可选的关键词过滤
            limit: 返回结果数量
            sort: 排序方式 (hot, new, rising, top)
            
        Returns:
            Reddit帖子列表
        """
        endpoint = f"/r/{subreddit}/{sort}"
        params = {'limit': min(limit, 100)}
        
        logger.info(f"获取 r/{subreddit} 的 {sort} 帖子, limit={limit}")
        
        try:
            response = await self._make_api_request(endpoint, params)
            posts = []
            
            for item in response.get("data", {}).get("children", []):
                post_data = item.get("data", {})
                
                post = {
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "content": f"{post_data.get('title', '')} {post_data.get('selftext', '')}".strip(),
                    "author": post_data.get('author', 'unknown'),
                    "source": "reddit",
                    "published_at": datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    "score": post_data.get('score', 0),
                    "comments_count": post_data.get('num_comments', 0),
                    "subreddit": subreddit,
                    "upvote_ratio": post_data.get('upvote_ratio', 0.5)
                }
                
                # 如果提供了关键词，进行过滤
                if keywords:
                    content_lower = post["content"].lower()
                    if any(keyword.lower() in content_lower for keyword in keywords):
                        posts.append(post)
                else:
                    posts.append(post)
            
            logger.info(f"从 r/{subreddit} 获取到 {len(posts)} 条帖子")
            return posts
            
        except Exception as e:
            logger.error(f"获取子版块帖子失败: {e}")
            return []
    
    async def get_trending_subreddits(self, keywords: List[str]) -> List[str]:
        """
        根据关键词推荐相关的活跃子版块
        
        Args:
            keywords: 关键词列表
            
        Returns:
            推荐的子版块列表
        """
        # 预定义的高质量子版块映射
        subreddit_mapping = {
            # 科技创业
            "startup": ["startups", "entrepreneur", "smallbusiness", "SideProject"],
            "ai": ["MachineLearning", "artificial", "ChatGPT", "OpenAI"],
            "tech": ["technology", "programming", "webdev", "DevTo"],
            "product": ["ProductManagement", "Design", "UXDesign", "product_design"],
            "marketing": ["marketing", "digitalmarketing", "growthacking", "SEO"],
            "funding": ["venturecapital", "investing", "finance", "business"],
            
            # 行业特定
            "crypto": ["cryptocurrency", "Bitcoin", "ethereum", "DeFi"],
            "fintech": ["fintech", "personalfinance", "investing", "Banking"],
            "healthcare": ["HealthTech", "medicine", "biotech", "health"],
            "ecommerce": ["ecommerce", "shopify", "amazon", "dropship"],
            
            # 通用商业
            "saas": ["SaaS", "B2B", "sales", "CustomerSuccess"],
            "mobile": ["androiddev", "iOSProgramming", "reactnative", "flutter"],
            "web": ["webdev", "reactjs", "vuejs", "angular"]
        }
        
        recommended_subreddits = set()
        
        # 基于关键词匹配推荐
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for category, subreddits in subreddit_mapping.items():
                if category in keyword_lower or keyword_lower in category:
                    recommended_subreddits.update(subreddits)
        
        # 如果没有匹配到，返回通用创业相关子版块
        if not recommended_subreddits:
            recommended_subreddits = {"startups", "entrepreneur", "technology", "business"}
        
        return list(recommended_subreddits)[:5]  # 限制返回数量


# 全局实例
reddit_service = RedditOfficialService()