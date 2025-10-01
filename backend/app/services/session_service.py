import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from user_agents import parse
import ipaddress

from ..data.models.database import User, UserSession, CreditTransaction
from ..core.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """会话管理服务 - 处理用户会话安全、多设备管理和异常登录检测"""
    
    def __init__(self):
        self.max_sessions_per_user = 5  # 每个用户最大会话数
        self.session_timeout_hours = 24  # 会话超时时间（小时）
        self.suspicious_login_threshold = 3  # 可疑登录阈值
        
    def create_session(
        self, 
        user: User, 
        token_jti: str, 
        ip_address: str, 
        user_agent: str,
        db: Session
    ) -> UserSession:
        """创建新的用户会话"""
        try:
            # 解析用户代理
            device_info = self._parse_user_agent(user_agent)
            
            # 检查是否为可疑登录
            is_suspicious = self._check_suspicious_login(user, ip_address, device_info, db)
            
            # 清理过期会话
            self._cleanup_expired_sessions(user.id, db)
            
            # 检查会话数量限制
            self._enforce_session_limit(user.id, db)
            
            # 创建新会话
            session = UserSession(
                user_id=user.id,
                token_jti=token_jti,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_info.get('device_type'),
                browser=device_info.get('browser'),
                os=device_info.get('os'),
                location=self._get_location_from_ip(ip_address),
                is_suspicious=is_suspicious,
                expires_at=datetime.utcnow() + timedelta(hours=self.session_timeout_hours),
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # 记录登录事件
            self._log_login_event(user, session, db)
            
            logger.info(f"Created session for user {user.id} from {ip_address}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session for user {user.id}: {e}")
            db.rollback()
            raise
    
    def validate_session(self, token_jti: str, db: Session) -> Optional[UserSession]:
        """验证会话有效性"""
        try:
            session = db.query(UserSession).filter(
                and_(
                    UserSession.token_jti == token_jti,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).first()
            
            if session:
                # 更新最后活动时间
                session.last_activity = datetime.utcnow()
                db.commit()
                
            return session
            
        except Exception as e:
            logger.error(f"Error validating session {token_jti}: {e}")
            return None
    
    def revoke_session(self, token_jti: str, db: Session) -> bool:
        """撤销会话"""
        try:
            session = db.query(UserSession).filter(
                UserSession.token_jti == token_jti
            ).first()
            
            if session:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
                db.commit()
                logger.info(f"Revoked session {token_jti}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error revoking session {token_jti}: {e}")
            return False
    
    def revoke_all_user_sessions(self, user_id: int, except_token: Optional[str] = None, db: Session = None) -> int:
        """撤销用户的所有会话（除了指定的token）"""
        try:
            query = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            )
            
            if except_token:
                query = query.filter(UserSession.token_jti != except_token)
            
            sessions = query.all()
            count = 0
            
            for session in sessions:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
                count += 1
            
            db.commit()
            logger.info(f"Revoked {count} sessions for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error revoking sessions for user {user_id}: {e}")
            return 0
    
    def get_user_sessions(self, user_id: int, db: Session) -> List[Dict]:
        """获取用户的活跃会话列表"""
        try:
            sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).order_by(desc(UserSession.last_activity)).all()
            
            session_list = []
            for session in sessions:
                session_info = {
                    "id": session.id,
                    "device_type": session.device_type,
                    "browser": session.browser,
                    "os": session.os,
                    "ip_address": session.ip_address,
                    "location": session.location,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "is_current": False,  # 需要在调用时设置
                    "is_suspicious": session.is_suspicious
                }
                session_list.append(session_info)
            
            return session_list
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    def detect_anomalous_activity(self, user_id: int, db: Session) -> Dict:
        """检测异常活动"""
        try:
            # 获取最近24小时的会话
            recent_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.created_at > datetime.utcnow() - timedelta(hours=24)
                )
            ).all()
            
            # 分析异常模式
            anomalies = {
                "multiple_locations": self._detect_multiple_locations(recent_sessions),
                "unusual_devices": self._detect_unusual_devices(user_id, recent_sessions, db),
                "rapid_logins": self._detect_rapid_logins(recent_sessions),
                "suspicious_ips": self._detect_suspicious_ips(recent_sessions)
            }
            
            # 计算风险评分
            risk_score = self._calculate_risk_score(anomalies)
            
            return {
                "risk_score": risk_score,
                "anomalies": anomalies,
                "recommendation": self._get_security_recommendation(risk_score)
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalous activity for user {user_id}: {e}")
            return {"risk_score": 0, "anomalies": {}, "recommendation": "Unable to analyze"}
    
    def cleanup_expired_sessions(self, db: Session) -> int:
        """清理所有过期会话"""
        try:
            expired_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.expires_at < datetime.utcnow()
                )
            ).all()
            
            count = 0
            for session in expired_sessions:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
                count += 1
            
            db.commit()
            logger.info(f"Cleaned up {count} expired sessions")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def get_session_statistics(self, db: Session) -> Dict:
        """获取会话统计信息"""
        try:
            # 活跃会话数
            active_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).count()
            
            # 今日新会话数
            today_sessions = db.query(UserSession).filter(
                UserSession.created_at > datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            # 可疑会话数
            suspicious_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.is_suspicious == True,
                    UserSession.created_at > datetime.utcnow() - timedelta(days=7)
                )
            ).count()
            
            # 设备类型分布
            device_stats = db.query(
                UserSession.device_type,
                func.count(UserSession.id).label('count')
            ).filter(
                UserSession.created_at > datetime.utcnow() - timedelta(days=30)
            ).group_by(UserSession.device_type).all()
            
            return {
                "active_sessions": active_sessions,
                "today_sessions": today_sessions,
                "suspicious_sessions": suspicious_sessions,
                "device_distribution": {stat.device_type: stat.count for stat in device_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {}
    
    # 私有方法
    def _parse_user_agent(self, user_agent: str) -> Dict:
        """解析用户代理字符串"""
        try:
            ua = parse(user_agent)
            return {
                "device_type": self._get_device_type(ua),
                "browser": f"{ua.browser.family} {ua.browser.version_string}",
                "os": f"{ua.os.family} {ua.os.version_string}"
            }
        except Exception:
            return {
                "device_type": "Unknown",
                "browser": "Unknown",
                "os": "Unknown"
            }
    
    def _get_device_type(self, ua) -> str:
        """确定设备类型"""
        if ua.is_mobile:
            return "Mobile"
        elif ua.is_tablet:
            return "Tablet"
        elif ua.is_pc:
            return "Desktop"
        else:
            return "Unknown"
    
    def _get_location_from_ip(self, ip_address: str) -> str:
        """从IP地址获取位置信息（简化版）"""
        try:
            # 这里可以集成GeoIP服务
            # 目前返回简化的位置信息
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return "Private Network"
            elif ip.is_loopback:
                return "Localhost"
            else:
                return "Unknown Location"
        except Exception:
            return "Unknown"
    
    def _check_suspicious_login(self, user: User, ip_address: str, device_info: Dict, db: Session) -> bool:
        """检查是否为可疑登录"""
        try:
            # 检查最近的登录历史
            recent_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user.id,
                    UserSession.created_at > datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(desc(UserSession.created_at)).limit(10).all()
            
            if not recent_sessions:
                return False  # 新用户不标记为可疑
            
            # 检查IP地址是否为新的
            known_ips = {session.ip_address for session in recent_sessions}
            if ip_address not in known_ips:
                return True
            
            # 检查设备是否为新的
            known_devices = {f"{session.device_type}-{session.browser}" for session in recent_sessions}
            current_device = f"{device_info.get('device_type')}-{device_info.get('browser')}"
            if current_device not in known_devices:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking suspicious login: {e}")
            return False
    
    def _cleanup_expired_sessions(self, user_id: int, db: Session):
        """清理用户的过期会话"""
        try:
            expired_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at < datetime.utcnow()
                )
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
            
            if expired_sessions:
                db.commit()
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions for user {user_id}: {e}")
    
    def _enforce_session_limit(self, user_id: int, db: Session):
        """强制执行会话数量限制"""
        try:
            active_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).order_by(UserSession.last_activity).all()
            
            if len(active_sessions) >= self.max_sessions_per_user:
                # 撤销最旧的会话
                sessions_to_revoke = active_sessions[:len(active_sessions) - self.max_sessions_per_user + 1]
                for session in sessions_to_revoke:
                    session.is_active = False
                    session.revoked_at = datetime.utcnow()
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error enforcing session limit for user {user_id}: {e}")
    
    def _log_login_event(self, user: User, session: UserSession, db: Session):
        """记录登录事件"""
        try:
            # 这里可以记录到专门的审计日志表
            logger.info(f"User {user.id} logged in from {session.ip_address} using {session.device_type}")
            
        except Exception as e:
            logger.error(f"Error logging login event: {e}")
    
    def _detect_multiple_locations(self, sessions: List[UserSession]) -> bool:
        """检测多地登录"""
        locations = {session.location for session in sessions if session.location}
        return len(locations) > 2
    
    def _detect_unusual_devices(self, user_id: int, recent_sessions: List[UserSession], db: Session) -> bool:
        """检测异常设备"""
        # 获取历史设备信息
        historical_sessions = db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.created_at < datetime.utcnow() - timedelta(days=7)
            )
        ).all()
        
        historical_devices = {f"{s.device_type}-{s.browser}" for s in historical_sessions}
        recent_devices = {f"{s.device_type}-{s.browser}" for s in recent_sessions}
        
        new_devices = recent_devices - historical_devices
        return len(new_devices) > 0
    
    def _detect_rapid_logins(self, sessions: List[UserSession]) -> bool:
        """检测快速登录"""
        if len(sessions) < 3:
            return False
        
        # 检查是否在短时间内有多次登录
        sorted_sessions = sorted(sessions, key=lambda x: x.created_at)
        for i in range(len(sorted_sessions) - 2):
            time_diff = sorted_sessions[i + 2].created_at - sorted_sessions[i].created_at
            if time_diff < timedelta(minutes=5):
                return True
        
        return False
    
    def _detect_suspicious_ips(self, sessions: List[UserSession]) -> bool:
        """检测可疑IP"""
        # 简化版：检查是否有来自不同网段的IP
        ips = [session.ip_address for session in sessions]
        unique_networks = set()
        
        for ip in ips:
            try:
                network = str(ipaddress.ip_network(f"{ip}/24", strict=False))
                unique_networks.add(network)
            except Exception:
                continue
        
        return len(unique_networks) > 2
    
    def _calculate_risk_score(self, anomalies: Dict) -> int:
        """计算风险评分（0-100）"""
        score = 0
        
        if anomalies.get("multiple_locations"):
            score += 25
        if anomalies.get("unusual_devices"):
            score += 30
        if anomalies.get("rapid_logins"):
            score += 20
        if anomalies.get("suspicious_ips"):
            score += 25
        
        return min(score, 100)
    
    def _get_security_recommendation(self, risk_score: int) -> str:
        """根据风险评分提供安全建议"""
        if risk_score >= 70:
            return "High risk detected. Consider changing password and reviewing account activity."
        elif risk_score >= 40:
            return "Medium risk detected. Review recent login activity and enable 2FA if not already enabled."
        elif risk_score >= 20:
            return "Low risk detected. Monitor account activity regularly."
        else:
            return "No significant security risks detected."


# 创建全局实例
session_service = SessionService()