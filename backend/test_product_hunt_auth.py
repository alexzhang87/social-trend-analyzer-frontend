#!/usr/bin/env python3
"""
Product Hunt API认证测试脚本
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

async def test_product_hunt_auth():
    """测试Product Hunt API认证"""
    print("测试Product Hunt API认证...")
    
    client_id = os.getenv('PRODUCT_HUNT_CLIENT_ID')
    client_secret = os.getenv('PRODUCT_HUNT_CLIENT_SECRET')
    
    print(f"Client ID: {client_id[:20] if client_id else 'None'}...")
    print(f"Client Secret: {client_secret[:20] if client_secret else 'None'}...")
    
    if not client_id or not client_secret:
        print("❌ 缺少Product Hunt API认证信息")
        return False
    
    # 测试获取访问令牌
    auth_url = "https://api.producthunt.com/v2/oauth/token"
    
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data) as response:
                print(f"认证响应状态: {response.status}")
                
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ 认证成功!")
                    print(f"访问令牌: {token_data.get('access_token', '')[:20]}...")
                    
                    # 测试API调用
                    await test_api_call(token_data.get('access_token'))
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 认证失败: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 认证请求失败: {e}")
        return False

async def test_api_call(access_token):
    """测试API调用"""
    print("\n测试API调用...")
    
    api_url = "https://api.producthunt.com/v2/api/graphql"
    
    # 简单的GraphQL查询
    query = """
    query {
        posts(first: 1) {
            edges {
                node {
                    id
                    name
                    tagline
                    votesCount
                }
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {"query": query}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as response:
                print(f"API调用状态: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ API调用成功!")
                    print(f"返回数据: {json.dumps(result, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ API调用失败: {error_text}")
                    
    except Exception as e:
        print(f"❌ API调用异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_product_hunt_auth())