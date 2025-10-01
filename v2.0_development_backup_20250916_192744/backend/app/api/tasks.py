"""
Task status API endpoints
"""
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from ..worker import celery_app
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/{task_id}")
def get_task_status(task_id: str):
    """
    获取任务状态 - 支持 Celery 和直接执行两种模式
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态和结果
    """
    try:
        # 首先尝试从 Redis 中查找直接执行模式的结果
        try:
            import redis
            import json
            redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
            direct_result = redis_client.get(f"task_result:{task_id}")
            if direct_result:
                result_data = json.loads(direct_result)
                logger.info(f"找到直接执行模式结果: {task_id}")
                return {
                    "status": result_data["status"],
                    "result": result_data.get("result"),
                    "progress": 100 if result_data["status"] == "SUCCESS" else 0
                }
        except Exception as redis_error:
            logger.debug(f"Redis 查询失败，尝试 Celery: {redis_error}")
        
        # 如果 Redis 中没有找到，尝试 Celery 任务
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            if task_result.successful():
                # 任务成功完成
                return {
                    "status": "SUCCESS",
                    "result": task_result.get(),
                    "progress": 100
                }
            else:
                # 任务失败
                return {
                    "status": "FAILURE", 
                    "error": str(task_result.info),
                    "progress": 0
                }
        else:
            # 任务还在进行中
            if task_result.state == 'PROGRESS':
                return {
                    "status": "PROGRESS",
                    "info": task_result.info,
                    "progress": task_result.info.get('progress', 0) if task_result.info else 0
                }
            else:
                return {
                    "status": "PENDING",
                    "progress": 0
                }
                
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.delete("/{task_id}")
def cancel_task(task_id: str):
    """
    取消任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        取消结果
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"任务 {task_id} 已取消"}
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")