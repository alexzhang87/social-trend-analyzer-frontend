from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SocialMediaService(ABC):
    """社交媒体数据服务的抽象基类"""
    
    @abstractmethod
    async def get_twitter_posts(self, query: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """获取Twitter帖子"""
        pass
        
    @abstractmethod
    async def get_reddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """获取Reddit帖子"""
        pass