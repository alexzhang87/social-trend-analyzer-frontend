"""Hacker News API服务

Hacker News提供免费的API，适合获取技术趋势、创业动态、开发者情感数据。

API文档：https://github.com/HackerNews/API
认证方式：无需认证
免费额度：无限制

优势：
- 免费无限制API
- 技术社区高质量内容
- 开发者和创业者聚集地
- 实时数据更新
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

logger = logging.getLogger(__name__)

class HackerNewsService:
    """Hacker News API服务"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = None
        
        # 速率限制（虽然API无限制，但为了礼貌使用）
        self.rate_limit_delay = 0.1  # 每次请求间隔100ms
        
        logger.info("Hacker News服务初始化成功")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """发起API请求"""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        try:
            await asyncio.sleep(self.rate_limit_delay)  # 速率限制
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Hacker News API请求失败: {response.status} - {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Hacker News API请求异常: {e} - {url}")
            return None
    
    async def get_top_stories(self, limit: int = 30) -> List[Dict[str, Any]]:
        """获取热门故事
        
        Args:
            limit: 返回的故事数量限制
            
        Returns:
            热门故事列表
        """
        try:
            # 获取热门故事ID列表
            story_ids = await self._make_request("/topstories.json")
            if not story_ids:
                return []
            
            # 限制数量
            story_ids = story_ids[:limit]
            
            # 并行获取故事详情
            tasks = [self._get_item_details(story_id) for story_id in story_ids]
            stories = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_stories = []
            for story in stories:
                if isinstance(story, dict) and story.get('title'):
                    valid_stories.append(story)
            
            logger.info(f"成功获取{len(valid_stories)}个热门故事")
            return valid_stories
            
        except Exception as e:
            logger.error(f"获取热门故事失败: {e}")
            return []
    
    async def get_new_stories(self, limit: int = 30) -> List[Dict[str, Any]]:
        """获取最新故事
        
        Args:
            limit: 返回的故事数量限制
            
        Returns:
            最新故事列表
        """
        try:
            # 获取最新故事ID列表
            story_ids = await self._make_request("/newstories.json")
            if not story_ids:
                return []
            
            # 限制数量
            story_ids = story_ids[:limit]
            
            # 并行获取故事详情
            tasks = [self._get_item_details(story_id) for story_id in story_ids]
            stories = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_stories = []
            for story in stories:
                if isinstance(story, dict) and story.get('title'):
                    valid_stories.append(story)
            
            logger.info(f"成功获取{len(valid_stories)}个最新故事")
            return valid_stories
            
        except Exception as e:
            logger.error(f"获取最新故事失败: {e}")
            return []
    
    async def search_stories(self, keywords: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """搜索相关故事
        
        Args:
            keywords: 搜索关键词列表
            limit: 返回的故事数量限制
            
        Returns:
            相关故事列表
        """
        try:
            # 获取热门和最新故事
            top_stories = await self.get_top_stories(100)
            new_stories = await self.get_new_stories(100)
            
            all_stories = top_stories + new_stories
            
            # 关键词匹配
            matched_stories = []
            keywords_lower = [kw.lower() for kw in keywords]
            
            for story in all_stories:
                title = story.get('title', '').lower()
                text = story.get('text', '').lower()
                
                # 检查标题和内容是否包含关键词
                for keyword in keywords_lower:
                    if keyword in title or keyword in text:
                        story['matched_keyword'] = keyword
                        matched_stories.append(story)
                        break
            
            # 按分数排序并限制数量
            matched_stories.sort(key=lambda x: x.get('score', 0), reverse=True)
            result = matched_stories[:limit]
            
            logger.info(f"关键词搜索找到{len(result)}个相关故事")
            return result
            
        except Exception as e:
            logger.error(f"搜索故事失败: {e}")
            return []
    
    async def _get_item_details(self, item_id: int) -> Dict[str, Any]:
        """获取项目详情
        
        Args:
            item_id: 项目ID
            
        Returns:
            项目详情
        """
        item_data = await self._make_request(f"/item/{item_id}.json")
        if not item_data:
            return {}
        
        # 标准化数据格式
        return {
            'id': item_data.get('id'),
            'title': item_data.get('title', ''),
            'text': item_data.get('text', ''),
            'url': item_data.get('url', ''),
            'score': item_data.get('score', 0),
            'by': item_data.get('by', ''),
            'time': item_data.get('time', 0),
            'descendants': item_data.get('descendants', 0),  # 评论数
            'kids': item_data.get('kids', []),  # 子评论ID列表
            'type': item_data.get('type', 'story'),
            'created_at': datetime.fromtimestamp(item_data.get('time', 0)).isoformat() if item_data.get('time') else None,
            'source': 'hacker_news'
        }
    
    async def get_item_comments(self, item_id: int, max_comments: int = 20) -> List[Dict[str, Any]]:
        """获取项目评论
        
        Args:
            item_id: 项目ID
            max_comments: 最大评论数
            
        Returns:
            评论列表
        """
        try:
            # 获取项目详情
            item = await self._get_item_details(item_id)
            if not item or not item.get('kids'):
                return []
            
            # 获取评论ID列表
            comment_ids = item['kids'][:max_comments]
            
            # 并行获取评论详情
            tasks = [self._get_item_details(comment_id) for comment_id in comment_ids]
            comments = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效评论
            valid_comments = []
            for comment in comments:
                if isinstance(comment, dict) and comment.get('text'):
                    valid_comments.append(comment)
            
            logger.info(f"获取到{len(valid_comments)}条评论")
            return valid_comments
            
        except Exception as e:
            logger.error(f"获取评论失败: {e}")
            return []
    
    async def get_trending_topics(self, limit: int = 50) -> List[str]:
        """获取热门话题
        
        Args:
            limit: 分析的故事数量
            
        Returns:
            热门话题关键词列表
        """
        try:
            # 获取热门故事
            stories = await self.get_top_stories(limit)
            
            # 提取标题中的关键词
            all_words = []
            for story in stories:
                title = story.get('title', '')
                # 简单的关键词提取（可以后续用更复杂的NLP）
                words = title.lower().split()
                # 过滤常见词汇
                filtered_words = [w for w in words if len(w) > 3 and w not in [
                    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'
                ]]
                all_words.extend(filtered_words)
            
            # 统计词频
            from collections import Counter
            word_counts = Counter(all_words)
            
            # 返回最常见的词汇
            trending_topics = [word for word, count in word_counts.most_common(20)]
            
            logger.info(f"提取到{len(trending_topics)}个热门话题")
            return trending_topics
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return []
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户信息
        """
        try:
            user_data = await self._make_request(f"/user/{username}.json")
            if not user_data:
                return {}
            
            return {
                'id': user_data.get('id'),
                'created': user_data.get('created'),
                'karma': user_data.get('karma', 0),
                'about': user_data.get('about', ''),
                'submitted': user_data.get('submitted', []),
                'source': 'hacker_news'
            }
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {}
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()

# 创建服务实例
hacker_news_service = HackerNewsService()