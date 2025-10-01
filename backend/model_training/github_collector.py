#!/usr/bin/env python3
"""
GitHub大规模数据收集器
收集仓库、Issue、讨论、代码等数据
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
import base64

logger = logging.getLogger(__name__)

@dataclass
class GitHubData:
    """GitHub数据结构"""
    id: str
    title: str
    body: str
    data_type: str  # 'issue', 'discussion', 'readme', 'code'
    repository: str
    language: str
    stars: int
    created_at: str
    url: str

class GitHubCollector:
    """GitHub数据收集器"""
    
    def __init__(self):
        # 支持多个token轮换使用
        self.tokens = [
            os.getenv('GITHUB_TOKEN_1'),
            os.getenv('GITHUB_TOKEN_2'),
            os.getenv('GITHUB_TOKEN_3'),
            os.getenv('GITHUB_TOKEN_4'),
            os.getenv('GITHUB_TOKEN_5')
        ]
        self.tokens = [token for token in self.tokens if token]  # 过滤空token
        
        if not self.tokens:
            logger.warning("未找到GitHub tokens，将使用未认证访问（限制较大）")
        
        self.current_token_index = 0
        self.requests_made = {}  # 每个token的请求计数
        self.last_reset = {}     # 每个token的重置时间
        
        # 初始化每个token的计数器
        for i, token in enumerate(self.tokens):
            self.requests_made[i] = 0
            self.last_reset[i] = time.time()
        
        # API限制：认证用户5000/小时，未认证60/小时
        self.max_requests_per_hour = 5000 if self.tokens else 60
        
        # 目标仓库类型（按专家类型分类）
        self.repo_topics = {
            'business_strategy': [
                'business', 'startup', 'entrepreneurship', 'strategy',
                'marketing', 'sales', 'growth-hacking', 'business-intelligence'
            ],
            'data_insight': [
                'data-science', 'analytics', 'machine-learning', 'data-analysis',
                'business-intelligence', 'data-visualization', 'statistics'
            ],
            'user_insight': [
                'user-experience', 'ux', 'ui', 'design', 'user-research',
                'customer-feedback', 'usability', 'product-design'
            ],
            'competitive_intelligence': [
                'competitive-analysis', 'market-research', 'competitor-analysis',
                'business-intelligence', 'market-intelligence'
            ],
            'failure_prevention': [
                'testing', 'quality-assurance', 'debugging', 'error-handling',
                'monitoring', 'reliability', 'best-practices'
            ]
        }
        
        logger.info(f"GitHub收集器初始化完成，可用tokens: {len(self.tokens)}")

    def get_current_token(self) -> Optional[str]:
        """获取当前可用的token"""
        if not self.tokens:
            return None
        
        # 检查当前token是否可用
        current_time = time.time()
        token_index = self.current_token_index
        
        # 重置计数器（每小时）
        if current_time - self.last_reset[token_index] >= 3600:
            self.requests_made[token_index] = 0
            self.last_reset[token_index] = current_time
        
        # 如果当前token达到限制，切换到下一个
        if self.requests_made[token_index] >= self.max_requests_per_hour:
            # 尝试找到可用的token
            for i in range(len(self.tokens)):
                test_index = (self.current_token_index + i + 1) % len(self.tokens)
                
                # 重置计数器
                if current_time - self.last_reset[test_index] >= 3600:
                    self.requests_made[test_index] = 0
                    self.last_reset[test_index] = current_time
                
                if self.requests_made[test_index] < self.max_requests_per_hour:
                    self.current_token_index = test_index
                    logger.info(f"切换到token {test_index}")
                    return self.tokens[test_index]
            
            # 所有token都达到限制，等待
            logger.warning("所有GitHub tokens都达到限制，等待重置")
            return None
        
        return self.tokens[token_index]

    async def check_rate_limit(self):
        """检查并管理API速率限制"""
        token = self.get_current_token()
        if token is None and self.tokens:
            # 等待最早重置的token
            min_wait_time = min(
                3600 - (time.time() - reset_time) 
                for reset_time in self.last_reset.values()
            )
            if min_wait_time > 0:
                logger.info(f"等待GitHub API限制重置: {min_wait_time:.1f}秒")
                await asyncio.sleep(min_wait_time)

    async def make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """发起GitHub API请求"""
        await self.check_rate_limit()
        
        token = self.get_current_token()
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'IdeaEden-DataCollector/1.0'
        }
        
        if token:
            headers['Authorization'] = f'token {token}'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    # 更新请求计数
                    if token:
                        self.requests_made[self.current_token_index] += 1
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403:
                        logger.warning(f"GitHub API限制: {response.status}")
                        # 检查是否是速率限制
                        if 'X-RateLimit-Remaining' in response.headers:
                            remaining = int(response.headers['X-RateLimit-Remaining'])
                            if remaining == 0:
                                reset_time = int(response.headers['X-RateLimit-Reset'])
                                wait_time = reset_time - time.time()
                                if wait_time > 0:
                                    logger.info(f"等待速率限制重置: {wait_time:.1f}秒")
                                    await asyncio.sleep(wait_time)
                        return None
                    else:
                        error_text = await response.text()
                        logger.error(f"GitHub API请求失败: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"GitHub API请求异常: {e}")
            return None

    async def search_repositories(self, query: str, per_page: int = 100) -> List[Dict]:
        """搜索仓库"""
        url = 'https://api.github.com/search/repositories'
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page
        }
        
        data = await self.make_request(url, params)
        if data and 'items' in data:
            return data['items']
        return []

    async def get_repository_issues(self, owner: str, repo: str, 
                                  state: str = 'all', per_page: int = 100) -> List[Dict]:
        """获取仓库的Issues"""
        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        params = {
            'state': state,
            'per_page': per_page,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        data = await self.make_request(url, params)
        if data:
            # 过滤掉Pull Requests（GitHub API中Issues包含PR）
            return [issue for issue in data if 'pull_request' not in issue]
        return []

    async def get_repository_discussions(self, owner: str, repo: str) -> List[Dict]:
        """获取仓库的Discussions（需要GraphQL API）"""
        # 这里简化处理，实际可以使用GraphQL API获取更多讨论数据
        # 暂时返回空列表，可以后续扩展
        return []

    async def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """获取仓库的README内容"""
        url = f'https://api.github.com/repos/{owner}/{repo}/readme'
        
        data = await self.make_request(url)
        if data and 'content' in data:
            try:
                # README内容是base64编码的
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
            except Exception as e:
                logger.error(f"解码README失败: {e}")
        return None

    def determine_expert_type(self, content: str, repo_topics: List[str] = None) -> str:
        """根据内容确定专家类型"""
        content_lower = content.lower()
        
        # 首先检查仓库主题
        if repo_topics:
            for expert_type, topics in self.repo_topics.items():
                if any(topic in repo_topics for topic in topics):
                    return expert_type
        
        # 关键词匹配
        type_keywords = {
            'business_strategy': [
                'business', 'strategy', 'startup', 'revenue', 'growth',
                'market', 'customer', 'sales', 'marketing', 'profit'
            ],
            'data_insight': [
                'data', 'analytics', 'analysis', 'metrics', 'dashboard',
                'visualization', 'statistics', 'insights', 'reporting'
            ],
            'user_insight': [
                'user', 'ux', 'ui', 'design', 'experience', 'interface',
                'usability', 'feedback', 'customer', 'persona'
            ],
            'competitive_intelligence': [
                'competitor', 'competitive', 'market', 'analysis',
                'benchmark', 'comparison', 'intelligence'
            ],
            'failure_prevention': [
                'error', 'bug', 'issue', 'problem', 'fix', 'debug',
                'test', 'quality', 'reliability', 'monitoring'
            ]
        }
        
        # 计算匹配分数
        scores = {}
        for expert_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[expert_type] = score
        
        # 返回得分最高的类型
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else 'business_strategy'

    def calculate_quality_score(self, data_item: Dict, data_type: str) -> float:
        """计算数据质量分数"""
        score = 0.5  # 基础分数
        
        if data_type == 'repository':
            # 仓库质量评分
            stars = data_item.get('stargazers_count', 0)
            forks = data_item.get('forks_count', 0)
            
            if stars > 1000:
                score += 0.3
            elif stars > 100:
                score += 0.2
            elif stars > 10:
                score += 0.1
            
            if forks > 100:
                score += 0.1
            elif forks > 10:
                score += 0.05
            
        elif data_type == 'issue':
            # Issue质量评分
            comments = data_item.get('comments', 0)
            
            if comments > 10:
                score += 0.2
            elif comments > 5:
                score += 0.1
            
            # 检查是否有标签
            if data_item.get('labels'):
                score += 0.05
        
        # 内容长度评分
        body = data_item.get('body', '') or ''
        if len(body) > 500:
            score += 0.15
        elif len(body) > 200:
            score += 0.1
        
        return min(1.0, score)

    async def collect_batch(self, target_count: int) -> List[Dict]:
        """收集一批数据"""
        logger.info(f"开始收集GitHub数据，目标: {target_count}条")
        
        collected_data = []
        
        # 为每个专家类型收集数据
        items_per_type = max(1, target_count // len(self.repo_topics))
        
        for expert_type, topics in self.repo_topics.items():
            if len(collected_data) >= target_count:
                break
            
            logger.info(f"收集 {expert_type} 类型数据")
            
            # 搜索相关仓库
            for topic in topics[:2]:  # 限制每个类型的主题数量
                if len(collected_data) >= target_count:
                    break
                
                try:
                    # 构建搜索查询
                    query = f'topic:{topic} stars:>10 language:python'
                    repos = await self.search_repositories(query, per_page=20)
                    
                    for repo in repos[:5]:  # 每个主题最多5个仓库
                        if len(collected_data) >= target_count:
                            break
                        
                        owner = repo['owner']['login']
                        repo_name = repo['name']
                        
                        # 收集README
                        readme_content = await self.get_repository_readme(owner, repo_name)
                        if readme_content and len(readme_content) > 100:
                            data_id = hashlib.md5(
                                f"github_readme_{repo['id']}".encode()
                            ).hexdigest()
                            
                            data_item = {
                                'text': f"Repository: {repo['full_name']}\n\n{readme_content}",
                                'expert_type': expert_type,
                                'quality_score': self.calculate_quality_score(repo, 'repository'),
                                'source': 'github',
                                'metadata': {
                                    'repository': repo['full_name'],
                                    'stars': repo['stargazers_count'],
                                    'forks': repo['forks_count'],
                                    'language': repo.get('language', 'Unknown'),
                                    'created_at': repo['created_at'],
                                    'url': repo['html_url'],
                                    'data_type': 'readme'
                                },
                                'timestamp': datetime.now(),
                                'data_id': data_id
                            }
                            
                            collected_data.append(data_item)
                        
                        # 收集Issues
                        issues = await self.get_repository_issues(owner, repo_name, per_page=10)
                        
                        for issue in issues[:3]:  # 每个仓库最多3个issue
                            if len(collected_data) >= target_count:
                                break
                            
                            if issue.get('body') and len(issue['body']) > 50:
                                data_id = hashlib.md5(
                                    f"github_issue_{issue['id']}".encode()
                                ).hexdigest()
                                
                                issue_text = f"Issue: {issue['title']}\n\n{issue['body']}"
                                
                                data_item = {
                                    'text': issue_text,
                                    'expert_type': self.determine_expert_type(issue_text),
                                    'quality_score': self.calculate_quality_score(issue, 'issue'),
                                    'source': 'github',
                                    'metadata': {
                                        'repository': repo['full_name'],
                                        'issue_number': issue['number'],
                                        'comments': issue['comments'],
                                        'state': issue['state'],
                                        'created_at': issue['created_at'],
                                        'url': issue['html_url'],
                                        'data_type': 'issue'
                                    },
                                    'timestamp': datetime.now(),
                                    'data_id': data_id
                                }
                                
                                collected_data.append(data_item)
                        
                        # 避免过于频繁的请求
                        await asyncio.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"收集主题 {topic} 数据失败: {e}")
                    continue
        
        logger.info(f"GitHub数据收集完成: {len(collected_data)}条")
        return collected_data

# 测试函数
async def test_github_collector():
    """测试GitHub收集器"""
    collector = GitHubCollector()
    
    # 测试收集少量数据
    data = await collector.collect_batch(5)
    
    print(f"收集到 {len(data)} 条数据")
    for item in data[:3]:  # 显示前3条
        print(f"类型: {item['expert_type']}")
        print(f"质量: {item['quality_score']:.2f}")
        print(f"仓库: {item['metadata']['repository']}")
        print(f"文本: {item['text'][:100]}...")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_github_collector())