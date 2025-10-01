import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import hashlib

from ..data.models.database import User
from ..core.config import settings

logger = logging.getLogger(__name__)


class LoginLimiter:
    """登录限制服务 - 防止暴力破解攻击"""
    
    def __init__(self):
        # 配置参数
        self.max_attempts = 5  # 最大尝试次数
        self.lockout_duration = 30  # 锁定时间（分钟）
        self.attempt_window = 15  # 尝试窗口时间（分钟）
        self.progressive_delay = True  # 是否启用渐进式延迟
        
        # 内存存储（生产环境建议使用Redis）
        self.failed_attempts = {}  # {key: {"count": int, "first_attempt": datetime, "last_attempt": datetime}}
        self.lockouts = {}  # {key: {"locked_until": datetime, "reason": str}}
        
    def check_login_allowed(self, identifier: str, ip_address: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        检查是否允许登录
        
        Args:
            identifier: 用户标识符（邮箱或用户名）
            ip_address: IP地址
            
        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (是否允许, 错误信息, 剩余锁定时间秒数)
        """
        try:
            # 生成检查键
            user_key = self._generate_key("user", identifier)
            ip_key = self._generate_key("ip", ip_address)
            
            # 检查用户级别锁定
            user_locked, user_msg, user_remaining = self._check_lockout(user_key)
            if user_locked:
                return False, user_msg, user_remaining
            
            # 检查IP级别锁定
            ip_locked, ip_msg, ip_remaining = self._check_lockout(ip_key)
            if ip_locked:
                return False, ip_msg, ip_remaining
            
            # 检查用户级别尝试次数
            user_attempts = self._get_attempts(user_key)
            if user_attempts >= self.max_attempts:
                self._apply_lockout(user_key, "Too many failed login attempts for this account")
                return False, "Account temporarily locked due to too many failed attempts", self.lockout_duration * 60
            
            # 检查IP级别尝试次数
            ip_attempts = self._get_attempts(ip_key)
            if ip_attempts >= self.max_attempts * 2:  # IP限制更宽松
                self._apply_lockout(ip_key, "Too many failed login attempts from this IP")
                return False, "IP temporarily blocked due to suspicious activity", self.lockout_duration * 60
            
            return True, None, None
            
        except Exception as e:
            logger.error(f"Error checking login permission: {e}")
            return True, None, None  # 出错时允许登录，避免影响正常用户
    
    def record_failed_attempt(self, identifier: str, ip_address: str, reason: str = "Invalid credentials"):
        """记录失败的登录尝试"""
        try:
            user_key = self._generate_key("user", identifier)
            ip_key = self._generate_key("ip", ip_address)
            
            # 记录用户级别失败
            self._increment_attempts(user_key)
            
            # 记录IP级别失败
            self._increment_attempts(ip_key)
            
            logger.warning(f"Failed login attempt for {identifier} from {ip_address}: {reason}")
            
        except Exception as e:
            logger.error(f"Error recording failed attempt: {e}")
    
    def record_successful_login(self, identifier: str, ip_address: str):
        """记录成功的登录，清除失败记录"""
        try:
            user_key = self._generate_key("user", identifier)
            ip_key = self._generate_key("ip", ip_address)
            
            # 清除失败记录
            self._clear_attempts(user_key)
            self._clear_lockout(user_key)
            
            # IP级别的记录保留，但重置计数
            if ip_key in self.failed_attempts:
                self.failed_attempts[ip_key]["count"] = max(0, self.failed_attempts[ip_key]["count"] - 1)
            
            logger.info(f"Successful login for {identifier} from {ip_address}")
            
        except Exception as e:
            logger.error(f"Error recording successful login: {e}")
    
    def get_attempt_info(self, identifier: str, ip_address: str) -> Dict:
        """获取尝试信息"""
        try:
            user_key = self._generate_key("user", identifier)
            ip_key = self._generate_key("ip", ip_address)
            
            user_attempts = self._get_attempts(user_key)
            ip_attempts = self._get_attempts(ip_key)
            
            user_locked, _, user_remaining = self._check_lockout(user_key)
            ip_locked, _, ip_remaining = self._check_lockout(ip_key)
            
            return {
                "user_attempts": user_attempts,
                "ip_attempts": ip_attempts,
                "max_attempts": self.max_attempts,
                "user_locked": user_locked,
                "ip_locked": ip_locked,
                "user_lockout_remaining": user_remaining,
                "ip_lockout_remaining": ip_remaining,
                "attempts_remaining": max(0, self.max_attempts - user_attempts)
            }
            
        except Exception as e:
            logger.error(f"Error getting attempt info: {e}")
            return {}
    
    def clear_user_attempts(self, identifier: str):
        """清除用户的失败尝试记录（管理员功能）"""
        try:
            user_key = self._generate_key("user", identifier)
            self._clear_attempts(user_key)
            self._clear_lockout(user_key)
            logger.info(f"Cleared login attempts for user {identifier}")
            
        except Exception as e:
            logger.error(f"Error clearing user attempts: {e}")
    
    def clear_ip_attempts(self, ip_address: str):
        """清除IP的失败尝试记录（管理员功能）"""
        try:
            ip_key = self._generate_key("ip", ip_address)
            self._clear_attempts(ip_key)
            self._clear_lockout(ip_key)
            logger.info(f"Cleared login attempts for IP {ip_address}")
            
        except Exception as e:
            logger.error(f"Error clearing IP attempts: {e}")
    
    def get_lockout_statistics(self) -> Dict:
        """获取锁定统计信息"""
        try:
            current_time = datetime.utcnow()
            
            # 统计当前锁定的用户和IP
            locked_users = 0
            locked_ips = 0
            
            for key, lockout_info in self.lockouts.items():
                if lockout_info["locked_until"] > current_time:
                    if key.startswith("user:"):
                        locked_users += 1
                    elif key.startswith("ip:"):
                        locked_ips += 1
            
            # 统计失败尝试
            total_attempts = len(self.failed_attempts)
            high_risk_attempts = sum(1 for attempts in self.failed_attempts.values() 
                                   if attempts["count"] >= self.max_attempts // 2)
            
            return {
                "locked_users": locked_users,
                "locked_ips": locked_ips,
                "total_failed_attempts": total_attempts,
                "high_risk_attempts": high_risk_attempts,
                "max_attempts_threshold": self.max_attempts,
                "lockout_duration_minutes": self.lockout_duration
            }
            
        except Exception as e:
            logger.error(f"Error getting lockout statistics: {e}")
            return {}
    
    def cleanup_expired_records(self):
        """清理过期的记录"""
        try:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(minutes=self.attempt_window * 2)
            
            # 清理过期的失败尝试记录
            expired_attempts = []
            for key, attempt_info in self.failed_attempts.items():
                if attempt_info["last_attempt"] < cutoff_time:
                    expired_attempts.append(key)
            
            for key in expired_attempts:
                del self.failed_attempts[key]
            
            # 清理过期的锁定记录
            expired_lockouts = []
            for key, lockout_info in self.lockouts.items():
                if lockout_info["locked_until"] < current_time:
                    expired_lockouts.append(key)
            
            for key in expired_lockouts:
                del self.lockouts[key]
            
            if expired_attempts or expired_lockouts:
                logger.info(f"Cleaned up {len(expired_attempts)} expired attempts and {len(expired_lockouts)} expired lockouts")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired records: {e}")
    
    # 私有方法
    def _generate_key(self, key_type: str, identifier: str) -> str:
        """生成缓存键"""
        # 使用哈希来保护敏感信息
        hash_obj = hashlib.sha256(identifier.lower().encode())
        return f"{key_type}:{hash_obj.hexdigest()[:16]}"
    
    def _check_lockout(self, key: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """检查是否被锁定"""
        if key not in self.lockouts:
            return False, None, None
        
        lockout_info = self.lockouts[key]
        current_time = datetime.utcnow()
        
        if lockout_info["locked_until"] > current_time:
            remaining_seconds = int((lockout_info["locked_until"] - current_time).total_seconds())
            return True, lockout_info["reason"], remaining_seconds
        else:
            # 锁定已过期，清除记录
            del self.lockouts[key]
            return False, None, None
    
    def _get_attempts(self, key: str) -> int:
        """获取尝试次数"""
        if key not in self.failed_attempts:
            return 0
        
        attempt_info = self.failed_attempts[key]
        current_time = datetime.utcnow()
        
        # 检查是否在时间窗口内
        if current_time - attempt_info["first_attempt"] > timedelta(minutes=self.attempt_window):
            # 重置计数器
            self.failed_attempts[key] = {
                "count": 0,
                "first_attempt": current_time,
                "last_attempt": current_time
            }
            return 0
        
        return attempt_info["count"]
    
    def _increment_attempts(self, key: str):
        """增加尝试次数"""
        current_time = datetime.utcnow()
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = {
                "count": 1,
                "first_attempt": current_time,
                "last_attempt": current_time
            }
        else:
            attempt_info = self.failed_attempts[key]
            
            # 检查是否需要重置时间窗口
            if current_time - attempt_info["first_attempt"] > timedelta(minutes=self.attempt_window):
                self.failed_attempts[key] = {
                    "count": 1,
                    "first_attempt": current_time,
                    "last_attempt": current_time
                }
            else:
                attempt_info["count"] += 1
                attempt_info["last_attempt"] = current_time
    
    def _apply_lockout(self, key: str, reason: str):
        """应用锁定"""
        current_time = datetime.utcnow()
        
        # 计算锁定时间（可以实现渐进式延迟）
        lockout_duration = self.lockout_duration
        if self.progressive_delay and key in self.lockouts:
            # 如果之前已经被锁定过，延长锁定时间
            lockout_duration *= 2
        
        self.lockouts[key] = {
            "locked_until": current_time + timedelta(minutes=lockout_duration),
            "reason": reason
        }
    
    def _clear_attempts(self, key: str):
        """清除尝试记录"""
        if key in self.failed_attempts:
            del self.failed_attempts[key]
    
    def _clear_lockout(self, key: str):
        """清除锁定记录"""
        if key in self.lockouts:
            del self.lockouts[key]


# 创建全局实例
login_limiter = LoginLimiter()