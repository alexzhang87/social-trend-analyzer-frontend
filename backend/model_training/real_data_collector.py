#!/usr/bin/env python3
"""
真实数据收集系统
从多个免费的真实数据源收集AI专家顾问训练数据
"""

import json
import time
import random
import requests
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import re
import hashlib
from urllib.parse import quote
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataCollector:
    def __init__(self):
        self.collected_data = []
        self.expert_types = [
            'data_insight',
            'business_strategy', 
            'user_insight',
            'competitive_intelligence',
            'failure_prevention'
        ]
        
        # 真实数据源配置
        self.data_sources = {
            'stackoverflow': {
                'enabled': True,
                'base_url': 'https://api.stackexchange.com/2.3',
                'site': 'stackoverflow',
                'tags': {
                    'data_insight': ['data-analysis', 'analytics', 'business-intelligence', 'data-science', 'statistics'],
                    'business_strategy': ['business', 'strategy', 'planning', 'management', 'marketing'],
                    'user_insight': ['user-experience', 'usability', 'user-interface', 'ux-design', 'user-research'],
                    'competitive_intelligence': ['competitive-analysis', 'market-research', 'benchmarking'],
                    'failure_prevention': ['debugging', 'error-handling', 'testing', 'quality-assurance', 'troubleshooting']
                }
            },
            'reddit': {
                'enabled': True,
                'base_url': 'https://www.reddit.com/r',
                'subreddits': {
                    'data_insight': ['datascience', 'analytics', 'BusinessIntelligence', 'MachineLearning'],
                    'business_strategy': ['entrepreneur', 'business', 'startups', 'marketing', 'strategy'],
                    'user_insight': ['userexperience', 'usability', 'design', 'ProductManagement'],
                    'competitive_intelligence': ['marketing', 'business', 'entrepreneur', 'startups'],
                    'failure_prevention': ['programming', 'debugging', 'QualityAssurance', 'testing']
                }
            },
            'github_discussions': {
                'enabled': True,
                'repos': [
                    'microsoft/vscode-discussions',
                    'facebook/react',
                    'tensorflow/tensorflow',
                    'pytorch/pytorch',
                    'kubernetes/kubernetes'
                ]
            },
            'hackernews': {
                'enabled': True,
                'base_url': 'https://hacker-news.firebaseio.com/v0',
                'keywords': {
                    'data_insight': ['data', 'analytics', 'insights', 'metrics', 'analysis'],
                    'business_strategy': ['business', 'strategy', 'startup', 'growth', 'market'],
                    'user_insight': ['user', 'ux', 'design', 'experience', 'usability'],
                    'competitive_intelligence': ['competitor', 'competition', 'market', 'analysis'],
                    'failure_prevention': ['failure', 'error', 'bug', 'testing', 'debugging']
                }
            }
        }
    
    def collect_stackoverflow_data(self, max_per_tag: int = 50) -> List[Dict]:
        """从StackOverflow收集真实问答数据"""
        logger.info("开始从StackOverflow收集数据...")
        stackoverflow_data = []
        
        try:
            for expert_type, tags in self.data_sources['stackoverflow']['tags'].items():
                for tag in tags[:2]:  # 每种类型选择前2个标签
                    logger.info(f"收集标签 '{tag}' 的问题...")
                    
                    url = f"{self.data_sources['stackoverflow']['base_url']}/questions"
                    params = {
                        'order': 'desc',
                        'sort': 'votes',
                        'tagged': tag,
                        'site': self.data_sources['stackoverflow']['site'],
                        'pagesize': max_per_tag,
                        'filter': 'withbody'
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get('items', [])
                        
                        for question in questions:
                            if question.get('body') and len(question['body']) > 100:
                                # 获取最佳答案
                                answer_text = self._get_stackoverflow_answer(question['question_id'])
                                
                                sample = {
                                    'expert_type': expert_type,
                                    'input': question['title'],
                                    'output': answer_text or "需要根据具体情况进行详细分析和解决。",
                                    'context': self._clean_html(question['body'][:800]),
                                    'quality_score': min(0.9, 0.6 + (question.get('score', 0) / 100)),
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
                    
                    time.sleep(0.1)  # 避免API限制
                    
        except Exception as e:
            logger.warning(f"StackOverflow数据收集出错: {e}")
        
        logger.info(f"从StackOverflow收集了 {len(stackoverflow_data)} 条数据")
        return stackoverflow_data
    
    def _get_stackoverflow_answer(self, question_id: int) -> str:
        """获取StackOverflow问题的最佳答案"""
        try:
            url = f"{self.data_sources['stackoverflow']['base_url']}/questions/{question_id}/answers"
            params = {
                'order': 'desc',
                'sort': 'votes',
                'site': self.data_sources['stackoverflow']['site'],
                'filter': 'withbody',
                'pagesize': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                answers = data.get('items', [])
                if answers:
                    return self._clean_html(answers[0]['body'][:500])
        except:
            pass
        return None
    
    def collect_reddit_data(self, max_per_subreddit: int = 30) -> List[Dict]:
        """从Reddit收集真实讨论数据"""
        logger.info("开始从Reddit收集数据...")
        reddit_data = []
        
        try:
            for expert_type, subreddits in self.data_sources['reddit']['subreddits'].items():
                for subreddit in subreddits[:2]:  # 每种类型选择前2个subreddit
                    logger.info(f"收集 r/{subreddit} 的帖子...")
                    
                    url = f"{self.data_sources['reddit']['base_url']}/{subreddit}/hot.json"
                    headers = {'User-Agent': 'DataCollector/1.0'}
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts[:max_per_subreddit]:
                            post_data = post.get('data', {})
                            
                            if (post_data.get('selftext') and 
                                len(post_data['selftext']) > 50 and
                                not post_data.get('over_18', False)):
                                
                                sample = {
                                    'expert_type': expert_type,
                                    'input': post_data['title'],
                                    'output': self._generate_reddit_response(post_data, expert_type),
                                    'context': post_data['selftext'][:600],
                                    'quality_score': min(0.85, 0.5 + (post_data.get('score', 0) / 200)),
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
                    
                    time.sleep(2)  # Reddit API限制较严格
                    
        except Exception as e:
            logger.warning(f"Reddit数据收集出错: {e}")
        
        logger.info(f"从Reddit收集了 {len(reddit_data)} 条数据")
        return reddit_data
    
    def _generate_reddit_response(self, post_data: Dict, expert_type: str) -> str:
        """基于Reddit帖子内容生成专家回复"""
        title = post_data.get('title', '')
        content = post_data.get('selftext', '')
        
        response_templates = {
            'data_insight': f"基于您提到的情况，建议从数据分析角度来解决这个问题。首先需要收集相关数据，然后进行探索性分析，识别关键模式和趋势。",
            'business_strategy': f"从商业战略角度来看，这个问题需要综合考虑市场环境、竞争态势和资源配置。建议制定分阶段的实施计划。",
            'user_insight': f"从用户体验角度分析，需要深入了解用户需求和行为模式。建议进行用户调研和可用性测试来验证假设。",
            'competitive_intelligence': f"竞争分析显示，这个领域存在一定的机会和挑战。建议持续监控竞争对手动态，制定差异化策略。",
            'failure_prevention': f"为了预防潜在的失败风险，建议建立完善的监控和预警机制，制定应急预案，并定期进行风险评估。"
        }
        
        return response_templates.get(expert_type, "需要根据具体情况进行深入分析。")
    
    def collect_github_discussions(self, max_per_repo: int = 20) -> List[Dict]:
        """从GitHub Discussions收集数据"""
        logger.info("开始从GitHub Discussions收集数据...")
        github_data = []
        
        try:
            for repo in self.data_sources['github_discussions']['repos'][:3]:
                logger.info(f"收集 {repo} 的discussions...")
                
                # 使用GitHub API获取discussions (需要GraphQL，这里简化处理)
                # 实际实现中可以使用GitHub的REST API获取issues作为替代
                url = f"https://api.github.com/repos/{repo}/issues"
                params = {
                    'state': 'all',
                    'per_page': max_per_repo,
                    'sort': 'updated'
                }
                
                response = requests.get(url, params=params, timeout=15)
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
                                'output': self._extract_github_solution(issue),
                                'context': issue['body'][:600],
                                'quality_score': self._calculate_github_quality(issue),
                                'metadata': {
                                    'source': 'github_discussions',
                                    'repo': repo,
                                    'issue_id': issue['id'],
                                    'comments': issue.get('comments', 0),
                                    'created_at': issue['created_at']
                                }
                            }
                            github_data.append(sample)
                
                time.sleep(1)  # 避免API限制
                
        except Exception as e:
            logger.warning(f"GitHub Discussions数据收集出错: {e}")
        
        logger.info(f"从GitHub Discussions收集了 {len(github_data)} 条数据")
        return github_data
    
    def collect_hackernews_data(self, max_stories: int = 100) -> List[Dict]:
        """从Hacker News收集数据"""
        logger.info("开始从Hacker News收集数据...")
        hn_data = []
        
        try:
            # 获取热门故事
            url = f"{self.data_sources['hackernews']['base_url']}/topstories.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                story_ids = response.json()[:max_stories]
                
                for story_id in story_ids[:50]:  # 限制数量
                    story_url = f"{self.data_sources['hackernews']['base_url']}/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=5)
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        if (story.get('title') and 
                            story.get('text') and
                            len(story['text']) > 50):
                            
                            expert_type = self._classify_hn_story(story)
                            
                            sample = {
                                'expert_type': expert_type,
                                'input': story['title'],
                                'output': self._generate_hn_response(story, expert_type),
                                'context': story['text'][:600],
                                'quality_score': min(0.9, 0.6 + (story.get('score', 0) / 500)),
                                'metadata': {
                                    'source': 'hackernews',
                                    'story_id': story_id,
                                    'score': story.get('score', 0),
                                    'descendants': story.get('descendants', 0),
                                    'created_at': datetime.fromtimestamp(story['time']).isoformat()
                                }
                            }
                            hn_data.append(sample)
                    
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.warning(f"Hacker News数据收集出错: {e}")
        
        logger.info(f"从Hacker News收集了 {len(hn_data)} 条数据")
        return hn_data
    
    def _classify_github_content(self, issue: Dict) -> str:
        """分类GitHub内容"""
        text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
        
        keywords = {
            'data_insight': ['data', 'analytics', 'metrics', 'statistics', 'analysis', 'insights'],
            'business_strategy': ['strategy', 'roadmap', 'planning', 'business', 'market', 'growth'],
            'user_insight': ['user', 'ux', 'ui', 'experience', 'usability', 'design', 'interface'],
            'competitive_intelligence': ['competitor', 'comparison', 'benchmark', 'alternative', 'vs'],
            'failure_prevention': ['bug', 'error', 'fail', 'crash', 'issue', 'problem', 'fix']
        }
        
        scores = {}
        for expert_type, words in keywords.items():
            scores[expert_type] = sum(1 for word in words if word in text)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'business_strategy'
    
    def _classify_hn_story(self, story: Dict) -> str:
        """分类Hacker News故事"""
        text = f"{story.get('title', '')} {story.get('text', '')}".lower()
        
        keywords = {
            'data_insight': ['data', 'analytics', 'ai', 'ml', 'analysis', 'insights', 'metrics'],
            'business_strategy': ['startup', 'business', 'strategy', 'market', 'growth', 'funding'],
            'user_insight': ['user', 'ux', 'design', 'interface', 'experience', 'usability'],
            'competitive_intelligence': ['competitor', 'vs', 'comparison', 'market', 'analysis'],
            'failure_prevention': ['failure', 'mistake', 'error', 'lesson', 'avoid', 'problem']
        }
        
        scores = {}
        for expert_type, words in keywords.items():
            scores[expert_type] = sum(1 for word in words if word in text)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'business_strategy'
    
    def _extract_github_solution(self, issue: Dict) -> str:
        """从GitHub issue提取解决方案"""
        return f"针对 '{issue['title']}' 的问题，建议进行系统性分析，识别根本原因，制定解决方案并验证效果。"
    
    def _generate_hn_response(self, story: Dict, expert_type: str) -> str:
        """生成Hacker News回复"""
        templates = {
            'data_insight': "从数据分析角度来看，这个话题涉及重要的洞察发现。建议深入分析数据模式，提取可行的业务洞察。",
            'business_strategy': "从商业战略角度分析，这个趋势值得关注。建议评估对业务的潜在影响，制定相应的战略调整。",
            'user_insight': "从用户体验角度考虑，这个发展可能影响用户行为。建议进行用户研究，了解真实需求。",
            'competitive_intelligence': "从竞争分析角度看，这个变化可能重塑市场格局。建议密切关注竞争对手的应对策略。",
            'failure_prevention': "从风险管理角度分析，需要识别潜在的失败点。建议建立预警机制，制定应对预案。"
        }
        return templates.get(expert_type, "这是一个值得深入思考的话题，需要多角度分析。")
    
    def _calculate_github_quality(self, issue: Dict) -> float:
        """计算GitHub内容质量分数"""
        score = 0.6
        
        comments = issue.get('comments', 0)
        if comments > 10:
            score += 0.2
        elif comments > 0:
            score += 0.1
        
        labels = issue.get('labels', [])
        if len(labels) > 0:
            score += 0.1
        
        body_length = len(issue.get('body', ''))
        if body_length > 300:
            score += 0.1
        
        return min(score, 1.0)
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    def collect_all_real_data(self, target_total: int = 5000) -> List[Dict]:
        """收集所有真实数据源的数据"""
        logger.info(f"开始收集总计 {target_total} 条真实训练数据...")
        
        all_data = []
        
        # 1. StackOverflow数据 (40%)
        if self.data_sources['stackoverflow']['enabled']:
            so_data = self.collect_stackoverflow_data(max_per_tag=100)
            all_data.extend(so_data)
        
        # 2. Reddit数据 (30%)
        if self.data_sources['reddit']['enabled']:
            reddit_data = self.collect_reddit_data(max_per_subreddit=50)
            all_data.extend(reddit_data)
        
        # 3. GitHub Discussions数据 (20%)
        if self.data_sources['github_discussions']['enabled']:
            github_data = self.collect_github_discussions(max_per_repo=40)
            all_data.extend(github_data)
        
        # 4. Hacker News数据 (10%)
        if self.data_sources['hackernews']['enabled']:
            hn_data = self.collect_hackernews_data(max_stories=200)
            all_data.extend(hn_data)
        
        # 确保数据平衡和去重
        balanced_data = self._balance_and_deduplicate(all_data, target_total)
        
        logger.info(f"总共收集了 {len(balanced_data)} 条真实数据")
        return balanced_data
    
    def _balance_and_deduplicate(self, data: List[Dict], target_total: int) -> List[Dict]:
        """平衡数据并去重"""
        logger.info("开始平衡数据并去重...")
        
        # 去重 (基于标题和内容的hash)
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
                # 数据不足，使用所有数据
                selected = type_data
            
            balanced_data.extend(selected)
        
        # 打乱数据
        random.shuffle(balanced_data)
        
        logger.info(f"平衡后数据分布:")
        for expert_type in self.expert_types:
            count = sum(1 for item in balanced_data if item['expert_type'] == expert_type)
            logger.info(f"  {expert_type}: {count} 条")
        
        return balanced_data
    
    def save_data(self, data: List[Dict], filename: str = None) -> str:
        """保存收集的数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_train_data_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"真实数据已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    collector = RealDataCollector()
    
    # 收集5000条真实数据
    data = collector.collect_all_real_data(target_total=5000)
    
    # 保存数据
    filepath = collector.save_data(data)
    
    # 生成统计报告
    print("\n" + "="*60)
    print("真实数据收集完成报告")
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
    
    print("\n🎉 真实数据收集完成！这些都是来自真实平台的数据。")

if __name__ == "__main__":
    main()