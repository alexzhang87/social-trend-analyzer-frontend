#!/usr/bin/env python3
"""
Reddit大规模数据收集器
支持多子版块、智能限流、数据质量评估
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RedditPost:
    """Reddit帖子数据结构"""
    id: str
    title: str
    selftext: str
    subreddit: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    author: str

class RedditCollector:
    """Reddit数据收集器"""
    
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = 'IdeaEden:v1.0 (by /u/ideaeden_bot)'
        self.access_token = None
        self.token_expires = 0
        
        # 目标子版块（按专家类型分类）
        self.subreddits = {
            'business_strategy': [
                'entrepreneur', 'startups', 'business', 'marketing', 'sales',
                'smallbusiness', 'investing', 'financialindependence'
            ],
            'data_insight': [
                'datascience', 'analytics', 'MachineLearning', 'statistics',
                'bigdata', 'dataengineering', 'BusinessIntelligence'
            ],
            'user_insight': [
                'userexperience', 'design', 'product', 'customerservice',
                'surveys', 'marketresearch', 'psychology'
            ],
            'competitive_intelligence': [
                'competitor', 'marketanalysis', 'industry', 'trends',
                'business', 'strategy'
            ],
            'failure_prevention': [
                'tifu', 'entrepreneur', 'startups', 'lessons',
                'mistakes', 'failure', 'learnings'
            ]
        }
        
        # API限制管理
        self.requests_made = 0
        self.last_reset = time.time()
        self.max_requests_per_minute = 60  # Reddit API限制
        
        logger.info("Reddit收集器初始化完成")

    async def get_access_token(self) -> str:
        """获取Reddit API访问令牌"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
        
        auth_url = 'https://www.reddit.com/api/v1/access_token'
        
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        headers = {'User-Agent': self.user_agent}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data, auth=auth, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.token_expires = time.time() + token_data['expires_in'] - 60  # 提前1分钟刷新
                    logger.info("Reddit访问令牌获取成功")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"获取Reddit访问令牌失败: {response.status} - {error_text}")
                    raise Exception(f"Reddit认证失败: {response.status}")

    async def check_rate_limit(self):
        """检查并管理API速率限制"""
        current_time = time.time()
        
        # 重置计数器（每分钟）
        if current_time - self.last_reset >= 60:
            self.requests_made = 0
            self.last_reset = current_time
        
        # 如果接近限制，等待
        if self.requests_made >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.last_reset)
            if wait_time > 0:
                logger.info(f"达到API限制，等待 {wait_time:.1f} 秒")
                await asyncio.sleep(wait_time)
                self.requests_made = 0
                self.last_reset = time.time()

    async def fetch_subreddit_posts(self, subreddit: str, limit: int = 100, 
                                  time_filter: str = 'day') -> List[RedditPost]:
        """获取指定子版块的帖子"""
        await self.check_rate_limit()
        
        access_token = await self.get_access_token()
        
        # 构建API URL
        url = f'https://oauth.reddit.com/r/{subreddit}/hot'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': self.user_agent
        }
        
        params = {
            'limit': min(limit, 100),  # Reddit API单次最大100
            't': time_filter
        }
        
        posts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    self.requests_made += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        for post_data in data['data']['children']:
                            post = post_data['data']
                            
                            # 过滤低质量帖子
                            if self.is_quality_post(post):
                                reddit_post = RedditPost(
                                    id=post['id'],
                                    title=post['title'],
                                    selftext=post.get('selftext', ''),
                                    subreddit=post['subreddit'],
                                    score=post['score'],
                                    num_comments=post['num_comments'],
                                    created_utc=post['created_utc'],
                                    url=f"https://reddit.com{post['permalink']}",
                                    author=post.get('author', '[deleted]')
                                )
                                posts.append(reddit_post)
                        
                        logger.info(f"从 r/{subreddit} 获取到 {len(posts)} 条高质量帖子")
                        
                    elif response.status == 429:
                        logger.warning("Reddit API速率限制，等待重试")
                        await asyncio.sleep(60)
                    else:
                        error_text = await response.text()
                        logger.error(f"获取 r/{subreddit} 数据失败: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"获取 r/{subreddit} 数据异常: {e}")
        
        return posts

    def is_quality_post(self, post: Dict) -> bool:
        """判断帖子质量"""
        # 基本质量过滤
        if post['score'] < 5:  # 至少5个赞
            return False
        
        if post['num_comments'] < 2:  # 至少2个评论
            return False
        
        # 内容长度检查
        title_len = len(post['title'])
        selftext_len = len(post.get('selftext', ''))
        
        if title_len < 10:  # 标题太短
            return False
        
        if selftext_len == 0 and title_len < 50:  # 没有正文且标题太短
            return False
        
        # 排除垃圾内容
        spam_indicators = ['[removed]', '[deleted]', 'spam', 'advertisement']
        content = (post['title'] + ' ' + post.get('selftext', '')).lower()
        
        if any(indicator in content for indicator in spam_indicators):
            return False
        
        return True

    def determine_expert_type(self, post: RedditPost) -> str:
        """根据帖子内容确定专家类型"""
        content = (post.title + ' ' + post.selftext).lower()
        
        # 关键词匹配
        type_keywords = {
            'business_strategy': [
                'business', 'strategy', 'startup', 'entrepreneur', 'revenue',
                'growth', 'market', 'competition', 'sales', 'marketing'
            ],
            'data_insight': [
                'data', 'analytics', 'metrics', 'analysis', 'statistics',
                'insights', 'dashboard', 'reporting', 'kpi'
            ],
            'user_insight': [
                'user', 'customer', 'feedback', 'experience', 'behavior',
                'satisfaction', 'survey', 'interview', 'persona'
            ],
            'competitive_intelligence': [
                'competitor', 'competitive', 'market share', 'benchmark',
                'industry', 'analysis', 'comparison'
            ],
            'failure_prevention': [
                'mistake', 'failure', 'lesson', 'avoid', 'problem',
                'issue', 'risk', 'warning', 'error'
            ]
        }
        
        # 计算每个类型的匹配分数
        scores = {}
        for expert_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[expert_type] = score
        
        # 返回得分最高的类型，如果都是0则根据子版块判断
        best_type = max(scores, key=scores.get)
        if scores[best_type] > 0:
            return best_type
        
        # 根据子版块分类
        for expert_type, subreddits in self.subreddits.items():
            if post.subreddit.lower() in [s.lower() for s in subreddits]:
                return expert_type
        
        return 'business_strategy'  # 默认类型

    def calculate_quality_score(self, post: RedditPost) -> float:
        """计算帖子质量分数"""
        score = 0.5  # 基础分数
        
        # 社区互动评分
        if post.score > 50:
            score += 0.2
        elif post.score > 20:
            score += 0.1
        
        if post.num_comments > 20:
            score += 0.15
        elif post.num_comments > 10:
            score += 0.1
        
        # 内容长度评分
        content_length = len(post.title + post.selftext)
        if content_length > 500:
            score += 0.1
        elif content_length > 200:
            score += 0.05
        
        # 时效性评分（越新越好）
        post_age_hours = (time.time() - post.created_utc) / 3600
        if post_age_hours < 24:
            score += 0.05
        
        return min(1.0, score)

    async def collect_batch(self, target_count: int) -> List[Dict]:
        """收集一批数据"""
        logger.info(f"开始收集Reddit数据，目标: {target_count}条")
        
        collected_data = []
        posts_per_subreddit = max(1, target_count // 20)  # 分散到多个子版块
        
        # 遍历所有专家类型和子版块
        for expert_type, subreddits in self.subreddits.items():
            for subreddit in subreddits:
                if len(collected_data) >= target_count:
                    break
                
                try:
                    posts = await self.fetch_subreddit_posts(
                        subreddit, 
                        limit=posts_per_subreddit,
                        time_filter='day'
                    )
                    
                    for post in posts:
                        if len(collected_data) >= target_count:
                            break
                        
                        # 生成唯一ID
                        data_id = hashlib.md5(
                            f"reddit_{post.id}_{post.created_utc}".encode()
                        ).hexdigest()
                        
                        # 构建训练数据
                        text = post.title
                        if post.selftext:
                            text += "\n\n" + post.selftext
                        
                        data_item = {
                            'text': text,
                            'expert_type': self.determine_expert_type(post),
                            'quality_score': self.calculate_quality_score(post),
                            'source': 'reddit',
                            'metadata': {
                                'subreddit': post.subreddit,
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'created_utc': post.created_utc,
                                'url': post.url,
                                'author': post.author
                            },
                            'timestamp': datetime.now(),
                            'data_id': data_id
                        }
                        
                        collected_data.append(data_item)
                    
                    # 避免过于频繁的请求
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"收集 r/{subreddit} 数据失败: {e}")
                    continue
        
        logger.info(f"Reddit数据收集完成: {len(collected_data)}条")
        return collected_data

    async def collect_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """收集帖子评论（可选功能）"""
        await self.check_rate_limit()
        
        access_token = await self.get_access_token()
        
        url = f'https://oauth.reddit.com/comments/{post_id}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': self.user_agent
        }
        
        params = {'limit': limit}
        
        comments = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    self.requests_made += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # 处理评论数据
                        if len(data) > 1:
                            comments_data = data[1]['data']['children']
                            
                            for comment_data in comments_data:
                                if comment_data['kind'] == 't1':  # 评论类型
                                    comment = comment_data['data']
                                    
                                    if comment.get('body') and comment['body'] != '[deleted]':
                                        comments.append({
                                            'id': comment['id'],
                                            'body': comment['body'],
                                            'score': comment['score'],
                                            'created_utc': comment['created_utc'],
                                            'author': comment.get('author', '[deleted]')
                                        })
                        
        except Exception as e:
            logger.error(f"获取评论失败: {e}")
        
        return comments

# 测试函数
async def test_reddit_collector():
    """测试Reddit收集器"""
    collector = RedditCollector()
    
    # 测试收集少量数据
    data = await collector.collect_batch(10)
    
    print(f"收集到 {len(data)} 条数据")
    for item in data[:3]:  # 显示前3条
        print(f"类型: {item['expert_type']}")
        print(f"质量: {item['quality_score']:.2f}")
        print(f"文本: {item['text'][:100]}...")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_reddit_collector())