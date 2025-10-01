import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_cache_system():
    """测试缓存系统"""
    print("\n" + "="*50)
    print("开始测试Redis缓存系统")
    print("="*50)
    
    # 首先登录获取token
    print("\n=== 管理员登录 ===")
    login_data = {
        "username": "admin@trendanalyzer.com",
        "password": "admin123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return False
    
    token = response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("管理员登录成功")
    
    # 测试缓存健康检查
    print("\n=== 测试缓存健康检查 ===")
    response = requests.get(f"{BASE_URL}/api/v1/cache/health", headers=auth_headers)
    print(f"健康检查状态码: {response.status_code}")
    if response.status_code == 200:
        health_data = response.json()
        print(f"缓存健康状态: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
    
    # 测试缓存统计
    print("\n=== 测试缓存统计 ===")
    response = requests.get(f"{BASE_URL}/api/v1/cache/stats", headers=auth_headers)
    print(f"统计状态码: {response.status_code}")
    if response.status_code == 200:
        stats_data = response.json()
        print(f"缓存统计: {json.dumps(stats_data, indent=2, ensure_ascii=False)}")
    
    # 测试趋势分析缓存
    print("\n=== 测试趋势分析缓存 ===")
    
    # 第一次调用（应该执行分析并缓存）
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/trends/",
        headers=auth_headers,
        json={"keywords": ["AI缓存测试"]}
    )
    first_call_time = time.time() - start_time
    print(f"第一次调用状态码: {response.status_code}")
    print(f"第一次调用耗时: {first_call_time:.2f}秒")
    
    if response.status_code == 200:
        # 第二次调用（应该从缓存获取）
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/trends/",
            headers=auth_headers,
            json={"keywords": ["AI缓存测试"]}
        )
        second_call_time = time.time() - start_time
        print(f"第二次调用状态码: {response.status_code}")
        print(f"第二次调用耗时: {second_call_time:.2f}秒")
        
        if second_call_time < first_call_time:
            print("✅ 缓存生效，第二次调用更快")
        else:
            print("⚠️ 缓存可能未生效")
    
    # 测试清除趋势缓存
    print("\n=== 测试清除趋势缓存 ===")
    response = requests.delete(f"{BASE_URL}/api/v1/cache/trends", headers=auth_headers)
    print(f"清除趋势缓存状态码: {response.status_code}")
    if response.status_code == 200:
        clear_data = response.json()
        print(f"清除结果: {json.dumps(clear_data, indent=2, ensure_ascii=False)}")
    
    # 再次检查缓存统计
    print("\n=== 清除后的缓存统计 ===")
    response = requests.get(f"{BASE_URL}/api/v1/cache/stats", headers=auth_headers)
    if response.status_code == 200:
        stats_data = response.json()
        print(f"清除后统计: {json.dumps(stats_data, indent=2, ensure_ascii=False)}")
    
    print("\n" + "="*50)
    print("缓存系统测试完成")
    print("="*50)
    
    return True

if __name__ == "__main__":
    test_cache_system()