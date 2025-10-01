import hashlib
import json
import logging
from typing import Any, Optional, Callable, Dict
from functools import wraps
from ..core.redis_client import redis_client

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.default_ttl = 3600  # 默认1小时过期
        self.memory_cache = {}  # 内存缓存作为备用
        
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 创建一个包含所有参数的字符串
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        # 使用MD5哈希来创建固定长度的键
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # 首先尝试Redis
        if redis_client.is_connected():
            value = redis_client.get(key)
            if value is not None:
                logger.debug(f"Redis缓存命中: {key}")
                return value
        
        # 如果Redis不可用，使用内存缓存
        if key in self.memory_cache:
            logger.debug(f"内存缓存命中: {key}")
            return self.memory_cache[key]
        
        logger.debug(f"缓存未命中: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        success = False
        
        # 尝试设置Redis缓存
        if redis_client.is_connected():
            success = redis_client.set(key, value, ttl)
            if success:
                logger.debug(f"Redis缓存设置成功: {key}")
        
        # 同时设置内存缓存作为备用
        try:
            self.memory_cache[key] = value
            logger.debug(f"内存缓存设置成功: {key}")
            success = True
        except Exception as e:
            logger.error(f"内存缓存设置失败: {e}")
        
        return success
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        success = False
        
        # 删除Redis缓存
        if redis_client.is_connected():
            success = redis_client.delete(key)
        
        # 删除内存缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
            success = True
        
        return success
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        count = 0
        
        # 清除Redis缓存
        if redis_client.is_connected():
            count += redis_client.clear_pattern(pattern)
        
        # 清除内存缓存
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            count += 1
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        redis_stats = redis_client.get_stats()
        
        return {
            "redis": redis_stats,
            "memory_cache": {
                "keys_count": len(self.memory_cache),
                "keys": list(self.memory_cache.keys())[:10]  # 只显示前10个键
            }
        }

# 全局缓存服务实例
cache_service = CacheService()

def cached(ttl: int = 3600, key_prefix: str = "default"):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_service._generate_cache_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"缓存命中: {func.__name__}")
                return cached_result
            
            # 执行函数
            logger.info(f"缓存未命中，执行函数: {func.__name__}")
            result = func(*args, **kwargs)
            
            # 存储到缓存
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_key_for_user(user_id: int, operation: str, *args) -> str:
    """为用户操作生成缓存键"""
    return cache_service._generate_cache_key(f"user:{user_id}:{operation}", *args)

def cache_key_for_trends(keywords: list, platform: str = None, time_range: str = None) -> str:
    """为趋势分析生成缓存键"""
    return cache_service._generate_cache_key(
        "trends", 
        tuple(sorted(keywords)), 
        platform=platform, 
        time_range=time_range
    )

def invalidate_user_cache(user_id: int):
    """清除用户相关的所有缓存"""
    pattern = f"*user:{user_id}:*"
    count = cache_service.clear_pattern(pattern)
    logger.info(f"清除用户 {user_id} 的 {count} 个缓存项")
    return count

def invalidate_trends_cache():
    """清除所有趋势分析缓存"""
    pattern = "*trends:*"
    count = cache_service.clear_pattern(pattern)
    logger.info(f"清除 {count} 个趋势分析缓存项")
    return count