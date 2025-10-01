from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import logging
from ..data.models.database import User
from ..core.auth import get_current_active_user, require_admin_user
from ..services.cache_optimization import cache_optimizer
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cache-optimization", tags=["缓存优化"])

@router.get("/health")
def cache_optimization_health() -> Dict[str, Any]:
    """缓存优化服务健康检查"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "cache-optimization",
        "timestamp": datetime.now().isoformat(),
        "message": "缓存优化服务运行正常"
    }

@router.get("/metrics")
def get_basic_metrics() -> Dict[str, Any]:
    """获取基础性能指标（无需认证）"""
    from datetime import datetime
    try:
        # 获取Redis基础信息
        from ..core.redis_client import redis_client
        info = redis_client.info()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "redis_info": {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
        }
    except Exception as e:
        logger.error(f"获取性能指标失败: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

class CachePrewarmRequest(BaseModel):
    user_ids: List[int] = []
    include_popular_trends: bool = True

class BatchCacheItem(BaseModel):
    key: str
    value: Any
    ttl: int = 3600

class BatchCacheRequest(BaseModel):
    items: List[BatchCacheItem]

@router.post("/prewarm")
async def prewarm_cache(
    request: CachePrewarmRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """缓存预热（仅管理员）"""
    try:
        results = {}
        
        # 预热用户缓存
        if request.user_ids:
            user_results = {}
            for user_id in request.user_ids[:10]:  # 限制最多10个用户
                user_result = await cache_optimizer.prewarm_user_cache(user_id)
                user_results[f"user_{user_id}"] = user_result
            results['users'] = user_results
        
        # 预热热门趋势
        if request.include_popular_trends:
            trends_result = await cache_optimizer.prewarm_popular_trends()
            results['popular_trends'] = trends_result
        
        logger.info(f"管理员 {current_user.email} 执行了缓存预热")
        
        return {
            "success": True,
            "message": "缓存预热完成",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"缓存预热失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")

@router.post("/batch-set")
def batch_set_cache(
    request: BatchCacheRequest,
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """批量设置缓存（仅管理员）"""
    try:
        if len(request.items) > 100:
            raise HTTPException(status_code=400, detail="批量操作最多支持100个项目")
        
        cache_items = [item.dict() for item in request.items]
        result = cache_optimizer.batch_set_cache(cache_items)
        
        logger.info(f"管理员 {current_user.email} 执行了批量缓存设置: {len(request.items)} 个项目")
        
        return {
            "success": True,
            "message": "批量缓存设置完成",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"批量缓存设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量缓存设置失败: {str(e)}")

@router.post("/batch-get")
def batch_get_cache(
    keys: List[str],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """批量获取缓存"""
    try:
        if len(keys) > 50:
            raise HTTPException(status_code=400, detail="批量获取最多支持50个键")
        
        result = cache_optimizer.batch_get_cache(keys)
        
        return {
            "success": True,
            "message": "批量缓存获取完成",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"批量缓存获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量缓存获取失败: {str(e)}")

@router.post("/cleanup")
def intelligent_cleanup(
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """智能缓存清理（仅管理员）"""
    try:
        result = cache_optimizer.intelligent_cache_cleanup()
        
        logger.info(f"管理员 {current_user.email} 执行了智能缓存清理")
        
        return {
            "success": True,
            "message": "智能缓存清理完成",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"智能缓存清理失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能缓存清理失败: {str(e)}")

@router.get("/health-report")
def get_cache_health_report(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取缓存健康报告"""
    try:
        report = cache_optimizer.get_cache_health_report()
        
        return {
            "success": True,
            "message": "缓存健康报告生成成功",
            "data": report
        }
        
    except Exception as e:
        logger.error(f"缓存健康报告生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓存健康报告生成失败: {str(e)}")

@router.get("/performance-metrics")
def get_performance_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取缓存性能指标"""
    try:
        from ..services.cache_service import cache_service
        
        # 获取基础统计
        stats = cache_service.get_stats()
        
        # 计算性能指标
        redis_stats = stats.get('redis', {})
        hits = redis_stats.get('keyspace_hits', 0)
        misses = redis_stats.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        metrics = {
            'cache_hit_rate': (hits / total_requests * 100) if total_requests > 0 else 0,
            'total_cache_requests': total_requests,
            'redis_memory_usage': redis_stats.get('used_memory', 'N/A'),
            'redis_connected_clients': redis_stats.get('connected_clients', 0),
            'memory_cache_size': stats.get('memory_cache', {}).get('keys_count', 0),
            'prewarmed_keys_count': len(cache_optimizer.prewarmed_keys)
        }
        
        return {
            "success": True,
            "message": "性能指标获取成功",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"性能指标获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"性能指标获取失败: {str(e)}")

@router.post("/auto-optimize")
async def auto_optimize_cache(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin_user)
) -> Dict[str, Any]:
    """自动缓存优化（仅管理员）"""
    try:
        # 在后台执行优化任务
        background_tasks.add_task(_perform_auto_optimization)
        
        logger.info(f"管理员 {current_user.email} 启动了自动缓存优化")
        
        return {
            "success": True,
            "message": "自动缓存优化已启动，将在后台执行",
            "data": {
                "status": "started",
                "estimated_duration": "1-2分钟"
            }
        }
        
    except Exception as e:
        logger.error(f"自动缓存优化启动失败: {e}")
        raise HTTPException(status_code=500, detail=f"自动缓存优化启动失败: {str(e)}")

async def _perform_auto_optimization():
    """执行自动优化任务"""
    try:
        logger.info("开始执行自动缓存优化")
        
        # 1. 智能清理
        cleanup_result = cache_optimizer.intelligent_cache_cleanup()
        logger.info(f"清理完成: {cleanup_result}")
        
        # 2. 预热热门趋势
        trends_result = await cache_optimizer.prewarm_popular_trends()
        logger.info(f"趋势预热完成: {trends_result}")
        
        # 3. 获取健康报告
        health_report = cache_optimizer.get_cache_health_report()
        logger.info(f"健康检查完成，评分: {health_report.get('health_score', 'N/A')}")
        
        logger.info("自动缓存优化完成")
        
    except Exception as e:
        logger.error(f"自动缓存优化执行失败: {e}")