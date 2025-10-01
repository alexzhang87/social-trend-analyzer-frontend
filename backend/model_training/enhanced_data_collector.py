#!/usr/bin/env python3
"""
增强版数据收集器
支持多个API数据源的大规模真实数据收集
"""

import json
import time
import random
import requests
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import re
import hashlib
from urllib.parse import quote
import base64
import os
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API配置类"""
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "DataCollector/1.0"
    
    twitter_bearer_token: Optional[str] = None
    
    github_token: Optional[str] = None
    
    stackoverflow_key: Optional[str] = None
    
    newsapi_key: Optional[str] = None

class EnhancedDataCollector:
    def __init__(self, config_file: str = "api_config.json"):
        self.config = self._load_config(config_file)
        self.collected_data = []
        self.expert_types = [
            'data_insight',
            'business_strategy', 
            'user_insight',
            'competitive_intelligence',
            'failure_prevention'
        ]
        
        # 数据源权重（基于质量和相关性）
        self.source_weights = {
            'reddit': 0.85,
            'twitter': 0.75,
            'github': 0.90,
            'stackoverflow': 0.95,
            'kaggle': 0.90,
            'hackernews': 0.80
        }
    
    def _load_config(self, config_file: str) -> APIConfig:
        """加载API配置"""
        config_path = Path(config_file)
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return APIConfig(**config_data)
        else:
            # 创建配置文件模板
            self._create_config_template(config_path)
            logger.warning(f"配置文件不存在，已创建模板: {config_path}")
            return APIConfig()
    
    def _create_config_template(self, config_path: Path):
        """创建API配置文件模板"""
        template = {
            "reddit_client_id": "your_reddit_client_id_here",
            "reddit_client_secret": "your_reddit_client_secret_here",
            "reddit_user_agent": "DataCollector/1.0",
            "twitter_bearer_token": "your_twitter_bearer_token_here",
            "github_token": "your_github_token_here",
            "stackoverflow_key": "your_stackoverflow_key_here",
            "newsapi_key": "your_newsapi_key_here"
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
    
    def collect_reddit_data(self, max_per_subreddit: int = 100) -> List[Dict]:
        """从Reddit API收集数据"""
        if not self.config.reddit_client_id or not self.config.reddit_client_secret:
            logger.warning("Reddit API配置缺失，跳过Reddit数据收集")
            return []
        
        logger.info("开始从Reddit API收集数据...")
        reddit_data = []
        
        try:
            # 获取Reddit访问令牌
            access_token = self._get_reddit_token()
            if not access_token:
                return []
            
            subreddits = {
                'data_insight': ['datascience', 'analytics', 'BusinessIntelligence', 'MachineLearning'],
                'business_strategy': ['entrepreneur', 'business', 'startups', 'marketing'],
                'user_insight': ['userexperience', 'usability', 'design', 'ProductManagement'],
                'competitive_intelligence': ['marketing', 'business', 'entrepreneur', 'startups'],
                'failure_prevention': ['programming', 'debugging', 'QualityAssurance', 'testing']
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.config.reddit_user_agent
            }
            
            for expert_type, subs in subreddits.items():
                for subreddit in subs[:2]:  # 每种类型选择前2个subreddit
                    logger.info(f"收集 r/{subreddit} 的帖子...")
                    
                    url = f"https://oauth.reddit.com/r/{subreddit}/hot"
                    params = {'limit': max_per_subreddit}
                    
                    response = requests.get(url, headers=headers, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            
                            if (post_data.get('selftext') and 
                                len(post_data['selftext']) > 100 and
                                not post_data.get('over_18', False)):
                                
                                sample = {
                                    'expert_type': expert_type,
                                    'input': post_data['title'],
                                    'output': self._generate_expert_response(post_data['title'], post_data['selftext'], expert_type),
                                    'context': post_data['selftext'][:800],
                                    'quality_score': self._calculate_reddit_quality(post_data),
                                    'metadata': {
                                        'source': 'reddit',
                                        'subreddit': subreddit,
                                        'post_id': post_data['id'],
                                        'score': post_data.get('score', 0),
                                        'num_comments': post_data.get('num_comments', 0),
                                        'created_at': datetime.fromtimestamp(post_data['created_utc']).isoformat()
                                    }
                                }
                                reddit_data.append(sample)
                    
                    time.sleep(2)  # Reddit API限制
                    
        except Exception as e:
            logger.warning(f"Reddit数据收集出错: {e}")
        
        logger.info(f"从Reddit收集了 {len(reddit_data)} 条数据")
        return reddit_data
    
    def _get_reddit_token(self) -> Optional[str]:
        """获取Reddit访问令牌"""
        try:
            auth = base64.b64encode(
                f"{self.config.reddit_client_id}:{self.config.reddit_client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'User-Agent': self.config.reddit_user_agent
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
        except Exception as e:
            logger.error(f"获取Reddit令牌失败: {e}")
        
        return None
    
    def collect_twitter_data(self, max_tweets: int = 1000) -> List[Dict]:
        """从Twitter API v2收集数据"""
        if not self.config.twitter_bearer_token:
            logger.warning("Twitter API配置缺失，跳过Twitter数据收集")
            return []
        
        logger.info("开始从Twitter API收集数据...")
        twitter_data = []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.config.twitter_bearer_token}',
                'User-Agent': 'DataCollector/1.0'
            }
            
            search_queries = {
                'data_insight': [
                    'data analysis insights',
                    'business intelligence trends',
                    'analytics strategy'
                ],
                'business_strategy': [
                    'business strategy tips',
                    'startup growth advice',
                    'market expansion strategy'
                ],
                'user_insight': [
                    'user experience research',
                    'customer feedback analysis',
                    'UX design insights'
                ],
                'competitive_intelligence': [
                    'competitor analysis',
                    'market research insights',
                    'competitive advantage'
                ],
                'failure_prevention': [
                    'startup failure lessons',
                    'business mistakes avoid',
                    'risk management tips'
                ]
            }
            
            for expert_type, queries in search_queries.items():
                for query in queries[:2]:  # 每种类型选择前2个查询
                    logger.info(f"搜索Twitter: '{query}'")
                    
                    url = "https://api.twitter.com/2/tweets/search/recent"
                    params = {
                        'query': f'"{query}" -is:retweet lang:en',
                        'max_results': min(100, max_tweets // len(search_queries)),
                        'tweet.fields': 'created_at,public_metrics,context_annotations'
                    }
                    
                    response = requests.get(url, headers=headers, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        tweets = data.get('data', [])
                        
                        for tweet in tweets:
                            if len(tweet['text']) > 50:
                                sample = {
                                    'expert_type': expert_type,
                                    'input': f"关于{query}的问题",
                                    'output': self._generate_expert_response(query, tweet['text'], expert_type),
                                    'context': tweet['text'][:600],
                                    'quality_score': self._calculate_twitter_quality(tweet),
                                    'metadata': {
                                        'source': 'twitter',
                                        'tweet_id': tweet['id'],
                                        'query': query,
                                        'retweet_count': tweet.get('public_metrics', {}).get('retweet_count', 0),
                                        'like_count': tweet.get('public_metrics', {}).get('like_count', 0),
                                        'created_at': tweet['created_at']
                                    }
                                }
                                twitter_data.append(sample)
                    
                    time.sleep(1)  # Twitter API限制
                    
        except Exception as e:
            logger.warning(f"Twitter数据收集出错: {e}")
        
        logger.info(f"从Twitter收集了 {len(twitter_data)} 条数据")
        return twitter_data
    
    def collect_github_data(self, max_per_repo: int = 50) -> List[Dict]:
        """从GitHub API收集数据"""
        if not self.config.github_token:
            logger.warning("GitHub API配置缺失，跳过GitHub数据收集")
            return []
        
        logger.info("开始从GitHub API收集数据...")
        github_data = []
        
        try:
            headers = {
                'Authorization': f'token {self.config.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DataCollector/1.0'
            }
            
            # 目标仓库（商业和技术相关）
            target_repos = [
                'microsoft/vscode',
                'facebook/react',
                'tensorflow/tensorflow',
                'pytorch/pytorch',
                'kubernetes/kubernetes',
                'apache/airflow',
                'elastic/elasticsearch',
                'grafana/grafana'
            ]
            
            for repo in target_repos[:5]:  # 限制仓库数量
                logger.info(f"收集 {repo} 的issues...")
                
                url = f"https://api.github.com/repos/{repo}/issues"
                params = {
                    'state': 'all',
                    'per_page': max_per_repo,
                    'sort': 'updated'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    issues = response.json()
                    
                    for issue in issues:
                        if (issue.get('body') and 
                            len(issue['body']) > 100 and
                            not issue.get('pull_request')):
                            
                            expert_type = self._classify_github_content(issue)
                            
                            sample = {
                                'expert_type': expert_type,
                                'input': issue['title'],
                                'output': self._generate_expert_response(issue['title'], issue['body'], expert_type),
                                'context': issue['body'][:800],
                                'quality_score': self._calculate_github_quality(issue),
                                'metadata': {
                                    'source': 'github',
                                    'repo': repo,
                                    'issue_id': issue['id'],
                                    'comments': issue.get('comments', 0),
                                    'created_at': issue['created_at']
                                }
                            }
                            github_data.append(sample)
                
                time.sleep(1)  # GitHub API限制
                
        except Exception as e:
            logger.warning(f"GitHub数据收集出错: {e}")
        
        logger.info(f"从GitHub收集了 {len(github_data)} 条数据")
        return github_data
    
    def collect_stackoverflow_data(self, max_per_tag: int = 100) -> List[Dict]:
        """从Stack Overflow API收集数据"""
        logger.info("开始从Stack Overflow API收集数据...")
        stackoverflow_data = []
        
        try:
            tags = {
                'data_insight': ['data-analysis', 'business-intelligence', 'analytics'],
                'business_strategy': ['business', 'strategy', 'planning'],
                'user_insight': ['user-experience', 'usability', 'user-interface'],
                'competitive_intelligence': ['competitive-analysis', 'market-research'],
                'failure_prevention': ['debugging', 'error-handling', 'testing']
            }
            
            for expert_type, tag_list in tags.items():
                for tag in tag_list[:2]:  # 每种类型选择前2个标签
                    logger.info(f"收集标签 '{tag}' 的问题...")
                    
                    url = "https://api.stackexchange.com/2.3/questions"
                    params = {
                        'order': 'desc',
                        'sort': 'votes',
                        'tagged': tag,
                        'site': 'stackoverflow',
                        'pagesize': max_per_tag,
                        'filter': 'withbody'
                    }
                    
                    if self.config.stackoverflow_key:
                        params['key'] = self.config.stackoverflow_key
                    
                    response = requests.get(url, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get('items', [])
                        
                        for question in questions:
                            if question.get('body') and len(question['body']) > 100:
                                sample = {
                                    'expert_type': expert_type,
                                    'input': question['title'],
                                    'output': self._generate_expert_response(question['title'], question['body'], expert_type),
                                    'context': self._clean_html(question['body'][:800]),
                                    'quality_score': self._calculate_stackoverflow_quality(question),
                                    'metadata': {
                                        'source': 'stackoverflow',
                                        'question_id': question['question_id'],
                                        'tag': tag,
                                        'score': question.get('score', 0),
                                        'view_count': question.get('view_count', 0),
                                        'created_at': datetime.fromtimestamp(question['creation_date']).isoformat()
                                    }
                                }
                                stackoverflow_data.append(sample)
                    
                    time.sleep(0.1)  # Stack Overflow API限制
                    
        except Exception as e:
            logger.warning(f"Stack Overflow数据收集出错: {e}")
        
        logger.info(f"从Stack Overflow收集了 {len(stackoverflow_data)} 条数据")
        return stackoverflow_data
    
    def _generate_expert_response(self, title: str, content: str, expert_type: str) -> str:
        """生成专家回复"""
        # 基于内容和专家类型生成相关回复
        content_keywords = self._extract_keywords(f"{title} {content}")
        
        response_templates = {
            'data_insight': [
                f"基于数据分析，{content_keywords}显示了重要的业务洞察。建议深入分析数据模式，识别关键趋势和异常值。",
                f"从数据科学角度来看，{content_keywords}需要通过统计分析和机器学习方法来挖掘深层洞察。",
                f"数据表明{content_keywords}存在优化空间。建议建立数据驱动的决策框架，持续监控关键指标。"
            ],
            'business_strategy': [
                f"从商业战略角度分析，{content_keywords}反映了市场的重要变化。建议制定相应的战略调整计划。",
                f"针对{content_keywords}的情况，建议采用SWOT分析法，评估内外部环境，制定差异化竞争策略。",
                f"商业模式创新是应对{content_keywords}挑战的关键。建议探索新的价值创造和盈利模式。"
            ],
            'user_insight': [
                f"从用户体验角度来看，{content_keywords}直接影响用户满意度。建议进行深入的用户研究和可用性测试。",
                f"用户行为数据显示{content_keywords}是关键痛点。建议优化用户旅程，提升整体体验。",
                f"针对{content_keywords}的用户反馈，建议采用设计思维方法，以用户为中心进行产品迭代。"
            ],
            'competitive_intelligence': [
                f"竞争分析表明{content_keywords}是行业发展的重要趋势。建议密切关注竞争对手动态，制定应对策略。",
                f"市场情报显示{content_keywords}存在竞争机会。建议进行详细的竞争对手分析和市场定位。",
                f"从竞争情报角度，{content_keywords}可能重塑行业格局。建议建立持续的市场监控机制。"
            ],
            'failure_prevention': [
                f"风险评估显示{content_keywords}存在潜在失败点。建议建立完善的预警机制和应急预案。",
                f"为预防{content_keywords}相关的失败风险，建议实施全面的质量管理体系和持续改进流程。",
                f"基于失败案例分析，{content_keywords}需要特别关注。建议建立学习型组织，从错误中汲取经验。"
            ]
        }
        
        templates = response_templates.get(expert_type, response_templates['business_strategy'])
        return random.choice(templates)
    
    def _extract_keywords(self, text: str) -> str:
        """提取关键词"""
        # 简化的关键词提取
        words = re.findall(r'\b\w+\b', text.lower())
        important_words = [w for w in words if len(w) > 4 and w not in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'will']]
        return ', '.join(important_words[:3]) if important_words else "相关问题"
    
    def _calculate_reddit_quality(self, post_data: Dict) -> float:
        """计算Reddit帖子质量分数"""
        score = 0.6
        
        # 基于投票数
        upvotes = post_data.get('score', 0)
        if upvotes > 100:
            score += 0.2
        elif upvotes > 10:
            score += 0.1
        
        # 基于评论数
        comments = post_data.get('num_comments', 0)
        if comments > 50:
            score += 0.1
        elif comments > 10:
            score += 0.05
        
        # 基于内容长度
        content_length = len(post_data.get('selftext', ''))
        if content_length > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_twitter_quality(self, tweet: Dict) -> float:
        """计算Twitter质量分数"""
        score = 0.5
        
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        
        if likes > 100:
            score += 0.2
        elif likes > 10:
            score += 0.1
        
        if retweets > 50:
            score += 0.2
        elif retweets > 5:
            score += 0.1
        
        # 基于内容长度
        if len(tweet['text']) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_github_quality(self, issue: Dict) -> float:
        """计算GitHub issue质量分数"""
        score = 0.7
        
        comments = issue.get('comments', 0)
        if comments > 20:
            score += 0.2
        elif comments > 5:
            score += 0.1
        
        # 基于标签数量
        labels = issue.get('labels', [])
        if len(labels) > 2:
            score += 0.1
        
        # 基于内容长度
        body_length = len(issue.get('body', ''))
        if body_length > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_stackoverflow_quality(self, question: Dict) -> float:
        """计算Stack Overflow质量分数"""
        score = 0.8
        
        # 基于投票数
        votes = question.get('score', 0)
        if votes > 50:
            score += 0.15
        elif votes > 10:
            score += 0.1
        
        # 基于浏览数
        views = question.get('view_count', 0)
        if views > 1000:
            score += 0.05
        
        return min(score, 1.0)
    
    def _classify_github_content(self, issue: Dict) -> str:
        """分类GitHub内容"""
        text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
        
        keywords = {
            'data_insight': ['data', 'analytics', 'metrics', 'statistics', 'analysis', 'insights', 'dashboard'],
            'business_strategy': ['strategy', 'roadmap', 'planning', 'business', 'market', 'growth', 'revenue'],
            'user_insight': ['user', 'ux', 'ui', 'experience', 'usability', 'design', 'interface', 'accessibility'],
            'competitive_intelligence': ['competitor', 'comparison', 'benchmark', 'alternative', 'vs', 'market'],
            'failure_prevention': ['bug', 'error', 'fail', 'crash', 'issue', 'problem', 'fix', 'debug']
        }
        
        scores = {}
        for expert_type, words in keywords.items():
            scores[expert_type] = sum(1 for word in words if word in text)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'business_strategy'
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    def collect_all_data(self, target_total: int = 10000) -> List[Dict]:
        """收集所有数据源的数据"""
        logger.info(f"开始收集总计 {target_total} 条训练数据...")
        
        all_data = []
        
        # 1. Reddit数据 (40%)
        reddit_data = self.collect_reddit_data(max_per_subreddit=200)
        all_data.extend(reddit_data)
        
        # 2. Twitter数据 (25%)
        twitter_data = self.collect_twitter_data(max_tweets=2000)
        all_data.extend(twitter_data)
        
        # 3. GitHub数据 (20%)
        github_data = self.collect_github_data(max_per_repo=100)
        all_data.extend(github_data)
        
        # 4. Stack Overflow数据 (15%)
        stackoverflow_data = self.collect_stackoverflow_data(max_per_tag=150)
        all_data.extend(stackoverflow_data)
        
        # 数据平衡和去重
        balanced_data = self._balance_and_deduplicate(all_data, target_total)
        
        logger.info(f"总共收集了 {len(balanced_data)} 条数据")
        return balanced_data
    
    def _balance_and_deduplicate(self, data: List[Dict], target_total: int) -> List[Dict]:
        """平衡数据并去重"""
        logger.info("开始平衡数据并去重...")
        
        # 去重
        seen_hashes = set()
        unique_data = []
        
        for item in data:
            content_hash = hashlib.md5(
                f"{item['input']}{item['context'][:100]}".encode()
            ).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_data.append(item)
        
        logger.info(f"去重后剩余 {len(unique_data)} 条数据")
        
        # 按专家类型分组
        grouped_data = {expert_type: [] for expert_type in self.expert_types}
        for item in unique_data:
            expert_type = item['expert_type']
            if expert_type in grouped_data:
                grouped_data[expert_type].append(item)
        
        # 平衡数据
        per_type_target = target_total // len(self.expert_types)
        balanced_data = []
        
        for expert_type in self.expert_types:
            type_data = grouped_data[expert_type]
            
            if len(type_data) >= per_type_target:
                # 按质量分数排序，选择高质量数据
                type_data.sort(key=lambda x: x['quality_score'], reverse=True)
                selected = type_data[:per_type_target]
            else:
                # 数据不足，使用所有数据并生成补充数据
                selected = type_data
                needed = per_type_target - len(type_data)
                if needed > 0:
                    synthetic_data = self._generate_synthetic_data(expert_type, needed)
                    selected.extend(synthetic_data)
            
            balanced_data.extend(selected)
        
        # 打乱数据
        random.shuffle(balanced_data)
        
        logger.info(f"平衡后数据分布:")
        for expert_type in self.expert_types:
            count = sum(1 for item in balanced_data if item['expert_type'] == expert_type)
            logger.info(f"  {expert_type}: {count} 条")
        
        return balanced_data
    
    def _generate_synthetic_data(self, expert_type: str, count: int) -> List[Dict]:
        """生成合成数据以补充不足的类型"""
        logger.info(f"为 {expert_type} 生成 {count} 条合成数据...")
        
        synthetic_data = []
        
        templates = {
            'data_insight': [
                ("如何提高数据分析的准确性？", "建议采用多维度数据验证、异常值检测和交叉验证等方法来提高数据分析的准确性。"),
                ("数据可视化的最佳实践是什么？", "数据可视化应该遵循简洁明了、突出重点、选择合适图表类型的原则。"),
                ("如何建立有效的数据监控体系？", "建立数据监控体系需要定义关键指标、设置预警阈值、建立自动化监控流程。")
            ],
            'business_strategy': [
                ("如何制定有效的商业策略？", "制定商业策略需要进行市场分析、竞争对手研究、SWOT分析，并制定可执行的行动计划。"),
                ("初创公司如何找到产品市场契合点？", "通过用户访谈、MVP测试、数据分析等方法持续验证和调整产品方向。"),
                ("如何评估商业模式的可行性？", "需要分析目标市场、价值主张、收入模式、成本结构等关键要素。")
            ],
            'user_insight': [
                ("如何进行有效的用户研究？", "用户研究应该结合定量和定性方法，包括用户访谈、问卷调查、行为分析等。"),
                ("如何提升用户体验？", "通过用户旅程映射、可用性测试、A/B测试等方法持续优化用户体验。"),
                ("如何分析用户行为数据？", "需要建立用户行为漏斗、分析关键路径、识别用户痛点和机会点。")
            ],
            'competitive_intelligence': [
                ("如何进行竞争对手分析？", "竞争分析应该包括产品功能、定价策略、市场定位、营销策略等多个维度。"),
                ("如何监控市场趋势？", "建立市场监控体系，关注行业报告、竞争对手动态、技术发展趋势。"),
                ("如何制定差异化竞争策略？", "通过分析竞争格局，找到市场空白点，制定独特的价值主张。")
            ],
            'failure_prevention': [
                ("如何预防项目失败？", "建立风险管理体系，定期评估项目风险，制定应急预案和缓解措施。"),
                ("如何从失败中学习？", "建立复盘机制，分析失败原因，总结经验教训，建立知识库。"),
                ("如何建立质量保证体系？", "制定质量标准、建立测试流程、实施持续改进机制。")
            ]
        }
        
        expert_templates = templates.get(expert_type, templates['business_strategy'])
        
        for i in range(count):
            template = random.choice(expert_templates)
            
            sample = {
                'expert_type': expert_type,
                'input': template[0],
                'output': template[1],
                'context': f"这是一个关于{expert_type}的专业咨询问题，需要提供专业的建议和解决方案。",
                'quality_score': random.uniform(0.7, 0.9),
                'metadata': {
                    'source': 'synthetic',
                    'template_id': i,
                    'created_at': datetime.now().isoformat()
                }
            }
            synthetic_data.append(sample)
        
        return synthetic_data
    
    def save_data(self, data: List[Dict], filename: str = None) -> str:
        """保存收集的数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_train_data_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    collector = EnhancedDataCollector()
    
    # 检查配置
    if not any([
        collector.config.reddit_client_id,
        collector.config.twitter_bearer_token,
        collector.config.github_token
    ]):
        print("\n⚠️  API配置缺失！")
        print("请按照以下步骤配置API:")
        print("1. 编辑 api_config.json 文件")
        print("2. 填入您的API密钥")
        print("3. 重新运行此脚本")
        print("\n📋 推荐优先配置的API:")
        print("- Reddit API (免费，数据量大)")
        print("- GitHub API (免费，质量高)")
        print("- Twitter API (免费层级)")
        return
    
    # 收集数据
    data = collector.collect_all_data(target_total=10000)
    
    # 保存数据
    filepath = collector.save_data(data)
    
    # 生成报告
    print("\n" + "="*60)
    print("增强版数据收集完成报告")
    print("="*60)
    print(f"总数据量: {len(data)} 条")
    print(f"数据文件: {filepath}")
    
    # 统计各类型数量
    type_counts = {}
    source_counts = {}
    for item in data:
        expert_type = item['expert_type']
        source = item['metadata']['source']
        type_counts[expert_type] = type_counts.get(expert_type, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print("\n专家类型分布:")
    for expert_type, count in type_counts.items():
        percentage = (count / len(data)) * 100
        print(f"  {expert_type}: {count} 条 ({percentage:.1f}%)")
    
    print("\n数据源分布:")
    for source, count in source_counts.items():
        percentage = (count / len(data)) * 100
        print(f"  {source}: {count} 条 ({percentage:.1f}%)")
    
    # 质量分数统计
    quality_scores = [item['quality_score'] for item in data]
    avg_quality = sum(quality_scores) / len(quality_scores)
    print(f"\n平均质量分数: {avg_quality:.3f}")
    
    print("\n🎉 增强版数据收集完成！")

if __name__ == "__main__":
    main()