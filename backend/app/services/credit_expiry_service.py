# 积分过期管理服务

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Optional
import logging
from ..data.models.database import User, CreditTransaction
from ..core.redis_client import redis_client

logger = logging.getLogger(__name__)

class CreditExpiryService:
    """积分过期管理服务"""
    
    def __init__(self):
        self.cache_prefix = "credit_expiry:"
        self.cache_ttl = 3600  # 1小时缓存
        self.batch_cache_prefix = "credit_batch:"
        self.user_cache_keys = "user_cache_keys:"
    
    def get_user_valid_credits(self, user_id: int, db: Session) -> int:
        """获取用户有效积分余额（排除已过期的积分）"""
        cache_key = f"{self.cache_prefix}valid_credits:{user_id}"
        
        # 尝试从缓存获取
        try:
            cached_balance = redis_client.get(cache_key)
            if cached_balance is not None:
                return int(cached_balance)
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")
        
        # 计算有效积分
        valid_balance = self._calculate_valid_credits(user_id, db)
        
        # 缓存结果
        try:
            redis_client.setex(cache_key, self.cache_ttl, valid_balance)
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
        
        return valid_balance
    
    def _calculate_valid_credits(self, user_id: int, db: Session) -> int:
        """计算用户的有效积分余额（优化版本）"""
        now = datetime.utcnow()
        
        # 分别获取积分增加和消费记录
        credit_additions = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.amount > 0
            )
        ).all()
        
        total_consumption = db.query(func.sum(CreditTransaction.amount)).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.amount < 0
            )
        ).scalar() or 0
        
        # 计算有效的积分增加（排除过期的）
        valid_additions = 0
        for credit in credit_additions:
            if credit.expires_at is None or credit.expires_at > now:
                valid_additions += credit.amount
        
        # 总的有效积分 = 有效增加 + 消费（消费是负数）
        valid_balance = valid_additions + total_consumption
        
        return max(0, valid_balance)
    
    def get_expiring_credits(self, user_id: int, days_ahead: int, db: Session) -> List[Dict]:
        """获取即将过期的积分"""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        expiring_transactions = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.amount > 0,  # 只查看积分增加的记录
                CreditTransaction.expires_at.isnot(None),
                CreditTransaction.expires_at <= future_date,
                CreditTransaction.expires_at > datetime.utcnow()
            )
        ).order_by(CreditTransaction.expires_at.asc()).all()
        
        return [
            {
                "id": t.id,
                "amount": t.amount,
                "description": t.description,
                "expires_at": t.expires_at,
                "days_until_expiry": (t.expires_at - datetime.utcnow()).days
            }
            for t in expiring_transactions
        ]
    
    def expire_credits(self, db: Session) -> Dict[str, int]:
        """清理过期积分"""
        now = datetime.utcnow()
        
        # 查找所有过期的积分增加记录
        expired_transactions = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.amount > 0,
                CreditTransaction.expires_at.isnot(None),
                CreditTransaction.expires_at <= now
            )
        ).all()
        
        expired_count = 0
        total_expired_amount = 0
        affected_users = set()
        
        for transaction in expired_transactions:
            # 创建过期记录
            expiry_transaction = CreditTransaction(
                user_id=transaction.user_id,
                amount=-transaction.amount,
                description=f"Credits expired from: {transaction.description}",
                transaction_type="expiry",
                expires_at=None
            )
            
            db.add(expiry_transaction)
            expired_count += 1
            total_expired_amount += transaction.amount
            affected_users.add(transaction.user_id)
        
        # 更新用户积分余额
        for user_id in affected_users:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # 重新计算有效积分
                valid_credits = self._calculate_valid_credits(user_id, db)
                user.credits_balance = valid_credits
                
                # 清除所有相关缓存
                self.invalidate_user_cache(user_id)
        
        db.commit()
        
        logger.info(f"Expired {expired_count} credit transactions, "
                   f"total amount: {total_expired_amount}, "
                   f"affected users: {len(affected_users)}")
        
        return {
            "expired_transactions": expired_count,
            "total_expired_amount": total_expired_amount,
            "affected_users": len(affected_users)
        }
    
    def consume_credits_fifo(self, user_id: int, amount: int, db: Session, description: str = "Credit consumption") -> bool:
        """按FIFO原则消费积分（优先使用即将过期的积分）"""
        # 检查总的有效积分是否足够
        valid_balance = self.get_user_valid_credits(user_id, db)
        if valid_balance < amount:
            return False
        
        # 获取所有可用的积分记录，按过期时间排序
        now = datetime.utcnow()
        available_credits = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.amount > 0,
                or_(
                    CreditTransaction.expires_at.is_(None),
                    CreditTransaction.expires_at > now
                )
            )
        ).order_by(
            CreditTransaction.expires_at.asc().nulls_last()
        ).all()
        
        # 计算每个积分记录的可用余额
        credit_balances = {}
        for credit in available_credits:
            # 计算这个积分记录已经被消费了多少
            consumed = db.query(func.sum(CreditTransaction.amount)).filter(
                and_(
                    CreditTransaction.user_id == user_id,
                    CreditTransaction.amount < 0,
                    CreditTransaction.created_at >= credit.created_at
                )
            ).scalar() or 0
            
            available_amount = credit.amount + consumed  # consumed是负数
            if available_amount > 0:
                credit_balances[credit.id] = {
                    "available": available_amount,
                    "expires_at": credit.expires_at,
                    "description": credit.description
                }
        
        # 按FIFO原则消费积分
        remaining_to_consume = amount
        consumption_records = []
        
        for credit_id, balance_info in credit_balances.items():
            if remaining_to_consume <= 0:
                break
            
            consume_from_this = min(remaining_to_consume, balance_info["available"])
            
            consumption_records.append({
                "source_credit_id": credit_id,
                "amount": consume_from_this,
                "source_description": balance_info["description"]
            })
            
            remaining_to_consume -= consume_from_this
        
        # 创建消费记录
        for record in consumption_records:
            transaction = CreditTransaction(
                user_id=user_id,
                amount=-record["amount"],
                description=f"{description} (from: {record['source_description']})",
                transaction_type="consumption",
                expires_at=None
            )
            db.add(transaction)
        
        # 更新用户积分余额
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits_balance -= amount
            
            # 清除所有相关缓存
            self.invalidate_user_cache(user_id)
        
        db.commit()
        return True
    
    def get_credit_breakdown(self, user_id: int, db: Session) -> Dict:
        """获取用户积分详细分解"""
        now = datetime.utcnow()
        
        # 获取所有积分增加记录
        credit_additions = db.query(CreditTransaction).filter(
            and_(
                CreditTransaction.user_id == user_id,
                CreditTransaction.amount > 0
            )
        ).order_by(CreditTransaction.created_at.desc()).all()
        
        breakdown = {
            "total_earned": 0,
            "total_consumed": 0,
            "valid_balance": 0,
            "expired_amount": 0,
            "expiring_soon": [],
            "credit_sources": []
        }
        
        for credit in credit_additions:
            is_expired = credit.expires_at and credit.expires_at <= now
            
            # 计算这个积分记录的消费情况
            consumed = db.query(func.sum(CreditTransaction.amount)).filter(
                and_(
                    CreditTransaction.user_id == user_id,
                    CreditTransaction.amount < 0,
                    CreditTransaction.created_at >= credit.created_at
                )
            ).scalar() or 0
            
            remaining = credit.amount + consumed  # consumed是负数
            
            breakdown["total_earned"] += credit.amount
            breakdown["total_consumed"] += abs(consumed)
            
            if is_expired:
                breakdown["expired_amount"] += remaining if remaining > 0 else 0
            else:
                breakdown["valid_balance"] += remaining if remaining > 0 else 0
                
                # 检查是否即将过期
                if credit.expires_at and (credit.expires_at - now).days <= 30:
                    breakdown["expiring_soon"].append({
                        "amount": remaining if remaining > 0 else 0,
                        "expires_at": credit.expires_at,
                        "days_until_expiry": (credit.expires_at - now).days
                    })
            
            breakdown["credit_sources"].append({
                "id": credit.id,
                "amount": credit.amount,
                "remaining": remaining if remaining > 0 else 0,
                "description": credit.description,
                "created_at": credit.created_at,
                "expires_at": credit.expires_at,
                "is_expired": is_expired
            })
        
        return breakdown
    
    def invalidate_user_cache(self, user_id: int):
        """清除用户相关的所有缓存"""
        try:
            cache_key = f"{self.cache_prefix}valid_credits:{user_id}"
            breakdown_key = f"{self.cache_prefix}breakdown:{user_id}"
            
            redis_client.delete(cache_key)
            redis_client.delete(breakdown_key)
            
            # 从用户缓存键集合中移除
            user_keys_set = f"{self.user_cache_keys}{user_id}"
            redis_client.delete(user_keys_set)
            
        except Exception as e:
            logger.warning(f"Cache invalidation error for user {user_id}: {e}")
    
    def batch_update_user_credits(self, user_ids: List[int], db: Session):
        """批量更新多个用户的积分缓存"""
        try:
            pipe = redis_client.pipeline()
            
            for user_id in user_ids:
                # 计算有效积分
                valid_credits = self._calculate_valid_credits(user_id, db)
                cache_key = f"{self.cache_prefix}valid_credits:{user_id}"
                
                # 批量设置缓存
                pipe.setex(cache_key, self.cache_ttl, valid_credits)
                
                # 记录用户缓存键
                user_keys_set = f"{self.user_cache_keys}{user_id}"
                pipe.sadd(user_keys_set, cache_key)
                pipe.expire(user_keys_set, self.cache_ttl)
            
            pipe.execute()
            logger.info(f"Batch updated credits cache for {len(user_ids)} users")
            
        except Exception as e:
            logger.error(f"Batch cache update error: {e}")
    
    def get_cached_breakdown(self, user_id: int, db: Session) -> Dict:
        """获取缓存的积分分解信息"""
        cache_key = f"{self.cache_prefix}breakdown:{user_id}"
        
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        # 计算并缓存
        breakdown = self.get_credit_breakdown(user_id, db)
        
        try:
            import json
            redis_client.setex(cache_key, self.cache_ttl, json.dumps(breakdown, default=str))
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
        
        return breakdown
    
    def get_users_with_expiring_credits(self, days_ahead: int, db: Session) -> List[Dict]:
        """获取有积分即将过期的用户列表"""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        # 查找即将过期的积分记录
        expiring_credits = db.query(
            CreditTransaction.user_id,
            func.sum(CreditTransaction.amount).label('expiring_amount'),
            func.min(CreditTransaction.expires_at).label('earliest_expiry')
        ).filter(
            and_(
                CreditTransaction.amount > 0,
                CreditTransaction.expires_at.isnot(None),
                CreditTransaction.expires_at <= future_date,
                CreditTransaction.expires_at > datetime.utcnow()
            )
        ).group_by(CreditTransaction.user_id).all()
        
        users_to_notify = []
        for record in expiring_credits:
            # 获取用户信息
            user = db.query(User).filter(User.id == record.user_id).first()
            if user and user.email:
                users_to_notify.append({
                    "user_id": record.user_id,
                    "email": user.email,
                    "username": user.username,
                    "expiring_amount": record.expiring_amount,
                    "earliest_expiry": record.earliest_expiry,
                    "days_until_expiry": (record.earliest_expiry - datetime.utcnow()).days
                })
        
        return users_to_notify
    
    def send_expiry_notifications(self, db: Session) -> Dict[str, int]:
        """发送积分过期提醒通知"""
        # 获取3天内即将过期的用户
        users_3_days = self.get_users_with_expiring_credits(3, db)
        # 获取7天内即将过期的用户
        users_7_days = self.get_users_with_expiring_credits(7, db)
        
        notifications_sent = 0
        
        # 这里可以集成邮件服务或其他通知方式
        for user in users_3_days:
            logger.info(f"User {user['username']} has {user['expiring_amount']} credits expiring in {user['days_until_expiry']} days")
            # TODO: 发送邮件通知
            notifications_sent += 1
        
        for user in users_7_days:
            if user not in users_3_days:  # 避免重复通知
                logger.info(f"User {user['username']} has {user['expiring_amount']} credits expiring in {user['days_until_expiry']} days")
                # TODO: 发送邮件通知
                notifications_sent += 1
        
        return {
            "notifications_sent": notifications_sent,
            "users_3_days": len(users_3_days),
            "users_7_days": len(users_7_days)
        }

# 全局服务实例
credit_expiry_service = CreditExpiryService()