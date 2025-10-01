#!/usr/bin/env python3
"""
Twitter大规模数据收集器
收集推文、回复、话题讨论等数据
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
class TwitterData:
    """Twitter数据结构"""
    id: str
    text: str
    author_id: str
    created_at: str
    public_metrics: Dict
    context_annotations: List[Dict]
    referenced_tweets: List[Dict]

class TwitterCollector:
    """Twitter数据收集器"""
    
    def __init__(self):
        # Twitter API v2 Bearer Token
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if not self.bearer_token:
            logger.error("未找到Twitter Bearer Token")
            raise ValueError("需要设置TWITTER_BEARER_TOKEN环境变量")
        
        # API限制管理
        self.requests_made = 0
        self.last_reset = time.time()
        
        # Twitter API v2 限制（基础层级）
        self.max_requests_per_15min = 300  # 大部分端点的限制
        self.max_tweets_per_month = 10000  # 基础层级月度限制
        
        # 搜索关键词（按专家类型分类）
        self.search_queries = {
            'business_strategy': [
                'business strategy', 'startup advice', 'entrepreneurship tips',
                'growth hacking', 'business model', 'revenue optimization',
                'market analysis', 'competitive advantage'
            ],
            'data_insight': [
                'data analytics', 'business intelligence', 'data visualization',
                'metrics analysis', 'KPI dashboard', 'data science insights',
                'analytics tools', 'data driven decisions'
            ],
            'user_insight': [
                'user experience', 'customer feedback', 'user research',
                'UX design', 'customer journey', 'user behavior analysis',
                'customer satisfaction', 'user testing'
            ],
            'competitive_intelligence': [
                'competitive analysis', 'market research', 'competitor insights',
                'industry trends', 'market intelligence', 'business intelligence',
                'competitive landscape'
            ],
            'failure_prevention': [
                'startup failures', 'business mistakes', 'lessons learned',
                'avoid pitfalls', 'risk management', 'failure analysis',
                'business risks', 'startup lessons'
            ]
        }
        
        logger.info("Twitter收集器初始化完成")

    async def check_rate_limit(self):
        """检查并管理API速率限制"""
        current_time = time.time()
        
        # 重置计数器（每15分钟）
        if current_time - self.last_reset >= 900:  # 15分钟 = 900秒
            self.requests_made = 0
            self.last_reset = current_time
        
        # 如果接近限制，等待
        if self.requests_made >= self.max_requests_per_15min:
            wait_time = 900 - (current_time - self.last_reset)
            if wait_time > 0:
                logger.info(f"达到Twitter API限制，等待 {wait_time:.1f} 秒")
                await asyncio.sleep(wait_time)
                self.requests_made = 0
                self.last_reset = time.time()

    async def make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """发起Twitter API请求"""
        await self.check_rate_limit()
        
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'IdeaEden-DataCollector/2.0'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    self.requests_made += 1
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        logger.warning("Twitter API速率限制")
                        # 从响应头获取重置时间
                        reset_time = response.headers.get('x-rate-limit-reset')
                        if reset_time:
                            wait_time = int(reset_time) - time.time()
                            if wait_time > 0:
                                logger.info(f"等待速率限制重置: {wait_time:.1f}秒")
                                await asyncio.sleep(wait_time)
                        else:
                            await asyncio.sleep(900)  # 默认等待15分钟
                        return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Twitter API请求失败: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Twitter API请求异常: {e}")
            return None

    async def search_tweets(self, query: str, max_results: int = 100) -> List[Dict]:
        """搜索推文"""
        url = 'https://api.twitter.com/2/tweets/search/recent'
        
        # 构建查询参数
        params = {
            'query': f'{query} -is:retweet lang:en',  # 排除转推，只要英文
            'max_results': min(max_results, 100),  # API单次最大100
            'tweet.fields': 'created_at,author_id,public_metrics,context_annotations,referenced_tweets,lang',
            'expansions': 'author_id,referenced_tweets.id',
            'user.fields': 'username,public_metrics,verified'
        }
        
        data = await self.make_request(url, params)
        
        if data and 'data' in data:
            tweets = data['data']
            
            # 过滤高质量推文
            quality_tweets = []
            for tweet in tweets:
                if self.is_quality_tweet(tweet):
                    quality_tweets.append(tweet)
            
            logger.info(f"搜索查询 '{query}' 获取到 {len(quality_tweets)} 条高质量推文")
            return quality_tweets
        
        return []

    def is_quality_tweet(self, tweet: Dict) -> bool:
        """判断推文质量"""
        # 基本质量过滤
        text = tweet.get('text', '')
        
        # 文本长度检查
        if len(text) < 50:  # 太短的推文
            return False
        
        # 检查互动指标
        metrics = tweet.get('public_metrics', {})
        like_count = metrics.get('like_count', 0)
        retweet_count = metrics.get('retweet_count', 0)
        reply_count = metrics.get('reply_count', 0)
        
        # 至少要有一些互动
        if like_count + retweet_count + reply_count < 2:
            return False
        
        # 排除垃圾内容
        spam_indicators = ['spam', 'advertisement', 'buy now', 'click here', 'follow me']
        text_lower = text.lower()
        
        if any(indicator in text_lower for indicator in spam_indicators):
            return False
        
        # 排除过多链接的推文
        if text.count('http') > 2:
            return False
        
        return True

    def determine_expert_type(self, tweet: Dict) -> str:
        """根据推文内容确定专家类型"""
        text = tweet.get('text', '').lower()
        
        # 检查上下文注释
        context_annotations = tweet.get('context_annotations', [])
        context_text = ' '.join([
            annotation.get('entity', {}).get('name', '') 
            for annotation in context_annotations
        ]).lower()
        
        full_text = text + ' ' + context_text
        
        # 关键词匹配
        type_keywords = {
            'business_strategy': [
                'business', 'strategy', 'startup', 'entrepreneur', 'revenue',
                'growth', 'market', 'sales', 'marketing', 'profit', 'ceo'
            ],
            'data_insight': [
                'data', 'analytics', 'metrics', 'analysis', 'insights',
                'dashboard', 'reporting', 'statistics', 'visualization'
            ],
            'user_insight': [
                'user', 'customer', 'ux', 'ui', 'design', 'experience',
                'feedback', 'satisfaction', 'journey', 'persona'
            ],
            'competitive_intelligence': [
                'competitor', 'competitive', 'market share', 'industry',
                'analysis', 'benchmark', 'intelligence', 'research'
            ],
            'failure_prevention': [
                'mistake', 'failure', 'lesson', 'avoid', 'risk',
                'problem', 'error', 'warning', 'pitfall'
            ]
        }
        
        # 计算每个类型的匹配分数
        scores = {}
        for expert_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            scores[expert_type] = score
        
        # 返回得分最高的类型
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else 'business_strategy'

    def calculate_quality_score(self, tweet: Dict) -> float:
        """计算推文质量分数"""
        score = 0.5  # 基础分数
        
        # 互动指标评分
        metrics = tweet.get('public_metrics', {})
        like_count = metrics.get('like_count', 0)
        retweet_count = metrics.get('retweet_count', 0)
        reply_count = metrics.get('reply_count', 0)
        
        # 点赞数评分
        if like_count > 100:
            score += 0.2
        elif like_count > 50:
            score += 0.15
        elif like_count > 10:
            score += 0.1
        
        # 转发数评分
        if retweet_count > 50:
            score += 0.15
        elif retweet_count > 10:
            score += 0.1
        elif retweet_count > 5:
            score += 0.05
        
        # 回复数评分
        if reply_count > 20:
            score += 0.1
        elif reply_count > 5:
            score += 0.05
        
        # 内容长度评分
        text_length = len(tweet.get('text', ''))
        if text_length > 200:
            score += 0.1
        elif text_length > 100:
            score += 0.05
        
        # 上下文注释评分（有主题标签的推文通常质量更高）
        if tweet.get('context_annotations'):
            score += 0.05
        
        return min(1.0, score)

    async def collect_batch(self, target_count: int) -> List[Dict]:
        """收集一批数据"""
        logger.info(f"开始收集Twitter数据，目标: {target_count}条")
        
        collected_data = []
        tweets_per_query = max(1, target_count // 10)  # 分散到多个查询
        
        # 遍历所有专家类型和查询
        for expert_type, queries in self.search_queries.items():
            if len(collected_data) >= target_count:
                break
            
            for query in queries:
                if len(collected_data) >= target_count:
                    break
                
                try:
                    tweets = await self.search_tweets(query, max_results=tweets_per_query)
                    
                    for tweet in tweets:
                        if len(collected_data) >= target_count:
                            break
                        
                        # 生成唯一ID
                        data_id = hashlib.md5(
                            f"twitter_{tweet['id']}_{tweet['created_at']}".encode()
                        ).hexdigest()
                        
                        # 构建训练数据
                        data_item = {
                            'text': tweet['text'],
                            'expert_type': self.determine_expert_type(tweet),
                            'quality_score': self.calculate_quality_score(tweet),
                            'source': 'twitter',
                            'metadata': {
                                'tweet_id': tweet['id'],
                                'author_id': tweet['author_id'],
                                'created_at': tweet['created_at'],
                                'public_metrics': tweet.get('public_metrics', {}),
                                'context_annotations': tweet.get('context_annotations', []),
                                'lang': tweet.get('lang', 'en'),
                                'search_query': query
                            },
                            'timestamp': datetime.now(),
                            'data_id': data_id
                        }
                        
                        collected_data.append(data_item)
                    
                    # 避免过于频繁的请求
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"收集查询 '{query}' 数据失败: {e}")
                    continue
        
        logger.info(f"Twitter数据收集完成: {len(collected_data)}条")
        return collected_data

    async def get_user_tweets(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """获取特定用户的推文（可选功能）"""
        url = f'https://api.twitter.com/2/users/{user_id}/tweets'
        
        params = {
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'exclude': 'retweets,replies'
        }
        
        data = await self.make_request(url, params)
        
        if data and 'data' in data:
            return data['data']
        return []

    async def get_tweet_conversation(self, tweet_id: str) -> List[Dict]:
        """获取推文的对话线程（可选功能）"""
        url = 'https://api.twitter.com/2/tweets/search/recent'
        
        params = {
            'query': f'conversation_id:{tweet_id}',
            'max_results': 100,
            'tweet.fields': 'created_at,author_id,public_metrics,referenced_tweets'
        }
        
        data = await self.make_request(url, params)
        
        if data and 'data' in data:
            return data['data']
        return []

# 测试函数
async def test_twitter_collector():
    """测试Twitter收集器"""
    collector = TwitterCollector()
    
    # 测试收集少量数据
    data = await collector.collect_batch(5)
    
    print(f"收集到 {len(data)} 条数据")
    for item in data[:3]:  # 显示前3条
        print(f"类型: {item['expert_type']}")
        print(f"质量: {item['quality_score']:.2f}")
        print(f"互动: {item['metadata']['public_metrics']}")
        print(f"文本: {item['text'][:100]}...")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_twitter_collector())