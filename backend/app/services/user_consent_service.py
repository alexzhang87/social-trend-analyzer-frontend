"""
用户授权管理服务
处理用户对AI训练数据收集的授权管理
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import uuid
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import logger
from app.models.user import User
from app.models.user_consent import UserConsent, ConsentRequest
from app.core.config import settings


class UserConsentService:
    """用户授权管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_consent_request(
        self, 
        user_id: str,
        request_context: Dict
    ) -> Dict:
        """创建用户授权请求"""
        
        consent_request = {
            "request_id": str(uuid.uuid4()),
            "user_id": user_id,
            "consent_type": "ai_training_data",
            "purpose": "改进AI助手的回答质量和专业性",
            "data_types": [
                "对话内容（经过脱敏处理）",
                "问题类型和分类标签",
                "用户反馈评分和建议",
                "会话时长和使用频率",
                "功能使用偏好数据"
            ],
            "data_usage": [
                "训练和优化AI模型",
                "改进专家推荐算法",
                "提升回答准确性和专业性",
                "开发新的AI功能特性"
            ],
            "retention_period": "24个月",
            "user_rights": [
                "随时撤回授权同意",
                "查询数据使用情况",
                "请求删除相关数据",
                "获取数据使用报告",
                "更新授权偏好设置"
            ],
            "data_protection": [
                "所有数据经过脱敏处理",
                "采用行业标准加密技术",
                "严格的访问权限控制",
                "定期安全审计和监控",
                "遵循相关法律法规要求"
            ],
            "benefits": [
                "获得更准确的AI回答",
                "享受个性化的专家建议",
                "体验持续改进的产品功能",
                "参与AI技术发展进程"
            ],
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "request_context": request_context
        }
        
        # 保存到数据库
        db_request = ConsentRequest(**consent_request)
        self.db.add(db_request)
        self.db.commit()
        
        logger.info(f"Created consent request for user {user_id}")
        return consent_request
    
    async def record_user_consent(
        self,
        user_id: str,
        consent_given: bool,
        consent_details: Dict
    ) -> Dict:
        """记录用户授权决定"""
        
        # 检查是否已有授权记录
        existing_consent = self.db.query(UserConsent).filter(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == "ai_training_data"
        ).first()
        
        consent_data = {
            "user_id": user_id,
            "consent_type": "ai_training_data",
            "consent_given": consent_given,
            "consent_timestamp": datetime.utcnow(),
            "consent_version": "v1.0",
            "ip_address": consent_details.get("ip_address"),
            "user_agent": consent_details.get("user_agent"),
            "consent_method": "explicit_checkbox",
            "consent_details": consent_details,
            "is_active": True
        }
        
        if existing_consent:
            # 更新现有记录
            for key, value in consent_data.items():
                setattr(existing_consent, key, value)
            self.db.commit()
            consent_record = existing_consent
        else:
            # 创建新记录
            consent_record = UserConsent(**consent_data)
            self.db.add(consent_record)
            self.db.commit()
        
        # 记录授权历史
        await self._log_consent_history(user_id, consent_given, consent_details)
        
        logger.info(f"Recorded consent for user {user_id}: {consent_given}")
        return {
            "consent_id": consent_record.id,
            "status": "recorded",
            "consent_given": consent_given,
            "timestamp": consent_record.consent_timestamp
        }
    
    async def check_user_consent(self, user_id: str) -> Dict:
        """检查用户授权状态"""
        
        consent_record = self.db.query(UserConsent).filter(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == "ai_training_data",
            UserConsent.is_active == True
        ).first()
        
        if not consent_record:
            return {
                "has_consent": False,
                "consent_status": "not_requested",
                "message": "用户尚未进行授权"
            }
        
        # 检查授权是否过期（2年有效期）
        expiry_date = consent_record.consent_timestamp + timedelta(days=730)
        is_expired = datetime.utcnow() > expiry_date
        
        if is_expired:
            return {
                "has_consent": False,
                "consent_status": "expired",
                "message": "用户授权已过期，需要重新授权",
                "expired_date": expiry_date
            }
        
        return {
            "has_consent": consent_record.consent_given,
            "consent_status": "active" if consent_record.consent_given else "declined",
            "consent_date": consent_record.consent_timestamp,
            "expires_date": expiry_date,
            "consent_version": consent_record.consent_version
        }
    
    async def revoke_user_consent(
        self, 
        user_id: str,
        revocation_reason: str = None
    ) -> Dict:
        """撤回用户授权"""
        
        consent_record = self.db.query(UserConsent).filter(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == "ai_training_data",
            UserConsent.is_active == True
        ).first()
        
        if not consent_record:
            return {
                "status": "error",
                "message": "未找到有效的授权记录"
            }
        
        # 标记授权为已撤回
        consent_record.consent_given = False
        consent_record.revoked_at = datetime.utcnow()
        consent_record.revocation_reason = revocation_reason
        consent_record.is_active = False
        
        self.db.commit()
        
        # 触发数据清理流程
        await self._trigger_data_cleanup(user_id)
        
        logger.info(f"User {user_id} revoked consent for AI training data")
        return {
            "status": "success",
            "message": "授权已成功撤回",
            "revoked_at": consent_record.revoked_at
        }
    
    async def get_user_data_usage_report(self, user_id: str) -> Dict:
        """获取用户数据使用报告"""
        
        # 检查用户是否有授权
        consent_status = await self.check_user_consent(user_id)
        if not consent_status["has_consent"]:
            return {
                "status": "error",
                "message": "用户未授权数据使用"
            }
        
        # 生成匿名用户ID（用于查询训练数据）
        anonymous_id = self._generate_anonymous_id(user_id)
        
        # 查询数据使用情况（这里需要连接到训练数据库）
        usage_stats = await self._query_data_usage_stats(anonymous_id)
        
        report = {
            "user_id": user_id,
            "report_generated_at": datetime.utcnow(),
            "consent_date": consent_status["consent_date"],
            "data_usage_stats": {
                "total_conversations_used": usage_stats.get("conversation_count", 0),
                "total_feedback_used": usage_stats.get("feedback_count", 0),
                "last_data_usage": usage_stats.get("last_usage_date"),
                "data_quality_score": usage_stats.get("avg_quality_score", 0)
            },
            "model_improvements": {
                "models_trained": usage_stats.get("models_trained", []),
                "improvement_metrics": usage_stats.get("improvement_metrics", {}),
                "user_benefit_score": usage_stats.get("user_benefit_score", 0)
            },
            "data_protection_measures": [
                "数据已完全脱敏处理",
                "使用加密存储和传输",
                "严格的访问控制",
                "定期安全审计",
                "符合隐私保护法规"
            ]
        }
        
        return report
    
    async def update_consent_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> Dict:
        """更新用户授权偏好"""
        
        consent_record = self.db.query(UserConsent).filter(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == "ai_training_data",
            UserConsent.is_active == True
        ).first()
        
        if not consent_record:
            return {
                "status": "error",
                "message": "未找到有效的授权记录"
            }
        
        # 更新偏好设置
        current_details = consent_record.consent_details or {}
        current_details.update({
            "preferences": preferences,
            "preferences_updated_at": datetime.utcnow()
        })
        
        consent_record.consent_details = current_details
        self.db.commit()
        
        logger.info(f"Updated consent preferences for user {user_id}")
        return {
            "status": "success",
            "message": "授权偏好已更新",
            "updated_preferences": preferences
        }
    
    def _generate_anonymous_id(self, user_id: str) -> str:
        """生成匿名用户ID"""
        salt = settings.DATA_HASH_SALT or "default_salt"
        return hashlib.sha256(f"{user_id}{salt}".encode()).hexdigest()[:16]
    
    async def _log_consent_history(
        self,
        user_id: str,
        consent_given: bool,
        details: Dict
    ):
        """记录授权历史"""
        # 这里可以记录到专门的历史表或日志系统
        logger.info(
            f"Consent history: user={user_id}, "
            f"consent={consent_given}, "
            f"timestamp={datetime.utcnow()}"
        )
    
    async def _trigger_data_cleanup(self, user_id: str):
        """触发数据清理流程"""
        # 这里应该触发异步任务来清理用户的训练数据
        logger.info(f"Triggered data cleanup for user {user_id}")
        # TODO: 实现具体的数据清理逻辑
    
    async def _query_data_usage_stats(self, anonymous_id: str) -> Dict:
        """查询数据使用统计"""
        # 这里应该查询训练数据库获取使用统计
        # 目前返回模拟数据
        return {
            "conversation_count": 0,
            "feedback_count": 0,
            "last_usage_date": None,
            "avg_quality_score": 0,
            "models_trained": [],
            "improvement_metrics": {},
            "user_benefit_score": 0
        }


# 依赖注入函数
def get_consent_service(db: Session = Depends(get_db)) -> UserConsentService:
    """获取用户授权服务实例"""
    return UserConsentService(db)