#!/usr/bin/env python3
"""
Railway 部署健康检查脚本
检查部署到Railway的应用是否正常运行
"""

import requests
import time
import sys
import json
from urllib.parse import urljoin

def check_endpoint(base_url, endpoint, expected_status=200, timeout=10):
    """检查单个端点"""
    url = urljoin(base_url, endpoint)
    try:
        print(f"检查端点: {url}")
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == expected_status:
            print(f"✅ {endpoint} - 状态码: {response.status_code}")
            return True
        else:
            print(f"❌ {endpoint} - 状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint} - 连接错误: {e}")
        return False

def test_api_endpoints(base_url):
    """测试主要API端点"""
    endpoints = [
        "/",  # 根路径
        "/docs",  # API文档
        "/api/v1/analysis/trends",  # 趋势分析（可能需要参数）
    ]
    
    results = []
    for endpoint in endpoints:
        result = check_endpoint(base_url, endpoint)
        results.append(result)
        time.sleep(1)  # 避免请求过快
    
    return results

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python railway_health_check.py <RAILWAY_APP_URL>")
        print("例如: python railway_health_check.py https://your-app.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 50)
    print("Railway 应用健康检查")
    print("=" * 50)
    print(f"检查应用: {base_url}")
    print()
    
    # 等待应用启动
    print("等待应用启动...")
    time.sleep(10)
    
    # 测试端点
    results = test_api_endpoints(base_url)
    
    # 总结结果
    print("\n" + "=" * 50)
    print("健康检查结果")
    print("=" * 50)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"✅ 所有检查通过 ({success_count}/{total_count})")
        print("应用部署成功！")
        sys.exit(0)
    else:
        print(f"❌ 部分检查失败 ({success_count}/{total_count})")
        print("请检查应用日志和配置")
        sys.exit(1)

if __name__ == "__main__":
    main()