#!/usr/bin/env python3
"""
Product Hunt API 快速测试脚本
验证API配置是否正确
"""

import os
import sys
import asyncio
import aiohttp
import json
from datetime import datetime

# 添加app路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ProductHuntAPITest:
    def __init__(self):
        self.client_id = os.getenv('PRODUCT_HUNT_CLIENT_ID')
        self.client_secret = os.getenv('PRODUCT_HUNT_CLIENT_SECRET')
        self.redirect_uri = os.getenv('PRODUCT_HUNT_REDIRECT_URI')
        
        # Product Hunt GraphQL API端点
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.oauth_url = "https://api.producthunt.com/v2/oauth/token"
        
        print("🔧 Product Hunt API 测试配置:")
        print(f"   Client ID: {self.client_id[:20]}..." if self.client_id else "   ❌ Client ID: 未配置")
        print(f"   Client Secret: {self.client_secret[:20]}..." if self.client_secret else "   ❌ Client Secret: 未配置")
        print(f"   Redirect URI: {self.redirect_uri}")
        print()
    
    async def test_client_credentials(self):
        """测试Client Credentials授权流程"""
        print("🔑 测试Client Credentials授权...")
        
        # 准备OAuth请求
        auth_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.oauth_url, data=auth_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        access_token = token_data.get('access_token')
                        
                        if access_token:
                            print(f"   ✅ 授权成功！Token: {access_token[:20]}...")
                            return access_token
                        else:
                            print(f"   ❌ 授权失败：未获得access_token")
                            print(f"   响应数据: {token_data}")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"   ❌ 授权失败: HTTP {response.status}")
                        print(f"   错误信息: {error_text}")
                        return None
        
        except Exception as e:
            print(f"   ❌ 授权请求异常: {e}")
            return None
    
    async def test_api_query(self, access_token):
        """测试GraphQL API查询"""
        print("\n📊 测试GraphQL API查询...")
        
        # 简单的GraphQL查询 - 获取今日产品
        query = """
        query {
            posts(first: 5) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        website
                        votesCount
                        commentsCount
                        createdAt
                        featuredAt
                        makers {
                            id
                            name
                            headline
                        }
                        topics {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, 
                                       headers=headers, 
                                       json=payload) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data:
                            print(f"   ❌ GraphQL查询错误:")
                            for error in data['errors']:
                                print(f"     - {error.get('message', error)}")
                            return False
                        
                        posts = data.get('data', {}).get('posts', {}).get('edges', [])
                        print(f"   ✅ 成功获取 {len(posts)} 个产品")
                        
                        # 显示前3个产品的信息
                        for i, edge in enumerate(posts[:3]):
                            product = edge['node']
                            print(f"\n   📱 产品 {i+1}:")
                            print(f"     名称: {product.get('name', 'N/A')}")
                            print(f"     口号: {product.get('tagline', 'N/A')}")
                            print(f"     投票数: {product.get('votesCount', 0)}")
                            print(f"     评论数: {product.get('commentsCount', 0)}")
                            print(f"     网站: {product.get('website', 'N/A')}")
                            
                            # 显示制作者
                            makers = product.get('makers', [])
                            if makers:
                                maker_names = [m.get('name', 'N/A') for m in makers]
                                print(f"     制作者: {', '.join(maker_names)}")
                            
                            # 显示分类
                            topics = product.get('topics', [])
                            if topics:
                                topic_names = [t.get('name', 'N/A') for t in topics]
                                print(f"     分类: {', '.join(topic_names)}")
                        
                        return True
                    
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API查询失败: HTTP {response.status}")
                        print(f"   错误信息: {error_text}")
                        return False
        
        except Exception as e:
            print(f"   ❌ API查询异常: {e}")
            return False
    
    async def run_test(self):
        """运行完整测试"""
        print("🚀 开始Product Hunt API测试")
        print("=" * 50)
        
        # 检查配置
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            print("❌ API配置不完整，请检查.env文件")
            return False
        
        # 测试授权
        access_token = await self.test_client_credentials()
        if not access_token:
            print("\n❌ 授权测试失败，无法继续API测试")
            return False
        
        # 测试API查询
        api_success = await self.test_api_query(access_token)
        
        print("\n" + "=" * 50)
        if api_success:
            print("🎉 Product Hunt API测试完全成功！")
            print("\n📋 后续可用功能:")
            print("   ✅ 获取每日产品列表")
            print("   ✅ 搜索相关产品")
            print("   ✅ 获取产品详细信息")
            print("   ✅ 分析产品趋势")
            print("   ✅ 集成到趋势分析服务")
        else:
            print("❌ Product Hunt API测试失败")
        
        return api_success


async def main():
    """主函数"""
    tester = ProductHuntAPITest()
    success = await tester.run_test()
    
    if success:
        print(f"\n🔗 重要提醒:")
        print(f"   Ngrok隧道地址: {tester.redirect_uri}")
        print(f"   请确保ngrok隧道保持运行状态")
        print(f"   后端服务地址: http://0.0.0.0:8001")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        print(f"\n🏁 测试完成，退出代码: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        sys.exit(1)