"""
Celery worker configuration for async task processing
"""
import os
import platform
from celery import Celery
from celery.signals import worker_ready
from .core.config import settings

# 为Windows环境下的Celery添加特殊配置
if platform.system() == "Windows":
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

# 关键补充：为结果后端设置额外参数，以实现更可靠的状态查询
celery_app.conf.update(
    result_extended=True,
    task_track_started=True,
    worker_prefetch_multiplier=4,
    result_expires=1800,  # 30分钟
    task_time_limit=300,  # 5分钟任务超时
    task_soft_time_limit=240,  # 4分钟软超时
    worker_max_tasks_per_child=1000, # 每个worker子进程最大任务数
    # 新增：配置Broker连接选项，启用TCP Keepalive以保持连接稳定
    broker_transport_options={
        'socket_keepalive': True,
    }
)

@worker_ready.connect
def at_start(sender, **k):
    """
    Signal handler for when the worker is ready.
    """
    print(f"Celery worker ready on {platform.system()}!")
    print(f"Broker: {settings.CELERY_BROKER_URL}")
    print(f"Result Backend: {settings.CELERY_RESULT_BACKEND}")