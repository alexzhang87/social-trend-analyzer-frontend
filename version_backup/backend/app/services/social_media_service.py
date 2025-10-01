from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SocialMediaService(ABC):
    """社交媒体数据服务的抽象基类"""

    @abstractmethod
    async def get_twitter_posts(self, username: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """获取指定用户的推文"""
        pass

    @abstractmethod
    async def search_twitter_posts_advanced(self, query: str, limit: int = 20) -> List[Dict[Any, Any]]:
        """使用高级搜索获取推文"""
        pass

    @abstractmethod
    async def get_reddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """获取Reddit帖子"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试服务连接"""
        pass