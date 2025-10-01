import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import urllib.parse

logger = logging.getLogger(__name__)

class StackOverflowService:
    """Stack Overflow API 服务
    
    提供Stack Overflow数据获取功能，包括:
    - 搜索问题和答案
    - 获取热门问题
    - 获取标签信息
    - 获取用户信息
    """
    
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        self.session = None
        self.rate_limit_delay = 0.1  # 每秒最多10次请求
        
        logger.info("StackOverflowService 已初始化")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Social-Trend-Analyzer/1.0'
                }
            )
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发起API请求"""
        session = await self._get_session()
        
        # 添加基础参数
        params.update({
            'site': self.site,
            'filter': 'default'
        })
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # 速率限制
            await asyncio.sleep(self.rate_limit_delay)
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 429:
                    logger.warning("Stack Overflow API 速率限制，等待重试")
                    await asyncio.sleep(5)
                    return await self._make_request(endpoint, params)
                else:
                    logger.error(f"Stack Overflow API 请求失败: {response.status}")
                    return {'items': []}
                    
        except Exception as e:
            logger.error(f"Stack Overflow API 请求异常: {e}")
            return {'items': []}
    
    async def search_questions(self, query: str, limit: int = 20, 
                             sort: str = 'relevance', 
                             time_filter: str = 'week') -> List[Dict[str, Any]]:
        """搜索问题
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            sort: 排序方式 (relevance, activity, votes, creation)
            time_filter: 时间过滤 (day, week, month, year)
        
        Returns:
            问题列表
        """
        try:
            # 计算时间范围
            now = datetime.now()
            if time_filter == 'day':
                from_date = now - timedelta(days=1)
            elif time_filter == 'week':
                from_date = now - timedelta(weeks=1)
            elif time_filter == 'month':
                from_date = now - timedelta(days=30)
            else:  # year
                from_date = now - timedelta(days=365)
            
            params = {
                'q': query,
                'pagesize': min(limit, 100),
                'sort': sort,
                'order': 'desc',
                'fromdate': int(from_date.timestamp())
            }
            
            data = await self._make_request('search', params)
            questions = data.get('items', [])
            
            # 格式化结果
            formatted_questions = []
            for question in questions:
                formatted_question = {
                    'id': question.get('question_id'),
                    'title': question.get('title', ''),
                    'body': question.get('body', ''),
                    'score': question.get('score', 0),
                    'view_count': question.get('view_count', 0),
                    'answer_count': question.get('answer_count', 0),
                    'tags': question.get('tags', []),
                    'creation_date': datetime.fromtimestamp(question.get('creation_date', 0)),
                    'last_activity_date': datetime.fromtimestamp(question.get('last_activity_date', 0)),
                    'owner': question.get('owner', {}),
                    'link': question.get('link', ''),
                    'is_answered': question.get('is_answered', False),
                    'platform': 'stackoverflow',
                    'type': 'question'
                }
                formatted_questions.append(formatted_question)
            
            logger.info(f"获取到 {len(formatted_questions)} 个Stack Overflow问题")
            return formatted_questions
            
        except Exception as e:
            logger.error(f"搜索Stack Overflow问题失败: {e}")
            return []
    
    async def get_hot_questions(self, limit: int = 20, 
                              time_filter: str = 'week') -> List[Dict[str, Any]]:
        """获取热门问题
        
        Args:
            limit: 返回结果数量限制
            time_filter: 时间过滤 (day, week, month)
        
        Returns:
            热门问题列表
        """
        try:
            # 计算时间范围
            now = datetime.now()
            if time_filter == 'day':
                from_date = now - timedelta(days=1)
            elif time_filter == 'week':
                from_date = now - timedelta(weeks=1)
            else:  # month
                from_date = now - timedelta(days=30)
            
            params = {
                'pagesize': min(limit, 100),
                'sort': 'hot',
                'order': 'desc',
                'fromdate': int(from_date.timestamp())
            }
            
            data = await self._make_request('questions', params)
            questions = data.get('items', [])
            
            # 格式化结果
            formatted_questions = []
            for question in questions:
                formatted_question = {
                    'id': question.get('question_id'),
                    'title': question.get('title', ''),
                    'body': question.get('body', ''),
                    'score': question.get('score', 0),
                    'view_count': question.get('view_count', 0),
                    'answer_count': question.get('answer_count', 0),
                    'tags': question.get('tags', []),
                    'creation_date': datetime.fromtimestamp(question.get('creation_date', 0)),
                    'last_activity_date': datetime.fromtimestamp(question.get('last_activity_date', 0)),
                    'owner': question.get('owner', {}),
                    'link': question.get('link', ''),
                    'is_answered': question.get('is_answered', False),
                    'platform': 'stackoverflow',
                    'type': 'hot_question'
                }
                formatted_questions.append(formatted_question)
            
            logger.info(f"获取到 {len(formatted_questions)} 个Stack Overflow热门问题")
            return formatted_questions
            
        except Exception as e:
            logger.error(f"获取Stack Overflow热门问题失败: {e}")
            return []
    
    async def get_trending_tags(self, limit: int = 20, 
                              time_filter: str = 'week') -> List[Dict[str, Any]]:
        """获取热门标签
        
        Args:
            limit: 返回结果数量限制
            time_filter: 时间过滤 (day, week, month)
        
        Returns:
            热门标签列表
        """
        try:
            params = {
                'pagesize': min(limit, 100),
                'sort': 'popular',
                'order': 'desc'
            }
            
            data = await self._make_request('tags', params)
            tags = data.get('items', [])
            
            # 格式化结果
            formatted_tags = []
            for tag in tags:
                formatted_tag = {
                    'name': tag.get('name', ''),
                    'count': tag.get('count', 0),
                    'excerpt': tag.get('excerpt', ''),
                    'wiki_url': tag.get('wiki_url', ''),
                    'platform': 'stackoverflow',
                    'type': 'tag'
                }
                formatted_tags.append(formatted_tag)
            
            logger.info(f"获取到 {len(formatted_tags)} 个Stack Overflow热门标签")
            return formatted_tags
            
        except Exception as e:
            logger.error(f"获取Stack Overflow热门标签失败: {e}")
            return []
    
    async def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息
        """
        try:
            params = {}
            
            data = await self._make_request(f'users/{user_id}', params)
            users = data.get('items', [])
            
            if users:
                user = users[0]
                formatted_user = {
                    'user_id': user.get('user_id'),
                    'display_name': user.get('display_name', ''),
                    'reputation': user.get('reputation', 0),
                    'badge_counts': user.get('badge_counts', {}),
                    'creation_date': datetime.fromtimestamp(user.get('creation_date', 0)),
                    'last_access_date': datetime.fromtimestamp(user.get('last_access_date', 0)),
                    'location': user.get('location', ''),
                    'website_url': user.get('website_url', ''),
                    'link': user.get('link', ''),
                    'profile_image': user.get('profile_image', ''),
                    'platform': 'stackoverflow'
                }
                
                logger.info(f"获取到Stack Overflow用户信息: {user.get('display_name')}")
                return formatted_user
            else:
                return {}
                
        except Exception as e:
            logger.error(f"获取Stack Overflow用户信息失败: {e}")
            return {}
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("StackOverflowService HTTP会话已关闭")
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # 在事件循环中关闭会话
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass