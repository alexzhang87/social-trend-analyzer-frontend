#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于现有API配置的真实数据收集器
利用已配置的Reddit和GitHub API收集高质量训练数据
"""

import json
import time
import random
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExistingAPICollector:
    """基于现有API配置的数据收集器"""
    
    def __init__(self):
        # 加载环境变量 - 指定正确的.env文件路径
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        self.data = []
        self.stats = {
            'reddit_collected': 0,
            'github_collected': 0,
            'total_collected': 0,
            'start_time': datetime.now(),
            'expert_distribution': {
                'business_strategy': 0,
                'data_insight': 0,
                'user_insight': 0,
                'competitive_intelligence': 0,
                'failure_prevention': 0
            }
        }
        
        # 从环境变量或.env文件读取API配置
        self.load_api_config()
        
        # 专家类型关键词映射
        self.expert_keywords = {
            'business_strategy': [
                'business model', 'strategy', 'revenue', 'growth', 'market',
                'startup', 'entrepreneur', 'funding', 'investment', 'scaling',
                'monetization', 'business plan', 'competitive advantage'
            ],
            'data_insight': [
                'data analysis', 'analytics', 'metrics', 'kpi', 'dashboard',
                'visualization', 'statistics', 'machine learning', 'ai',
                'data science', 'insights', 'trends', 'patterns'
            ],
            'user_insight': [
                'user experience', 'ux', 'ui', 'usability', 'user research',
                'customer feedback', 'user behavior', 'persona', 'journey',
                'design thinking', 'user testing', 'interface', 'accessibility'
            ],
            'competitive_intelligence': [
                'competitor', 'competition', 'market research', 'benchmarking',
                'competitive analysis', 'market share', 'positioning',
                'differentiation', 'swot', 'market intelligence'
            ],
            'failure_prevention': [
                'bug', 'error', 'failure', 'debugging', 'troubleshooting',
                'risk management', 'quality assurance', 'testing', 'security',
                'performance', 'optimization', 'best practices', 'lessons learned'
            ]
        }
    
    def load_api_config(self):
        """加载API配置"""
        try:
            # 尝试从.env文件读取 - 使用绝对路径
            current_file = os.path.abspath(__file__)  # 获取当前文件的绝对路径
            current_dir = os.path.dirname(current_file)  # model_training目录
            backend_dir = os.path.dirname(current_dir)  # backend目录
            env_path = os.path.join(backend_dir, '.env')
            
            logger.info(f"当前文件: {current_file}")
            logger.info(f"当前目录: {current_dir}")
            logger.info(f"Backend目录: {backend_dir}")
            logger.info(f"查找.env文件: {env_path}")
            
            if os.path.exists(env_path):
                logger.info(f"✅ 找到.env文件: {env_path}")
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
                            if 'API' in key or 'CLIENT' in key:
                                logger.info(f"加载环境变量: {key}={'*' * len(value) if value else '(空)'}")
            else:
                logger.warning(f"❌ .env文件不存在: {env_path}")
            
            # Reddit API配置
            self.reddit_config = {
                'client_id': os.getenv('REDDIT_CLIENT_ID', ''),
                'client_secret': os.getenv('REDDIT_CLIENT_SECRET', ''),
                'username': os.getenv('REDDIT_USERNAME', ''),
                'password': os.getenv('REDDIT_PASSWORD', ''),
                'user_agent': 'AI-Data-Collector/1.0'
            }
            
            # GitHub API配置
            self.github_config = {
                'client_id': os.getenv('GITHUB_CLIENT_ID', ''),
                'client_secret': os.getenv('GITHUB_CLIENT_SECRET', ''),
                'token': None  # 将通过OAuth获取
            }
            
            # Twitter.io API配置（如果有的话）
            self.twitter_config = {
                'api_key': os.getenv('TWITTERAPI_IO_KEY', '')
            }
            
            # Product Hunt API配置
            self.product_hunt_config = {
                'client_id': os.getenv('PRODUCT_HUNT_CLIENT_ID', ''),
                'client_secret': os.getenv('PRODUCT_HUNT_CLIENT_SECRET', '')
            }
            
            logger.info("API配置加载完成")
            logger.info(f"Reddit配置: {'✅' if self.reddit_config['client_id'] else '❌'}")
            logger.info(f"GitHub配置: {'✅' if self.github_config['client_id'] else '❌'}")
            logger.info(f"Twitter配置: {'✅' if self.twitter_config['api_key'] else '❌'}")
            logger.info(f"Product Hunt配置: {'✅' if self.product_hunt_config['client_id'] else '❌'}")
            
        except Exception as e:
            logger.error(f"加载API配置失败: {e}")
    
    async def get_reddit_access_token(self) -> Optional[str]:
        """获取Reddit访问令牌"""
        try:
            auth = aiohttp.BasicAuth(
                self.reddit_config['client_id'],
                self.reddit_config['client_secret']
            )
            
            data = {
                'grant_type': 'password',
                'username': self.reddit_config['username'],
                'password': self.reddit_config['password']
            }
            
            headers = {
                'User-Agent': self.reddit_config['user_agent']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://www.reddit.com/api/v1/access_token',
                    auth=auth,
                    data=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('access_token')
                    else:
                        logger.error(f"Reddit认证失败: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取Reddit访问令牌失败: {e}")
            return None
    
    async def collect_reddit_data(self, target_count: int = 3000) -> List[Dict[str, Any]]:
        """收集Reddit数据"""
        logger.info(f"开始收集Reddit数据，目标: {target_count}条")
        
        access_token = await self.get_reddit_access_token()
        if not access_token:
            logger.error("无法获取Reddit访问令牌")
            return []
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': self.reddit_config['user_agent']
        }
        
        # 目标subreddit列表
        subreddits = {
            'business_strategy': ['entrepreneur', 'startups', 'business', 'investing'],
            'data_insight': ['datascience', 'analytics', 'MachineLearning', 'statistics'],
            'user_insight': ['userexperience', 'design', 'usability', 'webdev'],
            'competitive_intelligence': ['marketing', 'SEO', 'growth', 'competitor'],
            'failure_prevention': ['programming', 'debugging', 'sysadmin', 'devops']
        }
        
        collected_data = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for expert_type, subs in subreddits.items():
                    posts_per_type = target_count // 5  # 每种专家类型平均分配
                    
                    for subreddit in subs:
                        if len([d for d in collected_data if d.get('expert_type') == expert_type]) >= posts_per_type:
                            break
                        
                        try:
                            # 获取热门帖子
                            url = f'https://oauth.reddit.com/r/{subreddit}/hot'
                            params = {'limit': 100}
                            
                            async with session.get(url, headers=headers, params=params) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    posts = data.get('data', {}).get('children', [])
                                    
                                    for post in posts:
                                        post_data = post.get('data', {})
                                        
                                        # 过滤质量较低的帖子
                                        if (post_data.get('score', 0) < 5 or 
                                            len(post_data.get('title', '')) < 20 or
                                            post_data.get('is_self') == False):
                                            continue
                                        
                                        # 构建训练数据
                                        text = post_data.get('title', '')
                                        if post_data.get('selftext'):
                                            text += ' ' + post_data.get('selftext', '')[:500]
                                        
                                        if len(text) < 50:  # 过滤太短的内容
                                            continue
                                        
                                        item = {
                                            'text': text.strip(),
                                            'expert_type': expert_type,
                                            'quality_score': min(0.9, 0.6 + (post_data.get('score', 0) / 100)),
                                            'source': 'reddit',
                                            'metadata': {
                                                'subreddit': subreddit,
                                                'score': post_data.get('score', 0),
                                                'num_comments': post_data.get('num_comments', 0),
                                                'created_utc': post_data.get('created_utc', 0),
                                                'url': f"https://reddit.com{post_data.get('permalink', '')}"
                                            }
                                        }
                                        
                                        collected_data.append(item)
                                        self.stats['reddit_collected'] += 1
                                        
                                        if len([d for d in collected_data if d.get('expert_type') == expert_type]) >= posts_per_type:
                                            break
                                
                                # 避免API限制
                                await asyncio.sleep(1)
                                
                        except Exception as e:
                            logger.error(f"收集subreddit {subreddit}数据失败: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Reddit数据收集失败: {e}")
        
        logger.info(f"Reddit数据收集完成，共收集 {len(collected_data)} 条")
        return collected_data
    
    async def collect_github_data(self, target_count: int = 2000) -> List[Dict[str, Any]]:
        """收集GitHub数据"""
        logger.info(f"开始收集GitHub数据，目标: {target_count}条")
        
        # GitHub搜索查询
        search_queries = {
            'business_strategy': [
                'business model', 'startup strategy', 'revenue model',
                'market analysis', 'competitive strategy'
            ],
            'data_insight': [
                'data analysis', 'machine learning', 'analytics dashboard',
                'data visualization', 'metrics tracking'
            ],
            'user_insight': [
                'user experience', 'ui design', 'usability testing',
                'user research', 'interface design'
            ],
            'competitive_intelligence': [
                'competitor analysis', 'market research', 'benchmarking',
                'competitive intelligence', 'market positioning'
            ],
            'failure_prevention': [
                'bug fix', 'error handling', 'debugging', 'testing',
                'quality assurance', 'performance optimization'
            ]
        }
        
        collected_data = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for expert_type, queries in search_queries.items():
                    issues_per_type = target_count // 5
                    
                    for query in queries:
                        if len([d for d in collected_data if d.get('expert_type') == expert_type]) >= issues_per_type:
                            break
                        
                        try:
                            # 搜索GitHub Issues
                            url = 'https://api.github.com/search/issues'
                            params = {
                                'q': f'{query} is:issue is:open',
                                'sort': 'updated',
                                'per_page': 50
                            }
                            
                            async with session.get(url, params=params) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    issues = data.get('items', [])
                                    
                                    for issue in issues:
                                        # 过滤质量较低的issue
                                        if (len(issue.get('title', '')) < 20 or
                                            not issue.get('body') or
                                            len(issue.get('body', '')) < 50):
                                            continue
                                        
                                        # 构建训练数据
                                        text = issue.get('title', '')
                                        if issue.get('body'):
                                            text += ' ' + issue.get('body', '')[:800]
                                        
                                        item = {
                                            'text': text.strip(),
                                            'expert_type': expert_type,
                                            'quality_score': min(0.95, 0.7 + (issue.get('comments', 0) / 20)),
                                            'source': 'github',
                                            'metadata': {
                                                'repository': issue.get('repository_url', '').split('/')[-1] if issue.get('repository_url') else '',
                                                'issue_number': issue.get('number', 0),
                                                'comments': issue.get('comments', 0),
                                                'created_at': issue.get('created_at', ''),
                                                'url': issue.get('html_url', '')
                                            }
                                        }
                                        
                                        collected_data.append(item)
                                        self.stats['github_collected'] += 1
                                        
                                        if len([d for d in collected_data if d.get('expert_type') == expert_type]) >= issues_per_type:
                                            break
                                
                                # 避免API限制
                                await asyncio.sleep(2)
                                
                        except Exception as e:
                            logger.error(f"搜索GitHub query '{query}'失败: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"GitHub数据收集失败: {e}")
        
        logger.info(f"GitHub数据收集完成，共收集 {len(collected_data)} 条")
        return collected_data
    
    async def collect_product_hunt_data(self, target_count: int = 1000) -> List[Dict[str, Any]]:
        """收集Product Hunt数据"""
        logger.info(f"开始收集Product Hunt数据，目标: {target_count}条")
        
        if not self.product_hunt_config['client_id']:
            logger.warning("Product Hunt API未配置，跳过收集")
            return []
        
        collected_data = []
        
        try:
            # Product Hunt GraphQL API
            url = 'https://api.producthunt.com/v2/api/graphql'
            
            # 获取访问令牌
            token_url = 'https://api.producthunt.com/v2/oauth/token'
            token_data = {
                'client_id': self.product_hunt_config['client_id'],
                'client_secret': self.product_hunt_config['client_secret'],
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                # 获取访问令牌
                async with session.post(token_url, data=token_data) as response:
                    if response.status == 200:
                        token_result = await response.json()
                        access_token = token_result.get('access_token')
                        
                        if not access_token:
                            logger.error("无法获取Product Hunt访问令牌")
                            return []
                        
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        }
                        
                        # GraphQL查询
                        query = """
                        query {
                          posts(first: 50, order: VOTES) {
                            edges {
                              node {
                                id
                                name
                                tagline
                                description
                                votesCount
                                commentsCount
                                createdAt
                                url
                                topics {
                                  edges {
                                    node {
                                      name
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                        """
                        
                        async with session.post(url, headers=headers, json={'query': query}) as response:
                            if response.status == 200:
                                data = await response.json()
                                posts = data.get('data', {}).get('posts', {}).get('edges', [])
                                
                                for post_edge in posts:
                                    post = post_edge.get('node', {})
                                    
                                    # 构建训练数据
                                    text = f"{post.get('name', '')} - {post.get('tagline', '')}"
                                    if post.get('description'):
                                        text += f" {post.get('description', '')[:300]}"
                                    
                                    if len(text) < 30:
                                        continue
                                    
                                    # 根据主题确定专家类型
                                    topics = [edge.get('node', {}).get('name', '') for edge in post.get('topics', {}).get('edges', [])]
                                    expert_type = self.classify_expert_type_by_topics(topics)
                                    
                                    item = {
                                        'text': text.strip(),
                                        'expert_type': expert_type,
                                        'quality_score': min(0.9, 0.6 + (post.get('votesCount', 0) / 100)),
                                        'source': 'product_hunt',
                                        'metadata': {
                                            'product_name': post.get('name', ''),
                                            'votes_count': post.get('votesCount', 0),
                                            'comments_count': post.get('commentsCount', 0),
                                            'created_at': post.get('createdAt', ''),
                                            'url': post.get('url', ''),
                                            'topics': topics
                                        }
                                    }
                                    
                                    collected_data.append(item)
                                    self.stats['product_hunt_collected'] = self.stats.get('product_hunt_collected', 0) + 1
                                    
                                    if len(collected_data) >= target_count:
                                        break
                            else:
                                logger.error(f"Product Hunt GraphQL查询失败: {response.status}")
                    else:
                        logger.error(f"Product Hunt认证失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"Product Hunt数据收集失败: {e}")
        
        logger.info(f"Product Hunt数据收集完成，共收集 {len(collected_data)} 条")
        return collected_data
    
    def classify_expert_type_by_topics(self, topics: List[str]) -> str:
        """根据主题分类专家类型"""
        topic_str = ' '.join(topics).lower()
        
        # 业务策略相关主题
        if any(keyword in topic_str for keyword in ['business', 'startup', 'entrepreneur', 'finance', 'marketing']):
            return 'business_strategy'
        
        # 数据洞察相关主题
        elif any(keyword in topic_str for keyword in ['analytics', 'data', 'ai', 'machine learning', 'tech']):
            return 'data_insight'
        
        # 用户洞察相关主题
        elif any(keyword in topic_str for keyword in ['design', 'user', 'interface', 'experience', 'mobile']):
            return 'user_insight'
        
        # 竞争情报相关主题
        elif any(keyword in topic_str for keyword in ['market', 'competition', 'research', 'growth']):
            return 'competitive_intelligence'
        
        # 故障预防相关主题
        elif any(keyword in topic_str for keyword in ['security', 'development', 'testing', 'quality']):
            return 'failure_prevention'
        
        # 默认分类
        return 'business_strategy'
    
    def balance_data(self, data: List[Dict[str, Any]], target_per_type: int = 2000) -> List[Dict[str, Any]]:
        """平衡数据分布"""
        logger.info("开始平衡数据分布...")
        
        # 按专家类型分组
        grouped_data = {}
        for item in data:
            expert_type = item.get('expert_type', 'unknown')
            if expert_type not in grouped_data:
                grouped_data[expert_type] = []
            grouped_data[expert_type].append(item)
        
        # 平衡每种类型的数据量
        balanced_data = []
        for expert_type in self.expert_keywords.keys():
            type_data = grouped_data.get(expert_type, [])
            
            if len(type_data) >= target_per_type:
                # 如果数据足够，随机选择
                selected = random.sample(type_data, target_per_type)
            else:
                # 如果数据不足，全部使用并生成补充数据
                selected = type_data.copy()
                needed = target_per_type - len(selected)
                
                if needed > 0:
                    logger.info(f"{expert_type} 数据不足，需要补充 {needed} 条")
                    # 生成高质量的合成数据
                    synthetic_data = self.generate_synthetic_data(expert_type, needed)
                    selected.extend(synthetic_data)
            
            balanced_data.extend(selected)
            self.stats['expert_distribution'][expert_type] = len(selected)
        
        logger.info(f"数据平衡完成，总计 {len(balanced_data)} 条")
        return balanced_data
    
    def generate_synthetic_data(self, expert_type: str, count: int) -> List[Dict[str, Any]]:
        """生成高质量的合成数据"""
        synthetic_templates = {
            'business_strategy': [
                "How to develop a sustainable business model for {industry}?",
                "What are the key metrics for measuring {business_aspect} success?",
                "Strategies for scaling {business_type} in competitive markets",
                "Revenue optimization techniques for {business_model}",
                "Market entry strategies for {market_type} businesses"
            ],
            'data_insight': [
                "Analyzing {data_type} patterns to improve {outcome}",
                "Key performance indicators for {domain} analytics",
                "Data-driven insights for {business_area} optimization",
                "Predictive modeling approaches for {use_case}",
                "Visualization techniques for {data_category} analysis"
            ],
            'user_insight': [
                "User experience best practices for {platform} design",
                "Improving user engagement through {ux_element}",
                "User research methodologies for {product_type}",
                "Accessibility considerations in {interface_type} design",
                "User journey optimization for {user_goal}"
            ],
            'competitive_intelligence': [
                "Competitive analysis framework for {industry} market",
                "Market positioning strategies against {competitor_type}",
                "Benchmarking {business_metric} across industry leaders",
                "Competitive intelligence gathering for {market_segment}",
                "Differentiation strategies in {competitive_landscape}"
            ],
            'failure_prevention': [
                "Common {system_type} failures and prevention strategies",
                "Error handling best practices for {technology}",
                "Quality assurance processes for {development_area}",
                "Performance optimization techniques for {system_component}",
                "Risk mitigation strategies for {project_type}"
            ]
        }
        
        variables = {
            'industry': ['tech', 'healthcare', 'finance', 'retail', 'education'],
            'business_aspect': ['growth', 'retention', 'acquisition', 'monetization'],
            'business_type': ['SaaS', 'e-commerce', 'marketplace', 'subscription'],
            'business_model': ['freemium', 'subscription', 'marketplace', 'advertising'],
            'market_type': ['emerging', 'mature', 'niche', 'global'],
            'data_type': ['customer', 'sales', 'marketing', 'operational', 'financial'],
            'outcome': ['conversion', 'retention', 'satisfaction', 'efficiency'],
            'domain': ['marketing', 'sales', 'operations', 'product', 'customer service'],
            'business_area': ['marketing', 'sales', 'product development', 'operations'],
            'use_case': ['churn prediction', 'demand forecasting', 'recommendation systems'],
            'data_category': ['time series', 'categorical', 'behavioral', 'transactional'],
            'platform': ['mobile', 'web', 'desktop', 'IoT'],
            'ux_element': ['navigation', 'onboarding', 'checkout', 'search'],
            'product_type': ['mobile apps', 'web applications', 'enterprise software'],
            'interface_type': ['mobile', 'web', 'voice', 'AR/VR'],
            'user_goal': ['conversion', 'engagement', 'retention', 'satisfaction'],
            'competitor_type': ['direct', 'indirect', 'substitute', 'emerging'],
            'business_metric': ['market share', 'pricing', 'features', 'performance'],
            'market_segment': ['B2B', 'B2C', 'enterprise', 'SMB'],
            'competitive_landscape': ['saturated markets', 'emerging markets', 'niche markets'],
            'system_type': ['distributed', 'microservices', 'monolithic', 'cloud'],
            'technology': ['APIs', 'databases', 'frontend', 'backend'],
            'development_area': ['software development', 'data pipelines', 'ML models'],
            'system_component': ['databases', 'APIs', 'user interfaces', 'algorithms'],
            'project_type': ['software projects', 'data projects', 'infrastructure projects']
        }
        
        synthetic_data = []
        templates = synthetic_templates.get(expert_type, [])
        
        for i in range(count):
            template = random.choice(templates)
            
            # 替换模板中的变量
            for var_name, var_values in variables.items():
                if f'{{{var_name}}}' in template:
                    template = template.replace(f'{{{var_name}}}', random.choice(var_values))
            
            item = {
                'text': template,
                'expert_type': expert_type,
                'quality_score': round(random.uniform(0.75, 0.9), 3),
                'source': 'synthetic',
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'template_based': True
                }
            }
            
            synthetic_data.append(item)
        
        return synthetic_data
    
    def calculate_quality_score(self, text: str, metadata: Dict[str, Any]) -> float:
        """计算数据质量分数"""
        score = 0.5  # 基础分数
        
        # 文本长度评分
        text_length = len(text)
        if text_length > 200:
            score += 0.2
        elif text_length > 100:
            score += 0.1
        
        # 来源评分
        source = metadata.get('source', '')
        if source == 'reddit':
            reddit_score = metadata.get('score', 0)
            score += min(0.2, reddit_score / 50)
        elif source == 'github':
            comments = metadata.get('comments', 0)
            score += min(0.2, comments / 10)
        
        # 确保分数在合理范围内
        return min(0.95, max(0.3, score))
    
    async def collect_all_data(self, target_total: int = 10000) -> List[Dict[str, Any]]:
        """收集所有数据"""
        logger.info(f"开始收集数据，目标总量: {target_total}条")
        
        all_data = []
        
        # 收集Reddit数据
        if self.reddit_config['client_id']:
            reddit_data = await self.collect_reddit_data(target_total // 2)
            all_data.extend(reddit_data)
        
        # 收集GitHub数据
        if self.github_config['client_id']:
            github_data = await self.collect_github_data(target_total // 3)
            all_data.extend(github_data)
        
        # 收集Product Hunt数据
        if self.product_hunt_config['client_id']:
            product_hunt_data = await self.collect_product_hunt_data(target_total // 5)
            all_data.extend(product_hunt_data)
        
        # 平衡数据
        balanced_data = self.balance_data(all_data, target_total // 5)
        
        # 更新统计信息
        self.stats['total_collected'] = len(balanced_data)
        self.stats['end_time'] = datetime.now()
        self.stats['duration'] = str(self.stats['end_time'] - self.stats['start_time'])
        
        # 计算平均质量分数
        quality_scores = [item.get('quality_score', 0) for item in balanced_data]
        self.stats['avg_quality_score'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return balanced_data
    
    def save_data(self, data: List[Dict[str, Any]], filename_prefix: str = "existing_api_data"):
        """保存数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存训练数据
        data_filename = f"{filename_prefix}_{timestamp}.json"
        data_path = Path(__file__).parent / data_filename
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 保存统计报告
        stats_filename = f"{filename_prefix}_stats_{timestamp}.json"
        stats_path = Path(__file__).parent / stats_filename
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"数据已保存到: {data_path}")
        logger.info(f"统计报告已保存到: {stats_path}")
        
        return data_path, stats_path
    
    def print_summary(self):
        """打印收集摘要"""
        print("\n" + "="*60)
        print("🎯 基于现有API的数据收集完成!")
        print("="*60)
        
        print(f"\n📊 收集统计:")
        print(f"   Reddit数据: {self.stats['reddit_collected']} 条")
        print(f"   GitHub数据: {self.stats['github_collected']} 条")
        print(f"   Product Hunt数据: {self.stats.get('product_hunt_collected', 0)} 条")
        print(f"   总计: {self.stats['total_collected']} 条")
        print(f"   平均质量分数: {self.stats.get('avg_quality_score', 0):.3f}")
        print(f"   收集耗时: {self.stats.get('duration', 'N/A')}")
        
        print(f"\n🎯 专家类型分布:")
        for expert_type, count in self.stats['expert_distribution'].items():
            percentage = (count / self.stats['total_collected'] * 100) if self.stats['total_collected'] > 0 else 0
            print(f"   {expert_type}: {count} 条 ({percentage:.1f}%)")
        
        print(f"\n✅ 数据质量评估:")
        real_data_count = self.stats['reddit_collected'] + self.stats['github_collected'] + self.stats.get('product_hunt_collected', 0)
        print(f"   真实数据比例: {(real_data_count / self.stats['total_collected'] * 100):.1f}%")
        print(f"   数据平衡度: {'✅ 优秀' if all(c >= 1800 for c in self.stats['expert_distribution'].values()) else '⚠️ 需要改进'}")
        print(f"   质量分数: {'✅ 优秀' if self.stats.get('avg_quality_score', 0) >= 0.8 else '⚠️ 需要改进'}")

async def main():
    """主函数"""
    collector = ExistingAPICollector()
    
    try:
        # 收集数据
        data = await collector.collect_all_data(target_total=10000)
        
        # 保存数据
        data_path, stats_path = collector.save_data(data)
        
        # 打印摘要
        collector.print_summary()
        
        print(f"\n🚀 下一步:")
        print(f"   1. 检查数据文件: {data_path}")
        print(f"   2. 查看统计报告: {stats_path}")
        print(f"   3. 使用此数据重新训练模型")
        
    except Exception as e:
        logger.error(f"数据收集失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())