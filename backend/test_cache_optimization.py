#!/usr/bin/env python3
"""
缓存优化功能测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_cache_optimization():
    """测试缓存优化功能"""
    print("=== 缓存优化功能测试 ===")
    
    # 1. 测试健康检查
    print("\n1. 测试缓存优化健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/cache-optimization/health")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试性能指标
    print("\n2. 测试性能指标获取...")
    try:
        response = requests.get(f"{BASE_URL}/cache-optimization/metrics")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"性能指标: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试批量缓存操作
    print("\n3. 测试批量缓存设置...")
    try:
        test_data = {
            "items": [
                {"key": "test_key_1", "value": "test_value_1", "ttl": 300},
                {"key": "test_key_2", "value": "test_value_2", "ttl": 300}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/cache-optimization/batch-set",
            json=test_data
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"批量设置结果: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试批量缓存获取
    print("\n4. 测试批量缓存获取...")
    try:
        test_keys = {"keys": ["test_key_1", "test_key_2"]}
        response = requests.post(
            f"{BASE_URL}/cache-optimization/batch-get",
            json=test_keys
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"批量获取结果: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n=== 缓存优化功能测试完成 ===")

if __name__ == "__main__":
    test_cache_optimization()