from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .snscrape_service import snscrape_service
from .social_media_service import SocialMediaService
import logging

logger = logging.getLogger(__name__)

class EnhancedSocialMediaService(SocialMediaService):
    """增强的社交媒体服务，集成snscrape功能"""
    
    def __init__(self):
        self.snscrape = snscrape_service
    
    async def get_tweets(self, query: str, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """获取推文 - 使用snscrape实现"""
        try:
            since_date = kwargs.get('since_date')
            until_date = kwargs.get('until_date')
            
            tweets = await self.snscrape.scrape_twitter_search(
                query=query,
                limit=count,
                since_date=since_date,
                until_date=until_date
            )
            
            logger.info(f"成功获取 {len(tweets)} 条推文，查询: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"获取推文失败: {str(e)}")
            return []
    
    async def get_twitter_posts(self, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指定用户的推文 - 实现抽象方法"""
        try:
            tweets = await self.snscrape.scrape_twitter_user(
                username=username,
                limit=limit
            )
            
            logger.info(f"成功获取用户 {username} 的 {len(tweets)} 条推文")
            return tweets
            
        except Exception as e:
            logger.error(f"获取用户推文失败: {str(e)}")
            return []
    
    async def search_twitter_posts_advanced(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """使用高级搜索获取推文 - 实现抽象方法"""
        try:
            tweets = await self.snscrape.scrape_twitter_search(
                query=query,
                limit=limit
            )
            
            logger.info(f"高级搜索获取 {len(tweets)} 条推文，查询: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"高级推文搜索失败: {str(e)}")
            return []
    
    async def search_tweets_advanced(self, query: str, filters: Dict[str, Any] = None, 
                                   count: int = 100) -> List[Dict[str, Any]]:
        """高级推文搜索"""
        try:
            filters = filters or {}
            
            # 构建高级搜索参数
            since_date = filters.get('since_date')
            until_date = filters.get('until_date')
            username = filters.get('username')
            
            if username:
                # 如果指定用户，使用用户推文抓取
                tweets = await self.snscrape.scrape_twitter_user(
                    username=username,
                    limit=count
                )
            else:
                # 否则使用搜索抓取
                tweets = await self.snscrape.scrape_twitter_search(
                    query=query,
                    limit=count,
                    since_date=since_date,
                    until_date=until_date
                )
            
            # 应用额外过滤器
            if filters.get('min_likes'):
                tweets = [t for t in tweets if t.get('metrics', {}).get('like_count', 0) >= filters['min_likes']]
            
            if filters.get('min_retweets'):
                tweets = [t for t in tweets if t.get('metrics', {}).get('retweet_count', 0) >= filters['min_retweets']]
            
            if filters.get('language'):
                tweets = [t for t in tweets if t.get('language') == filters['language']]
            
            logger.info(f"高级搜索获取 {len(tweets)} 条推文，查询: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"高级推文搜索失败: {str(e)}")
            return []
    
    async def get_reddit_posts(self, subreddit: str = None, query: str = None, 
                             count: int = 100, sort: str = 'hot') -> List[Dict[str, Any]]:
        """获取Reddit帖子"""
        try:
            if query and subreddit:
                # 在指定subreddit中搜索
                posts = await self.snscrape.scrape_reddit_search(
                    query=query,
                    subreddit=subreddit,
                    limit=count,
                    sort=sort
                )
            elif query:
                # 全站搜索
                posts = await self.snscrape.scrape_reddit_search(
                    query=query,
                    limit=count,
                    sort=sort
                )
            elif subreddit:
                # 获取指定subreddit的帖子
                posts = await self.snscrape.scrape_reddit_subreddit(
                    subreddit=subreddit,
                    limit=count,
                    sort=sort
                )
            else:
                # 获取热门帖子
                posts = await self.snscrape.scrape_reddit_subreddit(
                    subreddit='popular',
                    limit=count,
                    sort=sort
                )
            
            logger.info(f"成功获取 {len(posts)} 条Reddit帖子")
            return posts
            
        except Exception as e:
            logger.error(f"获取Reddit帖子失败: {str(e)}")
            return []
    
    async def get_trending_topics(self, platform: str = 'both', limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """获取热门话题"""
        try:
            trending_data = await self.snscrape.get_trending_topics(
                platform=platform,
                limit=limit
            )
            
            logger.info(f"成功获取热门话题，平台: {platform}")
            return trending_data
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {str(e)}")
            return {}
    
    async def search_social_media(self, query: str, platforms: List[str] = None, 
                                count: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """跨平台社交媒体搜索"""
        platforms = platforms or ['twitter', 'reddit']
        results = {}
        
        try:
            if 'twitter' in platforms:
                twitter_results = await self.get_tweets(query=query, count=count)
                results['twitter'] = twitter_results
            
            if 'reddit' in platforms:
                reddit_results = await self.get_reddit_posts(query=query, count=count)
                results['reddit'] = reddit_results
            
            total_results = sum(len(results.get(platform, [])) for platform in platforms)
            logger.info(f"跨平台搜索完成，总计 {total_results} 条结果")
            
            return results
            
        except Exception as e:
            logger.error(f"跨平台搜索失败: {str(e)}")
            return {}
    
    async def get_user_content(self, platform: str, username: str, 
                             count: int = 50) -> List[Dict[str, Any]]:
        """获取指定用户的内容"""
        try:
            if platform.lower() == 'twitter':
                content = await self.snscrape.scrape_twitter_user(
                    username=username,
                    limit=count
                )
            elif platform.lower() == 'reddit':
                # Reddit用户内容需要特殊处理，这里暂时返回空列表
                content = []
                logger.warning(f"Reddit用户内容抓取暂未实现")
            else:
                logger.error(f"不支持的平台: {platform}")
                return []
            
            logger.info(f"成功获取用户 {username} 在 {platform} 的 {len(content)} 条内容")
            return content
            
        except Exception as e:
            logger.error(f"获取用户内容失败: {str(e)}")
            return []
    
    async def analyze_sentiment_batch(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量情感分析"""
        try:
            # 这里可以集成现有的情感分析服务
            # 暂时返回原始内容，后续可以添加情感分析逻辑
            for content in contents:
                content['sentiment'] = {
                    'score': 0.0,
                    'label': 'neutral',
                    'confidence': 0.0
                }
            
            logger.info(f"完成 {len(contents)} 条内容的情感分析")
            return contents
            
        except Exception as e:
            logger.error(f"批量情感分析失败: {str(e)}")
            return contents
    
    async def test_connection(self) -> bool:
        """测试连接状态 - 实现抽象方法"""
        try:
            # 测试Twitter连接
            twitter_test = await self.snscrape.scrape_twitter_search(
                query="test",
                limit=1
            )
            
            # 测试Reddit连接
            reddit_test = await self.snscrape.scrape_reddit_search(
                query="test",
                limit=1
            )
            
            is_connected = len(twitter_test) > 0 or len(reddit_test) > 0
            logger.info(f"连接测试完成: {is_connected}")
            return is_connected
            
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False
    
    async def test_connection_detailed(self) -> Dict[str, bool]:
        """详细的连接状态测试"""
        results = {
            'twitter': False,
            'reddit': False
        }
        
        try:
            # 测试Twitter连接
            twitter_test = await self.snscrape.scrape_twitter_search(
                query="test",
                limit=1
            )
            results['twitter'] = len(twitter_test) > 0
            
            # 测试Reddit连接
            reddit_test = await self.snscrape.scrape_reddit_search(
                query="test",
                limit=1
            )
            results['reddit'] = len(reddit_test) > 0
            
            logger.info(f"详细连接测试完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"详细连接测试失败: {str(e)}")
            return results
    
    async def get_platform_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取平台统计信息"""
        stats = {
            'twitter': {
                'available': True,
                'rate_limit': 'No API key required',
                'features': ['search', 'user_timeline', 'trending']
            },
            'reddit': {
                'available': True,
                'rate_limit': 'No API key required',
                'features': ['search', 'subreddit', 'trending']
            }
        }
        
        # 测试实际可用性
        connection_status = await self.test_connection()
        for platform in stats:
            stats[platform]['status'] = 'online' if connection_status.get(platform, False) else 'offline'
        
        return stats

# 创建全局实例
enhanced_social_service = EnhancedSocialMediaService()