#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cache_service import cache_service
from app.core.redis_client import redis_client
import time
import json

def test_cache_basic():
    """测试基础缓存功能"""
    print("\n" + "="*50)
    print("测试基础缓存功能")
    print("="*50)
    
    # 测试Redis连接
    print("\n=== 测试Redis连接 ===")
    is_connected = redis_client.is_connected()
    print(f"Redis连接状态: {is_connected}")
    
    if is_connected:
        print("✅ Redis连接成功")
    else:
        print("⚠️ Redis未连接，将使用内存缓存")
    
    # 测试缓存设置和获取
    print("\n=== 测试缓存设置和获取 ===")
    test_key = "test_cache_key"
    test_value = {"message": "这是一个测试值", "timestamp": time.time()}
    
    # 设置缓存
    set_result = cache_service.set(test_key, test_value, 300)  # 5分钟过期
    print(f"设置缓存结果: {set_result}")
    
    # 获取缓存
    cached_value = cache_service.get(test_key)
    print(f"获取缓存结果: {cached_value}")
    
    if cached_value == test_value:
        print("✅ 缓存读写测试通过")
    else:
        print("❌ 缓存读写测试失败")
    
    # 测试缓存统计
    print("\n=== 测试缓存统计 ===")
    stats = cache_service.get_stats()
    print(f"缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 测试缓存删除
    print("\n=== 测试缓存删除 ===")
    delete_result = cache_service.delete(test_key)
    print(f"删除缓存结果: {delete_result}")
    
    # 验证删除
    cached_value_after_delete = cache_service.get(test_key)
    if cached_value_after_delete is None:
        print("✅ 缓存删除测试通过")
    else:
        print("❌ 缓存删除测试失败")
    
    print("\n" + "="*50)
    print("基础缓存功能测试完成")
    print("="*50)

def test_cache_decorator():
    """测试缓存装饰器"""
    print("\n" + "="*50)
    print("测试缓存装饰器")
    print("="*50)
    
    from app.services.cache_service import cached
    
    @cached(ttl=60, key_prefix="test_func")
    def expensive_function(param1, param2):
        """模拟耗时函数"""
        print(f"执行耗时函数: param1={param1}, param2={param2}")
        time.sleep(0.1)  # 模拟耗时操作
        return {"result": param1 + param2, "timestamp": time.time()}
    
    # 第一次调用
    print("\n=== 第一次调用（应该执行函数） ===")
    start_time = time.time()
    result1 = expensive_function("hello", "world")
    first_call_time = time.time() - start_time
    print(f"第一次调用结果: {result1}")
    print(f"第一次调用耗时: {first_call_time:.3f}秒")
    
    # 第二次调用（应该从缓存获取）
    print("\n=== 第二次调用（应该从缓存获取） ===")
    start_time = time.time()
    result2 = expensive_function("hello", "world")
    second_call_time = time.time() - start_time
    print(f"第二次调用结果: {result2}")
    print(f"第二次调用耗时: {second_call_time:.3f}秒")
    
    if result1 == result2 and second_call_time < first_call_time:
        print("✅ 缓存装饰器测试通过")
    else:
        print("❌ 缓存装饰器测试失败")
    
    print("\n" + "="*50)
    print("缓存装饰器测试完成")
    print("="*50)

if __name__ == "__main__":
    try:
        test_cache_basic()
        test_cache_decorator()
        print("\n🎉 所有缓存测试完成！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()