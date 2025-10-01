"""
订阅管理服务
提供订阅升级、降级、取消等功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..data.models.database import User, CreditTransaction, SubscriptionTier
from ..core.auth import SUBSCRIPTION_LIMITS
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """订阅管理服务"""
    
    def __init__(self):
        self.plan_prices = {
            SubscriptionTier.FREE: 0.0,
            SubscriptionTier.STARTER: 9.99,
            SubscriptionTier.PRO: 29.99,
            SubscriptionTier.PLUS: 49.99,
            SubscriptionTier.ENTERPRISE: 99.99
        }
        
        self.plan_features = {
            SubscriptionTier.FREE: {
                "name": "免费版",
                "description": "基础功能，适合个人用户",
                "features": ["基础分析", "有限API调用", "社区支持"],
                "monthly_credits": 100,
                "daily_limit": 10
            },
            SubscriptionTier.STARTER: {
                "name": "基础版",
                "description": "增强功能，适合小团队",
                "features": ["高级分析", "更多API调用", "邮件支持", "数据导出"],
                "monthly_credits": 1000,
                "daily_limit": 50
            },
            SubscriptionTier.PRO: {
                "name": "高级版",
                "description": "全功能版本，适合企业用户",
                "features": ["无限分析", "优先API调用", "专属支持", "高级报告", "API集成"],
                "monthly_credits": 5000,
                "daily_limit": 200
            },
            SubscriptionTier.PLUS: {
                "name": "专业版",
                "description": "高级功能，适合大型团队",
                "features": ["高级分析", "无限API调用", "优先支持", "定制报告", "团队协作"],
                "monthly_credits": 10000,
                "daily_limit": 500
            },
            SubscriptionTier.ENTERPRISE: {
                "name": "企业版",
                "description": "定制化解决方案",
                "features": ["定制功能", "无限制使用", "专属客户经理", "SLA保证", "私有部署"],
                "monthly_credits": 20000,
                "daily_limit": 1000
            }
        }
    
    def get_subscription_plans(self) -> List[Dict]:
        """获取所有订阅计划"""
        plans = []
        for tier in SubscriptionTier:
            plan_info = self.plan_features.get(tier, {})
            limits = SUBSCRIPTION_LIMITS.get(tier, {})
            
            plans.append({
                "tier": tier.value,
                "name": plan_info.get("name", tier.value.title()),
                "description": plan_info.get("description", ""),
                "price": self.plan_prices.get(tier, 0.0),
                "features": plan_info.get("features", []),
                "monthly_credits": plan_info.get("monthly_credits", 0),
                "daily_limit": plan_info.get("daily_limit", 0),
                "limits": limits
            })
        
        return plans
    
    def upgrade_subscription(
        self, 
        user: User, 
        new_tier: SubscriptionTier, 
        db: Session,
        reason: Optional[str] = None
    ) -> Dict:
        """升级用户订阅"""
        if new_tier.value <= user.subscription_tier.value:
            raise ValueError("New tier must be higher than current tier")
        
        old_tier = user.subscription_tier
        old_credits = SUBSCRIPTION_LIMITS[old_tier]["monthly_credits"]
        new_credits = SUBSCRIPTION_LIMITS[new_tier]["monthly_credits"]
        credits_diff = new_credits - old_credits
        
        # 更新用户订阅信息
        user.subscription_tier = new_tier
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        
        # 创建积分交易记录
        transaction = CreditTransaction(
            user_id=user.id,
            amount=credits_diff,
            description=f"Subscription upgrade: {old_tier.value} → {new_tier.value}",
            transaction_type="subscription_upgrade",
            expires_at=user.subscription_expires_at
        )
        
        # 更新用户积分余额
        user.credits_balance += credits_diff
        
        # 保存到数据库
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"User {user.id} upgraded from {old_tier.value} to {new_tier.value}")
        
        return {
            "success": True,
            "old_tier": old_tier.value,
            "new_tier": new_tier.value,
            "credits_added": credits_diff,
            "new_balance": user.credits_balance,
            "expires_at": user.subscription_expires_at,
            "transaction_id": transaction.id
        }
    
    def downgrade_subscription(
        self, 
        user: User, 
        new_tier: SubscriptionTier, 
        db: Session,
        reason: Optional[str] = None
    ) -> Dict:
        """降级用户订阅"""
        if new_tier.value >= user.subscription_tier.value:
            raise ValueError("New tier must be lower than current tier")
        
        old_tier = user.subscription_tier
        
        # 更新用户订阅信息
        user.subscription_tier = new_tier
        # 降级时保持原有到期时间，或设置为立即生效
        if new_tier == SubscriptionTier.FREE:
            user.subscription_expires_at = datetime.utcnow()
        else:
            # 保持原有到期时间，让用户用完当前周期
            pass
        
        # 创建降级记录
        transaction = CreditTransaction(
            user_id=user.id,
            amount=0,  # 降级不扣除积分
            description=f"Subscription downgrade: {old_tier.value} → {new_tier.value}",
            transaction_type="subscription_downgrade",
            expires_at=user.subscription_expires_at
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"User {user.id} downgraded from {old_tier.value} to {new_tier.value}")
        
        return {
            "success": True,
            "old_tier": old_tier.value,
            "new_tier": new_tier.value,
            "credits_balance": user.credits_balance,
            "expires_at": user.subscription_expires_at,
            "transaction_id": transaction.id,
            "note": "Downgrade will take effect at the end of current billing period" if new_tier != SubscriptionTier.FREE else "Downgrade effective immediately"
        }
    
    def cancel_subscription(
        self, 
        user: User, 
        db: Session,
        reason: Optional[str] = None,
        immediate: bool = False
    ) -> Dict:
        """取消用户订阅"""
        old_tier = user.subscription_tier
        
        if immediate or user.subscription_tier == SubscriptionTier.FREE:
            # 立即取消
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_expires_at = datetime.utcnow()
            effective_date = datetime.utcnow()
            note = "Subscription cancelled immediately"
        else:
            # 在当前周期结束时取消
            effective_date = user.subscription_expires_at
            note = f"Subscription will be cancelled on {effective_date.strftime('%Y-%m-%d')}"
        
        # 创建取消记录
        transaction = CreditTransaction(
            user_id=user.id,
            amount=0,
            description=f"Subscription cancelled: {old_tier.value} → FREE",
            transaction_type="subscription_cancellation",
            expires_at=effective_date
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"User {user.id} cancelled subscription from {old_tier.value}")
        
        return {
            "success": True,
            "old_tier": old_tier.value,
            "new_tier": "FREE",
            "effective_date": effective_date,
            "credits_balance": user.credits_balance,
            "transaction_id": transaction.id,
            "note": note
        }
    
    def renew_subscription(
        self, 
        user: User, 
        db: Session,
        extend_days: int = 30
    ) -> Dict:
        """续订用户订阅"""
        if user.subscription_tier == SubscriptionTier.FREE:
            raise ValueError("Cannot renew free subscription")
        
        current_tier = user.subscription_tier
        monthly_credits = SUBSCRIPTION_LIMITS[current_tier]["monthly_credits"]
        
        # 延长订阅时间
        if user.subscription_expires_at and user.subscription_expires_at > datetime.utcnow():
            # 如果还未过期，从当前到期时间延长
            user.subscription_expires_at += timedelta(days=extend_days)
        else:
            # 如果已过期，从现在开始计算
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=extend_days)
        
        # 添加月度积分
        transaction = CreditTransaction(
            user_id=user.id,
            amount=monthly_credits,
            description=f"Subscription renewal: {current_tier.value}",
            transaction_type="subscription_renewal",
            expires_at=user.subscription_expires_at
        )
        
        user.credits_balance += monthly_credits
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"User {user.id} renewed {current_tier.value} subscription")
        
        return {
            "success": True,
            "tier": current_tier.value,
            "credits_added": monthly_credits,
            "new_balance": user.credits_balance,
            "expires_at": user.subscription_expires_at,
            "transaction_id": transaction.id
        }
    
    def get_subscription_history(
        self, 
        user_id: int, 
        db: Session,
        limit: int = 50
    ) -> List[Dict]:
        """获取用户订阅历史"""
        transactions = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type.in_([
                    "subscription_upgrade",
                    "subscription_downgrade", 
                    "subscription_cancellation",
                    "subscription_renewal",
                    "subscription"
                ])
            )
        ).order_by(desc(CreditTransaction.created_at)).limit(limit).all()
        
        history = []
        for transaction in transactions:
            history.append({
                "id": transaction.id,
                "type": transaction.transaction_type,
                "description": transaction.description,
                "amount": transaction.amount,
                "created_at": transaction.created_at,
                "expires_at": transaction.expires_at
            })
        
        return history
    
    def get_subscription_analytics(self, db: Session) -> Dict:
        """获取订阅分析数据"""
        # 总订阅数
        total_subscriptions = db.query(User).count()
        
        # 按等级统计
        subscriptions_by_tier = {}
        revenue_by_tier = {}
        
        for tier in SubscriptionTier:
            count = db.query(User).filter(User.subscription_tier == tier).count()
            subscriptions_by_tier[tier.value] = count
            revenue_by_tier[tier.value] = count * self.plan_prices.get(tier, 0.0)
        
        # 活跃订阅（未过期）
        active_subscriptions = db.query(User).filter(
            User.subscription_expires_at > datetime.utcnow()
        ).count()
        
        # 计算转换率
        paid_users = sum(count for tier, count in subscriptions_by_tier.items() if tier != "free")
        conversion_rate = (paid_users / total_subscriptions * 100) if total_subscriptions > 0 else 0
        
        # 总收入
        total_revenue = sum(revenue_by_tier.values())
        
        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "subscriptions_by_tier": subscriptions_by_tier,
            "revenue_by_tier": revenue_by_tier,
            "total_revenue": total_revenue,
            "conversion_rate": conversion_rate,
            "churn_rate": max(0, 100 - conversion_rate)  # 简化计算
        }
    
    def check_subscription_expiry(self, db: Session) -> List[Dict]:
        """检查即将过期的订阅"""
        # 查找7天内过期的订阅
        expiry_threshold = datetime.utcnow() + timedelta(days=7)
        
        expiring_users = db.query(User).filter(
            and_(
                User.subscription_tier != SubscriptionTier.FREE,
                User.subscription_expires_at <= expiry_threshold,
                User.subscription_expires_at > datetime.utcnow()
            )
        ).all()
        
        expiring_list = []
        for user in expiring_users:
            days_until_expiry = (user.subscription_expires_at - datetime.utcnow()).days
            expiring_list.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "tier": user.subscription_tier.value,
                "expires_at": user.subscription_expires_at,
                "days_until_expiry": days_until_expiry
            })
        
        return expiring_list
    
    def process_expired_subscriptions(self, db: Session) -> Dict:
        """处理过期订阅"""
        # 查找已过期的付费订阅
        expired_users = db.query(User).filter(
            and_(
                User.subscription_tier != SubscriptionTier.FREE,
                User.subscription_expires_at <= datetime.utcnow()
            )
        ).all()
        
        processed_count = 0
        for user in expired_users:
            old_tier = user.subscription_tier
            
            # 降级到免费版
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_expires_at = datetime.utcnow()
            
            # 创建过期记录
            transaction = CreditTransaction(
                user_id=user.id,
                amount=0,
                description=f"Subscription expired: {old_tier.value} → FREE",
                transaction_type="subscription_expiry",
                expires_at=datetime.utcnow()
            )
            
            db.add(transaction)
            processed_count += 1
            
            logger.info(f"User {user.id} subscription expired, downgraded to FREE")
        
        db.commit()
        
        return {
            "processed_count": processed_count,
            "message": f"Processed {processed_count} expired subscriptions"
        }


# 创建全局实例
subscription_service = SubscriptionService()