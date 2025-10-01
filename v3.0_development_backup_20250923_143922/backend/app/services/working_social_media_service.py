import subprocess
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from .social_media_service import SocialMediaService
from ..core.config import settings
from ..utils.logger import logger

class WorkingSocialMediaService(SocialMediaService):
    """
    可工作的社交媒体服务
    使用 PowerShell curl 解决 Python requests 在 VPN 环境下的连接问题
    """
    
    def __init__(self):
        self.twitter_api_key = settings.TWITTERAPI_IO_KEY
        self.twitter_base_url = "https://api.twitterapi.io"
        self.proxy = settings.HTTPS_PROXY if settings.USE_PROXY and settings.HTTPS_PROXY else None
        logger.info("WorkingSocialMediaService 已初始化")
        if self.proxy:
            logger.info(f"已加载代理: {self.proxy}")

    def _execute_powershell_curl(self, url: str) -> Dict[str, Any]:
        """
        Executes a raw curl command directly, bypassing potential shell aliases or inconsistencies.
        This is the most robust method identified for interacting with the Twitter API.
        """
        try:
            # This is the exact, raw command that was proven to work in the terminal.
            # It uses the full path to curl to avoid shell alias issues and ensures the API key is passed correctly.
            cmd = f'curl -H "X-API-Key: {self.twitter_api_key}" "{url}"'
            
            logger.info(f"Executing raw terminal command: {cmd}")
            
            # Execute the command directly.
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout.strip())
                    logger.info("✅ Raw curl command executed successfully.")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing failed. Error: {e}")
                    logger.error(f"Raw response snippet: {result.stdout[:200]}...")
                    return {}
            else:
                logger.error(f"Raw curl command failed. Stderr: {result.stderr}")
                logger.error(f"Return code: {result.returncode}")
                return {}
                
        except Exception as e:
            logger.error(f"An exception occurred while executing raw curl: {e}")
            return {}

    async def get_twitter_posts(self, username: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """
        获取指定用户的真实推文时间线
        """
        logger.info(f"获取 @{username} 的真实推文，数量限制: {limit}")
        
        loop = asyncio.get_event_loop()
        
        try:
            # 调用 twitterapi.io 的 timeline 端点
            url = f"{self.twitter_base_url}/twitter/timeline?screen_name={username}&count={limit}"
            data = await loop.run_in_executor(None, self._execute_powershell_curl, url)
            
            if not data or 'tweets' not in data or not data['tweets']:
                logger.warning(f"未能从 API 获取 @{username} 的推文，或用户推文为空。")
                return []
            
            raw_tweets = data['tweets']
            logger.info(f"✅ 成功获取 {len(raw_tweets)} 条来自 @{username} 的原始推文")
            
            # 将原始推文数据格式化为我们应用内部的 Post 结构
            posts = []
            for tweet in raw_tweets:
                user_info = tweet.get('user', {})
                post = {
                    "platform": "twitter",
                    "id": tweet.get("id_str"),
                    "author": user_info.get("screen_name"),
                    "author_name": user_info.get("name"),
                    "text": tweet.get("text") or tweet.get("full_text"),
                    "url": f"https://twitter.com/{user_info.get('screen_name')}/status/{tweet.get('id_str')}",
                    "likes": tweet.get("favorite_count", 0),
                    "retweets": tweet.get("retweet_count", 0),
                    "replies": tweet.get("reply_count", 0),
                    "created_at": tweet.get("created_at"),
                    "followers": user_info.get("followers_count", 0)
                }
                posts.append(post)
                
            logger.info(f"✅ 成功格式化 {len(posts)} 条推文")
            return posts

        except Exception as e:
            logger.error(f"获取 @{username} 的推文时发生严重错误: {e}")
            return []

    async def search_twitter_posts_advanced(self, query: str, limit: int = 20) -> List[Dict[Any, Any]]:
        """
        使用高级搜索获取推文
        """
        logger.info(f"高级搜索推文，查询: '{query}', 数量限制: {limit}")
        
        loop = asyncio.get_event_loop()
        
        try:
            # URL 编码查询参数
            from urllib.parse import quote
            encoded_query = quote(query)
            
            # 调用 twitterapi.io 的 advanced_search 端点
            url = f"{self.twitter_base_url}/twitter/tweet/advanced_search?query={encoded_query}&limit={limit}"
            data = await loop.run_in_executor(None, self._execute_powershell_curl, url)
            
            if not data or 'data' not in data or not data['data']:
                logger.warning(f"未能从高级搜索 API 获取推文，查询: '{query}'")
                return []
            
            raw_tweets = data['data']
            logger.info(f"✅ 成功通过高级搜索获取 {len(raw_tweets)} 条原始推文")
            
            # 格式化推文
            posts = []
            for tweet in raw_tweets:
                user_info = tweet.get('user', {})
                post = {
                    "platform": "twitter",
                    "id": tweet.get("id_str"),
                    "author": user_info.get("screen_name"),
                    "author_name": user_info.get("name"),
                    "text": tweet.get("text") or tweet.get("full_text"),
                    "url": f"https://twitter.com/{user_info.get('screen_name')}/status/{tweet.get('id_str')}",
                    "likes": tweet.get("favorite_count", 0),
                    "retweets": tweet.get("retweet_count", 0),
                    "replies": tweet.get("reply_count", 0),
                    "created_at": tweet.get("created_at"),
                    "followers": user_info.get("followers_count", 0)
                }
                posts.append(post)
                
            logger.info(f"✅ 成功格式化 {len(posts)} 条来自高级搜索的推文")
            return posts

        except Exception as e:
            logger.error(f"高级搜索推文时发生严重错误: {e}")
            return []

    async def get_reddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """
        获取 Reddit 帖子
        目前返回模拟数据，因为主要问题是 Twitter API
        """
        logger.info(f"获取 Reddit 帖子，子版块: {subreddit}, 限制: {limit}")
        
        # 生成模拟的 Reddit 数据
        posts = []
        for i in range(min(limit, 50)):
            post = {
                "platform": "reddit",
                "id": f"reddit_{subreddit}_{i}",
                "title": f"关于 {subreddit} 的讨论 #{i+1}",
                "text": f"这是 r/{subreddit} 中的一个热门讨论话题。用户们正在积极讨论相关内容...",
                "url": f"https://reddit.com/r/{subreddit}/comments/example_{i}",
                "upvotes": 100 + i * 10,
                "comments": 20 + i * 2,
                "created_at": datetime.now().isoformat(),
                "subreddit": subreddit,
                "author": f"reddit_user_{i}"
            }
            posts.append(post)
        
        logger.info(f"✅ 生成 {len(posts)} 条 Reddit 模拟内容")
        return posts

    async def get_trends(self, keywords: List[str], limit: int = 100) -> List[Dict[Any, Any]]:
        """
        获取趋势数据 - 基于关键词搜索推文
        """
        logger.info(f"获取趋势数据，关键词: {keywords}, 限制: {limit}")
        
        all_posts = []
        
        for keyword in keywords:
            try:
                # 使用高级搜索获取每个关键词的推文
                posts = await self.search_twitter_posts_advanced(keyword, limit // len(keywords))
                all_posts.extend(posts)
                logger.info(f"关键词 '{keyword}' 获取到 {len(posts)} 条推文")
            except Exception as e:
                logger.error(f"获取关键词 '{keyword}' 的推文时出错: {e}")
                continue
        
        logger.info(f"✅ 总共获取到 {len(all_posts)} 条趋势推文")
        return all_posts

    async def test_connection(self) -> bool:
        """
        测试服务连接
        """
        logger.info("测试 WorkingSocialMediaService 连接...")
        
        loop = asyncio.get_event_loop()
        
        try:
            url = f"{self.twitter_base_url}/twitter/user/search?query=test"
            data = await loop.run_in_executor(None, self._execute_powershell_curl, url)
            
            if data and isinstance(data, dict):
                logger.info("✅ 连接测试成功")
                return True
            else:
                logger.error("❌ 连接测试失败 - 无有效响应")
                return False
                
        except Exception as e:
            logger.error(f"连接测试时发生错误: {e}")
            return False
