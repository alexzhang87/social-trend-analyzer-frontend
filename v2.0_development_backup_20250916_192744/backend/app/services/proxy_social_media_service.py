import json
import os
from datetime import datetime
from typing import List, Dict, Any
from .social_media_service import SocialMediaService
from ..utils.logger import logger

class ProxySocialMediaService(SocialMediaService):
    """
    一个模拟的社交媒体服务，从本地JSON文件加载数据。
    这在开发或外部API不可用时非常有用。
    """
    
    def __init__(self):
        self.seed_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'seed_data.json')
        self._load_seed_data()
        logger.info("模拟社交媒体服务已初始化，使用种子数据。")

    def _load_seed_data(self):
        """从JSON文件加载种子数据。"""
        try:
            with open(self.seed_data_path, 'r', encoding='utf-8') as f:
                self.seed_data = json.load(f)
            logger.info(f"成功从 {self.seed_data_path} 加载了 {len(self.seed_data)} 条种子数据。")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"加载种子数据失败: {e}")
            self.seed_data = []

    def get_twitter_posts(self, query: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """从种子数据中筛选出Twitter帖子。"""
        logger.info(f"正在从模拟数据中获取关于 '{query}' 的Twitter帖子。")
        twitter_posts = [post for post in self.seed_data if post.get("platform") == "twitter"]
        
        # 简单模拟查询 - 在实际应用中可以实现更复杂的过滤逻辑
        filtered_posts = [
            post for post in twitter_posts 
            if query.lower() in post.get('text', '').lower()
        ]

        logger.info(f"找到了 {len(filtered_posts)} 条匹配的Twitter模拟帖子。")
        return filtered_posts[:limit]

    def get_reddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """从种子数据中筛选出Reddit帖子。"""
        logger.info(f"正在从模拟数据中获取关于 '{subreddit}' 的Reddit帖子。")
        reddit_posts = [post for post in self.seed_data if post.get("platform") == "reddit"]
        
        # 简单模拟查询
        filtered_posts = [
            post for post in reddit_posts
            if subreddit.lower() in post.get('text', '').lower()
        ]

        logger.info(f"找到了 {len(filtered_posts)} 条匹配的Reddit模拟帖子。")
        return filtered_posts[:limit]

    def _format_twitter_data(self, api_response: Dict[str, Any]) -> List[Dict[Any, Any]]:
        # 在模拟模式下，数据已是正确格式，无需转换
        return api_response

    def _format_reddit_data(self, api_response: Dict[str, Any]) -> List[Dict[Any, Any]]:
        # 在模拟模式下，数据已是正确格式，无需转换
        return api_response