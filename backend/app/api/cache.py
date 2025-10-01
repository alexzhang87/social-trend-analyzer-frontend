from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from ..data.models.database import User, get_db
from ..core.auth import get_current_active_user, require_admin_user
from ..services.cache_service import cache_service, invalidate_user_cache, invalidate_trends_cache
from ..core.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
def get_cache_stats(
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """获取缓存统计信息（仅管理员）"""
    try:
        stats = cache_service.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取缓存统计失败")

@router.delete("/clear")
def clear_all_cache(
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """清除所有缓存（仅管理员）"""
    try:
        # 清除Redis缓存
        redis_cleared = 0
        if redis_client.is_connected():
            redis_cleared = redis_client.clear_pattern("*")
        
        # 清除内存缓存
        memory_cleared = len(cache_service.memory_cache)
        cache_service.memory_cache.clear()
        
        logger.info(f"管理员 {current_user.email} 清除了所有缓存")
        
        return {
            "success": True,
            "message": "所有缓存已清除",
            "data": {
                "redis_keys_cleared": redis_cleared,
                "memory_keys_cleared": memory_cleared
            }
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清除缓存失败")

@router.delete("/trends")
def clear_trends_cache(
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """清除趋势分析缓存（仅管理员）"""
    try:
        count = invalidate_trends_cache()
        
        logger.info(f"管理员 {current_user.email} 清除了趋势分析缓存")
        
        return {
            "success": True,
            "message": f"已清除 {count} 个趋势分析缓存项",
            "data": {
                "cleared_count": count
            }
        }
    except Exception as e:
        logger.error(f"清除趋势缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清除趋势缓存失败")

@router.delete("/user/{user_id}")
def clear_user_cache(
    user_id: int,
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """清除指定用户的缓存（仅管理员）"""
    try:
        count = invalidate_user_cache(user_id)
        
        logger.info(f"管理员 {current_user.email} 清除了用户 {user_id} 的缓存")
        
        return {
            "success": True,
            "message": f"已清除用户 {user_id} 的 {count} 个缓存项",
            "data": {
                "user_id": user_id,
                "cleared_count": count
            }
        }
    except Exception as e:
        logger.error(f"清除用户缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清除用户缓存失败")

@router.get("/health")
def check_cache_health(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """检查缓存系统健康状态"""
    try:
        redis_connected = redis_client.is_connected()
        
        # 测试缓存读写
        test_key = "health_check_test"
        test_value = "test_value"
        
        write_success = cache_service.set(test_key, test_value, 60)
        read_success = cache_service.get(test_key) == test_value
        
        # 清理测试数据
        cache_service.delete(test_key)
        
        return {
            "success": True,
            "data": {
                "redis_connected": redis_connected,
                "cache_write_test": write_success,
                "cache_read_test": read_success,
                "overall_health": redis_connected and write_success and read_success
            }
        }
    except Exception as e:
        logger.error(f"缓存健康检查失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "redis_connected": False,
                "cache_write_test": False,
                "cache_read_test": False,
                "overall_health": False
            }
        }