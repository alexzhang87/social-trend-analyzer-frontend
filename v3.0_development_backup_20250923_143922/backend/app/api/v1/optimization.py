from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import logging
from ...services.data_optimization_service import data_optimization_service
from ...core.auth import get_current_user_optional

logger = logging.getLogger("trend-analyzer")

router = APIRouter(prefix="/optimization", tags=["数据优化"])

# 请求模型
class BatchJobRequest(BaseModel):
    job_type: str
    job_data: dict
    priority: int = 1

class CacheInvalidateRequest(BaseModel):
    cache_type: str
    pattern: Optional[str] = None

# 缓存相关端点
@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        stats = await data_optimization_service.get_optimization_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")

@router.delete("/cache/invalidate")
async def invalidate_cache(request: CacheInvalidateRequest, current_user = Depends(get_current_user_optional)):
    """清除缓存"""
    try:
        deleted_count = await data_optimization_service.cache_service.invalidate_cache(
            request.cache_type, request.pattern
        )
        return {
            "success": True,
            "message": f"已清除 {deleted_count} 个缓存项",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")

# 批处理相关端点
@router.post("/batch/jobs")
async def create_batch_job(request: BatchJobRequest, background_tasks: BackgroundTasks):
    """创建批处理任务"""
    try:
        job_id = str(uuid.uuid4())
        
        # 验证任务类型
        valid_job_types = ["bulk_analysis", "data_export", "trend_calculation", "sentiment_batch"]
        if request.job_type not in valid_job_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的任务类型。支持的类型: {', '.join(valid_job_types)}"
            )
        
        # 添加批处理任务
        success = await data_optimization_service.batch_service.add_batch_job(
            job_id, request.job_type, request.job_data, request.priority
        )
        
        if success:
            return {
                "success": True,
                "job_id": job_id,
                "message": "批处理任务已创建",
                "job_type": request.job_type
            }
        else:
            raise HTTPException(status_code=500, detail="创建批处理任务失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建批处理任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建批处理任务失败: {str(e)}")

@router.get("/batch/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """获取批处理任务状态"""
    try:
        status = await data_optimization_service.batch_service.get_job_status(job_id)
        
        if status:
            return {"success": True, "data": status}
        else:
            raise HTTPException(status_code=404, detail="任务不存在或已完成")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.delete("/batch/jobs/{job_id}")
async def cancel_job(job_id: str, current_user = Depends(get_current_user_optional)):
    """取消批处理任务"""
    try:
        success = await data_optimization_service.batch_service.cancel_job(job_id)
        
        if success:
            return {"success": True, "message": f"任务 {job_id} 已取消"}
        else:
            raise HTTPException(status_code=404, detail="任务不存在或无法取消")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")

@router.get("/batch/queue/status")
async def get_queue_status():
    """获取批处理队列状态"""
    try:
        stats = await data_optimization_service.get_optimization_stats()
        batch_stats = stats.get("batch_processing", {})
        
        return {
            "success": True,
            "data": {
                "active_jobs": batch_stats.get("active_jobs", 0),
                "queue_size": batch_stats.get("queue_size", 0),
                "performance_metrics": stats.get("performance", {})
            }
        }
    except Exception as e:
        logger.error(f"获取队列状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取队列状态失败: {str(e)}")

# 性能优化端点
@router.get("/performance/stats")
async def get_performance_stats():
    """获取性能统计信息"""
    try:
        stats = await data_optimization_service.get_optimization_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能统计失败: {str(e)}")

# 批处理任务模板
@router.get("/batch/templates")
async def get_batch_templates():
    """获取批处理任务模板"""
    templates = {
        "bulk_analysis": {
            "description": "批量关键词分析",
            "required_fields": ["keywords_list", "analysis_type"],
            "optional_fields": ["time_range", "platform_filter"],
            "example": {
                "keywords_list": [["AI", "人工智能"], ["区块链", "blockchain"]],
                "analysis_type": "sentiment",
                "time_range": "7d"
            }
        },
        "data_export": {
            "description": "数据导出",
            "required_fields": ["export_type", "filters"],
            "optional_fields": ["format_options"],
            "example": {
                "export_type": "csv",
                "filters": {
                    "keywords": ["AI"],
                    "time_range": "30d",
                    "limit": 5000
                }
            }
        },
        "trend_calculation": {
            "description": "趋势计算",
            "required_fields": ["keywords", "time_period"],
            "optional_fields": ["calculation_method"],
            "example": {
                "keywords": ["ChatGPT", "GPT-4"],
                "time_period": "30d",
                "calculation_method": "advanced"
            }
        },
        "sentiment_batch": {
            "description": "批量情感分析",
            "required_fields": ["texts"],
            "optional_fields": ["language", "model_type"],
            "example": {
                "texts": ["这个产品很棒！", "不太满意这个服务", "还可以，有待改进"],
                "language": "zh",
                "model_type": "advanced"
            }
        }
    }
    
    return {"success": True, "data": templates}

# 系统优化建议
@router.get("/recommendations")
async def get_optimization_recommendations():
    """获取系统优化建议"""
    try:
        stats = await data_optimization_service.get_optimization_stats()
        cache_stats = stats.get("cache", {})
        performance = stats.get("performance", {})
        
        recommendations = []
        
        # 缓存命中率建议
        cache_hits = performance.get("cache_hits", 0)
        cache_misses = performance.get("cache_misses", 0)
        total_requests = cache_hits + cache_misses
        
        if total_requests > 0:
            hit_rate = cache_hits / total_requests * 100
            if hit_rate < 50:
                recommendations.append({
                    "type": "cache",
                    "priority": "high",
                    "message": f"缓存命中率较低 ({hit_rate:.1f}%)，建议优化缓存策略",
                    "suggestion": "增加缓存TTL时间或优化缓存键生成策略"
                })
        
        # 批处理队列建议
        queue_size = stats.get("batch_processing", {}).get("queue_size", 0)
        if queue_size > 50:
            recommendations.append({
                "type": "batch_processing",
                "priority": "medium",
                "message": f"批处理队列积压较多 ({queue_size} 个任务)",
                "suggestion": "考虑增加处理线程数或优化任务处理逻辑"
            })
        
        # Redis内存使用建议
        if cache_stats.get("status") == "正常":
            used_memory = cache_stats.get("used_memory", "")
            if "MB" in used_memory and int(used_memory.replace("MB", "").strip()) > 100:
                recommendations.append({
                    "type": "memory",
                    "priority": "low",
                    "message": f"Redis内存使用量较高 ({used_memory})",
                    "suggestion": "定期清理过期缓存或调整缓存策略"
                })
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "generated_at": stats.get("timestamp")
            }
        }
        
    except Exception as e:
        logger.error(f"获取优化建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取优化建议失败: {str(e)}")