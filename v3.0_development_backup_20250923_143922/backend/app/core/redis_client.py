import redis
import json
import logging
from typing import Any, Optional, Union
from ..core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """连接到Redis服务器"""
        try:
            # 从环境变量获取Redis配置
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            
            if redis_url.startswith('redis://'):
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            else:
                # 如果不是完整URL，使用默认配置
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    decode_responses=True
                )
            
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将使用内存缓存")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """检查Redis是否连接"""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.is_connected():
            return False
        
        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)
            
            if expire:
                return self.redis_client.setex(key, expire, value)
            else:
                return self.redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.is_connected():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis检查存在失败: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis设置过期时间失败: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        if not self.is_connected():
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis获取TTL失败: {e}")
            return -1
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有键"""
        if not self.is_connected():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis清除模式失败: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """获取Redis统计信息"""
        if not self.is_connected():
            return {"connected": False, "error": "Redis未连接"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get('used_memory_human', 'N/A'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Redis获取统计信息失败: {e}")
            return {"connected": False, "error": str(e)}

# 全局Redis客户端实例
redis_client = RedisClient()