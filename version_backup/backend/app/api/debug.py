from fastapi import APIRouter, BackgroundTasks
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def simple_background_task(message: str):
    """一个非常简单的后台任务，用于测试。"""
    logger.info(f"后台任务已启动，消息: '{message}'")
    time.sleep(5)
    logger.info("✅ 后台任务已完成。")

@router.post("/test-bg-task")
async def test_background_task(background_tasks: BackgroundTasks):
    """
    这个端点用于测试 BackgroundTasks 是否能正常工作。
    它应该会立即返回响应，而不会等待5秒。
    """
    logger.info("收到 /test-bg-task 请求")
    background_tasks.add_task(simple_background_task, "你好，后台！")
    logger.info("正在返回 /test-bg-task 的响应")
    return {"message": "后台任务已成功启动。"}