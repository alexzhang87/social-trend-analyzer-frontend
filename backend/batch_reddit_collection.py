#!/usr/bin/env python3
"""
批量Reddit数据收集脚本
目标：收集5000+条Reddit数据
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加服务路径
sys.path.append('app/services')

class BatchRedditCollector:
    def __init__(self):
        self.collected_data = []
        self.stats = {
            'total_collected': 0,
            'subreddits_processed': 0,
            'keywords_processed': 0,
            'failed_requests': 0
        }
        
        # 大幅扩展的subreddit列表
        self.subreddits = [
            # 创业和商业核心
            'startups', 'entrepreneur', 'business', 'smallbusiness', 'venturecapital',
            'investing', 'stocks', 'finance', 'personalfinance', 'ecommerce',
            'marketing', 'sales', 'growth', 'productivity', 'innovation',
            
            # 技术和编程
            'technology', 'programming', 'webdev', 'coding', 'softwareengineering',
            'MachineLearning', 'artificial', 'datascience', 'analytics', 'automation',
            'cloudcomputing', 'cybersecurity', 'iot', 'blockchain', 'cryptocurrency',
            
            # 行业特定
            'fintech', 'SaaS', 'digitalnomad', 'freelance', 'remotework',
            'biotech', 'cleantech', 'edtech', 'healthtech', 'proptech', 'foodtech',
            'mobility', 'logistics', 'supplychain', 'manufacturing', 'retail',
            
            # 市场和分析
            'marketresearch', 'competitoranalysis', 'customerexperience', 'ux',
            'design', 'product', 'lean', 'agile', 'scrum', 'projectmanagement',
            
            # 投资和金融
            'angelinvestors', 'crowdfunding', 'ipo', 'mergers', 'acquisitions',
            'privateequity', 'hedgefunds', 'trading', 'forex', 'options',
            
            # 新兴领域
            'artificialintelligence', 'machinelearning', 'deeplearning', 'nlp',
            'computervision', 'robotics', 'quantumcomputing', 'nanotechnology',
            'biotechnology', 'genetics', 'medtech', 'pharma', 'climatetech'
        ]
        
        # 大幅扩展的关键词列表
        self.keywords = [
            # 核心创业关键词
            'startup', 'entrepreneur', 'business model', 'market analysis',
            'product launch', 'funding', 'investment', 'venture capital',
            'seed funding', 'series a', 'series b', 'series c', 'ipo', 'acquisition',
            
            # 技术创业
            'AI startup', 'tech startup', 'SaaS', 'fintech', 'edtech',
            'healthtech', 'proptech', 'cleantech', 'biotech', 'foodtech',
            'mobility startup', 'logistics tech', 'supply chain tech',
            
            # 商业策略
            'digital transformation', 'innovation', 'disruption', 'scaling',
            'growth hacking', 'customer acquisition', 'product market fit',
            'user retention', 'churn rate', 'lifetime value', 'conversion rate',
            
            # 市场和竞争
            'market research', 'competitor analysis', 'market size', 'tam sam som',
            'go to market', 'pricing strategy', 'revenue model', 'monetization',
            'business development', 'partnership', 'strategic alliance',
            
            # 运营和管理
            'team building', 'hiring', 'company culture', 'remote work',
            'project management', 'agile development', 'lean startup',
            'mvp', 'prototype', 'user testing', 'feedback loop', 'pivot',
            
            # 技术趋势
            'artificial intelligence', 'machine learning', 'deep learning',
            'blockchain', 'cryptocurrency', 'web3', 'metaverse', 'nft',
            'cloud computing', 'edge computing', 'quantum computing',
            
            # 行业应用
            'digital health', 'telemedicine', 'medical devices', 'drug discovery',
            'renewable energy', 'electric vehicles', 'autonomous driving',
            'smart cities', 'iot devices', 'industrial automation'
        ]

    async def collect_reddit_data_comprehensive(self, target_posts=5000):
        """全面收集Reddit数据"""
        logger.info(f"开始全面收集Reddit数据，目标：{target_posts} 条")
        
        try:
            from reddit_official_service import RedditOfficialService
        except ImportError:
            logger.error("无法导入Reddit服务")
            return
        
        reddit_service = RedditOfficialService()
        collected_count = 0
        
        # 时间过滤器选项
        time_filters = ['week', 'month', 'year']
        
        for subreddit in self.subreddits:
            if collected_count >= target_posts:
                break
                
            self.stats['subreddits_processed'] += 1
            logger.info(f"处理 subreddit: r/{subreddit} ({self.stats['subreddits_processed']}/{len(self.subreddits)})")
            
            for keyword in self.keywords:
                if collected_count >= target_posts:
                    break
                    
                self.stats['keywords_processed'] += 1
                
                # 尝试不同的时间过滤器
                for time_filter in time_filters:
                    if collected_count >= target_posts:
                        break
                        
                    try:
                        posts = await reddit_service.search_posts_enhanced(
                            query=keyword,
                            subreddit=subreddit,
                            limit=25,  # 每次请求25条
                            time_filter=time_filter
                        )
                        
                        if posts:
                            # 过滤重复数据
                            new_posts = self.filter_duplicates(posts)
                            if new_posts:
                                self.collected_data.extend(new_posts)
                                collected_count += len(new_posts)
                                self.stats['total_collected'] = collected_count
                                
                                logger.info(f"从 r/{subreddit} 收集到 {len(new_posts)} 条新数据 "
                                          f"(关键词: {keyword}, 时间: {time_filter})，总计: {collected_count}")
                        
                        # 避免API限制
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        self.stats['failed_requests'] += 1
                        logger.error(f"收集失败 r/{subreddit} - {keyword} - {time_filter}: {e}")
                        continue
                
                # 每处理10个关键词保存一次检查点
                if self.stats['keywords_processed'] % 10 == 0:
                    await self.save_checkpoint()

    def filter_duplicates(self, new_posts):
        """过滤重复数据"""
        existing_ids = {item.get('metadata', {}).get('id') for item in self.collected_data}
        filtered_posts = []
        
        for post in new_posts:
            post_id = post.get('metadata', {}).get('id')
            if post_id and post_id not in existing_ids:
                filtered_posts.append(post)
                existing_ids.add(post_id)
        
        return filtered_posts

    async def save_checkpoint(self):
        """保存检查点"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_file = f'collected_data/checkpoint_{timestamp}.json'
        
        os.makedirs('collected_data', exist_ok=True)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': self.collected_data,
                'stats': self.stats,
                'timestamp': timestamp
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"检查点已保存：{checkpoint_file} (数据量: {len(self.collected_data)})")

    async def save_final_data(self):
        """保存最终数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        os.makedirs('collected_data', exist_ok=True)
        
        # 保存原始数据
        raw_file = f'collected_data/batch_reddit_raw_{timestamp}.json'
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据格式
        training_file = f'collected_data/batch_reddit_training_{timestamp}.json'
        training_data = []
        
        for item in self.collected_data:
            if len(item.get('text', '')) >= 50:  # 过滤太短的文本
                training_data.append(item)
        
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = f'collected_data/batch_reddit_stats_{timestamp}.json'
        final_stats = {
            'collection_stats': self.stats,
            'collection_time': timestamp,
            'total_items': len(self.collected_data),
            'training_items': len(training_data),
            'subreddits_count': len(self.subreddits),
            'keywords_count': len(self.keywords),
            'quality_distribution': self.get_quality_distribution(),
            'source_distribution': self.get_source_distribution(),
            'data_size_mb': os.path.getsize(raw_file) / (1024 * 1024) if os.path.exists(raw_file) else 0
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 原始数据已保存：{raw_file}")
        logger.info(f"🎯 训练数据已保存：{training_file}")
        logger.info(f"📊 统计信息已保存：{stats_file}")
        
        return final_stats

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

    def get_source_distribution(self):
        """获取数据来源分布"""
        subreddit_counts = {}
        
        for item in self.collected_data:
            subreddit = item.get('metadata', {}).get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        # 返回前20个最多的subreddit
        sorted_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_subreddits[:20])

    async def run_batch_collection(self):
        """运行批量收集"""
        start_time = time.time()
        logger.info("🚀 开始批量Reddit数据收集...")
        
        await self.collect_reddit_data_comprehensive(target_posts=5000)
        
        # 保存最终数据
        final_stats = await self.save_final_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 批量数据收集完成！")
        logger.info(f"📊 最终统计：")
        logger.info(f"   - 总数据量：{final_stats['total_items']} 条")
        logger.info(f"   - 训练数据：{final_stats['training_items']} 条")
        logger.info(f"   - 处理的subreddit：{self.stats['subreddits_processed']} 个")
        logger.info(f"   - 处理的关键词：{self.stats['keywords_processed']} 个")
        logger.info(f"   - 失败请求：{self.stats['failed_requests']} 次")
        logger.info(f"   - 数据大小：{final_stats['data_size_mb']:.2f} MB")
        logger.info(f"⏱️ 耗时：{duration:.2f} 秒")
        if final_stats['total_items'] > 0:
            logger.info(f"📈 平均速度：{final_stats['total_items'] / duration:.2f} 条/秒")

async def main():
    """主函数"""
    collector = BatchRedditCollector()
    await collector.run_batch_collection()

if __name__ == "__main__":
    asyncio.run(main())