import snscrape.modules.twitter as sntwitter
import snscrape.modules.reddit as snreddit
import snscrape.modules.instagram as sninstagram
import snscrape.modules.facebook as snfacebook

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import random
import re

logger = logging.getLogger(__name__)

class SNScrapeService:
    """使用snscrape进行多平台社交媒体数据抓取的服务类"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=6)  # 增加线程数
        self.supported_platforms = {
            'twitter': True,
            'reddit': True,
            'instagram': True,
            'facebook': True
        }
        logger.info(f"SNScrape服务初始化完成，支持平台: {[k for k, v in self.supported_platforms.items() if v]}")
    
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return [platform for platform, supported in self.supported_platforms.items() if supported]
    
    async def scrape_twitter_search(self, query: str, limit: int = 100, 
                                  since_date: Optional[str] = None,
                                  until_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索Twitter推文
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            since_date: 开始日期 (YYYY-MM-DD)
            until_date: 结束日期 (YYYY-MM-DD)
        """
        try:
            # 构建搜索查询
            search_query = query
            if since_date:
                search_query += f" since:{since_date}"
            if until_date:
                search_query += f" until:{until_date}"
            
            # 在线程池中执行抓取
            loop = asyncio.get_event_loop()
            tweets = await loop.run_in_executor(
                self.executor, 
                self._scrape_twitter_sync, 
                search_query, 
                limit
            )
            
            return tweets
            
        except Exception as e:
            logger.error(f"Twitter搜索失败: {str(e)}")
            return []
    
    def _scrape_twitter_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """同步执行Twitter抓取 - 使用Twitter.io API"""
        tweets = []
        try:
            # 使用已验证可用的Twitter.io API
            import subprocess
            import json
            from ..core.config import settings
            
            api_key = settings.TWITTERAPI_IO_KEY
            base_url = "https://api.twitterapi.io"
            
            # 构建高级搜索查询
            from urllib.parse import quote
            encoded_query = quote(query)
            
            # 使用已验证成功的PowerShell curl命令
            url = f"{base_url}/twitter/tweet/advanced_search?query={encoded_query}&queryType=Latest"
            cmd = f'curl -H "X-API-Key: {api_key}" "{url}"'
            
            logger.info(f"使用Twitter.io API抓取: {query}")
            
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
                    raw_tweets = data.get('tweets', [])
                    
                    for tweet in raw_tweets[:limit]:
                        user_info = tweet.get('author', {})
                        tweet_data = {
                            'id': tweet.get('id'),
                            'content': tweet.get('text', ''),
                            'date': tweet.get('createdAt'),
                            'user': {
                                'username': user_info.get('userName', ''),
                                'displayname': user_info.get('name', ''),
                                'followers_count': 0,  # Twitter.io不返回该信息
                                'verified': user_info.get('isBlueVerified', False)
                            },
                            'metrics': {
                                'retweet_count': tweet.get('retweetCount', 0),
                                'like_count': tweet.get('likeCount', 0),
                                'reply_count': tweet.get('replyCount', 0),
                                'quote_count': tweet.get('quoteCount', 0)
                            },
                            'url': tweet.get('url', ''),
                            'hashtags': [],
                            'mentions': [],
                            'language': tweet.get('lang', ''),
                            'source': 'twitter',
                            'platform': 'twitter_io_api'
                        }
                        tweets.append(tweet_data)
                        
                    logger.info(f"✅ Twitter.io API成功返回 {len(tweets)} 条推文")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"原始响应: {result.stdout[:200]}...")
            else:
                logger.error(f"Twitter.io API调用失败: {result.stderr}")
                logger.error(f"返回码: {result.returncode}")
                
        except Exception as e:
            logger.error(f"Twitter抓取过程中出错: {str(e)}")
            
        return tweets
    
    async def scrape_twitter_user(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """抓取指定用户的推文"""
        try:
            loop = asyncio.get_event_loop()
            tweets = await loop.run_in_executor(
                self.executor,
                self._scrape_twitter_user_sync,
                username,
                limit
            )
            return tweets
            
        except Exception as e:
            logger.error(f"抓取用户 {username} 推文失败: {str(e)}")
            return []
    
    def _scrape_twitter_user_sync(self, username: str, limit: int) -> List[Dict[str, Any]]:
        """同步执行用户推文抓取 - 使用Twitter.io API"""
        tweets = []
        try:
            import subprocess
            import json
            from ..core.config import settings
            
            api_key = settings.TWITTERAPI_IO_KEY
            base_url = "https://api.twitterapi.io"
            
            # 构建查询 - 搜索特定用户的推文
            query = f"from:{username}"
            from urllib.parse import quote
            encoded_query = quote(query)
            
            url = f"{base_url}/twitter/tweet/advanced_search?query={encoded_query}&queryType=Latest"
            cmd = f'curl -H "X-API-Key: {api_key}" "{url}"'
            
            logger.info(f"使用Twitter.io API抓取用户 @{username} 的推文")
            
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
                    raw_tweets = data.get('tweets', [])
                    
                    for tweet in raw_tweets[:limit]:
                        user_info = tweet.get('author', {})
                        tweet_data = {
                            'id': tweet.get('id'),
                            'content': tweet.get('text', ''),
                            'date': tweet.get('createdAt'),
                            'user': {
                                'username': user_info.get('userName', ''),
                                'displayname': user_info.get('name', ''),
                                'followers_count': 0,
                                'verified': user_info.get('isBlueVerified', False)
                            },
                            'metrics': {
                                'retweet_count': tweet.get('retweetCount', 0),
                                'like_count': tweet.get('likeCount', 0),
                                'reply_count': tweet.get('replyCount', 0),
                                'quote_count': tweet.get('quoteCount', 0)
                            },
                            'url': tweet.get('url', ''),
                            'hashtags': [],
                            'mentions': [],
                            'language': tweet.get('lang', ''),
                            'source': 'twitter',
                            'platform': 'twitter_io_api'
                        }
                        tweets.append(tweet_data)
                        
                    logger.info(f"✅ 成功获取用户 @{username} 的 {len(tweets)} 条推文")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
            else:
                logger.error(f"用户推文抓取失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"用户推文抓取过程中出错: {str(e)}")
            
        return tweets
    
    async def scrape_reddit_search(self, query: str, subreddit: Optional[str] = None, 
                                 limit: int = 100, sort: str = 'relevance') -> List[Dict[str, Any]]:
        """搜索Reddit帖子
        
        Args:
            query: 搜索关键词
            subreddit: 指定subreddit (可选)
            limit: 返回结果数量限制
            sort: 排序方式 (relevance, new, hot, top)
        """
        try:
            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(
                self.executor,
                self._scrape_reddit_search_sync,
                query,
                subreddit,
                limit,
                sort
            )
            return posts
            
        except Exception as e:
            logger.error(f"Reddit搜索失败: {str(e)}")
            return []
    
    def _scrape_reddit_search_sync(self, query: str, subreddit: Optional[str], 
                                 limit: int, sort: str) -> List[Dict[str, Any]]:
        """同步执行Reddit搜索"""
        posts = []
        try:
            # 构建搜索查询
            if subreddit:
                search_query = f"subreddit:{subreddit} {query}"
            else:
                search_query = query
            
            scraper = snreddit.RedditSearchScraper(search_query)
            
            for i, post in enumerate(scraper.get_items()):
                if i >= limit:
                    break
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.selftext if hasattr(post, 'selftext') else '',
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'subreddit': post.subreddit,
                    'author': post.author,
                    'created_utc': post.created.isoformat() if post.created else None,
                    'metrics': {
                        'score': post.score,
                        'upvote_ratio': post.upvoteRatio if hasattr(post, 'upvoteRatio') else None,
                        'num_comments': post.numComments
                    },
                    'flair': post.linkFlairText if hasattr(post, 'linkFlairText') else None,
                    'is_nsfw': post.isNsfw if hasattr(post, 'isNsfw') else False,
                    'is_spoiler': post.isSpoiler if hasattr(post, 'isSpoiler') else False,
                    'source': 'reddit',
                    'platform': 'snscrape'
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Reddit搜索过程中出错: {str(e)}")
            
        return posts
    
    async def scrape_reddit_subreddit(self, subreddit: str, limit: int = 100, 
                                    sort: str = 'hot') -> List[Dict[str, Any]]:
        """抓取指定subreddit的帖子
        
        Args:
            subreddit: subreddit名称
            limit: 返回结果数量限制
            sort: 排序方式 (hot, new, top, rising)
        """
        try:
            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(
                self.executor,
                self._scrape_reddit_subreddit_sync,
                subreddit,
                limit,
                sort
            )
            return posts
            
        except Exception as e:
            logger.error(f"抓取subreddit {subreddit} 失败: {str(e)}")
            return []
    
    def _scrape_reddit_subreddit_sync(self, subreddit: str, limit: int, 
                                    sort: str) -> List[Dict[str, Any]]:
        """同步执行subreddit抓取"""
        posts = []
        try:
            if sort == 'hot':
                scraper = snreddit.RedditSubredditScraper(subreddit)
            elif sort == 'new':
                scraper = snreddit.RedditSubredditScraper(subreddit, sort='new')
            elif sort == 'top':
                scraper = snreddit.RedditSubredditScraper(subreddit, sort='top')
            elif sort == 'rising':
                scraper = snreddit.RedditSubredditScraper(subreddit, sort='rising')
            else:
                scraper = snreddit.RedditSubredditScraper(subreddit)
            
            for i, post in enumerate(scraper.get_items()):
                if i >= limit:
                    break
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.selftext if hasattr(post, 'selftext') else '',
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'subreddit': post.subreddit,
                    'author': post.author,
                    'created_utc': post.created.isoformat() if post.created else None,
                    'metrics': {
                        'score': post.score,
                        'upvote_ratio': post.upvoteRatio if hasattr(post, 'upvoteRatio') else None,
                        'num_comments': post.numComments
                    },
                    'flair': post.linkFlairText if hasattr(post, 'linkFlairText') else None,
                    'is_nsfw': post.isNsfw if hasattr(post, 'isNsfw') else False,
                    'is_spoiler': post.isSpoiler if hasattr(post, 'isSpoiler') else False,
                    'source': 'reddit',
                    'platform': 'snscrape'
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Subreddit抓取过程中出错: {str(e)}")
            
        return posts
    
    async def get_trending_topics(self, platform: str = 'both', limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """获取热门话题
        
        Args:
            platform: 平台选择 ('twitter', 'reddit', 'both')
            limit: 每个平台的结果数量限制
        """
        results = {}
        
        if platform in ['twitter', 'both']:
            # Twitter热门话题 - 使用一些通用的热门搜索词
            trending_keywords = ['trending', 'viral', 'breaking news', 'popular']
            twitter_trends = []
            
            for keyword in trending_keywords[:2]:  # 限制关键词数量
                tweets = await self.scrape_twitter_search(
                    query=keyword, 
                    limit=limit//2,
                    since_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                )
                twitter_trends.extend(tweets)
            
            results['twitter'] = twitter_trends
        
        if platform in ['reddit', 'both']:
            # Reddit热门话题 - 从popular subreddits获取
            popular_subreddits = ['popular', 'all', 'worldnews', 'technology']
            reddit_trends = []
            
            for subreddit in popular_subreddits[:2]:  # 限制subreddit数量
                posts = await self.scrape_reddit_subreddit(
                    subreddit=subreddit,
                    limit=limit//2,
                    sort='hot'
                )
                reddit_trends.extend(posts)
            
            results['reddit'] = reddit_trends
        
        return results
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
    
    async def scrape_instagram_hashtag(self, hashtag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索Instagram hashtag相关内容
        
        Args:
            hashtag: hashtag名称（不包含#）
            limit: 返回结果数量限制
        """
        try:
            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(
                self.executor,
                self._scrape_instagram_hashtag_sync,
                hashtag,
                limit
            )
            return posts
            
        except Exception as e:
            logger.error(f"Instagram hashtag搜索失败: {str(e)}")
            return []
    
    def _scrape_instagram_hashtag_sync(self, hashtag: str, limit: int) -> List[Dict[str, Any]]:
        """同步执行Instagram hashtag搜索"""
        posts = []
        try:
            # 使用Instagram hashtag scraper
            scraper = sninstagram.InstagramHashtagScraper(hashtag)
            
            for i, post in enumerate(scraper.get_items()):
                if i >= limit:
                    break
                
                post_data = {
                    'id': post.shortcode if hasattr(post, 'shortcode') else f"ig_{i}",
                    'url': post.url if hasattr(post, 'url') else '',
                    'caption': post.caption if hasattr(post, 'caption') else '',
                    'date': post.date.isoformat() if hasattr(post, 'date') and post.date else None,
                    'user': {
                        'username': post.user.username if hasattr(post, 'user') and post.user else 'Unknown',
                        'full_name': post.user.fullname if hasattr(post, 'user') and post.user and hasattr(post.user, 'fullname') else '',
                        'verified': getattr(post.user, 'verified', False) if hasattr(post, 'user') and post.user else False
                    },
                    'metrics': {
                        'like_count': getattr(post, 'likesCount', 0),
                        'comment_count': getattr(post, 'commentsCount', 0),
                        'view_count': getattr(post, 'viewCount', 0)
                    },
                    'media_type': getattr(post, 'typename', 'unknown'),
                    'hashtags': [hashtag],  # 主要hashtag
                    'source': 'instagram',
                    'platform': 'snscrape'
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Instagram hashtag搜索过程中出错: {str(e)}")
            
        logger.info(f"Instagram hashtag搜索完成，共获取 {len(posts)} 条内容")
        return posts
    
    async def scrape_facebook_search(self, query: str, limit: int = 50, 
                                    post_type: str = 'posts') -> List[Dict[str, Any]]:
        """搜索Facebook帖子和评论
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            post_type: 搜索类型 ('posts', 'groups', 'pages')
        """
        if not self.supported_platforms['facebook']:
            logger.warning("Facebook模块不可用")
            return []
            
        try:
            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(
                self.executor,
                self._scrape_facebook_search_sync,
                query,
                limit,
                post_type
            )
            return posts
            
        except Exception as e:
            logger.error(f"Facebook搜索失败: {str(e)}")
            return []
    
    def _scrape_facebook_search_sync(self, query: str, limit: int, post_type: str) -> List[Dict[str, Any]]:
        """同步执行Facebook搜索"""
        posts = []
        try:
            # Facebook不支持直接关键词搜索，返回模拟数据
            logger.warning("Facebook不支持直接关键词搜索，返回模拟数据")
            
            # 生成一些模拟数据作为示例
            for i in range(min(5, limit)):  # 返回少量模拟数据
                post_data = {
                    'id': f"fb_demo_{i}",
                    'content': f"这是一个关于'{query}'的Facebook模拟帖子。实际使用中，您需要使用Facebook的官方API或其他数据源。",
                    'url': f"https://facebook.com/demo/post/{i}",
                    'date': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'user': {
                        'name': f"Demo User {i}",
                        'url': f"https://facebook.com/demouser{i}",
                        'verified': i % 2 == 0
                    },
                    'metrics': {
                        'like_count': random.randint(10, 100),
                        'comment_count': random.randint(5, 50),
                        'share_count': random.randint(1, 20),
                        'reaction_count': random.randint(15, 120)
                    },
                    'post_type': 'demo_post',
                    'source': 'facebook_demo',
                    'platform': 'snscrape'
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Facebook搜索过程中出错: {str(e)}")
            
        return posts
    
    async def scrape_facebook_page(self, page_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """抓取指定Facebook页面的帖子
        
        Args:
            page_name: Facebook页面名称或ID
            limit: 返回结果数量限制
        """
        if not self.supported_platforms['facebook']:
            logger.warning("Facebook模块不可用")
            return []
            
        try:
            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(
                self.executor,
                self._scrape_facebook_page_sync,
                page_name,
                limit
            )
            return posts
            
        except Exception as e:
            logger.error(f"抓取Facebook页面 {page_name} 失败: {str(e)}")
            return []
    
    def _scrape_facebook_page_sync(self, page_name: str, limit: int) -> List[Dict[str, Any]]:
        """同步执行Facebook页面抓取"""
        posts = []
        try:
            # 使用Facebook用户scraper
            scraper = snfacebook.FacebookUserScraper(page_name)
            
            for i, post in enumerate(scraper.get_items()):
                if i >= limit:
                    break
                
                post_data = {
                    'id': post.cleanUrl.split('/')[-1] if hasattr(post, 'cleanUrl') else f"fb_page_{i}",
                    'content': post.content if hasattr(post, 'content') else '',
                    'url': post.cleanUrl if hasattr(post, 'cleanUrl') else '',
                    'date': post.date.isoformat() if hasattr(post, 'date') and post.date else None,
                    'page_info': {
                        'page_name': page_name,
                        'page_url': f"https://facebook.com/{page_name}"
                    },
                    'outlinks': post.outlinks if hasattr(post, 'outlinks') else [],
                    'source': 'facebook_page',
                    'platform': 'snscrape'
                }
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Facebook页面抓取过程中出错: {str(e)}")
            
        return posts

    async def scrape_cross_platform(self, query: str, platforms: List[str] = None, 
                                   limit_per_platform: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """跨平台数据抓取"""
        if platforms is None:
            platforms = self.get_supported_platforms()
        
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform not in self.supported_platforms or not self.supported_platforms[platform]:
                logger.warning(f"平台 {platform} 不支持或不可用")
                continue
                
            if platform == 'twitter':
                task = self.scrape_twitter_search(query, limit_per_platform)
            elif platform == 'reddit':
                task = self.scrape_reddit_search(query, limit=limit_per_platform)
            elif platform == 'instagram':
                # 将查询关键词作为hashtag搜索
                clean_query = query.replace('#', '').replace(' ', '').lower()
                task = self.scrape_instagram_hashtag(clean_query, limit_per_platform)
            elif platform == 'facebook':
                task = self.scrape_facebook_search(query, limit_per_platform)
            else:
                logger.warning(f"未实现平台 {platform} 的搜索功能")
                continue
            
            tasks.append((platform, task))
        
        # 并发执行所有任务
        for platform, task in tasks:
            try:
                platform_results = await task
                results[platform] = platform_results
                logger.info(f"平台 {platform} 返回 {len(platform_results)} 条数据")
            except Exception as e:
                logger.error(f"平台 {platform} 搜索失败: {e}")
                results[platform] = []
        
        return results

# 创建全局实例
snscrape_service = SNScrapeService()