#!/usr/bin/env python3
"""
增强版Reddit数据收集脚本
基于现有reddit_official_service扩展收集范围
目标：收集数千条高质量数据
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

class EnhancedRedditCollector:
    def __init__(self):
        self.collected_data = []
        self.processed_ids = set()
        
        # 扩展的高质量subreddit列表（专注于创业和技术）
        self.subreddits = [
            # 核心创业社区
            'startups', 'entrepreneur', 'business', 'smallbusiness',
            'venturecapital', 'investing', 'stocks', 'finance',
            
            # 技术和产品
            'technology', 'programming', 'webdev', 'MachineLearning',
            'artificial', 'datascience', 'SaaS', 'fintech',
            
            # 行业特定
            'digitalnomad', 'freelance', 'remotework', 'productivity',
            'marketing', 'sales', 'growth', 'innovation',
            
            # 新兴领域
            'biotech', 'cleantech', 'edtech', 'healthtech',
            'blockchain', 'cryptocurrency', 'automation'
        ]
        
        # 高价值关键词
        self.keywords = [
            'startup', 'entrepreneur', 'business model', 'funding',
            'investment', 'venture capital', 'product launch',
            'market analysis', 'AI startup', 'tech startup',
            'SaaS', 'fintech', 'digital transformation',
            'innovation', 'scaling', 'growth hacking',
            'customer acquisition', 'product market fit',
            'artificial intelligence', 'machine learning',
            'blockchain', 'cryptocurrency', 'automation'
        ]

    async def collect_from_subreddit_comprehensive(self, subreddit, target_per_subreddit=200):
        """从单个subreddit全面收集数据"""
        logger.info(f"开始收集 r/{subreddit} 数据，目标：{target_per_subreddit} 条")
        
        try:
            from reddit_official_service import RedditOfficialService
        except ImportError:
            logger.error("无法导入Reddit服务")
            return []
        
        reddit_service = RedditOfficialService()
        subreddit_data = []
        
        # 1. 收集热门帖子
        try:
            hot_posts = await reddit_service.get_subreddit_posts(
                subreddit=subreddit,
                sort='hot',
                limit=50
            )
            if hot_posts:
                new_posts = self.filter_new_posts(hot_posts)
                subreddit_data.extend(new_posts)
                logger.info(f"从 r/{subreddit} 热门收集到 {len(new_posts)} 条")
        except Exception as e:
            logger.error(f"收集热门帖子失败 r/{subreddit}: {e}")
        
        await asyncio.sleep(1)  # 避免API限制
        
        # 2. 收集新帖子
        try:
            new_posts = await reddit_service.get_subreddit_posts(
                subreddit=subreddit,
                sort='new',
                limit=50
            )
            if new_posts:
                filtered_posts = self.filter_new_posts(new_posts)
                subreddit_data.extend(filtered_posts)
                logger.info(f"从 r/{subreddit} 新帖收集到 {len(filtered_posts)} 条")
        except Exception as e:
            logger.error(f"收集新帖子失败 r/{subreddit}: {e}")
        
        await asyncio.sleep(1)
        
        # 3. 使用关键词搜索
        for keyword in self.keywords[:10]:  # 限制关键词数量避免过多请求
            if len(subreddit_data) >= target_per_subreddit:
                break
                
            try:
                search_posts = await reddit_service.search_posts_enhanced(
                    query=keyword,
                    subreddit=subreddit,
                    limit=20,
                    time_filter='month'
                )
                if search_posts:
                    filtered_posts = self.filter_new_posts(search_posts)
                    subreddit_data.extend(filtered_posts)
                    logger.info(f"从 r/{subreddit} 搜索'{keyword}'收集到 {len(filtered_posts)} 条")
                
                await asyncio.sleep(0.5)  # 短暂延迟
                
            except Exception as e:
                logger.error(f"搜索失败 r/{subreddit} - {keyword}: {e}")
                continue
        
        logger.info(f"✅ r/{subreddit} 收集完成，共 {len(subreddit_data)} 条数据")
        return subreddit_data

    def filter_new_posts(self, posts):
        """过滤新帖子，避免重复"""
        new_posts = []
        for post in posts:
            post_id = post.get('metadata', {}).get('id')
            if post_id and post_id not in self.processed_ids:
                new_posts.append(post)
                self.processed_ids.add(post_id)
        return new_posts

    async def run_enhanced_collection(self, target_total=3000):
        """运行增强收集"""
        start_time = time.time()
        logger.info(f"🚀 开始增强Reddit数据收集，目标：{target_total} 条")
        
        target_per_subreddit = max(50, target_total // len(self.subreddits))
        
        for i, subreddit in enumerate(self.subreddits):
            if len(self.collected_data) >= target_total:
                break
                
            logger.info(f"处理进度：{i+1}/{len(self.subreddits)} - r/{subreddit}")
            
            try:
                subreddit_data = await self.collect_from_subreddit_comprehensive(
                    subreddit, target_per_subreddit
                )
                self.collected_data.extend(subreddit_data)
                
                current_total = len(self.collected_data)
                logger.info(f"📊 当前总数据量：{current_total} 条")
                
                # 每收集500条保存一次检查点
                if current_total % 500 == 0 and current_total > 0:
                    await self.save_checkpoint(current_total)
                
            except Exception as e:
                logger.error(f"处理 r/{subreddit} 时出错：{e}")
                continue
        
        # 保存最终数据
        final_stats = await self.save_final_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 增强数据收集完成！")
        logger.info(f"📊 最终统计：")
        logger.info(f"   - 总数据量：{final_stats['total_items']} 条")
        logger.info(f"   - 训练数据：{final_stats['training_items']} 条")
        logger.info(f"   - 处理的subreddit：{len(self.subreddits)} 个")
        logger.info(f"   - 数据大小：{final_stats.get('data_size_mb', 0):.2f} MB")
        logger.info(f"⏱️ 耗时：{duration:.2f} 秒")
        if final_stats['total_items'] > 0:
            logger.info(f"📈 平均速度：{final_stats['total_items'] / duration:.2f} 条/秒")

    async def save_checkpoint(self, count):
        """保存检查点"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_file = f'collected_data/enhanced_checkpoint_{count}_{timestamp}.json'
        
        os.makedirs('collected_data', exist_ok=True)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': self.collected_data,
                'count': count,
                'timestamp': timestamp
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 检查点已保存：{checkpoint_file}")

    async def save_final_data(self):
        """保存最终数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        os.makedirs('collected_data', exist_ok=True)
        
        # 保存原始数据
        raw_file = f'collected_data/enhanced_reddit_raw_{timestamp}.json'
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据格式（过滤质量）
        training_data = []
        for item in self.collected_data:
            text_length = len(item.get('text', ''))
            quality_score = item.get('quality_score', 0)
            
            # 质量过滤：文本长度>=100字符，质量分>=0.5
            if text_length >= 100 and quality_score >= 0.5:
                training_data.append(item)
        
        training_file = f'collected_data/enhanced_reddit_training_{timestamp}.json'
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 统计信息
        stats = {
            'collection_time': timestamp,
            'total_items': len(self.collected_data),
            'training_items': len(training_data),
            'subreddits_processed': len(self.subreddits),
            'quality_distribution': self.get_quality_distribution(),
            'source_distribution': self.get_source_distribution(),
            'text_length_stats': self.get_text_length_stats()
        }
        
        if os.path.exists(raw_file):
            stats['data_size_mb'] = os.path.getsize(raw_file) / (1024 * 1024)
        
        stats_file = f'collected_data/enhanced_reddit_stats_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 原始数据：{raw_file}")
        logger.info(f"🎯 训练数据：{training_file}")
        logger.info(f"📊 统计信息：{stats_file}")
        
        return stats

    def get_quality_distribution(self):
        """获取质量分布"""
        high, medium, low = 0, 0, 0
        for item in self.collected_data:
            score = item.get('quality_score', 0)
            if score >= 0.7:
                high += 1
            elif score >= 0.4:
                medium += 1
            else:
                low += 1
        return {'high': high, 'medium': medium, 'low': low}

    def get_source_distribution(self):
        """获取来源分布"""
        sources = {}
        for item in self.collected_data:
            subreddit = item.get('metadata', {}).get('subreddit', 'unknown')
            sources[subreddit] = sources.get(subreddit, 0) + 1
        return dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:15])

    def get_text_length_stats(self):
        """获取文本长度统计"""
        lengths = [len(item.get('text', '')) for item in self.collected_data]
        if not lengths:
            return {}
        
        lengths.sort()
        n = len(lengths)
        return {
            'min': min(lengths),
            'max': max(lengths),
            'avg': sum(lengths) / n,
            'median': lengths[n//2],
            'over_100_chars': sum(1 for l in lengths if l >= 100),
            'over_500_chars': sum(1 for l in lengths if l >= 500)
        }

async def main():
    """主函数"""
    collector = EnhancedRedditCollector()
    await collector.run_enhanced_collection(target_total=3000)

if __name__ == "__main__":
    asyncio.run(main())