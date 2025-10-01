#!/usr/bin/env python3
"""
Redis连接测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.redis_client import redis_client
from app.services.cache_service import cache_service
import json

def test_redis_connection():
    """测试Redis连接"""
    print("🔧 测试Redis连接...")
    
    # 测试Redis客户端连接
    if redis_client.is_connected():
        print("✅ Redis客户端连接成功")
        
        # 测试基本操作
        test_key = "test:connection"
        test_value = {"message": "Hello Redis!", "timestamp": "2025-09-28"}
        
        # 设置值
        success = redis_client.set(test_key, test_value, 60)
        if success:
            print("✅ Redis设置值成功")
            
            # 获取值
            retrieved_value = redis_client.get(test_key)
            if retrieved_value:
                print(f"✅ Redis获取值成功: {retrieved_value}")
                
                # 删除测试键
                redis_client.delete(test_key)
                print("✅ Redis删除值成功")
            else:
                print("❌ Redis获取值失败")
        else:
            print("❌ Redis设置值失败")
    else:
        print("❌ Redis客户端连接失败")

def test_cache_service():
    """测试缓存服务"""
    print("\n🔧 测试缓存服务...")
    
    test_key = "test:cache_service"
    test_data = {
        "user_id": 123,
        "analysis_result": {
            "sentiment": "positive",
            "score": 0.85,
            "keywords": ["AI", "technology", "innovation"]
        }
    }
    
    # 设置缓存
    success = cache_service.set(test_key, test_data, 300)
    if success:
        print("✅ 缓存服务设置成功")
        
        # 获取缓存
        cached_data = cache_service.get(test_key)
        if cached_data:
            print(f"✅ 缓存服务获取成功: {json.dumps(cached_data, indent=2, ensure_ascii=False)}")
            
            # 清除缓存
            cache_service.delete(test_key)
            print("✅ 缓存服务删除成功")
        else:
            print("❌ 缓存服务获取失败")
    else:
        print("❌ 缓存服务设置失败")

def test_redis_info():
    """获取Redis信息"""
    print("\n📊 Redis服务器信息:")
    
    if redis_client.is_connected():
        try:
            # 获取Redis信息
            info = redis_client.redis_client.info()
            print(f"Redis版本: {info.get('redis_version', 'Unknown')}")
            print(f"运行模式: {info.get('redis_mode', 'Unknown')}")
            print(f"已用内存: {info.get('used_memory_human', 'Unknown')}")
            print(f"连接数: {info.get('connected_clients', 'Unknown')}")
            print(f"运行时间: {info.get('uptime_in_seconds', 'Unknown')} 秒")
        except Exception as e:
            print(f"❌ 获取Redis信息失败: {e}")
    else:
        print("❌ Redis未连接，无法获取信息")

if __name__ == "__main__":
    print("🚀 开始Redis缓存系统测试")
    print("=" * 50)
    
    test_redis_connection()
    test_cache_service()
    test_redis_info()
    
    print("\n" + "=" * 50)
    print("✅ Redis缓存系统测试完成")