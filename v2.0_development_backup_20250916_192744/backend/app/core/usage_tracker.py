from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from ..data.models.database import get_db, User
import redis
import json
from .config import settings

class UsageTracker:
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host='localhost', port=6380, db=1, decode_responses=True)
            self.redis_client.ping()
        except:
            self.redis_client = None
    
    def get_daily_usage_key(self, user_id: int, date: str = None) -> str:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"usage:daily:{user_id}:{date}"
    
    def get_monthly_usage_key(self, user_id: int, month: str = None) -> str:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        return f"usage:monthly:{user_id}:{month}"
    
    def get_system_stats_keys(self, date: str = None) -> Dict[str, str]:
        """获取系统统计的Redis键"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        month = date[:7]  # YYYY-MM
        
        return {
            "daily_total": f"system:daily_total:{date}",
            "monthly_total": f"system:monthly_total:{month}",
            "daily_features": f"system:daily_features:{date}",
            "monthly_features": f"system:monthly_features:{month}",
            "active_users_daily": f"system:active_users:{date}",
            "active_users_monthly": f"system:active_users:{month}"
        }
    
    def increment_system_usage(self, user_id: int, feature: str, count: int = 1):
        """增加系统级使用统计"""
        if not self.redis_client:
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        keys = self.get_system_stats_keys(today)
        
        pipe = self.redis_client.pipeline()
        
        # 总请求数统计
        pipe.incrby(keys["daily_total"], count)
        pipe.incrby(keys["monthly_total"], count)
        
        # 按功能统计
        pipe.hincrby(keys["daily_features"], feature, count)
        pipe.hincrby(keys["monthly_features"], feature, count)
        
        # 活跃用户统计
        pipe.sadd(keys["active_users_daily"], user_id)
        pipe.sadd(keys["active_users_monthly"], user_id)
        
        # 设置过期时间
        pipe.expire(keys["daily_total"], 86400 * 30)  # 30天
        pipe.expire(keys["monthly_total"], 86400 * 365)  # 1年
        pipe.expire(keys["daily_features"], 86400 * 30)
        pipe.expire(keys["monthly_features"], 86400 * 365)
        pipe.expire(keys["active_users_daily"], 86400 * 30)
        pipe.expire(keys["active_users_monthly"], 86400 * 365)
        
        pipe.execute()
    
    def get_system_usage_stats(self, days: int = 7) -> Dict:
        """获取系统使用统计"""
        if not self.redis_client:
            return {
                "total_requests_today": 0,
                "total_requests_month": 0,
                "active_users_today": 0,
                "active_users_month": 0,
                "daily_stats": [],
                "feature_stats_daily": {},
                "feature_stats_monthly": {}
            }
        
        today = datetime.now()
        month = today.strftime("%Y-%m")
        
        # 今日和本月总计
        today_keys = self.get_system_stats_keys(today.strftime("%Y-%m-%d"))
        total_requests_today = int(self.redis_client.get(today_keys["daily_total"]) or 0)
        total_requests_month = int(self.redis_client.get(today_keys["monthly_total"]) or 0)
        
        # 活跃用户数
        active_users_today = self.redis_client.scard(today_keys["active_users_daily"])
        active_users_month = self.redis_client.scard(today_keys["active_users_monthly"])
        
        # 最近几天的统计
        daily_stats = []
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            keys = self.get_system_stats_keys(date)
            
            daily_total = int(self.redis_client.get(keys["daily_total"]) or 0)
            daily_active = self.redis_client.scard(keys["active_users_daily"])
            
            daily_stats.append({
                "date": date,
                "total_requests": daily_total,
                "active_users": daily_active
            })
        
        # 功能使用统计
        feature_stats_daily = self.redis_client.hgetall(today_keys["daily_features"]) or {}
        feature_stats_monthly = self.redis_client.hgetall(today_keys["monthly_features"]) or {}
        
        # 转换为整数
        feature_stats_daily = {k: int(v) for k, v in feature_stats_daily.items()}
        feature_stats_monthly = {k: int(v) for k, v in feature_stats_monthly.items()}
        
        return {
            "total_requests_today": total_requests_today,
            "total_requests_month": total_requests_month,
            "active_users_today": active_users_today,
            "active_users_month": active_users_month,
            "daily_stats": daily_stats,
            "feature_stats_daily": feature_stats_daily,
            "feature_stats_monthly": feature_stats_monthly
        }
    
    def get_user_activity_stats(self, days: int = 30) -> Dict:
        """获取用户活动统计"""
        if not self.redis_client:
            return {"user_activity": []}
        
        today = datetime.now()
        user_activity = []
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            keys = self.get_system_stats_keys(date)
            
            active_users = self.redis_client.scard(keys["active_users_daily"])
            total_requests = int(self.redis_client.get(keys["daily_total"]) or 0)
            
            user_activity.append({
                "date": date,
                "active_users": active_users,
                "total_requests": total_requests
            })
        
        return {"user_activity": user_activity}
    
    def get_top_users_by_usage(self, limit: int = 10, period: str = "daily") -> List[Dict]:
        """获取使用量最高的用户"""
        if not self.redis_client:
            return []
        
        from ..data.models.database import get_db, User
        from sqlalchemy.orm import Session
        
        # 这里需要遍历所有用户的使用量数据
        # 实际实现中可能需要更高效的方法
        top_users = []
        
        # 简化实现：返回空列表，实际使用中可以通过数据库查询活跃用户
        # 然后获取他们的使用量数据进行排序
        
        return top_users

    def increment_usage(self, user_id: int, feature: str, count: int = 1) -> Dict:
        """增加用户使用量"""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        daily_key = self.get_daily_usage_key(user_id, today)
        monthly_key = self.get_monthly_usage_key(user_id, month)
        
        if self.redis_client:
            # 使用Redis存储
            pipe = self.redis_client.pipeline()
            pipe.hincrby(daily_key, feature, count)
            pipe.hincrby(monthly_key, feature, count)
            pipe.expire(daily_key, 86400 * 7)  # 7天过期
            pipe.expire(monthly_key, 86400 * 32)  # 32天过期
            results = pipe.execute()
            
            # 同时更新系统统计
            self.increment_system_usage(user_id, feature, count)
            
            return {
                "daily_usage": results[0],
                "monthly_usage": results[1]
            }
        else:
            # 内存存储（临时方案）
            return {"daily_usage": count, "monthly_usage": count}
    
    def get_usage(self, user_id: int, period: str = "daily") -> Dict:
        """获取用户使用量"""
        if period == "daily":
            key = self.get_daily_usage_key(user_id)
        else:
            key = self.get_monthly_usage_key(user_id)
        
        if self.redis_client:
            usage = self.redis_client.hgetall(key)
            return {k: int(v) for k, v in usage.items()}
        else:
            return {}
    
    def check_rate_limit(self, user: User, feature: str, count: int = 1) -> bool:
        """检查是否超过使用限制"""
        from .auth import SUBSCRIPTION_LIMITS
        
        limits = SUBSCRIPTION_LIMITS.get(user.subscription_tier)
        if not limits or limits["daily_requests"] == -1:
            return True
        
        daily_usage = self.get_usage(user.id, "daily")
        current_usage = daily_usage.get(feature, 0)
        
        return (current_usage + count) <= limits["daily_requests"]
    
    def get_remaining_requests(self, user: User) -> Dict:
        """获取用户剩余请求数"""
        from .auth import SUBSCRIPTION_LIMITS
        
        limits = SUBSCRIPTION_LIMITS.get(user.subscription_tier)
        if not limits:
            return {"daily_remaining": 0, "monthly_remaining": 0}
        
        if limits["daily_requests"] == -1:
            return {"daily_remaining": -1, "monthly_remaining": -1}  # 无限制
        
        daily_usage = self.get_usage(user.id, "daily")
        monthly_usage = self.get_usage(user.id, "monthly")
        
        # 计算总使用量（所有功能）
        daily_total = sum(daily_usage.values())
        monthly_total = sum(monthly_usage.values())
        
        daily_remaining = max(0, limits["daily_requests"] - daily_total)
        # 假设月度限制是日限制的30倍
        monthly_limit = limits["daily_requests"] * 30
        monthly_remaining = max(0, monthly_limit - monthly_total)
        
        return {
            "daily_remaining": daily_remaining,
            "monthly_remaining": monthly_remaining,
            "daily_limit": limits["daily_requests"],
            "monthly_limit": monthly_limit
        }
    
    def get_usage_stats(self, user: User) -> Dict:
        """获取用户使用统计"""
        daily_usage = self.get_usage(user.id, "daily")
        monthly_usage = self.get_usage(user.id, "monthly")
        remaining = self.get_remaining_requests(user)
        
        return {
            "daily_usage": daily_usage,
            "monthly_usage": monthly_usage,
            "remaining_requests": remaining,
            "subscription_tier": user.subscription_tier.value
        }
    
    def reset_user_usage(self, user_id: int, period: str = "daily") -> bool:
        """重置用户使用量（管理员功能）"""
        if period == "daily":
            key = self.get_daily_usage_key(user_id)
        else:
            key = self.get_monthly_usage_key(user_id)
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except:
                return False
        return True

usage_tracker = UsageTracker()