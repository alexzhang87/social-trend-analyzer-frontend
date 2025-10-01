#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_complete_system():
    """完整系统测试"""
    print("\n" + "="*60)
    print("🚀 社交趋势分析器 - 完整系统测试")
    print("="*60)
    
    test_results = {
        "health_check": False,
        "api_docs": False,
        "user_registration": False,
        "user_login": False,
        "protected_endpoints": False,
        "trends_analysis": False,
        "admin_login": False,
        "admin_apis": False,
        "cache_system": False,
        "credits_system": False
    }
    
    # 1. 健康检查
    print("\n=== 1. 健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            test_results["health_check"] = True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 2. API文档
    print("\n=== 2. API文档访问 ===")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API文档可访问")
            test_results["api_docs"] = True
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档访问异常: {e}")
    
    # 3. 用户注册
    print("\n=== 3. 用户注册 ===")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "email": f"testuser_{timestamp}@example.com",
        "username": f"testuser_{timestamp}",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=test_user)
        if response.status_code == 200:
            print(f"✅ 用户注册成功: {test_user['username']}")
            test_results["user_registration"] = True
        else:
            print(f"❌ 用户注册失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 用户注册异常: {e}")
    
    # 4. 用户登录
    print("\n=== 4. 用户登录 ===")
    user_token = None
    try:
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            user_token = response.json()["access_token"]
            print("✅ 用户登录成功")
            test_results["user_login"] = True
        else:
            print(f"❌ 用户登录失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 用户登录异常: {e}")
    
    # 5. 受保护端点测试
    if user_token:
        print("\n=== 5. 受保护端点测试 ===")
        auth_headers = {"Authorization": f"Bearer {user_token}"}
        
        try:
            # 获取用户信息
            response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=auth_headers)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功: {user_info['username']}")
                
                # 获取积分余额
                response = requests.get(f"{BASE_URL}/api/v1/credits/balance", headers=auth_headers)
                if response.status_code == 200:
                    balance = response.json()
                    print(f"✅ 获取积分余额成功: {balance['credits_balance']}")
                    test_results["protected_endpoints"] = True
                    test_results["credits_system"] = True
        except Exception as e:
            print(f"❌ 受保护端点测试异常: {e}")
    
    # 6. 趋势分析API测试
    if user_token:
        print("\n=== 6. 趋势分析API测试 ===")
        try:
            # 测试基础分析
            response = requests.post(
                f"{BASE_URL}/api/v1/trends/",
                headers=auth_headers,
                json={"keywords": ["AI测试"]}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 趋势分析成功: {len(result.get('results', []))} 个结果")
                test_results["trends_analysis"] = True
            else:
                print(f"❌ 趋势分析失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 趋势分析异常: {e}")
    
    # 7. 管理员登录
    print("\n=== 7. 管理员登录 ===")
    admin_token = None
    try:
        admin_login_data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=admin_login_data)
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
            print("✅ 管理员登录成功")
            test_results["admin_login"] = True
        else:
            print(f"❌ 管理员登录失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 管理员登录异常: {e}")
    
    # 8. 管理员API测试
    if admin_token:
        print("\n=== 8. 管理员API测试 ===")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            # 获取用户列表
            response = requests.get(f"{BASE_URL}/api/v1/admin/users?limit=5", headers=admin_headers)
            if response.status_code == 200:
                users = response.json()
                # API返回的是用户列表，不是包含users字段的字典
                user_count = len(users) if isinstance(users, list) else 0
                print(f"✅ 获取用户列表成功: {user_count} 个用户")
                
                # 获取系统统计
                response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=admin_headers)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ 获取系统统计成功: 总用户数 {stats.get('total_users', 0)}")
                    test_results["admin_apis"] = True
        except Exception as e:
            print(f"❌ 管理员API测试异常: {e}")
    
    # 9. 缓存系统测试
    if admin_token:
        print("\n=== 9. 缓存系统测试 ===")
        try:
            # 缓存健康检查
            response = requests.get(f"{BASE_URL}/api/v1/cache/health", headers=admin_headers)
            if response.status_code == 200:
                health = response.json()
                if health.get('data', {}).get('overall_health', False):
                    print("✅ 缓存系统健康")
                    
                    # 获取缓存统计
                    response = requests.get(f"{BASE_URL}/api/v1/cache/stats", headers=admin_headers)
                    if response.status_code == 200:
                        stats = response.json()
                        redis_connected = stats.get('data', {}).get('redis', {}).get('connected', False)
                        print(f"✅ 缓存统计获取成功: Redis连接 {redis_connected}")
                        test_results["cache_system"] = True
                else:
                    print("⚠️ 缓存系统不健康")
        except Exception as e:
            print(f"❌ 缓存系统测试异常: {e}")
    
    # 测试结果汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        test_display = test_name.replace("_", " ").title()
        print(f"{test_display:<20} {status}")
    
    print("\n" + "="*60)
    print(f"总计: {passed_tests}/{total_tests} 个测试通过")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 系统测试优秀！")
    elif success_rate >= 80:
        print("👍 系统测试良好！")
    elif success_rate >= 70:
        print("⚠️ 系统测试一般，需要改进")
    else:
        print("❌ 系统测试不合格，需要修复")
    
    print("="*60)
    
    return success_rate >= 80

if __name__ == "__main__":
    test_complete_system()