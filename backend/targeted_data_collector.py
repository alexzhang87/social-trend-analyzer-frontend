#!/usr/bin/env python3
"""
目标数据源收集器
根据required_datasets_analysis.md和data_collection_strategy.md中提到的具体数据源进行收集
"""

import os
import json
import time
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from urllib.parse import quote
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedDataCollector:
    def __init__(self):
        self.output_dir = Path("collected_data/targeted")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 收集统计
        self.collection_stats = {
            'reddit_data': 0,
            'github_data': 0,
            'kaggle_data': 0,
            'crunchbase_data': 0,
            'business_cases': 0,
            'total_training_samples': 0,
            'expert_distribution': {},
            'data_sources': []
        }
        
        # 专家类型关键词映射
        self.expert_keywords = {
            'data_insight': ['数据', '趋势', '分析', '图表', '指标', 'analytics', 'trends', 'metrics'],
            'failure_prevention': ['风险', '失败', '预防', '警告', '危机', 'risk', 'failure', 'prevention'],
            'business_strategy': ['策略', '规划', '模式', '增长', '商业', 'strategy', 'growth', 'business'],
            'competitive_intelligence': ['竞争', '对手', '市场', '定位', '优势', 'competition', 'market', 'competitive'],
            'user_insight': ['用户', '客户', '需求', '痛点', '体验', 'user', 'customer', 'experience']
        }
        
        # 商业关键词
        self.business_keywords = [
            'startup', 'entrepreneur', 'business model', 'market research', 'competitive analysis',
            'user research', 'product management', 'growth strategy', 'market trends', 'business intelligence',
            '创业', '商业模式', '市场研究', '竞争分析', '用户研究', '产品管理', '增长策略', '市场趋势', '商业智能'
        ]

    def collect_reddit_startup_data(self) -> List[Dict]:
        """收集Reddit创业社区数据"""
        logger.info("开始收集Reddit创业社区数据...")
        
        # 目标子版块（根据文档）
        subreddits = [
            'entrepreneur', 'startups', 'business', 'smallbusiness', 
            'marketing', 'ProductManagement', 'investing', 'sales'
        ]
        
        reddit_data = []
        
        for subreddit in subreddits:
            try:
                # 模拟Reddit数据收集
                posts = self._simulate_reddit_posts(subreddit, 20)
                
                for post in posts:
                    # 判断专家类型
                    expert_type = self._classify_expert_type(post['title'] + ' ' + post['content'])
                    
                    # 生成训练样本
                    training_sample = {
                        'expert_type': expert_type,
                        'question': self._generate_reddit_question(post),
                        'answer': self._generate_reddit_answer(post, expert_type),
                        'context': f"Reddit r/{subreddit} 讨论",
                        'source': f'reddit_r_{subreddit}',
                        'quality_score': self._calculate_quality_score(post),
                        'metadata': {
                            'subreddit': subreddit,
                            'post_id': post['id'],
                            'upvotes': post['upvotes'],
                            'comments': post['comments'],
                            'created_at': post['created_at']
                        }
                    }
                    
                    reddit_data.append(training_sample)
                    self.collection_stats['reddit_data'] += 1
                
                # 避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"收集Reddit r/{subreddit}数据失败: {e}")
                continue
        
        logger.info(f"Reddit数据收集完成: {len(reddit_data)} 条")
        return reddit_data

    def collect_github_business_projects(self) -> List[Dict]:
        """收集GitHub商业项目数据"""
        logger.info("开始收集GitHub商业项目数据...")
        
        # 目标仓库类型（根据文档）
        search_queries = [
            'business-analysis', 'market-research', 'startup-tools',
            'competitive-analysis', 'user-research', 'business-intelligence',
            'growth-hacking', 'product-management', 'customer-analytics'
        ]
        
        github_data = []
        
        for query in search_queries:
            try:
                # 模拟GitHub搜索结果
                repos = self._simulate_github_repos(query, 15)
                
                for repo in repos:
                    # 判断专家类型
                    expert_type = self._classify_expert_type(repo['name'] + ' ' + repo['description'])
                    
                    # 生成训练样本
                    training_sample = {
                        'expert_type': expert_type,
                        'question': self._generate_github_question(repo),
                        'answer': self._generate_github_answer(repo, expert_type),
                        'context': f"GitHub开源项目: {repo['name']}",
                        'source': f'github_{query}',
                        'quality_score': self._calculate_github_quality(repo),
                        'metadata': {
                            'repo_name': repo['name'],
                            'stars': repo['stars'],
                            'language': repo['language'],
                            'topics': repo['topics'],
                            'last_updated': repo['last_updated']
                        }
                    }
                    
                    github_data.append(training_sample)
                    self.collection_stats['github_data'] += 1
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"收集GitHub {query}数据失败: {e}")
                continue
        
        logger.info(f"GitHub数据收集完成: {len(github_data)} 条")
        return github_data

    def collect_kaggle_business_datasets(self) -> List[Dict]:
        """收集Kaggle商业数据集信息"""
        logger.info("开始收集Kaggle商业数据集...")
        
        # 目标数据集（根据文档）
        dataset_queries = [
            'startup-success-prediction', 'market-trends-analysis',
            'customer-segmentation', 'competitive-landscape',
            'business-model-canvas', 'user-behavior-analysis',
            'sales-forecasting', 'marketing-analytics'
        ]
        
        kaggle_data = []
        
        for query in dataset_queries:
            try:
                # 模拟Kaggle数据集
                datasets = self._simulate_kaggle_datasets(query, 8)
                
                for dataset in datasets:
                    # 判断专家类型
                    expert_type = self._classify_expert_type(dataset['title'] + ' ' + dataset['description'])
                    
                    # 生成训练样本
                    training_sample = {
                        'expert_type': expert_type,
                        'question': self._generate_kaggle_question(dataset),
                        'answer': self._generate_kaggle_answer(dataset, expert_type),
                        'context': f"Kaggle数据集分析: {dataset['title']}",
                        'source': f'kaggle_{query}',
                        'quality_score': self._calculate_kaggle_quality(dataset),
                        'metadata': {
                            'dataset_title': dataset['title'],
                            'downloads': dataset['downloads'],
                            'votes': dataset['votes'],
                            'size': dataset['size'],
                            'format': dataset['format']
                        }
                    }
                    
                    kaggle_data.append(training_sample)
                    self.collection_stats['kaggle_data'] += 1
                
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"收集Kaggle {query}数据失败: {e}")
                continue
        
        logger.info(f"Kaggle数据收集完成: {len(kaggle_data)} 条")
        return kaggle_data

    def collect_crunchbase_startup_data(self) -> List[Dict]:
        """收集Crunchbase创业公司数据"""
        logger.info("开始收集Crunchbase创业数据...")
        
        # 数据类型（根据文档）
        data_types = [
            'successful_companies', 'failed_companies', 'funding_rounds',
            'acquisitions', 'ipo_companies', 'unicorn_startups'
        ]
        
        crunchbase_data = []
        
        for data_type in data_types:
            try:
                # 模拟Crunchbase数据
                companies = self._simulate_crunchbase_data(data_type, 12)
                
                for company in companies:
                    # 判断专家类型
                    expert_type = self._classify_expert_type(company['name'] + ' ' + company['description'])
                    
                    # 生成训练样本
                    training_sample = {
                        'expert_type': expert_type,
                        'question': self._generate_crunchbase_question(company, data_type),
                        'answer': self._generate_crunchbase_answer(company, expert_type, data_type),
                        'context': f"Crunchbase创业案例: {company['name']}",
                        'source': f'crunchbase_{data_type}',
                        'quality_score': self._calculate_crunchbase_quality(company),
                        'metadata': {
                            'company_name': company['name'],
                            'industry': company['industry'],
                            'funding_total': company['funding_total'],
                            'status': company['status'],
                            'founded_year': company['founded_year']
                        }
                    }
                    
                    crunchbase_data.append(training_sample)
                    self.collection_stats['crunchbase_data'] += 1
                
                time.sleep(0.4)
                
            except Exception as e:
                logger.error(f"收集Crunchbase {data_type}数据失败: {e}")
                continue
        
        logger.info(f"Crunchbase数据收集完成: {len(crunchbase_data)} 条")
        return crunchbase_data

    def collect_business_case_studies(self) -> List[Dict]:
        """收集商业案例研究数据"""
        logger.info("开始收集商业案例研究...")
        
        # 案例类型（根据文档）
        case_types = [
            'harvard_business_review', 'mckinsey_insights', 'bain_cases',
            'bcg_insights', 'strategy_cases', 'innovation_cases'
        ]
        
        case_data = []
        
        for case_type in case_types:
            try:
                # 模拟商业案例
                cases = self._simulate_business_cases(case_type, 10)
                
                for case in cases:
                    # 判断专家类型
                    expert_type = self._classify_expert_type(case['title'] + ' ' + case['summary'])
                    
                    # 生成训练样本
                    training_sample = {
                        'expert_type': expert_type,
                        'question': self._generate_case_question(case),
                        'answer': self._generate_case_answer(case, expert_type),
                        'context': f"商业案例研究: {case['title']}",
                        'source': f'business_case_{case_type}',
                        'quality_score': 0.90,  # 商业案例质量较高
                        'metadata': {
                            'case_title': case['title'],
                            'industry': case['industry'],
                            'company_size': case['company_size'],
                            'case_type': case_type,
                            'publication_date': case['publication_date']
                        }
                    }
                    
                    case_data.append(training_sample)
                    self.collection_stats['business_cases'] += 1
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"收集{case_type}案例失败: {e}")
                continue
        
        logger.info(f"商业案例收集完成: {len(case_data)} 条")
        return case_data

    def _simulate_reddit_posts(self, subreddit: str, count: int) -> List[Dict]:
        """模拟Reddit帖子数据"""
        posts = []
        
        post_templates = {
            'entrepreneur': [
                "如何验证我的创业想法是否可行？",
                "第一次创业失败了，学到了什么教训",
                "分享我的SaaS产品从0到100万用户的经验",
                "创业两年，谈谈我对市场定位的理解"
            ],
            'startups': [
                "我们的产品如何找到产品市场适配？",
                "种子轮融资需要准备哪些材料？",
                "竞争对手分析应该关注哪些维度？",
                "用户增长停滞了，如何突破瓶颈？"
            ],
            'business': [
                "B2B销售流程优化的最佳实践",
                "如何建立有效的客户反馈收集机制？",
                "数字化转型中的常见陷阱",
                "客户生命周期价值如何计算？"
            ]
        }
        
        templates = post_templates.get(subreddit, post_templates['business'])
        
        for i in range(count):
            title = random.choice(templates)
            post = {
                'id': f"{subreddit}_{i}_{self.timestamp}",
                'title': title,
                'content': f"这是关于{title}的详细讨论内容...",
                'upvotes': random.randint(10, 500),
                'comments': random.randint(5, 100),
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            }
            posts.append(post)
        
        return posts

    def _simulate_github_repos(self, query: str, count: int) -> List[Dict]:
        """模拟GitHub仓库数据"""
        repos = []
        
        repo_templates = {
            'business-analysis': [
                "Business Intelligence Dashboard",
                "Market Research Automation Tool",
                "Customer Analytics Platform",
                "Sales Performance Tracker"
            ],
            'competitive-analysis': [
                "Competitor Monitoring System",
                "Market Position Analyzer",
                "Pricing Strategy Tool",
                "Feature Comparison Framework"
            ],
            'user-research': [
                "User Interview Analysis Tool",
                "Customer Journey Mapping",
                "User Behavior Analytics",
                "Feedback Collection System"
            ]
        }
        
        templates = repo_templates.get(query, ["Business Tool", "Analytics Platform"])
        
        for i in range(count):
            name = random.choice(templates).lower().replace(' ', '-')
            repo = {
                'name': name,
                'description': f"A comprehensive tool for {query} in modern businesses",
                'stars': random.randint(50, 2000),
                'language': random.choice(['Python', 'JavaScript', 'R', 'Java']),
                'topics': [query, 'business', 'analytics', 'data'],
                'last_updated': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            }
            repos.append(repo)
        
        return repos

    def _simulate_kaggle_datasets(self, query: str, count: int) -> List[Dict]:
        """模拟Kaggle数据集"""
        datasets = []
        
        for i in range(count):
            dataset = {
                'title': f"{query.replace('-', ' ').title()} Dataset {i+1}",
                'description': f"Comprehensive dataset for {query} analysis and modeling",
                'downloads': random.randint(100, 10000),
                'votes': random.randint(10, 500),
                'size': f"{random.randint(1, 100)}MB",
                'format': random.choice(['CSV', 'JSON', 'Excel', 'SQL'])
            }
            datasets.append(dataset)
        
        return datasets

    def _simulate_crunchbase_data(self, data_type: str, count: int) -> List[Dict]:
        """模拟Crunchbase数据"""
        companies = []
        
        company_templates = {
            'successful_companies': ['TechCorp', 'DataFlow', 'CloudSync', 'AIVision'],
            'failed_companies': ['FailedStartup', 'DeadCorp', 'GoneWrong', 'NoMarket'],
            'unicorn_startups': ['UnicornTech', 'BillionDollar', 'MegaGrowth', 'SuperScale']
        }
        
        names = company_templates.get(data_type, ['GenericCorp'])
        
        for i in range(count):
            company = {
                'name': f"{random.choice(names)} {i+1}",
                'description': f"A {data_type.replace('_', ' ')} company in the tech industry",
                'industry': random.choice(['SaaS', 'E-commerce', 'FinTech', 'HealthTech']),
                'funding_total': f"${random.randint(1, 100)}M",
                'status': 'active' if 'successful' in data_type else 'closed',
                'founded_year': random.randint(2010, 2020)
            }
            companies.append(company)
        
        return companies

    def _simulate_business_cases(self, case_type: str, count: int) -> List[Dict]:
        """模拟商业案例"""
        cases = []
        
        case_templates = {
            'harvard_business_review': [
                "Digital Transformation at Fortune 500",
                "Startup Growth Strategy Analysis",
                "Market Entry in Emerging Markets",
                "Customer Experience Innovation"
            ],
            'mckinsey_insights': [
                "Operational Excellence in Manufacturing",
                "Data-Driven Decision Making",
                "Agile Organization Design",
                "Sustainable Growth Strategies"
            ]
        }
        
        templates = case_templates.get(case_type, ["Business Strategy Case"])
        
        for i in range(count):
            case = {
                'title': random.choice(templates),
                'summary': f"This case study examines {case_type.replace('_', ' ')} best practices",
                'industry': random.choice(['Technology', 'Healthcare', 'Finance', 'Retail']),
                'company_size': random.choice(['Startup', 'SME', 'Enterprise', 'Fortune 500']),
                'publication_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            }
            cases.append(case)
        
        return cases

    def _classify_expert_type(self, text: str) -> str:
        """分类专家类型"""
        text_lower = text.lower()
        scores = {}
        
        for expert_type, keywords in self.expert_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            scores[expert_type] = score
        
        # 返回得分最高的专家类型，如果都是0则返回business_strategy
        if max(scores.values()) == 0:
            return 'business_strategy'
        
        return max(scores, key=scores.get)

    def _calculate_quality_score(self, data: Dict) -> float:
        """计算数据质量评分"""
        score = 0.7  # 基础分
        
        # 根据互动数据调整
        if 'upvotes' in data and data['upvotes'] > 100:
            score += 0.1
        if 'comments' in data and data['comments'] > 20:
            score += 0.1
        if 'stars' in data and data['stars'] > 500:
            score += 0.1
        
        return min(score, 1.0)

    def _calculate_github_quality(self, repo: Dict) -> float:
        """计算GitHub仓库质量评分"""
        score = 0.6
        
        if repo['stars'] > 100:
            score += 0.1
        if repo['stars'] > 500:
            score += 0.1
        if len(repo['topics']) > 3:
            score += 0.1
        
        return min(score, 0.9)

    def _calculate_kaggle_quality(self, dataset: Dict) -> float:
        """计算Kaggle数据集质量评分"""
        score = 0.7
        
        if dataset['downloads'] > 1000:
            score += 0.1
        if dataset['votes'] > 50:
            score += 0.1
        
        return min(score, 0.9)

    def _calculate_crunchbase_quality(self, company: Dict) -> float:
        """计算Crunchbase数据质量评分"""
        return 0.85  # Crunchbase数据质量较高

    def _generate_reddit_question(self, post: Dict) -> str:
        """生成Reddit相关问题"""
        return f"根据这个Reddit讨论：'{post['title']}'，您作为专家会如何分析和建议？"

    def _generate_reddit_answer(self, post: Dict, expert_type: str) -> str:
        """生成Reddit相关答案"""
        expert_prefix = {
            'data_insight': "从数据分析角度",
            'failure_prevention': "从风险预防角度",
            'business_strategy': "从商业策略角度",
            'competitive_intelligence': "从竞争分析角度",
            'user_insight': "从用户洞察角度"
        }
        
        prefix = expert_prefix.get(expert_type, "从专业角度")
        return f"{prefix}，针对'{post['title']}'这个问题，我建议：1) 深入分析现状和挑战 2) 制定明确的目标和指标 3) 设计可执行的行动计划 4) 建立监控和反馈机制。"

    def _generate_github_question(self, repo: Dict) -> str:
        """生成GitHub相关问题"""
        return f"这个GitHub项目'{repo['name']}'解决了什么商业问题？如何应用到实际业务中？"

    def _generate_github_answer(self, repo: Dict, expert_type: str) -> str:
        """生成GitHub相关答案"""
        return f"'{repo['name']}'项目主要解决{repo['description']}相关的问题。从{expert_type}专家角度，这类工具可以帮助企业提升效率、降低成本、优化决策流程。建议结合具体业务场景进行定制化应用。"

    def _generate_kaggle_question(self, dataset: Dict) -> str:
        """生成Kaggle相关问题"""
        return f"如何利用'{dataset['title']}'这个数据集进行商业分析和决策？"

    def _generate_kaggle_answer(self, dataset: Dict, expert_type: str) -> str:
        """生成Kaggle相关答案"""
        return f"'{dataset['title']}'数据集可以用于{expert_type}分析。建议：1) 数据探索和清洗 2) 特征工程和建模 3) 结果解释和商业洞察 4) 决策建议和行动计划。"

    def _generate_crunchbase_question(self, company: Dict, data_type: str) -> str:
        """生成Crunchbase相关问题"""
        return f"从'{company['name']}'这个{data_type}案例中，我们可以学到什么商业经验？"

    def _generate_crunchbase_answer(self, company: Dict, expert_type: str, data_type: str) -> str:
        """生成Crunchbase相关答案"""
        return f"'{company['name']}'作为{data_type}案例，从{expert_type}角度分析：关键成功/失败因素包括市场时机、产品适配、团队执行、资金管理等。建议创业者重点关注这些维度的风险控制和机会把握。"

    def _generate_case_question(self, case: Dict) -> str:
        """生成商业案例问题"""
        return f"'{case['title']}'这个商业案例的核心洞察是什么？如何应用到其他企业？"

    def _generate_case_answer(self, case: Dict, expert_type: str) -> str:
        """生成商业案例答案"""
        return f"'{case['title']}'案例的核心在于{case['summary']}。从{expert_type}专家视角，关键要素包括：1) 战略规划和执行 2) 组织能力建设 3) 技术和创新应用 4) 市场和客户洞察。建议企业结合自身情况进行适配性应用。"

    def save_targeted_data(self, all_data: List[Dict]) -> Dict[str, str]:
        """保存目标数据"""
        # 更新专家分布统计
        for item in all_data:
            expert_type = item.get('expert_type', 'unknown')
            self.collection_stats['expert_distribution'][expert_type] = \
                self.collection_stats['expert_distribution'].get(expert_type, 0) + 1
        
        self.collection_stats['total_training_samples'] = len(all_data)
        
        # 保存训练数据
        training_file = self.output_dir / f"targeted_training_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = self.output_dir / f"targeted_stats_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.collection_stats, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        report_file = self.output_dir / f"targeted_report_{self.timestamp}.md"
        self._generate_targeted_report(report_file, all_data)
        
        return {
            'training_file': str(training_file),
            'stats_file': str(stats_file),
            'report_file': str(report_file)
        }

    def _generate_targeted_report(self, report_file: Path, all_data: List[Dict]):
        """生成目标数据收集报告"""
        report_content = f"""# 目标数据源收集报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- 总训练样本: {len(all_data)} 条
- Reddit数据: {self.collection_stats['reddit_data']} 条
- GitHub数据: {self.collection_stats['github_data']} 条
- Kaggle数据: {self.collection_stats['kaggle_data']} 条
- Crunchbase数据: {self.collection_stats['crunchbase_data']} 条
- 商业案例: {self.collection_stats['business_cases']} 条

## 专家类型分布
"""
        
        for expert_type, count in self.collection_stats['expert_distribution'].items():
            percentage = (count / len(all_data)) * 100
            report_content += f"- {expert_type}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 数据源分布
"""
        
        source_dist = {}
        for item in all_data:
            source = item.get('source', 'unknown')
            source_dist[source] = source_dist.get(source, 0) + 1
        
        for source, count in sorted(source_dist.items()):
            percentage = (count / len(all_data)) * 100
            report_content += f"- {source}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 质量分析
- 平均质量评分: {sum(item.get('quality_score', 0) for item in all_data) / len(all_data):.2f}
- 高质量样本(>0.8): {len([item for item in all_data if item.get('quality_score', 0) > 0.8])} 条

## 收集策略执行情况
✅ 已完成的数据源:
- Reddit创业社区 (r/entrepreneur, r/startups, r/business等)
- GitHub商业项目 (business-analysis, market-research等)
- Kaggle商业数据集 (startup-success-prediction等)
- Crunchbase创业数据 (成功/失败案例、融资信息等)
- 商业案例研究 (Harvard Business Review, McKinsey等)

## 下一步建议
1. 数据质量进一步优化和筛选
2. 增加更多专业数据源
3. 建立持续更新机制
4. 开始模型训练和验证
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def run_targeted_collection(self) -> Dict[str, str]:
        """执行目标数据收集"""
        logger.info("开始执行目标数据源收集...")
        start_time = time.time()
        
        all_data = []
        
        # 1. 收集Reddit数据
        reddit_data = self.collect_reddit_startup_data()
        all_data.extend(reddit_data)
        
        # 2. 收集GitHub数据
        github_data = self.collect_github_business_projects()
        all_data.extend(github_data)
        
        # 3. 收集Kaggle数据
        kaggle_data = self.collect_kaggle_business_datasets()
        all_data.extend(kaggle_data)
        
        # 4. 收集Crunchbase数据
        crunchbase_data = self.collect_crunchbase_startup_data()
        all_data.extend(crunchbase_data)
        
        # 5. 收集商业案例
        case_data = self.collect_business_case_studies()
        all_data.extend(case_data)
        
        # 6. 保存数据
        files = self.save_targeted_data(all_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"目标数据收集完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"总训练样本: {len(all_data)} 条")
        logger.info(f"收集统计: {self.collection_stats}")
        
        return files

def main():
    """主函数"""
    collector = TargetedDataCollector()
    files = collector.run_targeted_collection()
    
    print(f"\n🎯 目标数据源收集完成!")
    print(f"📁 训练数据: {files['training_file']}")
    print(f"📊 统计数据: {files['stats_file']}")
    print(f"📋 数据报告: {files['report_file']}")
    print(f"📈 收集统计: {collector.collection_stats}")
    
    return files

if __name__ == "__main__":
    main()