#!/usr/bin/env python3
"""
简化的Product Hunt数据收集脚本
直接使用API调用，避免复杂的服务导入
"""
import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

class SimpleProductHuntCollector:
    """简化的Product Hunt数据收集器"""
    
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
    
    async def get_products_by_date(self, date_str, limit=20):
        """获取指定日期的产品"""
        query = f"""
        query {{
            posts(postedAfter: "{date_str}T00:00:00Z", postedBefore: "{date_str}T23:59:59Z", first: {limit}) {{
                edges {{
                    node {{
                        id
                        name
                        tagline
                        description
                        url
                        votesCount
                        commentsCount
                        createdAt
                        featuredAt
                        website
                        topics {{
                            edges {{
                                node {{
                                    name
                                }}
                            }}
                        }}
                        makers {{
                            edges {{
                                node {{
                                    name
                                    username
                                }}
                            }}
                        }}
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
                            
                            # 提取主题
                            topics = [topic['node']['name'] for topic in node.get('topics', {}).get('edges', [])]
                            
                            # 提取制作者
                            makers = [maker['node']['name'] for maker in node.get('makers', {}).get('edges', [])]
                            
                            product = {
                                'id': node['id'],
                                'name': node['name'],
                                'tagline': node['tagline'],
                                'description': node.get('description', ''),
                                'url': node['url'],
                                'website': node.get('website', ''),
                                'votes': node['votesCount'],
                                'comments_count': node['commentsCount'],
                                'created_at': node['createdAt'],
                                'featured_at': node.get('featuredAt'),
                                'topics': topics,
                                'makers': makers,
                                'source': 'product_hunt',
                                'collected_at': datetime.now().isoformat()
                            }
                            products.append(product)
                        
                        print(f"✅ 获取到 {len(products)} 个产品 ({date_str})")
                        return products
                    else:
                        print(f"⚠️ 没有找到产品数据 ({date_str})")
                        return []
                else:
                    error_text = await response.text()
                    print(f"❌ API调用失败: {response.status} - {error_text}")
                    return []
    
    async def collect_data(self, days=7, min_votes=10, output_dir="collected_data"):
        """收集数据"""
        print(f"=== Product Hunt 数据收集开始 ===")
        print(f"收集天数: {days}")
        print(f"最小投票数: {min_votes}")
        print(f"输出目录: {output_dir}")
        
        # 获取访问令牌
        if not await self.get_access_token():
            return False
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        all_products = []
        
        # 收集最近几天的数据
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            products = await self.get_products_by_date(date_str)
            
            # 过滤低投票产品
            filtered_products = [p for p in products if p['votes'] >= min_votes]
            
            print(f"  过滤后: {len(filtered_products)} 个产品 (>= {min_votes} votes)")
            
            all_products.extend(filtered_products)
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        # 按投票数排序
        all_products.sort(key=lambda x: x['votes'], reverse=True)
        
        # 保存数据
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存原始数据
        raw_file = output_path / f"product_hunt_raw_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        # 生成训练数据格式
        training_data = []
        for product in all_products:
            training_item = {
                "text": f"{product['name']}: {product['tagline']}. {product['description']}",
                "metadata": {
                    "source": "product_hunt",
                    "votes": product['votes'],
                    "comments": product['comments_count'],
                    "topics": product['topics'],
                    "makers": product['makers'],
                    "url": product['url'],
                    "collected_at": product['collected_at']
                },
                "quality_score": min(1.0, product['votes'] / 100.0),  # 简单的质量评分
                "category": "product_innovation"
            }
            training_data.append(training_item)
        
        # 保存训练数据
        training_file = output_path / f"product_hunt_training_{timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 生成统计报告
        stats = {
            "collection_date": datetime.now().isoformat(),
            "total_products": len(all_products),
            "days_collected": days,
            "min_votes_filter": min_votes,
            "top_products": all_products[:10] if all_products else [],
            "vote_distribution": {
                "max_votes": max([p['votes'] for p in all_products]) if all_products else 0,
                "min_votes": min([p['votes'] for p in all_products]) if all_products else 0,
                "avg_votes": sum([p['votes'] for p in all_products]) / len(all_products) if all_products else 0
            },
            "files_generated": [
                str(raw_file.name),
                str(training_file.name)
            ]
        }
        
        stats_file = output_path / f"product_hunt_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 数据收集完成 ===")
        print(f"总产品数: {len(all_products)}")
        print(f"文件保存位置:")
        print(f"  原始数据: {raw_file}")
        print(f"  训练数据: {training_file}")
        print(f"  统计报告: {stats_file}")
        
        if all_products:
            print(f"\n前5个热门产品:")
            for i, product in enumerate(all_products[:5], 1):
                print(f"  {i}. {product['name']} - {product['votes']} votes")
                print(f"     {product['tagline']}")
        
        return True

async def main():
    """主函数"""
    collector = SimpleProductHuntCollector()
    
    # 配置参数
    days = 7  # 收集最近7天
    min_votes = 10  # 最小投票数
    output_dir = "collected_data"
    
    success = await collector.collect_data(days=days, min_votes=min_votes, output_dir=output_dir)
    
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