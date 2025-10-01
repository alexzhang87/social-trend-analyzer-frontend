#!/usr/bin/env python3
"""
大规模数据收集系统 - 简化版
目标：收集万条级别的高质量训练数据

支持的数据源：
1. Reddit (多个subreddit，多个关键词)
2. Hacker News (免费API)
3. GitHub (开源项目和讨论)
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LargeScaleDataCollector:
    def __init__(self):
        self.session = None
        self.collected_data = []
        self.stats = {
            'reddit': 0,
            'hacker_news': 0,
            'github': 0,
            'total': 0
        }
        
        # 扩展的Reddit subreddit列表
        self.reddit_subreddits = [
            'startups', 'entrepreneur', 'business', 'technology', 'programming',
            'MachineLearning', 'artificial', 'datascience', 'investing', 'stocks',
            'marketing', 'SaaS', 'webdev', 'coding', 'innovation', 'fintech',
            'blockchain', 'cryptocurrency', 'venturecapital', 'smallbusiness',
            'ecommerce', 'digitalnomad', 'freelance', 'productivity', 'growth',
            'analytics', 'automation', 'cloudcomputing', 'cybersecurity', 'iot',
            'biotech', 'cleantech', 'edtech', 'healthtech', 'proptech', 'foodtech'
        ]
        
        # 扩展的关键词列表
        self.keywords = [
            'startup', 'entrepreneur', 'business model', 'market analysis',
            'product launch', 'funding', 'investment', 'venture capital',
            'AI startup', 'tech startup', 'SaaS', 'fintech', 'edtech',
            'healthtech', 'proptech', 'cleantech', 'biotech', 'foodtech',
            'mobility', 'logistics', 'e-commerce', 'marketplace', 'platform',
            'digital transformation', 'innovation', 'disruption', 'scaling',
            'growth hacking', 'customer acquisition', 'product market fit',
            'seed funding', 'series a', 'ipo', 'acquisition', 'merger',
            'mvp', 'prototype', 'user testing', 'feedback loop', 'pivot'
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def collect_reddit_data_bulk(self, target_posts=4000):
        """批量收集Reddit数据"""
        logger.info(f"开始批量收集Reddit数据，目标：{target_posts} 条")
        
        # 导入Reddit服务
        sys.path.append('app/services')
        try:
            from reddit_official_service import RedditOfficialService
        except ImportError:
            logger.error("无法导入Reddit服务，跳过Reddit数据收集")
            return
        
        reddit_service = RedditOfficialService()
        collected_count = 0
        
        # 为每个subreddit收集数据
        for subreddit in self.reddit_subreddits:
            if collected_count >= target_posts:
                break
                
            # 为每个关键词收集数据
            for keyword in self.keywords:
                if collected_count >= target_posts:
                    break
                    
                try:
                    posts = await reddit_service.search_posts_enhanced(
                        query=keyword,
                        subreddit=subreddit,
                        limit=50,  # 每次请求50条
                        time_filter='month'
                    )
                    
                    if posts:
                        self.collected_data.extend(posts)
                        collected_count += len(posts)
                        self.stats['reddit'] += len(posts)
                        logger.info(f"从 r/{subreddit} 收集到 {len(posts)} 条数据 (关键词: {keyword})，总计: {collected_count}")
                    
                    # 避免API限制
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"收集 r/{subreddit} 数据失败: {e}")
                    continue

    async def collect_hacker_news_data(self, target_items=2000):
        """收集Hacker News数据"""
        logger.info(f"开始收集Hacker News数据，目标：{target_items} 条")
        
        try:
            # 获取不同类型的story IDs
            story_types = ['topstories', 'newstories', 'beststories', 'askstories', 'showstories']
            collected_count = 0
            
            for story_type in story_types:
                if collected_count >= target_items:
                    break
                    
                try:
                    url = f'https://hacker-news.firebaseio.com/v0/{story_type}.json'
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            story_ids = await response.json()
                            # 限制每种类型的数量
                            story_ids = story_ids[:target_items // len(story_types)]
                            
                            # 批量获取story详情
                            tasks = []
                            for story_id in story_ids:
                                if collected_count >= target_items:
                                    break
                                task = self.get_hacker_news_item(story_id)
                                tasks.append(task)
                                
                                # 控制并发数量
                                if len(tasks) >= 20:
                                    results = await asyncio.gather(*tasks, return_exceptions=True)
                                    new_items = self.process_hacker_news_results(results)
                                    collected_count += new_items
                                    tasks = []
                                    await asyncio.sleep(0.5)
                            
                            # 处理剩余任务
                            if tasks:
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                new_items = self.process_hacker_news_results(results)
                                collected_count += new_items
                            
                            logger.info(f"从 {story_type} 收集到数据，总计: {collected_count}")
                            
                except Exception as e:
                    logger.error(f"收集 {story_type} 失败: {e}")
                    continue
                        
        except Exception as e:
            logger.error(f"收集Hacker News数据失败: {e}")

    async def get_hacker_news_item(self, item_id):
        """获取单个Hacker News条目"""
        try:
            url = f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json'
            async with self.session.get(url) as response:
                if response.status == 200:
                    item = await response.json()
                    if item and item.get('type') == 'story' and item.get('title'):
                        # 过滤低质量内容
                        score = item.get('score', 0)
                        if score >= 5:  # 最少5分
                            return {
                                'text': f"{item.get('title', '')} {item.get('text', '')}",
                                'metadata': {
                                    'source': 'hacker_news',
                                    'id': item.get('id'),
                                    'score': score,
                                    'comments_count': len(item.get('kids', [])),
                                    'url': item.get('url', ''),
                                    'created_at': datetime.fromtimestamp(item.get('time', 0)).isoformat(),
                                    'author': item.get('by', '')
                                },
                                'quality_score': min(score / 100, 1.0),
                                'category': 'technology',
                                'type': 'news'
                            }
        except Exception as e:
            logger.error(f"获取Hacker News条目 {item_id} 失败: {e}")
        return None

    def process_hacker_news_results(self, results):
        """处理Hacker News收集结果"""
        new_items = 0
        for result in results:
            if result and isinstance(result, dict):
                self.collected_data.append(result)
                self.stats['hacker_news'] += 1
                new_items += 1
        return new_items

    async def collect_github_data(self, target_repos=1500):
        """收集GitHub数据"""
        logger.info(f"开始收集GitHub数据，目标：{target_repos} 个仓库")
        
        queries = [
            'startup', 'business', 'fintech', 'saas', 'marketplace',
            'ai-startup', 'machine-learning', 'data-science', 'ecommerce',
            'automation', 'analytics', 'dashboard', 'crm', 'erp'
        ]
        
        collected_count = 0
        
        for query in queries:
            if collected_count >= target_repos:
                break
                
            try:
                # GitHub搜索API
                url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={min(100, target_repos // len(queries))}'
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        repos = data.get('items', [])
                        new_items = self.process_github_results(repos)
                        collected_count += new_items
                        logger.info(f"从GitHub查询 '{query}' 收集到 {new_items} 个仓库，总计: {collected_count}")
                        await asyncio.sleep(1)  # GitHub API限制
                    elif response.status == 403:
                        logger.warning("GitHub API限制，跳过GitHub数据收集")
                        break
                        
            except Exception as e:
                logger.error(f"收集GitHub数据失败 (查询: {query}): {e}")

    def process_github_results(self, repos):
        """处理GitHub收集结果"""
        new_items = 0
        for repo in repos:
            try:
                # 过滤低质量仓库
                stars = repo.get('stargazers_count', 0)
                if stars >= 10:  # 最少10个star
                    repo_data = {
                        'text': f"{repo.get('name', '')} {repo.get('description', '')}",
                        'metadata': {
                            'source': 'github',
                            'name': repo.get('name'),
                            'stars': stars,
                            'forks': repo.get('forks_count', 0),
                            'language': repo.get('language'),
                            'url': repo.get('html_url'),
                            'created_at': repo.get('created_at'),
                            'updated_at': repo.get('updated_at')
                        },
                        'quality_score': min(stars / 1000, 1.0),
                        'category': 'technology',
                        'type': 'repository'
                    }
                    self.collected_data.append(repo_data)
                    self.stats['github'] += 1
                    new_items += 1
                    
            except Exception as e:
                logger.error(f"处理GitHub仓库数据失败: {e}")
        
        return new_items

    async def run_large_scale_collection(self):
        """运行大规模数据收集"""
        start_time = time.time()
        logger.info("🚀 开始大规模数据收集...")
        
        # 设置目标数量
        targets = {
            'reddit': 4000,
            'hacker_news': 2000,
            'github': 1500
        }
        
        # 并发收集不同数据源
        tasks = [
            self.collect_reddit_data_bulk(targets['reddit']),
            self.collect_hacker_news_data(targets['hacker_news']),
            self.collect_github_data(targets['github'])
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 更新总计
        self.stats['total'] = len(self.collected_data)
        
        # 保存数据
        await self.save_collected_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 大规模数据收集完成！")
        logger.info(f"📊 收集统计：{self.stats}")
        logger.info(f"⏱️ 耗时：{duration:.2f} 秒")
        if self.stats['total'] > 0:
            logger.info(f"📈 平均速度：{self.stats['total'] / duration:.2f} 条/秒")

    async def save_collected_data(self):
        """保存收集的数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 确保输出目录存在
        os.makedirs('collected_data', exist_ok=True)
        
        # 保存原始数据
        raw_file = f'collected_data/large_scale_raw_{timestamp}.json'
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = f'collected_data/large_scale_stats_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collection_stats': self.stats,
                'collection_time': timestamp,
                'total_items': len(self.collected_data),
                'data_sources': list(self.stats.keys()),
                'quality_distribution': self.get_quality_distribution(),
                'target_achievement': {
                    'reddit_target': 4000,
                    'reddit_actual': self.stats['reddit'],
                    'reddit_percentage': (self.stats['reddit'] / 4000) * 100,
                    'hacker_news_target': 2000,
                    'hacker_news_actual': self.stats['hacker_news'],
                    'hacker_news_percentage': (self.stats['hacker_news'] / 2000) * 100,
                    'github_target': 1500,
                    'github_actual': self.stats['github'],
                    'github_percentage': (self.stats['github'] / 1500) * 100,
                    'total_target': 7500,
                    'total_actual': self.stats['total'],
                    'total_percentage': (self.stats['total'] / 7500) * 100
                }
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 数据已保存：{raw_file}")
        logger.info(f"📈 统计已保存：{stats_file}")

    def get_quality_distribution(self):
        """获取数据质量分布"""
        quality_ranges = {'high': 0, 'medium': 0, 'low': 0}
        
        for item in self.collected_data:
            score = item.get('quality_score', 0)
            if score >= 0.7:
                quality_ranges['high'] += 1
            elif score >= 0.4:
                quality_ranges['medium'] += 1
            else:
                quality_ranges['low'] += 1
        
        return quality_ranges

async def main():
    """主函数"""
    async with LargeScaleDataCollector() as collector:
        await collector.run_large_scale_collection()

if __name__ == "__main__":
    asyncio.run(main())