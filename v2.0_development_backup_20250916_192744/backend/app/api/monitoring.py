from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..core.monitoring import performance_monitor, health_checker
from ..core.auth import get_current_user
from ..data.models.database import User, UserRole

router = APIRouter()

@router.get("/health", summary="系统健康检查")
async def get_health_status():
    """获取系统健康状态"""
    try:
        health_status = await health_checker.get_comprehensive_health()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.get("/health/simple", summary="简单健康检查")
async def get_simple_health():
    """简单的健康检查，用于负载均衡器"""
    return {"status": "ok", "timestamp": performance_monitor.start_time.isoformat()}

@router.get("/metrics", summary="性能指标")
async def get_performance_metrics(current_user: User = Depends(get_current_user)):
    """获取性能指标（需要登录）"""
    try:
        stats = performance_monitor.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")

@router.get("/metrics/admin", summary="管理员性能指标")
async def get_admin_metrics(current_user: User = Depends(get_current_user)):
    """获取详细的管理员性能指标"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        stats = performance_monitor.get_stats()
        
        # 添加更详细的管理员信息
        admin_stats = {
            **stats,
            "detailed_requests": {
                "recent_response_times": list(performance_monitor.request_times)[-50:],  # 最近50个请求的响应时间
                "request_distribution": dict(performance_monitor.request_counts),
                "error_distribution": dict(performance_monitor.error_counts)
            }
        }
        
        return {
            "success": True,
            "data": admin_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取管理员指标失败: {str(e)}")

@router.get("/database/health", summary="数据库健康检查")
async def check_database_health():
    """检查数据库健康状态"""
    try:
        result = await health_checker.check_database()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库健康检查失败: {str(e)}")

@router.get("/redis/health", summary="Redis健康检查")
async def check_redis_health():
    """检查Redis健康状态"""
    try:
        result = await health_checker.check_redis()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis健康检查失败: {str(e)}")

@router.post("/reset-stats", summary="重置统计数据")
async def reset_performance_stats(current_user: User = Depends(get_current_user)):
    """重置性能统计数据（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        # 清空统计数据
        performance_monitor.request_times.clear()
        performance_monitor.request_counts.clear()
        performance_monitor.error_counts.clear()
        
        return {
            "success": True,
            "message": "性能统计数据已重置"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置统计数据失败: {str(e)}")

@router.get("/alerts", summary="系统告警")
async def get_system_alerts(current_user: User = Depends(get_current_user)):
    """获取系统告警信息"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        stats = performance_monitor.get_stats()
        alerts = []
        
        # 检查各种告警条件
        if stats["system"]["cpu_percent"] > 80:
            alerts.append({
                "level": "warning",
                "type": "high_cpu",
                "message": f"CPU使用率过高: {stats['system']['cpu_percent']}%",
                "value": stats["system"]["cpu_percent"]
            })
        
        if stats["system"]["memory"]["used_percent"] > 85:
            alerts.append({
                "level": "warning",
                "type": "high_memory",
                "message": f"内存使用率过高: {stats['system']['memory']['used_percent']}%",
                "value": stats["system"]["memory"]["used_percent"]
            })
        
        if stats["system"]["disk"]["used_percent"] > 90:
            alerts.append({
                "level": "critical",
                "type": "high_disk",
                "message": f"磁盘使用率过高: {stats['system']['disk']['used_percent']}%",
                "value": stats["system"]["disk"]["used_percent"]
            })
        
        if stats["requests"]["avg_response_time_ms"] > 1000:
            alerts.append({
                "level": "warning",
                "type": "slow_response",
                "message": f"平均响应时间过长: {stats['requests']['avg_response_time_ms']}ms",
                "value": stats["requests"]["avg_response_time_ms"]
            })
        
        error_rate = 0
        if stats["requests"]["total"] > 0:
            error_rate = (stats["errors"]["total"] / stats["requests"]["total"]) * 100
        
        if error_rate > 5:  # 错误率超过5%
            alerts.append({
                "level": "critical",
                "type": "high_error_rate",
                "message": f"错误率过高: {error_rate:.2f}%",
                "value": error_rate
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "alert_count": len(alerts),
                "critical_count": len([a for a in alerts if a["level"] == "critical"]),
                "warning_count": len([a for a in alerts if a["level"] == "warning"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统告警失败: {str(e)}")