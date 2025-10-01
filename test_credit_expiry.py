#!/usr/bin/env python3
"""
积分过期功能测试脚本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def register_test_user():
    """注册测试用户"""
    print("注册测试用户...")
    user_data = {
        "email": "test_credit@example.com",
        "password": "testpass123",
        "username": "test_credit_user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        print(f"注册状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"注册成功: {data.get('message', '用户已创建')}")
            return True
        else:
            print(f"注册响应: {response.text}")
            # 如果用户已存在，也算成功
            if "already exists" in response.text or "已存在" in response.text:
                print("用户已存在，继续登录...")
                return True
            return False
    except Exception as e:
        print(f"注册失败: {e}")
        return False

def login_test_user():
    """登录测试用户获取token"""
    print("登录测试用户...")
    login_data = {
        "username": "test_credit@example.com",  # 使用email作为username
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"登录成功，获取到token: {token[:20]}...")
            return token
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_credit_apis(token):
    """测试积分相关API"""
    
    print("=== 积分过期功能测试 ===\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试获取积分余额（包含过期信息）
    print("1. 测试获取积分余额...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/credits/balance", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试获取积分详细分解
    print("2. 测试获取积分详细分解...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/credits/breakdown", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试获取即将过期的积分
    print("3. 测试获取即将过期的积分...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/credits/expiring", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试获取积分使用历史
    print("4. 测试获取积分使用历史...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/credits/history", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "="*50 + "\n")

def test_health_check():
    """测试服务健康状态"""
    print("0. 测试服务健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"服务状态: {data}")
        else:
            print(f"服务异常: {response.text}")
    except Exception as e:
        print(f"连接失败: {e}")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # 测试服务健康状态
    test_health_check()
    
    # 注册测试用户
    if register_test_user():
        # 登录获取token
        token = login_test_user()
        if token:
            # 测试积分API
            test_credit_apis(token)
        else:
            print("无法获取认证token，跳过API测试")
    else:
        print("无法注册测试用户，跳过API测试")
    
    print("测试完成！")