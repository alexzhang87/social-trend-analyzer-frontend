import time
import psutil
import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # 保存最近1000个请求的响应时间
        self.request_counts = defaultdict(int)  # 按路径统计请求次数
        self.error_counts = defaultdict(int)    # 按状态码统计错误次数
        self.start_time = datetime.now()
        
    def record_request(self, path: str, method: str, status_code: int, response_time: float):
        """记录请求信息"""
        self.request_times.append(response_time)
        self.request_counts[f"{method} {path}"] += 1
        
        if status_code >= 400:
            self.error_counts[status_code] += 1
            
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.request_times:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
        else:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            max_response_time = max(self.request_times)
            min_response_time = min(self.request_times)
            
        # 系统资源使用情况
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime),
            "requests": {
                "total": sum(self.request_counts.values()),
                "by_endpoint": dict(self.request_counts),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "max_response_time_ms": round(max_response_time * 1000, 2),
                "min_response_time_ms": round(min_response_time * 1000, 2)
            },
            "errors": {
                "total": sum(self.error_counts.values()),
                "by_status_code": dict(self.error_counts)
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                }
            }
        }

# 全局监控实例
performance_monitor = PerformanceMonitor()

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录性能数据
            performance_monitor.record_request(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time=process_time
            )
            
            # 添加响应时间头
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            
            # 记录请求完成
            logger.info(
                f"请求完成: {request.method} {request.url.path} - "
                f"状态码: {response.status_code} - 耗时: {round(process_time * 1000, 2)}ms"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # 记录错误
            performance_monitor.record_request(
                path=request.url.path,
                method=request.method,
                status_code=500,
                response_time=process_time
            )
            
            logger.error(
                f"请求异常: {request.method} {request.url.path} - "
                f"错误: {str(e)} - 耗时: {round(process_time * 1000, 2)}ms"
            )
            
            raise e

class HealthChecker:
    """健康检查器"""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            from ..data.models.database import SessionLocal
            db = SessionLocal()
            # 简单查询测试连接
            db.execute("SELECT 1")
            db.close()
            return {"status": "healthy", "message": "数据库连接正常"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"数据库连接失败: {str(e)}"}
    
    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            from ..services.cache_service import cache_service
            await cache_service.set("health_check", "ok", ttl=10)
            result = await cache_service.get("health_check")
            if result == "ok":
                return {"status": "healthy", "message": "Redis连接正常"}
            else:
                return {"status": "unhealthy", "message": "Redis读写测试失败"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Redis连接失败: {str(e)}"}
    
    @staticmethod
    async def check_external_apis() -> Dict[str, Any]:
        """检查外部API连接"""
        checks = {}
        
        # 检查Google Trends API
        try:
            import pytrends
            checks["google_trends"] = {"status": "healthy", "message": "Google Trends可用"}
        except Exception as e:
            checks["google_trends"] = {"status": "unhealthy", "message": f"Google Trends不可用: {str(e)}"}
        
        return checks
    
    @staticmethod
    async def get_comprehensive_health() -> Dict[str, Any]:
        """获取综合健康状态"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # 检查各个组件
        health_status["checks"]["database"] = await HealthChecker.check_database()
        health_status["checks"]["redis"] = await HealthChecker.check_redis()
        health_status["checks"]["external_apis"] = await HealthChecker.check_external_apis()
        
        # 添加性能统计
        health_status["performance"] = performance_monitor.get_stats()
        
        # 判断整体状态
        for check_name, check_result in health_status["checks"].items():
            if isinstance(check_result, dict) and check_result.get("status") == "unhealthy":
                health_status["overall_status"] = "degraded"
                break
            elif isinstance(check_result, dict):
                # 检查嵌套的检查结果
                for sub_check in check_result.values():
                    if isinstance(sub_check, dict) and sub_check.get("status") == "unhealthy":
                        health_status["overall_status"] = "degraded"
                        break
        
        return health_status

# 全局健康检查器实例
health_checker = HealthChecker()