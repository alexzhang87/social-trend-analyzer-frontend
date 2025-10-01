#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Trends API测试脚本
测试Google Trends服务的各项功能
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_api_endpoint(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """测试API端点
    
    Args:
        endpoint: API端点路径
        params: 查询参数
        
    Returns:
        API响应结果
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"\n🔍 测试端点: {endpoint}")
        print(f"📍 URL: {url}")
        if params:
            print(f"📋 参数: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            
            # 显示响应数据的基本信息
            if isinstance(data, dict):
                if 'status' in data:
                    print(f"🔄 状态: {data['status']}")
                if 'data' in data and isinstance(data['data'], list):
                    print(f"📈 数据条数: {len(data['data'])}")
                elif 'data' in data and isinstance(data['data'], dict):
                    print(f"📈 数据字段: {list(data['data'].keys())}")
                if 'message' in data:
                    print(f"💬 消息: {data['message']}")
            
            return data
        else:
            print(f"❌ 请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🚨 错误详情: {error_data}")
            except:
                print(f"🚨 错误内容: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        print(f"⏰ 请求超时")
        return {"error": "请求超时"}
    except requests.exceptions.ConnectionError:
        print(f"🔌 连接错误")
        return {"error": "连接错误"}
    except Exception as e:
        print(f"💥 异常: {str(e)}")
        return {"error": str(e)}

def main():
    """主测试函数"""
    print("🚀 开始测试Google Trends API")
    print("=" * 50)
    
    # 测试1: 检查服务状态
    print("\n📋 测试1: 检查服务状态")
    status_result = test_api_endpoint("/api/google-trends/status")
    
    # 测试2: 快速功能测试
    print("\n📋 测试2: 快速功能测试")
    quick_test_result = test_api_endpoint("/api/google-trends/quick-test")
    
    # 测试3: 获取热门搜索
    print("\n📋 测试3: 获取热门搜索（中国）")
    trending_cn_result = test_api_endpoint("/api/google-trends/trending-searches", {"geo": "CN"})
    
    print("\n📋 测试4: 获取热门搜索（美国）")
    trending_us_result = test_api_endpoint("/api/google-trends/trending-searches", {"geo": "US"})
    
    # 测试5: 获取关键词时间趋势
    print("\n📋 测试5: 获取关键词时间趋势")
    interest_result = test_api_endpoint("/api/google-trends/interest-over-time", {
        "keywords": "人工智能,机器学习",
        "timeframe": "today 3-m",
        "geo": "CN"
    })
    
    # 测试6: 获取地区分布
    print("\n📋 测试6: 获取地区分布")
    region_result = test_api_endpoint("/api/google-trends/interest-by-region", {
        "keywords": "人工智能",
        "timeframe": "today 3-m",
        "geo": "CN"
    })
    
    # 测试7: 获取相关查询
    print("\n📋 测试7: 获取相关查询")
    related_result = test_api_endpoint("/api/google-trends/related-queries", {
        "keywords": "人工智能",
        "timeframe": "today 3-m",
        "geo": "CN"
    })
    
    # 汇总测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    tests = [
        ("服务状态检查", status_result),
        ("快速功能测试", quick_test_result),
        ("热门搜索(CN)", trending_cn_result),
        ("热门搜索(US)", trending_us_result),
        ("时间趋势", interest_result),
        ("地区分布", region_result),
        ("相关查询", related_result)
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for test_name, result in tests:
        if 'error' not in result and result.get('status') == 'success':
            print(f"✅ {test_name}: 成功")
            success_count += 1
        else:
            print(f"❌ {test_name}: 失败")
    
    print(f"\n🎯 总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！Google Trends API工作正常")
    elif success_count > 0:
        print("⚠️ 部分测试通过，请检查失败的测试项")
    else:
        print("🚨 所有测试失败，请检查服务配置")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 测试过程中发生异常: {e}")
        exit(1)