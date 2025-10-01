#!/usr/bin/env python3
"""
同步API测试脚本 - 验证趋势分析功能
"""
import requests
import json
import sys

def test_sync_analysis():
    print("🔍 测试同步趋势分析功能...")
    
    try:
        # 发起同步分析请求
        print("\n1️⃣ 发起同步分析请求...")
        # 修复URL，移除多余的/analyze部分
        url = 'http://localhost:8001/api/v1/trends'
        data = {'keywords': ['Vision Pro']}
        
        print(f"请求URL: {url}")
        print(f"请求数据: {data}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
        
        result = response.json()
        print(f"✅ 分析完成！")
        
        # 显示结果摘要
        print("\n📈 结果摘要:")
        print(f"   状态: {result.get('status', 'N/A')}")
        print(f"   消息: {result.get('message', 'N/A')}")
        
        analysis_result = result.get('result', {})
        if analysis_result:
            print(f"   热度指数: {analysis_result.get('hypeIndex', {}).get('score', 'N/A')}")
            print(f"   核心主题: {len(analysis_result.get('keyThemes', []))} 个")
            print(f"   商业机会: {len(analysis_result.get('actionableOpportunities', []))} 个")
            print(f"   热门帖子: {len(analysis_result.get('top_mentions', []))} 条")
            
            # 显示情感分布
            sentiment = analysis_result.get('sentimentSpectrum', {})
            if sentiment:
                print(f"   情感分布: 积极{sentiment.get('positive', 0)}% | 中性{sentiment.get('neutral', 0)}% | 消极{sentiment.get('negative', 0)}%")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://localhost:8001)")
        print("请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_batch_analysis():
    print("\n🔍 测试批量分析功能...")
    
    try:
        url = 'http://localhost:8001/api/v1/trends/batch'
        data = {
            'keywords_groups': [
                ['Vision Pro'],
                ['机器学习']
            ]
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量分析完成！处理了 {len(result.get('results', []))} 个请求")
            return True
        else:
            print(f"❌ 批量分析失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 批量测试异常: {e}")
        return False

def test_cache_stats():
    print("\n🔍 测试缓存统计...")
    
    try:
        url = 'http://localhost:8001/api/v1/trends/cache/stats'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 缓存统计获取成功")
            print(f"   内存缓存: {stats.get('memory_cache', {}).get('size', 0)} 条")
            print(f"   Redis缓存: {stats.get('redis_cache', {}).get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ 缓存统计失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 缓存测试异常: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 社交媒体趋势分析 - 同步API测试")
    print("=" * 60)
    
    # 测试同步分析
    sync_success = test_sync_analysis()
    
    # 测试批量分析
    batch_success = test_batch_analysis()
    
    # 测试缓存统计
    cache_success = test_cache_stats()
    
    print("\n" + "=" * 60)
    if sync_success and batch_success and cache_success:
        print("🎉 所有测试通过！")
    else:
        print("❌ 部分测试失败！需要检查系统状态")
        print("\n🔧 建议检查:")
        print("1. Redis服务是否在端口6380运行")
        print("2. 后端服务是否正常启动")
        print("3. 数据集是否包含测试关键词")
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())