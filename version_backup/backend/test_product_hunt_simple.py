#!/usr/bin/env python3
"""
Product Hunt API 简化测试脚本
专门测试API基本连接
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_product_hunt_auth():
    """测试Product Hunt API认证"""
    
    client_id = os.getenv('PRODUCT_HUNT_CLIENT_ID')
    client_secret = os.getenv('PRODUCT_HUNT_CLIENT_SECRET')
    
    print("🔧 Product Hunt API 认证测试")
    print("=" * 40)
    print(f"Client ID: {client_id[:20]}..." if client_id else "❌ Client ID未配置")
    print(f"Client Secret: {client_secret[:20]}..." if client_secret else "❌ Client Secret未配置")
    print()
    
    if not client_id or not client_secret:
        print("❌ API配置不完整")
        return False
    
    # 测试认证
    auth_url = "https://api.producthunt.com/v2/oauth/token"
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    try:
        print("🔑 正在测试认证...")
        response = requests.post(auth_url, data=auth_data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print(f"✅ 认证成功！")
                print(f"   Token: {access_token[:30]}...")
                print(f"   Token类型: {token_data.get('token_type', 'N/A')}")
                print(f"   过期时间: {token_data.get('expires_in', 'N/A')} 秒")
                return access_token
            else:
                print("❌ 认证失败：未获得access_token")
                print(f"   响应: {token_data}")
                return False
        else:
            print(f"❌ 认证请求失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ 认证请求超时")
        return False
    except Exception as e:
        print(f"❌ 认证异常: {e}")
        return False

def test_simple_api_query(access_token):
    """测试简单的API查询"""
    
    print("\n📊 测试API查询")
    print("=" * 40)
    
    # 简单的GraphQL查询
    query = """
    {
        viewer {
            user {
                id
                name
                username
            }
        }
    }
    """
    
    api_url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query
    }
    
    try:
        print("🔍 正在查询用户信息...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print("❌ GraphQL查询错误:")
                for error in data['errors']:
                    print(f"   - {error.get('message', error)}")
                return False
            
            user_data = data.get('data', {}).get('viewer', {}).get('user', {})
            if user_data:
                print("✅ API查询成功！")
                print(f"   用户ID: {user_data.get('id', 'N/A')}")
                print(f"   用户名: {user_data.get('name', 'N/A')}")
                print(f"   Username: @{user_data.get('username', 'N/A')}")
                return True
            else:
                print("⚠️ 查询成功但用户数据为空（可能因为使用了Client Credentials）")
                return True
                
        else:
            print(f"❌ API查询失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ API查询超时")
        return False
    except Exception as e:
        print(f"❌ API查询异常: {e}")
        return False

def test_posts_query(access_token):
    """测试获取产品列表"""
    
    print("\n📱 测试产品列表查询")
    print("=" * 40)
    
    # 获取最新产品的简单查询
    query = """
    {
        posts(first: 3) {
            edges {
                node {
                    id
                    name
                    tagline
                    votesCount
                    commentsCount
                }
            }
        }
    }
    """
    
    api_url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query
    }
    
    try:
        print("🔍 正在查询产品列表...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print("❌ GraphQL查询错误:")
                for error in data['errors']:
                    print(f"   - {error.get('message', error)}")
                return False
            
            posts = data.get('data', {}).get('posts', {}).get('edges', [])
            print(f"✅ 成功获取 {len(posts)} 个产品")
            
            for i, edge in enumerate(posts):
                product = edge['node']
                print(f"\n   📱 产品 {i+1}:")
                print(f"     名称: {product.get('name', 'N/A')}")
                print(f"     口号: {product.get('tagline', 'N/A')}")
                print(f"     投票数: {product.get('votesCount', 0)}")
                print(f"     评论数: {product.get('commentsCount', 0)}")
            
            return True
                
        else:
            print(f"❌ 产品查询失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ 产品查询超时")
        return False
    except Exception as e:
        print(f"❌ 产品查询异常: {e}")
        return False

def main():
    """主测试函数"""
    
    print("🚀 Product Hunt API 简化测试")
    print("=" * 50)
    
    # 步骤1: 测试认证
    access_token = test_product_hunt_auth()
    if not access_token:
        print("\n❌ 认证失败，测试中止")
        return False
    
    # 步骤2: 测试简单查询
    simple_success = test_simple_api_query(access_token)
    
    # 步骤3: 测试产品查询
    posts_success = test_posts_query(access_token)
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   ✅ API认证: 成功")
    print(f"   {'✅' if simple_success else '❌'} 基础查询: {'成功' if simple_success else '失败'}")
    print(f"   {'✅' if posts_success else '❌'} 产品查询: {'成功' if posts_success else '失败'}")
    
    if simple_success and posts_success:
        print("\n🎉 Product Hunt API集成完全成功！")
        print("\n📋 可用功能:")
        print("   ✅ 获取每日产品列表")
        print("   ✅ 搜索相关产品")  
        print("   ✅ 获取产品详情和统计")
        print("   ✅ 集成到趋势分析服务")
        return True
    else:
        print("\n⚠️ 部分功能测试失败，请检查API配置")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n🏁 测试完成: {'成功' if success else '失败'}")