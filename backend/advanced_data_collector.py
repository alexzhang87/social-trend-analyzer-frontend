#!/usr/bin/env python3
"""
高级数据收集器 - Reddit和GitHub深度挖掘
专门收集高质量的商业洞察训练数据
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedDataCollector:
    def __init__(self):
        self.output_dir = Path("collected_data/advanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 高质量Reddit子版块
        self.premium_subreddits = [
            'entrepreneur', 'startups', 'business', 'smallbusiness',
            'marketing', 'ProductManagement', 'investing', 'venturecapital',
            'growthstrategy', 'businessanalysis', 'marketresearch',
            'consulting', 'finance', 'economics', 'sales', 'leadership',
            'innovation', 'strategy', 'customerservice', 'userexperience'
        ]
        
        # GitHub高价值搜索查询
        self.github_queries = [
            'business-intelligence language:python stars:>50',
            'market-analysis language:python stars:>30',
            'customer-analytics language:python stars:>20',
            'startup-tools language:python stars:>10',
            'business-metrics language:python stars:>15',
            'competitive-analysis language:python stars:>25',
            'user-research language:python stars:>20',
            'venture-capital language:python stars:>10',
            'business-strategy language:python stars:>15',
            'market-research language:python stars:>20',
            'financial-analysis language:python stars:>30',
            'customer-segmentation language:python stars:>25'
        ]
        
        # 商业洞察关键词扩展
        self.business_keywords_extended = [
            # 创业相关
            'startup', 'entrepreneur', 'founder', 'co-founder', 'venture',
            'seed funding', 'series a', 'series b', 'ipo', 'exit strategy',
            
            # 商业策略
            'business model', 'revenue model', 'pricing strategy', 'go-to-market',
            'product market fit', 'customer acquisition', 'retention rate',
            
            # 市场分析
            'market size', 'tam sam som', 'market penetration', 'market share',
            'competitive landscape', 'swot analysis', 'porter five forces',
            
            # 用户研究
            'user persona', 'customer journey', 'pain points', 'user feedback',
            'customer satisfaction', 'nps score', 'churn rate', 'ltv cac',
            
            # 数据洞察
            'kpi', 'metrics', 'analytics', 'data driven', 'business intelligence',
            'dashboard', 'reporting', 'insights', 'trends', 'forecasting'
        ]
        
        # 专家对话模板
        self.expert_templates = {
            'data_insight': {
                'questions': [
                    "这个数据趋势说明了什么？",
                    "如何解读这些关键指标？",
                    "数据背后的商业洞察是什么？",
                    "这些指标对业务决策有什么影响？"
                ],
                'response_style': "基于数据分析，我观察到..."
            },
            'failure_prevention': {
                'questions': [
                    "这种情况有什么潜在风险？",
                    "如何预防这类问题？",
                    "有哪些预警信号需要注意？",
                    "风险缓解策略是什么？"
                ],
                'response_style': "从风险管理角度，我建议..."
            },
            'business_strategy': {
                'questions': [
                    "最佳的商业策略是什么？",
                    "如何制定有效的增长计划？",
                    "商业模式如何优化？",
                    "战略执行的关键要素是什么？"
                ],
                'response_style': "从战略角度分析，我认为..."
            },
            'competitive_intelligence': {
                'questions': [
                    "竞争对手的策略如何？",
                    "市场定位应该怎样调整？",
                    "竞争优势在哪里？",
                    "如何应对竞争威胁？"
                ],
                'response_style': "竞争分析显示..."
            },
            'user_insight': {
                'questions': [
                    "用户真正的需求是什么？",
                    "如何改善用户体验？",
                    "用户行为模式如何？",
                    "客户满意度如何提升？"
                ],
                'response_style': "用户研究表明..."
            }
        }
        
        self.collection_stats = {
            'reddit_advanced': {'collected': 0, 'failed': 0, 'high_quality': 0},
            'github_advanced': {'collected': 0, 'failed': 0, 'high_quality': 0},
            'total_training_samples': 0
        }

    def collect_reddit_advanced(self) -> List[Dict]:
        """高级Reddit数据收集"""
        logger.info("开始高级Reddit数据收集...")
        
        reddit_data = []
        
        for subreddit in self.premium_subreddits:
            try:
                # 收集热门帖子
                hot_posts = self._fetch_reddit_posts(subreddit, 'hot', 50)
                reddit_data.extend(hot_posts)
                
                # 收集最新帖子
                new_posts = self._fetch_reddit_posts(subreddit, 'new', 30)
                reddit_data.extend(new_posts)
                
                # 收集本周热门
                week_posts = self._fetch_reddit_posts(subreddit, 'top', 25, 'week')
                reddit_data.extend(week_posts)
                
                logger.info(f"r/{subreddit}: 收集到 {len(hot_posts + new_posts + week_posts)} 条帖子")
                time.sleep(3)  # 避免请求过快
                
            except Exception as e:
                logger.error(f"收集Reddit数据失败 (r/{subreddit}): {e}")
                self.collection_stats['reddit_advanced']['failed'] += 1
        
        # 数据质量筛选和增强
        high_quality_data = self._enhance_reddit_data(reddit_data)
        
        logger.info(f"Reddit高级收集完成: {len(high_quality_data)} 条高质量数据")
        return high_quality_data

    def collect_github_advanced(self) -> List[Dict]:
        """高级GitHub数据收集"""
        logger.info("开始高级GitHub数据收集...")
        
        github_data = []
        
        for query in self.github_queries:
            try:
                # 搜索仓库
                repos = self._fetch_github_repos(query, 30)
                
                for repo in repos:
                    # 获取仓库详细信息
                    detailed_repo = self._fetch_repo_details(repo)
                    if detailed_repo:
                        github_data.append(detailed_repo)
                        self.collection_stats['github_advanced']['collected'] += 1
                
                logger.info(f"GitHub查询 '{query}': 收集到 {len(repos)} 个仓库")
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"收集GitHub数据失败 (查询: {query}): {e}")
                self.collection_stats['github_advanced']['failed'] += 1
        
        # 数据质量筛选和增强
        high_quality_data = self._enhance_github_data(github_data)
        
        logger.info(f"GitHub高级收集完成: {len(high_quality_data)} 条高质量数据")
        return high_quality_data

    def _fetch_reddit_posts(self, subreddit: str, sort: str, limit: int, time_filter: str = None) -> List[Dict]:
        """获取Reddit帖子"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
            if time_filter:
                url += f"&t={time_filter}"
            
            headers = {'User-Agent': 'AdvancedBusinessCollector/1.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                filtered_posts = []
                for post in posts:
                    post_data = post.get('data', {})
                    
                    # 高质量筛选
                    if self._is_high_quality_reddit_post(post_data):
                        enhanced_post = self._enhance_reddit_post(post_data, subreddit)
                        filtered_posts.append(enhanced_post)
                        self.collection_stats['reddit_advanced']['collected'] += 1
                
                return filtered_posts
                
        except Exception as e:
            logger.error(f"获取Reddit帖子失败 (r/{subreddit}): {e}")
            return []

    def _fetch_github_repos(self, query: str, per_page: int) -> List[Dict]:
        """获取GitHub仓库"""
        try:
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
                
        except Exception as e:
            logger.error(f"获取GitHub仓库失败 (查询: {query}): {e}")
            return []

    def _fetch_repo_details(self, repo: Dict) -> Optional[Dict]:
        """获取仓库详细信息"""
        try:
            # 获取README
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_response = requests.get(readme_url, timeout=10)
            
            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                # 这里简化处理，实际应该解码base64内容
                readme_content = readme_data.get('content', '')[:500]  # 限制长度
            
            # 获取最近的提交
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits?per_page=5"
            commits_response = requests.get(commits_url, timeout=10)
            
            recent_commits = []
            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                recent_commits = [commit.get('commit', {}).get('message', '') for commit in commits_data[:3]]
            
            return {
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'description': repo.get('description', ''),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', ''),
                'topics': repo.get('topics', []),
                'url': repo.get('html_url'),
                'readme_preview': readme_content,
                'recent_commits': recent_commits,
                'created_at': repo.get('created_at'),
                'updated_at': repo.get('updated_at'),
                'source': 'github_advanced'
            }
            
        except Exception as e:
            logger.error(f"获取仓库详情失败 ({repo.get('full_name')}): {e}")
            return None

    def _is_high_quality_reddit_post(self, post_data: Dict) -> bool:
        """判断Reddit帖子是否高质量"""
        # 基本质量标准
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        title = post_data.get('title', '')
        selftext = post_data.get('selftext', '')
        
        # 质量筛选条件
        if score < 5:  # 至少5个赞
            return False
        
        if len(title) < 20:  # 标题太短
            return False
        
        if len(selftext) < 100:  # 内容太短
            return False
        
        # 检查商业相关性
        text = f"{title} {selftext}".lower()
        keyword_matches = sum(1 for keyword in self.business_keywords_extended if keyword.lower() in text)
        
        if keyword_matches < 2:  # 至少包含2个商业关键词
            return False
        
        return True

    def _enhance_reddit_post(self, post_data: Dict, subreddit: str) -> Dict:
        """增强Reddit帖子数据"""
        title = post_data.get('title', '')
        selftext = post_data.get('selftext', '')
        
        return {
            'title': title,
            'content': selftext,
            'subreddit': subreddit,
            'score': post_data.get('score', 0),
            'num_comments': post_data.get('num_comments', 0),
            'url': f"https://reddit.com{post_data.get('permalink', '')}",
            'created_utc': post_data.get('created_utc', 0),
            'author': post_data.get('author', ''),
            'expert_type': self._classify_expert_type(f"{title} {selftext}"),
            'business_relevance': self._calculate_business_relevance(f"{title} {selftext}"),
            'quality_score': self._calculate_quality_score(post_data),
            'keywords_found': self._extract_keywords(f"{title} {selftext}"),
            'source': 'reddit_advanced',
            'collected_at': datetime.now().isoformat()
        }

    def _enhance_reddit_data(self, reddit_data: List[Dict]) -> List[Dict]:
        """增强Reddit数据质量"""
        high_quality_data = []
        
        for post in reddit_data:
            if post.get('quality_score', 0) > 0.7:  # 只保留高质量数据
                # 生成专家对话样本
                expert_samples = self._generate_expert_conversations(post)
                high_quality_data.extend(expert_samples)
                self.collection_stats['reddit_advanced']['high_quality'] += 1
        
        return high_quality_data

    def _enhance_github_data(self, github_data: List[Dict]) -> List[Dict]:
        """增强GitHub数据质量"""
        high_quality_data = []
        
        for repo in github_data:
            if repo.get('stars', 0) > 10:  # 只保留有一定星数的项目
                # 生成专家对话样本
                expert_samples = self._generate_github_conversations(repo)
                high_quality_data.extend(expert_samples)
                self.collection_stats['github_advanced']['high_quality'] += 1
        
        return high_quality_data

    def _generate_expert_conversations(self, post: Dict) -> List[Dict]:
        """为Reddit帖子生成专家对话"""
        conversations = []
        expert_type = post.get('expert_type', 'business_strategy')
        
        if expert_type in self.expert_templates:
            template = self.expert_templates[expert_type]
            
            for i, question_template in enumerate(template['questions']):
                conversation = {
                    'expert_type': expert_type,
                    'question': self._contextualize_question(question_template, post),
                    'answer': self._generate_expert_answer(post, question_template, template['response_style']),
                    'context': {
                        'title': post.get('title', ''),
                        'content_preview': post.get('content', '')[:200],
                        'subreddit': post.get('subreddit', ''),
                        'score': post.get('score', 0)
                    },
                    'source': 'reddit_advanced',
                    'quality_score': post.get('quality_score', 0),
                    'conversation_id': f"reddit_{post.get('subreddit')}_{i+1}_{self.timestamp}",
                    'metadata': {
                        'original_url': post.get('url', ''),
                        'keywords': post.get('keywords_found', []),
                        'business_relevance': post.get('business_relevance', 0),
                        'collected_at': post.get('collected_at')
                    }
                }
                conversations.append(conversation)
                self.collection_stats['total_training_samples'] += 1
        
        return conversations

    def _generate_github_conversations(self, repo: Dict) -> List[Dict]:
        """为GitHub项目生成专家对话"""
        conversations = []
        expert_type = self._classify_expert_type(f"{repo.get('name', '')} {repo.get('description', '')}")
        
        if expert_type in self.expert_templates:
            template = self.expert_templates[expert_type]
            
            for i, question_template in enumerate(template['questions']):
                conversation = {
                    'expert_type': expert_type,
                    'question': self._contextualize_github_question(question_template, repo),
                    'answer': self._generate_github_expert_answer(repo, question_template, template['response_style']),
                    'context': {
                        'project_name': repo.get('name', ''),
                        'description': repo.get('description', ''),
                        'stars': repo.get('stars', 0),
                        'language': repo.get('language', ''),
                        'topics': repo.get('topics', [])
                    },
                    'source': 'github_advanced',
                    'quality_score': min(repo.get('stars', 0) / 100, 1.0),  # 基于星数的质量评分
                    'conversation_id': f"github_{repo.get('name', '').replace('/', '_')}_{i+1}_{self.timestamp}",
                    'metadata': {
                        'repo_url': repo.get('url', ''),
                        'topics': repo.get('topics', []),
                        'language': repo.get('language', ''),
                        'last_updated': repo.get('updated_at'),
                        'collected_at': datetime.now().isoformat()
                    }
                }
                conversations.append(conversation)
                self.collection_stats['total_training_samples'] += 1
        
        return conversations

    def _contextualize_question(self, question_template: str, post: Dict) -> str:
        """为Reddit帖子上下文化问题"""
        title = post.get('title', '')
        subreddit = post.get('subreddit', '')
        
        return f"在r/{subreddit}上有人提到：'{title[:100]}...'。{question_template}"

    def _contextualize_github_question(self, question_template: str, repo: Dict) -> str:
        """为GitHub项目上下文化问题"""
        name = repo.get('name', '') or 'Unknown'
        description = repo.get('description', '') or 'No description'
        
        return f"GitHub项目 '{name}' ({description[:100]}...)。{question_template}"

    def _generate_expert_answer(self, post: Dict, question: str, response_style: str) -> str:
        """生成专家风格的答案"""
        content = post.get('content', '')
        expert_type = post.get('expert_type', '')
        keywords = post.get('keywords_found', [])
        
        # 基于内容和专家类型生成答案
        answer = f"{response_style} "
        
        if expert_type == 'data_insight':
            answer += f"从这个案例中，我们可以看到几个关键数据点：{', '.join(keywords[:3])}。"
            answer += f"这表明{content[:150]}...的趋势值得深入分析。"
        
        elif expert_type == 'failure_prevention':
            answer += f"这种情况存在潜在风险。根据描述，{content[:150]}..."
            answer += f"建议重点关注{', '.join(keywords[:2])}等风险指标。"
        
        elif expert_type == 'business_strategy':
            answer += f"从战略角度，{content[:150]}...提供了重要启示。"
            answer += f"关键成功因素包括{', '.join(keywords[:3])}。"
        
        elif expert_type == 'competitive_intelligence':
            answer += f"竞争分析显示，{content[:150]}...反映了市场动态。"
            answer += f"需要特别关注{', '.join(keywords[:2])}等竞争要素。"
        
        elif expert_type == 'user_insight':
            answer += f"用户研究表明，{content[:150]}...揭示了用户需求。"
            answer += f"关键洞察包括{', '.join(keywords[:3])}。"
        
        return answer

    def _generate_github_expert_answer(self, repo: Dict, question: str, response_style: str) -> str:
        """为GitHub项目生成专家答案"""
        description = repo.get('description', '') or 'No description available'
        topics = repo.get('topics', []) or []
        stars = repo.get('stars', 0) or 0
        
        answer = f"{response_style} "
        answer += f"这个项目 ({description}) 在GitHub上获得了{stars}个星标，"
        answer += f"主要技术栈包括{', '.join(topics[:3]) if topics else '未指定'}。"
        answer += f"从商业应用角度，它可以帮助解决{description[:100]}...相关的问题。"
        
        return answer

    def _classify_expert_type(self, text: str) -> str:
        """分类专家类型"""
        text_lower = text.lower()
        
        expert_scores = {
            'data_insight': 0,
            'failure_prevention': 0,
            'business_strategy': 0,
            'competitive_intelligence': 0,
            'user_insight': 0
        }
        
        # 数据洞察关键词
        data_keywords = ['data', 'analytics', 'metrics', 'kpi', 'dashboard', 'insights', 'trends', 'analysis']
        expert_scores['data_insight'] = sum(1 for kw in data_keywords if kw in text_lower)
        
        # 失败预防关键词
        risk_keywords = ['risk', 'failure', 'crisis', 'warning', 'prevention', 'mistake', 'avoid', 'danger']
        expert_scores['failure_prevention'] = sum(1 for kw in risk_keywords if kw in text_lower)
        
        # 商业策略关键词
        strategy_keywords = ['strategy', 'business', 'model', 'growth', 'planning', 'execution', 'roadmap']
        expert_scores['business_strategy'] = sum(1 for kw in strategy_keywords if kw in text_lower)
        
        # 竞争情报关键词
        competitive_keywords = ['competition', 'competitor', 'market', 'positioning', 'advantage', 'threat']
        expert_scores['competitive_intelligence'] = sum(1 for kw in competitive_keywords if kw in text_lower)
        
        # 用户洞察关键词
        user_keywords = ['user', 'customer', 'client', 'experience', 'satisfaction', 'feedback', 'persona']
        expert_scores['user_insight'] = sum(1 for kw in user_keywords if kw in text_lower)
        
        # 返回得分最高的类型
        return max(expert_scores, key=expert_scores.get) if max(expert_scores.values()) > 0 else 'business_strategy'

    def _calculate_business_relevance(self, text: str) -> float:
        """计算商业相关性"""
        text_lower = text.lower()
        
        relevance_score = 0.0
        keyword_matches = sum(1 for keyword in self.business_keywords_extended if keyword.lower() in text_lower)
        
        # 基于关键词匹配计算相关性
        relevance_score = min(keyword_matches * 0.1, 1.0)
        
        return relevance_score

    def _calculate_quality_score(self, post_data: Dict) -> float:
        """计算质量评分"""
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        title_length = len(post_data.get('title', ''))
        content_length = len(post_data.get('selftext', ''))
        
        # 综合质量评分
        quality = 0.0
        
        # 社区反馈权重
        quality += min(score / 50, 0.3)  # 最多0.3分
        quality += min(num_comments / 20, 0.2)  # 最多0.2分
        
        # 内容质量权重
        quality += min(title_length / 100, 0.2)  # 最多0.2分
        quality += min(content_length / 500, 0.3)  # 最多0.3分
        
        return min(quality, 1.0)

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.business_keywords_extended:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # 最多返回10个关键词

    def save_advanced_data(self, reddit_data: List[Dict], github_data: List[Dict]) -> Dict[str, str]:
        """保存高级收集的数据"""
        all_training_data = reddit_data + github_data
        
        # 保存原始数据
        raw_file = self.output_dir / f"advanced_raw_{self.timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump({
                'reddit_data': reddit_data,
                'github_data': github_data,
                'collection_stats': self.collection_stats
            }, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据
        training_file = self.output_dir / f"advanced_training_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(all_training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = self.output_dir / f"advanced_stats_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.collection_stats, f, ensure_ascii=False, indent=2)
        
        return {
            'raw_file': str(raw_file),
            'training_file': str(training_file),
            'stats_file': str(stats_file)
        }

    def run_advanced_collection(self) -> Dict[str, str]:
        """执行高级数据收集"""
        logger.info("开始执行高级数据收集...")
        start_time = time.time()
        
        # 收集Reddit高质量数据
        reddit_data = self.collect_reddit_advanced()
        
        # 收集GitHub高质量数据
        github_data = self.collect_github_advanced()
        
        # 保存数据
        files = self.save_advanced_data(reddit_data, github_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"高级数据收集完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"Reddit高质量数据: {len(reddit_data)} 条")
        logger.info(f"GitHub高质量数据: {len(github_data)} 条")
        logger.info(f"总训练样本: {self.collection_stats['total_training_samples']} 条")
        
        return files

def main():
    """主函数"""
    collector = AdvancedDataCollector()
    files = collector.run_advanced_collection()
    
    print(f"\n🎉 高级数据收集完成!")
    print(f"📁 原始数据: {files['raw_file']}")
    print(f"📁 训练数据: {files['training_file']}")
    print(f"📊 统计数据: {files['stats_file']}")
    print(f"📈 收集统计: {collector.collection_stats}")
    
    return files

if __name__ == "__main__":
    main()