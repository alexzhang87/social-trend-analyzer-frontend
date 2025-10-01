#!/usr/bin/env python3
"""
API端点测试脚本
测试各种API功能，包括认证和非认证端点
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8001"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.content else None,
            "url": url
        }
    except Exception as e:
        return {
            "error": str(e),
            "url": url
        }

def main():
    """主测试函数"""
    print("🚀 开始测试API端点...")
    print("=" * 50)
    
    # 测试基础端点
    tests = [
        ("GET", "/", None),
        ("GET", "/api/v1/health/", None),
        ("GET", "/docs", None),
        ("GET", "/api/v1/ai-analysis/health", None),
    ]
    
    # 需要认证的端点测试数据
    auth_tests = [
        ("GET", "/api/v1/ai-analysis/models/status", None),
        ("POST", "/api/v1/ai-analysis/sentiment", {"text": "This is a test message", "use_advanced": False}),
        ("GET", "/api/v1/mobile/status", None),
        ("GET", "/api/v1/feedback/health", None),
    ]
    
    # 测试公开端点
    print("📋 测试公开端点:")
    for method, endpoint, data in tests:
        result = test_endpoint(method, endpoint, data)
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {method} {endpoint} - Status: {result.get('status_code', 'Error')}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
    
    print("\n🔐 测试需要认证的端点:")
    for method, endpoint, data in auth_tests:
        result = test_endpoint(method, endpoint, data)
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {method} {endpoint} - Status: {result.get('status_code', 'Error')}")
        if result.get("data") and "message" in result["data"]:
            print(f"   Message: {result['data']['message']}")
    
    print("\n" + "=" * 50)
    print("✨ API端点测试完成!")

if __name__ == "__main__":
    main()