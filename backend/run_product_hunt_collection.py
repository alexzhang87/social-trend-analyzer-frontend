#!/usr/bin/env python3
"""
Product Hunt 高质量数据收集脚本

使用Product Hunt官方API收集产品创新和市场趋势数据，适用于产品训练。

使用方法:
python run_product_hunt_collection.py --days 7 --max-products 200 --output-dir production_product_hunt_data

参数说明:
--days: 收集最近几天的数据
--max-products: 最大产品数量
--output-dir: 输出目录
--min-votes: 最小投票数阈值（默认50）
--categories: 产品类别过滤
"""

import os
import sys
import asyncio
import argparse
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 添加app路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.product_hunt_service import ProductHuntOfficialService
from app.services.data_quality_service import DataQualityService
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('product_hunt_collection.log')
    ]
)
logger = logging.getLogger(__name__)


class ProductHuntDataCollector:
    """Product Hunt数据收集器"""
    
    def __init__(self, output_dir: str = "product_hunt_data"):
        self.product_hunt_service = ProductHuntOfficialService()
        self.quality_service = DataQualityService()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 数据收集统计
        self.stats = {
            'total_collected': 0,
            'high_quality_count': 0,
            'category_stats': {},
            'collection_time': datetime.now().isoformat(),
            'quality_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        }
    
    async def collect_daily_products(self, date: datetime, max_products: int, min_votes: int) -> list:
        """收集指定日期的产品数据"""
        logger.info(f"收集 {date.strftime('%Y-%m-%d')} 的产品数据...")
        
        try:
            # 获取当日产品
            products = await self.product_hunt_service.get_daily_products(
                date=date,
                limit=max_products
            )
            
            # 过滤低质量产品
            filtered_products = []
            for product in products:
                if (product.get('votes', 0) >= min_votes and
                    product.get('name') and
                    product.get('tagline') and
                    len(product.get('content', '')) > 50):
                    
                    # 设置默认评论为空（暂时不获取详细信息）
                    product['comments'] = []
                    
                    filtered_products.append(product)
            
            logger.info(f"{date.strftime('%Y-%m-%d')} 收集到 {len(filtered_products)} 个高质量产品")
            return filtered_products
            
        except Exception as e:
            logger.error(f"收集 {date.strftime('%Y-%m-%d')} 产品数据失败: {e}")
            return []
    
    async def collect_trending_products(self, max_products: int, min_votes: int) -> list:
        """收集趋势产品"""
        logger.info("收集趋势产品数据...")
        
        try:
            # 收集趋势产品（获取最近一周的热门产品）
            trending_products = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_products = await self.product_hunt_service.get_daily_products(date, 10)
                trending_products.extend(daily_products)
            
            # 按投票数排序，取前max_products个
            trending_products.sort(key=lambda x: x.get('votes', 0), reverse=True)
            products = trending_products[:max_products]
            
            # 过滤和增强数据
            filtered_products = []
            for product in products:
                if (product.get('votes', 0) >= min_votes and
                    product.get('name') and
                    product.get('tagline')):
                    
                    # 设置默认评论为空（暂时不获取详细信息）
                    product['comments'] = []
                    
                    filtered_products.append(product)
            
            logger.info(f"收集到 {len(filtered_products)} 个趋势产品")
            return filtered_products
            
        except Exception as e:
            logger.error(f"收集趋势产品失败: {e}")
            return []
    
    def format_training_data(self, products: list) -> list:
        """格式化为训练数据格式"""
        training_data = []
        
        for product in products:
            platform_specific = product.get('platform_specific', {})
            
            # 主产品信息
            main_content = {
                'question': f"What is {platform_specific.get('name', '')}?",
                'answer': f"{platform_specific.get('tagline', '')}. {product.get('description', '')}",
                'source': 'product_hunt',
                'domain': 'product_discovery',
                'product_id': platform_specific.get('product_hunt_id', ''),
                'product_name': platform_specific.get('name', ''),
                'tagline': platform_specific.get('tagline', ''),
                'website': platform_specific.get('website', ''),
                'votes': product.get('votes', 0),
                'comments_count': product.get('comments_count', 0),
                'featured_at': platform_specific.get('featured_at', ''),
                'topics': platform_specific.get('topics', []),
                'makers': platform_specific.get('makers', []),
                'thumbnail_url': platform_specific.get('thumbnail_url', ''),
                'url': product.get('url', ''),
                'quality_score': self._calculate_quality_score(product),
                'created_at': product.get('created_at', '')
            }
            
            training_data.append(main_content)
            
            # 产品特性问答
            if platform_specific.get('tagline'):
                feature_qa = {
                    'question': f"What does {platform_specific.get('name', '')} do?",
                    'answer': platform_specific.get('tagline', ''),
                    'source': 'product_hunt',
                    'domain': 'product_features',
                    'product_id': platform_specific.get('product_hunt_id', ''),
                    'product_name': platform_specific.get('name', ''),
                    'votes': product.get('votes', 0),
                    'quality_score': self._calculate_quality_score(product),
                    'data_type': 'feature_description'
                }
                training_data.append(feature_qa)
            
            # 产品类别问答
            if platform_specific.get('topics'):
                topics_str = ', '.join(platform_specific.get('topics', []))
                category_qa = {
                    'question': f"What category does {platform_specific.get('name', '')} belong to?",
                    'answer': f"{platform_specific.get('name', '')} belongs to {topics_str} category.",
                    'source': 'product_hunt',
                    'domain': 'product_categorization',
                    'product_id': platform_specific.get('product_hunt_id', ''),
                    'product_name': platform_specific.get('name', ''),
                    'topics': platform_specific.get('topics', []),
                    'votes': product.get('votes', 0),
                    'quality_score': self._calculate_quality_score(product),
                    'data_type': 'category_classification'
                }
                training_data.append(category_qa)
            
            # 高质量评论作为用户反馈
            for comment in product.get('comments', []):
                if (len(comment.get('body', '')) > 30 and
                    comment.get('body', '') not in ['Great!', 'Nice!', 'Awesome!']):
                    
                    comment_data = {
                        'question': f"What do users think about {platform_specific.get('name', '')}?",
                        'answer': comment.get('body', ''),
                        'source': 'product_hunt',
                        'domain': 'user_feedback',
                        'product_id': platform_specific.get('product_hunt_id', ''),
                        'product_name': platform_specific.get('name', ''),
                        'comment_id': comment.get('id', ''),
                        'comment_author': comment.get('user', {}).get('name', ''),
                        'votes': product.get('votes', 0),
                        'quality_score': self._calculate_comment_quality_score(comment),
                        'data_type': 'user_feedback'
                    }
                    
                    training_data.append(comment_data)
        
        return training_data
    
    def _calculate_quality_score(self, product: dict) -> float:
        """计算产品质量分数"""
        score = 0.0
        platform_specific = product.get('platform_specific', {})
        
        # 投票数权重
        votes = product.get('votes', 0)
        if votes > 500:
            score += 0.3
        elif votes > 200:
            score += 0.25
        elif votes > 100:
            score += 0.2
        elif votes > 50:
            score += 0.15
        elif votes > 20:
            score += 0.1
        
        # 评论数权重
        comments_count = product.get('comments_count', 0)
        if comments_count > 50:
            score += 0.2
        elif comments_count > 20:
            score += 0.15
        elif comments_count > 10:
            score += 0.1
        elif comments_count > 5:
            score += 0.05
        
        # 描述质量权重
        description_length = len(product.get('description', ''))
        if description_length > 300:
            score += 0.2
        elif description_length > 150:
            score += 0.15
        elif description_length > 50:
            score += 0.1
        
        # 标语质量权重
        tagline = platform_specific.get('tagline', '')
        if 20 <= len(tagline) <= 100:
            score += 0.1
        
        # 是否有网站
        if platform_specific.get('website'):
            score += 0.1
        
        # 是否有制作者信息
        if platform_specific.get('makers'):
            score += 0.05
        
        # 是否有主题标签
        if platform_specific.get('topics'):
            score += 0.05
        
        # 是否有缩略图
        if platform_specific.get('thumbnail_url'):
            score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_comment_quality_score(self, comment: dict) -> float:
        """计算评论质量分数"""
        score = 0.0
        
        # 内容长度权重
        content_length = len(comment.get('body', ''))
        if content_length > 200:
            score += 0.4
        elif content_length > 100:
            score += 0.3
        elif content_length > 50:
            score += 0.2
        elif content_length > 30:
            score += 0.1
        
        # 用户信息权重
        user = comment.get('user', {})
        if user.get('name'):
            score += 0.1
        
        # 是否包含有用信息（简单启发式）
        body = comment.get('body', '').lower()
        useful_keywords = ['feature', 'use', 'help', 'problem', 'solution', 'recommend', 'experience']
        if any(keyword in body for keyword in useful_keywords):
            score += 0.2
        
        # 避免过短或无意义的评论
        if content_length < 20 or body in ['great!', 'nice!', 'awesome!', 'cool!']:
            score = max(0, score - 0.3)
        
        return min(score, 1.0)
    
    def apply_quality_filter(self, training_data: list, min_quality: float = 0.4) -> tuple:
        """应用质量过滤"""
        high_quality_data = []
        quality_stats = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for item in training_data:
            quality_score = item.get('quality_score', 0.0)
            
            if quality_score >= 0.8:
                quality_stats['excellent'] += 1
            elif quality_score >= 0.6:
                quality_stats['good'] += 1
            elif quality_score >= 0.4:
                quality_stats['fair'] += 1
            else:
                quality_stats['poor'] += 1
            
            if quality_score >= min_quality:
                high_quality_data.append(item)
        
        self.stats['quality_distribution'] = quality_stats
        self.stats['high_quality_count'] = len(high_quality_data)
        
        return high_quality_data, quality_stats
    
    def analyze_categories(self, training_data: list):
        """分析产品类别分布"""
        category_stats = {}
        
        for item in training_data:
            topics = item.get('topics', [])
            if isinstance(topics, list):
                for topic in topics:
                    if topic not in category_stats:
                        category_stats[topic] = {'count': 0, 'avg_votes': 0, 'total_votes': 0}
                    category_stats[topic]['count'] += 1
                    category_stats[topic]['total_votes'] += item.get('votes', 0)
        
        # 计算平均投票数
        for topic, stats in category_stats.items():
            if stats['count'] > 0:
                stats['avg_votes'] = stats['total_votes'] / stats['count']
        
        self.stats['category_stats'] = category_stats
        return category_stats
    
    def save_data(self, training_data: list, collection_params: dict):
        """保存数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存训练数据集
        training_file = self.output_dir / "product_hunt_training_dataset.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存过滤后的高质量数据
        filtered_data, quality_stats = self.apply_quality_filter(training_data)
        filtered_file = self.output_dir / "product_hunt_filtered_training_dataset.json"
        with open(filtered_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
        # 保存CSV格式
        csv_file = self.output_dir / "product_hunt_training_data.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if filtered_data:
                writer = csv.DictWriter(f, fieldnames=filtered_data[0].keys())
                writer.writeheader()
                writer.writerows(filtered_data)
        
        # 分析类别分布
        category_stats = self.analyze_categories(training_data)
        
        # 保存质量报告
        quality_report = {
            'total_processed': len(training_data),
            'high_quality_count': len(filtered_data),
            'medium_quality_count': 0,
            'low_quality_count': len(training_data) - len(filtered_data),
            'duplicate_count': 0,
            'high_quality_percentage': (len(filtered_data) / len(training_data) * 100) if training_data else 0,
            'quality_standards': {
                'min_votes': collection_params.get('min_votes', 50),
                'min_description_length': 50,
                'required_fields': ['question', 'answer', 'source', 'domain', 'product_name'],
                'min_quality_score': 0.4
            },
            'quality_distribution': quality_stats,
            'category_distribution': category_stats,
            'processed_at': datetime.now().isoformat()
        }
        
        quality_file = self.output_dir / "quality_report.json"
        with open(quality_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        
        # 保存最终报告
        final_report = {
            'collection_summary': f'Product Hunt数据收集完成 - {collection_params.get("days", 0)}天数据',
            'collection_time': self.stats['collection_time'],
            'collection_parameters': collection_params,
            'total_count': len(training_data),
            'high_quality_count': len(filtered_data),
            'average_quality': sum(item.get('quality_score', 0) for item in training_data) / len(training_data) if training_data else 0,
            'quality_distribution': quality_stats,
            'category_distribution': category_stats,
            'vote_statistics': {
                'avg_votes': sum(item.get('votes', 0) for item in training_data) / len(training_data) if training_data else 0,
                'max_votes': max((item.get('votes', 0) for item in training_data), default=0),
                'min_votes': min((item.get('votes', 0) for item in training_data), default=0)
            },
            'product_statistics': {
                'unique_products': len(set(item.get('product_id', '') for item in training_data if item.get('product_id'))),
                'avg_comments': sum(item.get('comments_count', 0) for item in training_data if item.get('comments_count')) / len([item for item in training_data if item.get('comments_count')]) if training_data else 0
            },
            'data_sample': training_data[:3] if training_data else []
        }
        
        final_report_file = self.output_dir / f"product_hunt_final_report_{timestamp}.json"
        with open(final_report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        self.generate_markdown_report(final_report, timestamp)
        
        logger.info(f"数据已保存到 {self.output_dir}")
        logger.info(f"训练数据集: {len(training_data)} 条")
        logger.info(f"高质量数据: {len(filtered_data)} 条")
        logger.info(f"质量分布: {quality_stats}")
        logger.info(f"类别分布: {len(category_stats)} 个类别")
    
    def generate_markdown_report(self, report: dict, timestamp: str):
        """生成Markdown格式的报告"""
        markdown_content = f"""# Product Hunt 数据收集报告

## 📊 收集概览
- **收集时间**: {report['collection_time']}
- **收集参数**: {report['collection_parameters']}
- **总数据量**: {report['total_count']} 条
- **高质量数据**: {report['high_quality_count']} 条
- **平均质量分数**: {report['average_quality']:.3f}

## 📈 质量分布
- **优秀 (0.8-1.0)**: {report['quality_distribution']['excellent']} 条
- **良好 (0.6-0.8)**: {report['quality_distribution']['good']} 条
- **一般 (0.4-0.6)**: {report['quality_distribution']['fair']} 条
- **较差 (0.0-0.4)**: {report['quality_distribution']['poor']} 条

## 🎯 产品类别分布
"""
        
        # 按产品数量排序显示前10个类别
        sorted_categories = sorted(
            report['category_distribution'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        for category, stats in sorted_categories:
            markdown_content += f"""
### {category}
- **产品数量**: {stats['count']} 个
- **平均投票数**: {stats['avg_votes']:.1f}
"""
        
        markdown_content += f"""
## 📊 统计信息

### 投票统计
- **平均投票数**: {report['vote_statistics']['avg_votes']:.1f}
- **最高投票数**: {report['vote_statistics']['max_votes']}
- **最低投票数**: {report['vote_statistics']['min_votes']}

### 产品统计
- **独特产品数**: {report['product_statistics']['unique_products']}
- **平均评论数**: {report['product_statistics']['avg_comments']:.1f}

## 📁 生成文件
- `product_hunt_training_dataset.json` - 完整训练数据集
- `product_hunt_filtered_training_dataset.json` - 高质量过滤数据集
- `product_hunt_training_data.csv` - CSV格式数据
- `quality_report.json` - 质量分析报告
- `product_hunt_final_report_{timestamp}.json` - 最终收集报告

## 🎯 数据特点
- 来源于Product Hunt官方API，数据真实可靠
- 包含产品信息、用户评论和市场反馈
- 已进行质量评分和过滤
- 适用于产品推荐、市场分析和创新趋势预测

## 💡 应用场景
- **产品发现**: 帮助用户发现新产品和工具
- **市场趋势**: 分析产品创新方向和热门领域
- **竞品分析**: 了解同类产品的特点和用户反馈
- **创业灵感**: 发现市场机会和用户需求

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        markdown_file = self.output_dir / f"product_hunt_report_{timestamp}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)


async def main():
    parser = argparse.ArgumentParser(description='Product Hunt高质量数据收集')
    parser.add_argument('--days', type=int, default=7,
                       help='收集最近几天的数据')
    parser.add_argument('--max-products', type=int, default=200,
                       help='最大产品数量')
    parser.add_argument('--output-dir', type=str, default='production_product_hunt_data',
                       help='输出目录')
    parser.add_argument('--min-votes', type=int, default=50,
                       help='最小投票数阈值')
    parser.add_argument('--include-trending', action='store_true',
                       help='包含趋势产品')
    
    args = parser.parse_args()
    
    logger.info(f"开始收集Product Hunt数据...")
    logger.info(f"收集天数: {args.days}")
    logger.info(f"最大产品数: {args.max_products}")
    logger.info(f"输出目录: {args.output_dir}")
    logger.info(f"最小投票数: {args.min_votes}")
    
    # 创建收集器
    collector = ProductHuntDataCollector(args.output_dir)
    
    # 收集所有数据
    all_products = []
    
    # 收集每日数据
    for i in range(args.days):
        date = datetime.now() - timedelta(days=i)
        products = await collector.collect_daily_products(
            date=date,
            max_products=args.max_products // args.days,
            min_votes=args.min_votes
        )
        all_products.extend(products)
    
    # 收集趋势产品（如果启用）
    if args.include_trending:
        trending_products = await collector.collect_trending_products(
            max_products=50,
            min_votes=args.min_votes
        )
        all_products.extend(trending_products)
    
    if all_products:
        # 去重（基于产品ID）
        unique_products = []
        seen_ids = set()
        for product in all_products:
            product_id = product.get('platform_specific', {}).get('product_hunt_id')
            if product_id and product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_products.append(product)
        
        # 格式化训练数据
        training_data = collector.format_training_data(unique_products)
        
        # 保存数据
        collection_params = {
            'days': args.days,
            'max_products': args.max_products,
            'min_votes': args.min_votes,
            'include_trending': args.include_trending
        }
        
        collector.save_data(training_data, collection_params)
        
        logger.info("✅ Product Hunt数据收集完成！")
        logger.info(f"📊 总计收集: {len(training_data)} 条数据")
        logger.info(f"🎯 独特产品: {len(unique_products)} 个")
        logger.info(f"📁 数据已保存到: {args.output_dir}")
    else:
        logger.warning("⚠️ 未收集到任何数据，请检查配置和网络连接")


if __name__ == "__main__":
    asyncio.run(main())