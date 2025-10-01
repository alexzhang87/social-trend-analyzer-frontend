#!/usr/bin/env python3
"""
获取最新Product Hunt产品的脚本
不按日期过滤，直接获取最新产品
"""
import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

class LatestProductHuntCollector:
    """最新Product Hunt数据收集器"""
    
    def __init__(self):
        self.client_id = os.getenv('PRODUCT_HUNT_CLIENT_ID')
        self.client_secret = os.getenv('PRODUCT_HUNT_CLIENT_SECRET')
        self.access_token = None
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
        
    async def get_access_token(self):
        """获取访问令牌"""
        token_url = "https://api.producthunt.com/v2/oauth/token"
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_response = await response.json()
                    self.access_token = token_response.get('access_token')
                    print(f"✅ 成功获取访问令牌")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 获取令牌失败: {response.status} - {error_text}")
                    return False
    
    async def get_latest_products(self, limit=20):
        """获取最新产品"""
        query = f"""
        query {{
            posts(first: {limit}) {{
                edges {{
                    node {{
                        id
                        name
                        tagline
                        url
                        votesCount
                        commentsCount
                        createdAt
                    }}
                }}
            }}
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json={"query": query},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and 'posts' in data['data']:
                        products = []
                        for edge in data['data']['posts']['edges']:
                            node = edge['node']
                            
                            product = {
                                'id': node['id'],
                                'name': node['name'],
                                'tagline': node['tagline'],
                                'description': '',  # 简化查询中未包含
                                'url': node['url'],
                                'website': '',  # 简化查询中未包含
                                'votes': node['votesCount'],
                                'comments_count': node['commentsCount'],
                                'created_at': node['createdAt'],
                                'featured_at': '',  # 简化查询中未包含
                                'topics': [],  # 简化查询中未包含
                                'makers': [],  # 简化查询中未包含
                                'source': 'product_hunt',
                                'collected_at': datetime.now().isoformat()
                            }
                            products.append(product)
                        
                        print(f"✅ 获取到 {len(products)} 个最新产品")
                        return products
                    else:
                        print(f"⚠️ 没有找到产品数据")
                        if 'errors' in data:
                            print(f"API错误: {data['errors']}")
                        return []
                else:
                    error_text = await response.text()
                    print(f"❌ API调用失败: {response.status} - {error_text}")
                    return []
    
    async def collect_data(self, min_votes=5, max_products=100, output_dir="collected_data"):
        """收集数据"""
        print(f"=== Product Hunt 最新数据收集开始 ===")
        print(f"最大产品数: {max_products}")
        print(f"最小投票数: {min_votes}")
        print(f"输出目录: {output_dir}")
        
        # 获取访问令牌
        if not await self.get_access_token():
            return False
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 获取最新产品
        all_products = await self.get_latest_products(limit=max_products)
        
        if not all_products:
            print("❌ 没有获取到任何产品数据")
            return False
        
        # 过滤低投票产品
        filtered_products = [p for p in all_products if p['votes'] >= min_votes]
        print(f"过滤后: {len(filtered_products)} 个产品 (>= {min_votes} votes)")
        
        # 按投票数排序
        filtered_products.sort(key=lambda x: x['votes'], reverse=True)
        
        # 保存数据
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存原始数据
        raw_file = output_path / f"product_hunt_latest_raw_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_products, f, ensure_ascii=False, indent=2)
        
        # 生成训练数据格式
        training_data = []
        for product in filtered_products:
            # 构建完整的产品描述
            full_text = f"{product['name']}: {product['tagline']}"
            if product['description']:
                full_text += f". {product['description']}"
            
            training_item = {
                "text": full_text,
                "metadata": {
                    "source": "product_hunt",
                    "product_id": product['id'],
                    "votes": product['votes'],
                    "comments": product['comments_count'],
                    "topics": product['topics'],
                    "makers": product['makers'],
                    "url": product['url'],
                    "website": product['website'],
                    "created_at": product['created_at'],
                    "collected_at": product['collected_at']
                },
                "quality_score": min(1.0, product['votes'] / 100.0),  # 基于投票数的质量评分
                "category": "product_innovation",
                "type": "product_launch"
            }
            training_data.append(training_item)
        
        # 保存训练数据
        training_file = output_path / f"product_hunt_latest_training_{timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 生成统计报告
        if filtered_products:
            vote_counts = [p['votes'] for p in filtered_products]
            comment_counts = [p['comments_count'] for p in filtered_products]
            
            # 统计主题分布
            topic_counter = {}
            for product in filtered_products:
                for topic in product['topics']:
                    topic_counter[topic] = topic_counter.get(topic, 0) + 1
            
            top_topics = sorted(topic_counter.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats = {
            "collection_date": datetime.now().isoformat(),
            "total_products_fetched": len(all_products),
            "filtered_products": len(filtered_products),
            "min_votes_filter": min_votes,
            "vote_statistics": {
                "max_votes": max(vote_counts) if vote_counts else 0,
                "min_votes": min(vote_counts) if vote_counts else 0,
                "avg_votes": sum(vote_counts) / len(vote_counts) if vote_counts else 0
            },
            "comment_statistics": {
                "max_comments": max(comment_counts) if comment_counts else 0,
                "min_comments": min(comment_counts) if comment_counts else 0,
                "avg_comments": sum(comment_counts) / len(comment_counts) if comment_counts else 0
            },
            "top_topics": top_topics,
            "top_products": [
                {
                    "name": p['name'],
                    "votes": p['votes'],
                    "tagline": p['tagline']
                } for p in filtered_products[:10]
            ],
            "files_generated": [
                str(raw_file.name),
                str(training_file.name)
            ]
        }
        
        stats_file = output_path / f"product_hunt_latest_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 数据收集完成 ===")
        print(f"原始产品数: {len(all_products)}")
        print(f"过滤后产品数: {len(filtered_products)}")
        print(f"文件保存位置:")
        print(f"  原始数据: {raw_file}")
        print(f"  训练数据: {training_file}")
        print(f"  统计报告: {stats_file}")
        
        if filtered_products:
            print(f"\n前5个热门产品:")
            for i, product in enumerate(filtered_products[:5], 1):
                print(f"  {i}. {product['name']} - {product['votes']} votes")
                print(f"     {product['tagline']}")
        
        if top_topics:
            print(f"\n热门主题:")
            for topic, count in top_topics[:5]:
                print(f"  {topic}: {count} 个产品")
        
        return True

async def main():
    """主函数"""
    collector = LatestProductHuntCollector()
    
    # 配置参数
    min_votes = 5  # 降低最小投票数
    max_products = 20  # 减少产品数量以降低复杂度
    output_dir = "collected_data"
    
    success = await collector.collect_data(
        min_votes=min_votes, 
        max_products=max_products, 
        output_dir=output_dir
    )
    
    if success:
        print("\n🎉 Product Hunt 数据收集成功!")
    else:
        print("\n❌ Product Hunt 数据收集失败!")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n数据收集被中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 数据收集出错: {e}")
        exit(1)