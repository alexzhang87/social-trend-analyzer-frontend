"""
速率限制服务
提供API速率限制、防止滥用和DDoS攻击
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)

class LimitType(Enum):
    """限制类型"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    BURST = "burst"

@dataclass
class RateLimit:
    """速率限制配置"""
    requests: int  # 允许的请求数
    window: int    # 时间窗口（秒）
    limit_type: LimitType
    
@dataclass
class LimitResult:
    """限制检查结果"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None

class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.request_history: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # 默认限制配置
        self.default_limits = {
            "global": [
                RateLimit(100, 60, LimitType.PER_MINUTE),    # 每分钟100请求
                RateLimit(1000, 3600, LimitType.PER_HOUR),   # 每小时1000请求
                RateLimit(10000, 86400, LimitType.PER_DAY),  # 每天10000请求
            ],
            "auth": [
                RateLimit(5, 60, LimitType.PER_MINUTE),      # 认证接口每分钟5次
                RateLimit(20, 3600, LimitType.PER_HOUR),     # 每小时20次
            ],
            "upload": [
                RateLimit(10, 60, LimitType.PER_MINUTE),     # 上传每分钟10次
                RateLimit(50, 3600, LimitType.PER_HOUR),     # 每小时50次
            ],
            "analysis": [
                RateLimit(30, 60, LimitType.PER_MINUTE),     # 分析接口每分钟30次
                RateLimit(200, 3600, LimitType.PER_HOUR),    # 每小时200次
            ]
        }
        
        # 订阅用户的限制倍数
        self.subscription_multipliers = {
            "free": 1.0,
            "basic": 2.0,
            "premium": 5.0,
            "enterprise": 10.0
        }
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """生成限制键"""
        return f"{identifier}:{endpoint}"
    
    def _clean_old_requests(self, key: str, window: int):
        """清理过期的请求记录"""
        current_time = time.time()
        cutoff_time = current_time - window
        
        while self.request_history[key] and self.request_history[key][0] < cutoff_time:
            self.request_history[key].popleft()
    
    def check_rate_limit(
        self, 
        identifier: str, 
        endpoint: str, 
        subscription_tier: str = "free"
    ) -> LimitResult:
        """检查速率限制"""
        try:
            # 检查IP是否被阻止
            if identifier in self.blocked_ips:
                if datetime.now() < self.blocked_ips[identifier]:
                    return LimitResult(
                        allowed=False,
                        remaining=0,
                        reset_time=self.blocked_ips[identifier],
                        retry_after=int((self.blocked_ips[identifier] - datetime.now()).total_seconds())
                    )
                else:
                    # 解除阻止
                    del self.blocked_ips[identifier]
            
            # 获取适用的限制
            limits = self._get_applicable_limits(endpoint)
            multiplier = self.subscription_multipliers.get(subscription_tier, 1.0)
            
            current_time = time.time()
            most_restrictive_result = None
            
            for limit in limits:
                key = self._get_key(identifier, f"{endpoint}:{limit.limit_type.value}")
                
                # 清理过期记录
                self._clean_old_requests(key, limit.window)
                
                # 计算当前请求数
                current_requests = len(self.request_history[key])
                adjusted_limit = int(limit.requests * multiplier)
                
                if current_requests >= adjusted_limit:
                    # 超出限制
                    reset_time = datetime.fromtimestamp(
                        self.request_history[key][0] + limit.window
                    )
                    
                    result = LimitResult(
                        allowed=False,
                        remaining=0,
                        reset_time=reset_time,
                        retry_after=int((reset_time - datetime.now()).total_seconds())
                    )
                    
                    if most_restrictive_result is None or result.retry_after < most_restrictive_result.retry_after:
                        most_restrictive_result = result
                
                else:
                    # 未超出限制，记录请求
                    self.request_history[key].append(current_time)
                    
                    if most_restrictive_result is None:
                        most_restrictive_result = LimitResult(
                            allowed=True,
                            remaining=adjusted_limit - current_requests - 1,
                            reset_time=datetime.fromtimestamp(current_time + limit.window)
                        )
            
            # 检查可疑活动
            if most_restrictive_result and not most_restrictive_result.allowed:
                self._track_suspicious_activity(identifier)
            
            return most_restrictive_result or LimitResult(
                allowed=True,
                remaining=999,
                reset_time=datetime.now() + timedelta(minutes=1)
            )
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # 出错时允许请求，但记录错误
            return LimitResult(
                allowed=True,
                remaining=0,
                reset_time=datetime.now() + timedelta(minutes=1)
            )
    
    def _get_applicable_limits(self, endpoint: str) -> List[RateLimit]:
        """获取适用的限制"""
        # 根据端点类型返回相应的限制
        if "auth" in endpoint or "login" in endpoint or "register" in endpoint:
            return self.default_limits["auth"]
        elif "upload" in endpoint:
            return self.default_limits["upload"]
        elif "analysis" in endpoint or "analyze" in endpoint:
            return self.default_limits["analysis"]
        else:
            return self.default_limits["global"]
    
    def _track_suspicious_activity(self, identifier: str):
        """跟踪可疑活动"""
        self.suspicious_ips[identifier] += 1
        
        # 如果短时间内多次超限，临时阻止
        if self.suspicious_ips[identifier] >= 5:
            block_duration = min(300 * (2 ** (self.suspicious_ips[identifier] - 5)), 3600)  # 最多1小时
            self.blocked_ips[identifier] = datetime.now() + timedelta(seconds=block_duration)
            
            logger.warning(f"IP {identifier} blocked for {block_duration} seconds due to suspicious activity")
    
    def reset_user_limits(self, identifier: str):
        """重置用户限制（管理员功能）"""
        keys_to_remove = [key for key in self.request_history.keys() if key.startswith(f"{identifier}:")]
        for key in keys_to_remove:
            del self.request_history[key]
        
        if identifier in self.blocked_ips:
            del self.blocked_ips[identifier]
        
        if identifier in self.suspicious_ips:
            del self.suspicious_ips[identifier]
        
        logger.info(f"Reset rate limits for {identifier}")
    
    def get_user_status(self, identifier: str) -> Dict:
        """获取用户限制状态"""
        status = {
            "identifier": identifier,
            "is_blocked": identifier in self.blocked_ips,
            "suspicious_count": self.suspicious_ips.get(identifier, 0),
            "active_limits": {}
        }
        
        if identifier in self.blocked_ips:
            status["blocked_until"] = self.blocked_ips[identifier].isoformat()
        
        # 获取当前活跃的限制
        for key, history in self.request_history.items():
            if key.startswith(f"{identifier}:"):
                status["active_limits"][key] = len(history)
        
        return status
    
    def get_global_stats(self) -> Dict:
        """获取全局统计"""
        return {
            "total_tracked_users": len(set(key.split(":")[0] for key in self.request_history.keys())),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "total_request_records": sum(len(history) for history in self.request_history.values())
        }
    
    async def cleanup_expired_records(self):
        """清理过期记录（定期任务）"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, history in self.request_history.items():
            # 清理1天前的记录
            cutoff_time = current_time - 86400
            while history and history[0] < cutoff_time:
                history.popleft()
            
            # 如果队列为空，标记删除
            if not history:
                keys_to_remove.append(key)
        
        # 删除空队列
        for key in keys_to_remove:
            del self.request_history[key]
        
        # 清理过期的阻止记录
        expired_blocks = [
            ip for ip, until in self.blocked_ips.items() 
            if datetime.now() > until
        ]
        for ip in expired_blocks:
            del self.blocked_ips[ip]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} expired rate limit records and {len(expired_blocks)} expired blocks")

# 全局实例
rate_limiter = RateLimiter()