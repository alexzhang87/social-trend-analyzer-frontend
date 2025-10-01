#!/usr/bin/env python3
"""
直接测试Product Hunt API连接
"""
import asyncio
import aiohttp
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_product_hunt_auth():
    """测试Product Hunt API认证"""
    print("=== Product Hunt API 认证测试 ===")
    
    # 获取环境变量
    client_id = os.getenv('PRODUCT_HUNT_CLIENT_ID')
    client_secret = os.getenv('PRODUCT_HUNT_CLIENT_SECRET')
    
    print(f"Client ID: {client_id[:10]}..." if client_id else "Client ID: 未设置")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "Client Secret: 未设置")
    
    if not client_id or not client_secret:
        print("❌ Product Hunt API 认证信息未配置")
        return False
    
    # 获取访问令牌
    token_url = "https://api.producthunt.com/v2/oauth/token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("正在获取访问令牌...")
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_response = await response.json()
                    access_token = token_response.get('access_token')
                    print(f"✅ 成功获取访问令牌: {access_token[:20]}...")
                    
                    # 测试API调用
                    await test_api_call(session, access_token)
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 获取令牌失败: {response.status}")
                    print(f"错误信息: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False

async def test_api_call(session, access_token):
    """测试API调用"""
    print("\n=== 测试API调用 ===")
    
    # GraphQL查询
    query = """
    query {
        posts(first: 3) {
            edges {
                node {
                    id
                    name
                    tagline
                    votesCount
                    createdAt
                }
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    api_url = "https://api.producthunt.com/v2/api/graphql"
    
    try:
        async with session.post(
            api_url,
            json={"query": query},
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ API调用成功!")
                
                if 'data' in data and 'posts' in data['data']:
                    posts = data['data']['posts']['edges']
                    print(f"获取到 {len(posts)} 个产品:")
                    
                    for i, post in enumerate(posts, 1):
                        node = post['node']
                        print(f"  {i}. {node['name']} - {node['votesCount']} votes")
                        print(f"     {node['tagline']}")
                else:
                    print("⚠️ 响应格式异常:")
                    print(data)
            else:
                error_text = await response.text()
                print(f"❌ API调用失败: {response.status}")
                print(f"错误信息: {error_text}")
                
    except Exception as e:
        print(f"❌ API调用错误: {str(e)}")

async def main():
    """主函数"""
    print("开始Product Hunt API测试...\n")
    
    success = await test_product_hunt_auth()
    
    if success:
        print("\n🎉 Product Hunt API测试成功!")
    else:
        print("\n❌ Product Hunt API测试失败!")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)