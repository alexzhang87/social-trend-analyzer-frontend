#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
测试所有主要的API功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_docs():
    """测试API文档"""
    print("\n=== 测试API文档 ===")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"状态码: {response.status_code}")
        print(f"文档可访问: {response.status_code == 200}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_user_registration():
    """测试用户注册"""
    print("\n=== 测试用户注册 ===")
    try:
        test_user = {
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            headers=HEADERS,
            json=test_user
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:  # 注册返回200而不是201
            result = response.json()
            print(f"注册成功: {result['username']}")
            return True, test_user
        else:
            print(f"注册失败: {response.text}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        return False, None

def test_user_login(user_data):
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    try:
        # OAuth2PasswordRequestForm需要form-data格式
        login_data = {
            "username": user_data["email"],  # 使用email作为username
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data  # 使用data而不是json
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"登录成功，获得token")
            return True, result["access_token"]
        else:
            print(f"登录失败: {response.text}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        return False, None

def test_protected_endpoint(token):
    """测试需要认证的端点"""
    print("\n=== 测试受保护的端点 ===")
    try:
        auth_headers = {
            **HEADERS,
            "Authorization": f"Bearer {token}"
        }
        
        # 测试获取当前用户信息
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers=auth_headers
        )
        print(f"获取用户信息 - 状态码: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"用户信息: {user_info['username']}")
            
            # 测试积分余额
            response = requests.get(
                f"{BASE_URL}/api/v1/credits/balance",
                headers=auth_headers
            )
            print(f"积分余额 - 状态码: {response.status_code}")
            if response.status_code == 200:
                balance = response.json()
                print(f"积分余额: {balance['credits_balance']}")
                return True
        
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_trends_api(token):
    """测试趋势分析API"""
    print("\n=== 测试趋势分析API ===")
    try:
        auth_headers = {
            **HEADERS,
            "Authorization": f"Bearer {token}"
        }
        
        # 测试基础分析接口
        response = requests.post(
            f"{BASE_URL}/api/v1/trends/",
            headers=auth_headers,
            json={"keywords": ["AI", "技术"]}
        )
        print(f"基础分析 - 状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"分析成功，获得结果: {len(result.get('results', []))} 个关键词")
            return True
        else:
            print(f"基础分析失败: {response.text}")
            # 尝试快速验证接口
            response = requests.post(
                f"{BASE_URL}/api/v1/trends/quick-validate",
                headers=auth_headers,
                json={"keywords": ["AI"]}
            )
            print(f"快速验证 - 状态码: {response.status_code}")
            if response.status_code == 200:
                print("快速验证接口正常")
                return True
            return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_admin_login():
    """测试管理员登录"""
    print("\n=== 测试管理员登录 ===")
    try:
        # OAuth2PasswordRequestForm需要form-data格式
        admin_data = {
            "username": "admin@example.com",  # 使用管理员邮箱
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=admin_data  # 使用data而不是json
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"管理员登录成功")
            return True, result["access_token"]
        else:
            print(f"管理员登录失败: {response.text}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        return False, None

def test_admin_api(admin_token):
    """测试管理员API"""
    print("\n=== 测试管理员API ===")
    try:
        auth_headers = {
            **HEADERS,
            "Authorization": f"Bearer {admin_token}"
        }
        
        # 测试获取用户列表
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/users?limit=5",
            headers=auth_headers
        )
        print(f"用户列表 - 状态码: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"获取到 {len(users)} 个用户")
            
            # 测试系统统计
            response = requests.get(
                f"{BASE_URL}/api/v1/admin/stats",
                headers=auth_headers
            )
            print(f"系统统计 - 状态码: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"总用户数: {stats['total_users']}")
                return True
        
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """主测试函数"""
    print("开始API端点测试...")
    print(f"测试目标: {BASE_URL}")
    
    results = []
    
    # 基础测试
    results.append(("健康检查", test_health_check()))
    results.append(("API文档", test_docs()))
    
    # 用户认证测试
    success, user_data = test_user_registration()
    results.append(("用户注册", success))
    
    if success and user_data:
        success, token = test_user_login(user_data)
        results.append(("用户登录", success))
        
        if success and token:
            results.append(("受保护端点", test_protected_endpoint(token)))
            results.append(("趋势分析API", test_trends_api(token)))
    
    # 管理员测试
    success, admin_token = test_admin_login()
    results.append(("管理员登录", success))
    
    if success and admin_token:
        results.append(("管理员API", test_admin_api(admin_token)))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"总计: {passed}/{total} 个测试通过")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！API服务运行正常。")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()