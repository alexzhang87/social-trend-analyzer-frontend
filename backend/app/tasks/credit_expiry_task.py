# 积分过期清理定时任务

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..data.models.database import get_db
from ..services.credit_expiry_service import credit_expiry_service
from ..core.redis_client import redis_client

logger = logging.getLogger(__name__)

class CreditExpiryTask:
    """积分过期清理任务"""
    
    def __init__(self):
        self.task_name = "credit_expiry_cleanup"
        self.lock_key = f"task_lock:{self.task_name}"
        self.lock_timeout = 3600  # 1小时锁定时间
        self.last_run_key = f"task_last_run:{self.task_name}"
    
    async def acquire_lock(self) -> bool:
        """获取任务锁，防止重复执行"""
        try:
            # 使用Redis SET NX EX 命令获取锁
            result = redis_client.set(
                self.lock_key, 
                datetime.utcnow().isoformat(), 
                nx=True, 
                ex=self.lock_timeout
            )
            return result is not None
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return False
    
    def release_lock(self):
        """释放任务锁"""
        try:
            redis_client.delete(self.lock_key)
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
    
    def should_run(self) -> bool:
        """检查是否应该运行任务（每天运行一次）"""
        try:
            last_run_str = redis_client.get(self.last_run_key)
            if last_run_str is None:
                return True
            
            last_run = datetime.fromisoformat(last_run_str.decode())
            now = datetime.utcnow()
            
            # 如果距离上次运行超过23小时，则可以运行
            return (now - last_run) > timedelta(hours=23)
        except Exception as e:
            logger.error(f"Error checking last run time: {e}")
            return True
    
    def update_last_run(self):
        """更新最后运行时间"""
        try:
            redis_client.set(
                self.last_run_key, 
                datetime.utcnow().isoformat(),
                ex=86400 * 7  # 保存7天
            )
        except Exception as e:
            logger.error(f"Failed to update last run time: {e}")
    
    async def run_cleanup(self):
        """执行积分过期清理"""
        if not self.should_run():
            logger.info("Credit expiry cleanup skipped - already ran recently")
            return
        
        if not await self.acquire_lock():
            logger.info("Credit expiry cleanup skipped - another instance is running")
            return
        
        try:
            logger.info("Starting credit expiry cleanup task")
            
            # 获取数据库会话
            db = next(get_db())
            
            try:
                # 执行过期清理
                result = credit_expiry_service.expire_credits(db)
                
                # 更新最后运行时间
                self.update_last_run()
                
                logger.info(f"Credit expiry cleanup completed: {result}")
                
                # 发送通知（如果有过期积分）
                if result["expired_transactions"] > 0:
                    await self.send_expiry_notifications(result, db)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Credit expiry cleanup failed: {e}")
        finally:
            self.release_lock()
    
    async def send_expiry_notifications(self, result: dict, db: Session):
        """发送过期通知（可以扩展为邮件、短信等）"""
        try:
            # 这里可以实现发送邮件通知用户积分过期
            # 目前只记录日志
            logger.info(f"Would send expiry notifications for {result['affected_users']} users")
            
            # 可以在这里添加邮件发送逻辑
            # await email_service.send_credit_expiry_notification(affected_users)
            
        except Exception as e:
            logger.error(f"Failed to send expiry notifications: {e}")
    
    async def run_periodic_cleanup(self, interval_hours: int = 24):
        """定期运行清理任务"""
        while True:
            try:
                await self.run_cleanup()
                
                # 等待指定时间间隔
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
                # 出错时等待1小时后重试
                await asyncio.sleep(3600)

# 全局任务实例
credit_expiry_task = CreditExpiryTask()

# 启动定时任务的函数
async def start_credit_expiry_scheduler():
    """启动积分过期清理调度器"""
    logger.info("Starting credit expiry scheduler")
    task = asyncio.create_task(credit_expiry_task.run_periodic_cleanup())
    return task