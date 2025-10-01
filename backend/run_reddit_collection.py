#!/usr/bin/env python3
"""
Reddit 数据收集脚本

功能：
1. 使用Reddit OAuth API收集高质量数据
2. 支持多关键词搜索和过滤
3. 执行文本分析和情感分析
4. 生成训练数据和统计报告
5. 数据质量验证

使用方法：
python run_reddit_collection.py
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from app.services.reddit_official_service import RedditOfficialService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RedditDataCollector:
    """Reddit数据收集器"""
    
    def __init__(self):
        self.reddit_service = RedditOfficialService()
        self.collected_data = []
        self.stats = {
            'total_posts': 0,
            'filtered_posts': 0,
            'keywords_used': [],
            'collection_time': None,
            'subreddits': {},
            'score_stats': {},
            'sentiment_stats': {},
            'top_posts': []
        }
    
    async def collect_reddit_data(self, keywords: List[str], max_posts: int = 100, 
                                 min_score: int = 5, time_filter: str = "week") -> List[Dict[str, Any]]:
        """
        收集Reddit数据
        
        Args:
            keywords: 搜索关键词列表
            max_posts: 最大帖子数量
            min_score: 最小评分过滤
            time_filter: 时间过滤器
            
        Returns:
            收集到的帖子列表
        """
        logger.info(f"开始收集Reddit数据: 关键词={keywords}, 最大数量={max_posts}")
        
        self.stats['keywords_used'] = keywords
        self.stats['collection_time'] = datetime.now().isoformat()
        
        try:
            # 使用增强搜索获取数据
            posts = await self.reddit_service.search_posts_enhanced(
                keywords=keywords,
                limit=max_posts,
                time_filter=time_filter
            )
            
            logger.info(f"从Reddit API获取到 {len(posts)} 条原始帖子")
            self.stats['total_posts'] = len(posts)
            
            # 过滤数据
            filtered_posts = []
            subreddit_counts = {}
            
            for post in posts:
                # 评分过滤
                if post.get('score', 0) >= min_score:
                    # 统计subreddit
                    subreddit = post.get('subreddit', 'unknown')
                    subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
                    
                    filtered_posts.append(post)
            
            self.stats['filtered_posts'] = len(filtered_posts)
            self.stats['subreddits'] = subreddit_counts
            
            # 计算评分统计
            if filtered_posts:
                scores = [post.get('score', 0) for post in filtered_posts]
                self.stats['score_stats'] = {
                    'min': min(scores),
                    'max': max(scores),
                    'avg': sum(scores) / len(scores)
                }
                
                # 获取热门帖子
                sorted_posts = sorted(filtered_posts, key=lambda x: x.get('score', 0), reverse=True)
                self.stats['top_posts'] = [
                    {
                        'title': post.get('content', '')[:100] + '...',
                        'subreddit': post.get('subreddit'),
                        'score': post.get('score'),
                        'comments': post.get('comments_count'),
                        'url': post.get('url')
                    }
                    for post in sorted_posts[:5]
                ]
            
            self.collected_data = filtered_posts
            logger.info(f"过滤后获得 {len(filtered_posts)} 条高质量帖子")
            
            return filtered_posts
            
        except Exception as e:
            logger.error(f"Reddit数据收集失败: {e}")
            raise
    
    def generate_training_data(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成训练数据格式"""
        training_data = []
        
        for post in posts:
            # 构建训练数据格式
            training_item = {
                'text': post.get('content', ''),
                'metadata': {
                    'source': 'reddit',
                    'post_id': post.get('platform_specific', {}).get('reddit_id'),
                    'subreddit': post.get('subreddit'),
                    'score': post.get('score'),
                    'comments_count': post.get('comments_count'),
                    'url': post.get('url'),
                    'published_at': post.get('published_at'),
                    'author': post.get('author'),
                    'upvote_ratio': post.get('upvote_ratio')
                },
                'quality_score': self._calculate_quality_score(post),
                'category': self._determine_category(post),
                'type': 'social_media_post'
            }
            
            # 添加分析结果
            if 'sentiment_analysis' in post:
                training_item['sentiment'] = post['sentiment_analysis']
            
            if 'keywords' in post:
                training_item['keywords'] = post['keywords']
            
            training_data.append(training_item)
        
        return training_data
    
    def _calculate_quality_score(self, post: Dict[str, Any]) -> float:
        """计算帖子质量评分"""
        score = 0.0
        
        # 基于评分
        reddit_score = post.get('score', 0)
        if reddit_score > 100:
            score += 0.4
        elif reddit_score > 50:
            score += 0.3
        elif reddit_score > 10:
            score += 0.2
        
        # 基于评论数
        comments = post.get('comments_count', 0)
        if comments > 50:
            score += 0.3
        elif comments > 20:
            score += 0.2
        elif comments > 5:
            score += 0.1
        
        # 基于内容长度
        content_length = len(post.get('content', ''))
        if content_length > 200:
            score += 0.2
        elif content_length > 100:
            score += 0.1
        
        # 基于upvote比例
        upvote_ratio = post.get('upvote_ratio', 0.5)
        if upvote_ratio > 0.8:
            score += 0.1
        
        return min(score, 1.0)  # 最大值为1.0
    
    def _determine_category(self, post: Dict[str, Any]) -> str:
        """确定帖子类别"""
        subreddit = post.get('subreddit', '').lower()
        content = post.get('content', '').lower()
        
        # 基于subreddit分类
        if any(tech in subreddit for tech in ['technology', 'programming', 'ai', 'machinelearning']):
            return 'technology'
        elif any(biz in subreddit for biz in ['business', 'entrepreneur', 'startup']):
            return 'business'
        elif any(news in subreddit for news in ['news', 'worldnews', 'politics']):
            return 'news'
        
        # 基于内容分类
        if any(tech in content for tech in ['ai', 'artificial intelligence', 'machine learning', 'technology']):
            return 'technology'
        elif any(biz in content for biz in ['startup', 'business', 'entrepreneur', 'company']):
            return 'business'
        
        return 'general'
    
    def save_data(self, posts: List[Dict[str, Any]], training_data: List[Dict[str, Any]]):
        """保存数据到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 确保目录存在
        os.makedirs('collected_data', exist_ok=True)
        
        # 保存原始数据
        raw_filename = f"collected_data/reddit_raw_{timestamp}.json"
        with open(raw_filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f"原始数据已保存: {raw_filename}")
        
        # 保存训练数据
        training_filename = f"collected_data/reddit_training_{timestamp}.json"
        with open(training_filename, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        logger.info(f"训练数据已保存: {training_filename}")
        
        # 保存统计报告
        stats_filename = f"collected_data/reddit_stats_{timestamp}.json"
        with open(stats_filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        logger.info(f"统计报告已保存: {stats_filename}")
        
        return {
            'raw_file': raw_filename,
            'training_file': training_filename,
            'stats_file': stats_filename
        }
    
    def print_summary(self):
        """打印收集摘要"""
        print("\n" + "="*60)
        print("📊 Reddit 数据收集摘要")
        print("="*60)
        print(f"🔍 搜索关键词: {', '.join(self.stats['keywords_used'])}")
        print(f"📈 总帖子数: {self.stats['total_posts']}")
        print(f"✅ 过滤后帖子数: {self.stats['filtered_posts']}")
        
        if self.stats['score_stats']:
            print(f"📊 评分统计: 最小={self.stats['score_stats']['min']}, "
                  f"最大={self.stats['score_stats']['max']}, "
                  f"平均={self.stats['score_stats']['avg']:.1f}")
        
        print(f"\n🏆 热门Subreddit:")
        for subreddit, count in sorted(self.stats['subreddits'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
            print(f"   r/{subreddit}: {count} 帖子")
        
        print(f"\n🔥 热门帖子 Top 5:")
        for i, post in enumerate(self.stats['top_posts'], 1):
            print(f"   {i}. {post['title']}")
            print(f"      r/{post['subreddit']} | 评分: {post['score']} | 评论: {post['comments']}")

async def main():
    """主函数"""
    print("🚀 Reddit 数据收集开始")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境变量
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {missing_vars}")
        print("请在.env文件中配置Reddit API凭据")
        return
    
    # 配置参数
    keywords = [
        "AI", "artificial intelligence", "machine learning", 
        "startup", "entrepreneur", "technology", "innovation"
    ]
    max_posts = 50  # 适中的数量，避免API限制
    min_score = 5   # 最小评分过滤
    time_filter = "week"  # 一周内的帖子
    
    try:
        # 创建收集器
        collector = RedditDataCollector()
        
        # 收集数据
        print(f"\n🔍 搜索关键词: {keywords}")
        print(f"📊 最大帖子数: {max_posts}")
        print(f"⭐ 最小评分: {min_score}")
        print(f"📅 时间范围: {time_filter}")
        
        posts = await collector.collect_reddit_data(
            keywords=keywords,
            max_posts=max_posts,
            min_score=min_score,
            time_filter=time_filter
        )
        
        if not posts:
            print("⚠️ 未收集到任何数据")
            return
        
        # 生成训练数据
        print("\n🔄 生成训练数据...")
        training_data = collector.generate_training_data(posts)
        
        # 保存数据
        print("\n💾 保存数据...")
        saved_files = collector.save_data(posts, training_data)
        
        # 打印摘要
        collector.print_summary()
        
        print(f"\n📁 生成的文件:")
        for file_type, filename in saved_files.items():
            print(f"   {file_type}: {filename}")
        
        print(f"\n✅ Reddit 数据收集完成！")
        print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"数据收集失败: {e}")
        print(f"\n❌ 数据收集失败: {e}")
        print("请检查网络连接和API凭据")

if __name__ == "__main__":
    asyncio.run(main())