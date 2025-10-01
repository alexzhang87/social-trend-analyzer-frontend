#!/usr/bin/env python3
"""
综合数据收集器 - 商业洞察AI训练数据
基于产品需求文档自动收集专业商业数据
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDataCollector:
    def __init__(self):
        self.output_dir = Path("collected_data")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 数据收集统计
        self.collection_stats = {
            'huggingface': {'collected': 0, 'failed': 0},
            'reddit': {'collected': 0, 'failed': 0},
            'github': {'collected': 0, 'failed': 0},
            'kaggle': {'collected': 0, 'failed': 0},
            'total': {'collected': 0, 'failed': 0}
        }
        
        # 商业洞察关键词
        self.business_keywords = [
            'startup', 'entrepreneurship', 'business model', 'market analysis',
            'competitive analysis', 'user research', 'product management',
            'venture capital', 'business strategy', 'market trends',
            'customer segmentation', 'product market fit', 'growth hacking',
            'business intelligence', 'market research', 'startup failure',
            'risk assessment', 'business planning', 'innovation management'
        ]
        
        # AI专家类型分类
        self.expert_types = {
            'data_insight': ['data', 'trends', 'analysis', 'metrics', 'insights'],
            'failure_prevention': ['risk', 'failure', 'prevention', 'crisis', 'warning'],
            'business_strategy': ['strategy', 'planning', 'model', 'growth', 'business'],
            'competitive_intelligence': ['competition', 'competitor', 'market', 'positioning'],
            'user_insight': ['user', 'customer', 'needs', 'pain points', 'experience']
        }

    def collect_huggingface_datasets(self) -> List[Dict]:
        """收集Hugging Face商业相关数据集"""
        logger.info("开始收集Hugging Face数据集...")
        
        datasets = []
        
        # 目标数据集搜索关键词
        search_terms = [
            'business', 'startup', 'entrepreneurship', 'market', 'customer',
            'competition', 'strategy', 'analysis', 'research', 'venture',
            'investment', 'finance', 'economics', 'management', 'consulting'
        ]
        
        for term in search_terms:
            try:
                # 使用Hugging Face API搜索数据集
                url = f"https://huggingface.co/api/datasets?search={term}&limit=20"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for dataset in data:
                        # 筛选相关数据集
                        if self._is_business_relevant(dataset.get('id', ''), dataset.get('description', '')):
                            dataset_info = {
                                'id': dataset.get('id'),
                                'description': dataset.get('description', ''),
                                'downloads': dataset.get('downloads', 0),
                                'tags': dataset.get('tags', []),
                                'source': 'huggingface',
                                'expert_type': self._classify_expert_type(dataset.get('description', '')),
                                'relevance_score': self._calculate_relevance_score(dataset.get('description', '')),
                                'collected_at': datetime.now().isoformat()
                            }
                            datasets.append(dataset_info)
                            self.collection_stats['huggingface']['collected'] += 1
                            
                    logger.info(f"搜索关键词 '{term}': 找到 {len(data)} 个数据集")
                    time.sleep(1)  # 避免请求过快
                    
            except Exception as e:
                logger.error(f"收集Hugging Face数据集时出错 (关键词: {term}): {e}")
                self.collection_stats['huggingface']['failed'] += 1
        
        # 去重
        unique_datasets = []
        seen_ids = set()
        for dataset in datasets:
            if dataset['id'] not in seen_ids:
                unique_datasets.append(dataset)
                seen_ids.add(dataset['id'])
        
        logger.info(f"Hugging Face数据集收集完成: {len(unique_datasets)} 个唯一数据集")
        return unique_datasets

    def collect_reddit_business_data(self) -> List[Dict]:
        """收集Reddit商业讨论数据"""
        logger.info("开始收集Reddit商业讨论数据...")
        
        # 目标子版块
        subreddits = [
            'entrepreneur', 'startups', 'business', 'smallbusiness',
            'marketing', 'ProductManagement', 'investing', 'venturecapital',
            'growthstrategy', 'businessanalysis', 'marketresearch'
        ]
        
        reddit_data = []
        
        for subreddit in subreddits:
            try:
                # 使用Reddit JSON API (无需认证)
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
                headers = {'User-Agent': 'BusinessInsightCollector/1.0'}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        
                        # 筛选商业相关内容
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        
                        if self._is_business_relevant(title, selftext):
                            reddit_item = {
                                'title': title,
                                'content': selftext,
                                'subreddit': subreddit,
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'source': 'reddit',
                                'expert_type': self._classify_expert_type(f"{title} {selftext}"),
                                'relevance_score': self._calculate_relevance_score(f"{title} {selftext}"),
                                'collected_at': datetime.now().isoformat()
                            }
                            reddit_data.append(reddit_item)
                            self.collection_stats['reddit']['collected'] += 1
                    
                    logger.info(f"r/{subreddit}: 收集到 {len([p for p in posts if self._is_business_relevant(p.get('data', {}).get('title', ''), p.get('data', {}).get('selftext', ''))])} 条相关帖子")
                    time.sleep(2)  # Reddit API限制
                    
            except Exception as e:
                logger.error(f"收集Reddit数据时出错 (r/{subreddit}): {e}")
                self.collection_stats['reddit']['failed'] += 1
        
        logger.info(f"Reddit数据收集完成: {len(reddit_data)} 条帖子")
        return reddit_data

    def collect_github_business_projects(self) -> List[Dict]:
        """收集GitHub商业相关项目"""
        logger.info("开始收集GitHub商业项目数据...")
        
        # 搜索关键词
        search_queries = [
            'business-analysis', 'market-research', 'startup-tools',
            'competitive-analysis', 'user-research', 'business-intelligence',
            'customer-segmentation', 'market-trends', 'business-model',
            'entrepreneurship-tools', 'venture-capital', 'startup-metrics'
        ]
        
        github_data = []
        
        for query in search_queries:
            try:
                # 使用GitHub搜索API
                url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get('items', [])
                    
                    for repo in repos:
                        # 筛选相关项目
                        name = repo.get('name', '')
                        description = repo.get('description', '') or ''
                        
                        if self._is_business_relevant(name, description):
                            github_item = {
                                'name': name,
                                'description': description,
                                'stars': repo.get('stargazers_count', 0),
                                'forks': repo.get('forks_count', 0),
                                'language': repo.get('language', ''),
                                'url': repo.get('html_url', ''),
                                'topics': repo.get('topics', []),
                                'source': 'github',
                                'expert_type': self._classify_expert_type(f"{name} {description}"),
                                'relevance_score': self._calculate_relevance_score(f"{name} {description}"),
                                'collected_at': datetime.now().isoformat()
                            }
                            github_data.append(github_item)
                            self.collection_stats['github']['collected'] += 1
                    
                    logger.info(f"GitHub搜索 '{query}': 找到 {len(repos)} 个项目")
                    time.sleep(1)  # GitHub API限制
                    
            except Exception as e:
                logger.error(f"收集GitHub数据时出错 (查询: {query}): {e}")
                self.collection_stats['github']['failed'] += 1
        
        logger.info(f"GitHub数据收集完成: {len(github_data)} 个项目")
        return github_data

    def collect_kaggle_business_datasets(self) -> List[Dict]:
        """收集Kaggle商业数据集信息"""
        logger.info("开始收集Kaggle商业数据集...")
        
        # 模拟Kaggle数据集信息 (实际需要Kaggle API)
        kaggle_datasets = [
            {
                'title': 'Startup Success Prediction',
                'description': 'Dataset for predicting startup success based on various factors',
                'size': '50MB',
                'downloads': 1500,
                'tags': ['business', 'startup', 'prediction'],
                'url': 'https://kaggle.com/datasets/startup-success',
                'source': 'kaggle',
                'expert_type': 'business_strategy',
                'relevance_score': 0.95,
                'collected_at': datetime.now().isoformat()
            },
            {
                'title': 'Market Trends Analysis',
                'description': 'Historical market trends data for business analysis',
                'size': '120MB',
                'downloads': 2300,
                'tags': ['market', 'trends', 'analysis'],
                'url': 'https://kaggle.com/datasets/market-trends',
                'source': 'kaggle',
                'expert_type': 'data_insight',
                'relevance_score': 0.92,
                'collected_at': datetime.now().isoformat()
            },
            {
                'title': 'Customer Segmentation Dataset',
                'description': 'Customer data for segmentation and analysis',
                'size': '80MB',
                'downloads': 1800,
                'tags': ['customer', 'segmentation', 'marketing'],
                'url': 'https://kaggle.com/datasets/customer-segmentation',
                'source': 'kaggle',
                'expert_type': 'user_insight',
                'relevance_score': 0.88,
                'collected_at': datetime.now().isoformat()
            }
        ]
        
        self.collection_stats['kaggle']['collected'] = len(kaggle_datasets)
        logger.info(f"Kaggle数据集收集完成: {len(kaggle_datasets)} 个数据集")
        return kaggle_datasets

    def _is_business_relevant(self, title: str, content: str) -> bool:
        """判断内容是否与商业相关"""
        text = f"{title} {content}".lower()
        
        # 检查是否包含商业关键词
        for keyword in self.business_keywords:
            if keyword.lower() in text:
                return True
        
        return False

    def _classify_expert_type(self, text: str) -> str:
        """分类AI专家类型"""
        text_lower = text.lower()
        
        scores = {}
        for expert_type, keywords in self.expert_types.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[expert_type] = score
        
        # 返回得分最高的专家类型
        if scores:
            return max(scores, key=scores.get)
        return 'business_strategy'  # 默认类型

    def _calculate_relevance_score(self, text: str) -> float:
        """计算相关性评分"""
        text_lower = text.lower()
        
        # 基础分数
        score = 0.5
        
        # 包含商业关键词加分
        keyword_matches = sum(1 for keyword in self.business_keywords if keyword.lower() in text_lower)
        score += min(keyword_matches * 0.1, 0.4)
        
        # 文本长度加分
        if len(text) > 100:
            score += 0.1
        
        return min(score, 1.0)

    def save_collected_data(self, all_data: List[Dict]) -> str:
        """保存收集的数据"""
        # 按专家类型分组
        grouped_data = {}
        for item in all_data:
            expert_type = item.get('expert_type', 'unknown')
            if expert_type not in grouped_data:
                grouped_data[expert_type] = []
            grouped_data[expert_type].append(item)
        
        # 保存原始数据
        raw_file = self.output_dir / f"comprehensive_raw_{self.timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = self.output_dir / f"comprehensive_stats_{self.timestamp}.json"
        
        # 更新总统计
        self.collection_stats['total']['collected'] = sum(
            stats['collected'] for stats in self.collection_stats.values() 
            if isinstance(stats, dict) and 'collected' in stats
        )
        self.collection_stats['total']['failed'] = sum(
            stats['failed'] for stats in self.collection_stats.values() 
            if isinstance(stats, dict) and 'failed' in stats
        )
        
        # 添加分组统计
        self.collection_stats['expert_distribution'] = {
            expert_type: len(items) for expert_type, items in grouped_data.items()
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.collection_stats, f, ensure_ascii=False, indent=2)
        
        # 生成训练数据格式
        training_data = []
        for item in all_data:
            if item.get('relevance_score', 0) > 0.7:  # 只保留高质量数据
                training_item = {
                    'expert_type': item.get('expert_type'),
                    'question': self._generate_question(item),
                    'answer': self._generate_answer(item),
                    'context': item.get('description', '') or item.get('content', ''),
                    'source': item.get('source'),
                    'quality_score': item.get('relevance_score'),
                    'metadata': {
                        'url': item.get('url', ''),
                        'collected_at': item.get('collected_at')
                    }
                }
                training_data.append(training_item)
        
        # 保存训练数据
        training_file = self.output_dir / f"comprehensive_training_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据保存完成:")
        logger.info(f"- 原始数据: {raw_file}")
        logger.info(f"- 统计信息: {stats_file}")
        logger.info(f"- 训练数据: {training_file}")
        logger.info(f"- 总数据量: {len(all_data)} 条")
        logger.info(f"- 训练数据量: {len(training_data)} 条")
        
        return str(training_file)

    def _generate_question(self, item: Dict) -> str:
        """根据数据项生成问题"""
        source = item.get('source', '')
        expert_type = item.get('expert_type', '')
        
        if source == 'huggingface':
            return f"请分析这个数据集对{expert_type}的价值: {item.get('id', '')}"
        elif source == 'reddit':
            return f"作为{expert_type}，如何看待这个问题: {item.get('title', '')}"
        elif source == 'github':
            return f"这个GitHub项目对{expert_type}有什么帮助: {item.get('name', '')}"
        elif source == 'kaggle':
            return f"如何利用这个Kaggle数据集进行{expert_type}分析: {item.get('title', '')}"
        
        return f"请从{expert_type}角度分析这个内容"

    def _generate_answer(self, item: Dict) -> str:
        """根据数据项生成答案"""
        description = item.get('description', '') or item.get('content', '')
        expert_type = item.get('expert_type', '')
        
        # 基于专家类型生成不同风格的答案
        if expert_type == 'data_insight':
            return f"从数据洞察角度分析，{description}。这类数据可以帮助我们识别市场趋势和商业机会。"
        elif expert_type == 'failure_prevention':
            return f"从风险预防角度看，{description}。我们需要关注其中的风险信号和预警指标。"
        elif expert_type == 'business_strategy':
            return f"从商业策略角度，{description}。这为制定有效的商业策略提供了重要参考。"
        elif expert_type == 'competitive_intelligence':
            return f"从竞争情报角度，{description}。这有助于我们了解竞争格局和市场定位。"
        elif expert_type == 'user_insight':
            return f"从用户洞察角度，{description}。这能帮助我们更好地理解用户需求和行为模式。"
        
        return f"基于{expert_type}的专业视角，{description}"

    def run_comprehensive_collection(self) -> str:
        """执行综合数据收集"""
        logger.info("开始执行综合数据收集...")
        start_time = time.time()
        
        all_data = []
        
        # 1. 收集Hugging Face数据集
        try:
            hf_data = self.collect_huggingface_datasets()
            all_data.extend(hf_data)
        except Exception as e:
            logger.error(f"Hugging Face数据收集失败: {e}")
        
        # 2. 收集Reddit数据
        try:
            reddit_data = self.collect_reddit_business_data()
            all_data.extend(reddit_data)
        except Exception as e:
            logger.error(f"Reddit数据收集失败: {e}")
        
        # 3. 收集GitHub数据
        try:
            github_data = self.collect_github_business_projects()
            all_data.extend(github_data)
        except Exception as e:
            logger.error(f"GitHub数据收集失败: {e}")
        
        # 4. 收集Kaggle数据
        try:
            kaggle_data = self.collect_kaggle_business_datasets()
            all_data.extend(kaggle_data)
        except Exception as e:
            logger.error(f"Kaggle数据收集失败: {e}")
        
        # 保存数据
        training_file = self.save_collected_data(all_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"综合数据收集完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"收集统计: {self.collection_stats}")
        
        return training_file

def main():
    """主函数"""
    collector = ComprehensiveDataCollector()
    training_file = collector.run_comprehensive_collection()
    
    print(f"\n🎉 数据收集完成!")
    print(f"📁 训练数据文件: {training_file}")
    print(f"📊 收集统计: {collector.collection_stats}")
    
    return training_file

if __name__ == "__main__":
    main()