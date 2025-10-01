# 积分和订阅管理API

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..data.models.database import get_db, User, CreditTransaction, SubscriptionTier
from ..core.auth import get_current_active_user, SUBSCRIPTION_LIMITS
from ..services.credit_expiry_service import credit_expiry_service
from ..services.subscription_service import subscription_service

# Schema definitions
class CreditTransactionCreate(BaseModel):
    amount: int
    description: str
    transaction_type: str

class CreditTransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: int
    description: str
    transaction_type: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    tier: str

class SubscriptionResponse(BaseModel):
    subscription_tier: str
    subscription_expires_at: Optional[datetime] = None
    credits_balance: int

router = APIRouter(prefix="/api/v1/credits", tags=["credits"])

@router.get("/balance", response_model=dict)
async def get_credit_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的积分余额"""
    subscription_tier = current_user.subscription_tier
    monthly_credits = SUBSCRIPTION_LIMITS[subscription_tier]["monthly_credits"]
    
    # 获取有效积分余额（排除过期积分）
    valid_balance = credit_expiry_service.get_user_valid_credits(current_user.id, db)
    
    # 获取即将过期的积分
    expiring_credits = credit_expiry_service.get_expiring_credits(current_user.id, 30, db)
    
    return {
        "credits_balance": valid_balance,
        "stored_balance": current_user.credits_balance,  # 数据库中存储的余额
        "subscription_tier": subscription_tier.value,
        "monthly_credits": monthly_credits,
        "subscription_expires_at": current_user.subscription_expires_at,
        "expiring_soon": expiring_credits
    }

@router.get("/transactions", response_model=List[CreditTransactionResponse])
async def get_credit_transactions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取用户的积分交易历史"""
    transactions = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == current_user.id
    ).order_by(
        CreditTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return transactions

@router.post("/purchase", response_model=CreditTransactionResponse)
async def purchase_credits(
    package: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """购买积分包"""
    # 定义积分包配置
    credit_packages = {
        "small": {"credits": 10, "price": 4.99, "expires_in_days": 180},
        "medium": {"credits": 30, "price": 11.99, "expires_in_days": 180},
        "large": {"credits": 75, "price": 24.99, "expires_in_days": 180}
     }

@router.post("/admin/send-expiry-notifications")
async def send_expiry_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """管理员手动发送积分过期提醒"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = credit_expiry_service.send_expiry_notifications(db)
    
    return {
        "message": "Expiry notifications sent successfully",
        "details": result
    }

@router.get("/admin/expiring-users")
async def get_expiring_users(
    days: int = Query(7, description="查看几天内过期的用户", ge=1, le=30),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """管理员查看有积分即将过期的用户"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = credit_expiry_service.get_users_with_expiring_credits(days, db)
    
    return {
        "days_ahead": days,
        "users_count": len(users),
        "users": users
    }
    
    # 验证包类型
    if package not in credit_packages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package type. Available options: {', '.join(credit_packages.keys())}"
        )
    
    # 获取包配置
    package_config = credit_packages[package]
    
    # 创建交易记录
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=package_config["credits"],
        description=f"Credit package purchase: {package}",
        transaction_type="purchase",
        expires_at=datetime.utcnow() + timedelta(days=package_config["expires_in_days"])
    )
    
    # 更新用户积分余额
    current_user.credits_balance += package_config["credits"]
    
    # 保存到数据库
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

@router.post("/subscription", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新用户订阅计划"""
    # 验证订阅类型
    try:
        new_tier = SubscriptionTier(subscription_data.tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription tier. Available options: {[tier.value for tier in SubscriptionTier]}"
        )
    
    # 如果是降级，不重置积分
    if new_tier.value < current_user.subscription_tier.value:
        current_user.subscription_tier = new_tier
        current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        db.commit()
        return {
            "subscription_tier": new_tier.value,
            "subscription_expires_at": current_user.subscription_expires_at,
            "credits_balance": current_user.credits_balance
        }
    
    # 如果是升级或续订，重置月度积分
    old_tier = current_user.subscription_tier
    current_user.subscription_tier = new_tier
    current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
    
    # 计算积分变更量
    old_credits = SUBSCRIPTION_LIMITS[old_tier]["monthly_credits"]
    new_credits = SUBSCRIPTION_LIMITS[new_tier]["monthly_credits"]
    credits_diff = new_credits - old_credits
    
    # 只有正向差值才增加积分
    if credits_diff > 0:
        # 创建积分交易记录
        transaction = CreditTransaction(
            user_id=current_user.id,
            amount=credits_diff,
            description=f"Subscription upgrade: {old_tier.value} → {new_tier.value}",
            transaction_type="subscription",
            expires_at=current_user.subscription_expires_at
        )
        
        # 更新用户积分余额
        current_user.credits_balance += credits_diff
        
        # 保存到数据库
        db.add(transaction)
    
    db.commit()
    
    if credits_diff > 0:
        db.refresh(transaction)
    
    return {
        "subscription_tier": new_tier.value,
        "subscription_expires_at": current_user.subscription_expires_at,
        "credits_balance": current_user.credits_balance
    }

@router.post("/reset", response_model=dict)
async def reset_monthly_credits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """管理员重置用户的月度积分"""
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    
    # 查询所有有效订阅用户
    active_subscribers = db.query(User).filter(
        User.subscription_expires_at > datetime.utcnow()
    ).all()
    
    reset_count = 0
    for user in active_subscribers:
        tier = user.subscription_tier
        monthly_credits = SUBSCRIPTION_LIMITS[tier]["monthly_credits"]
        
        # 创建积分交易记录
        transaction = CreditTransaction(
            user_id=user.id,
            amount=monthly_credits,
            description=f"Monthly credits reset: {tier.value}",
            transaction_type="subscription",
            expires_at=user.subscription_expires_at
        )
        
        # 更新用户积分余额
        user.credits_balance += monthly_credits
        
        # 保存到数据库
        db.add(transaction)
        reset_count += 1
    
    db.commit()
    
    return {"message": f"Reset monthly credits for {reset_count} users"}


# 新的订阅管理API端点

@router.get("/subscription/plans")
async def get_subscription_plans():
    """获取所有订阅计划"""
    return subscription_service.get_subscription_plans()


@router.post("/subscription/upgrade")
async def upgrade_subscription(
    new_tier: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """升级用户订阅"""
    try:
        tier = SubscriptionTier(new_tier)
        result = subscription_service.upgrade_subscription(
            user=current_user,
            new_tier=tier,
            db=db,
            reason=reason
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error upgrading subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade subscription"
        )


@router.post("/subscription/downgrade")
async def downgrade_subscription(
    new_tier: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """降级用户订阅"""
    try:
        tier = SubscriptionTier(new_tier)
        result = subscription_service.downgrade_subscription(
            user=current_user,
            new_tier=tier,
            db=db,
            reason=reason
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error downgrading subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to downgrade subscription"
        )


@router.post("/subscription/cancel")
async def cancel_subscription(
    reason: Optional[str] = None,
    immediate: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消用户订阅"""
    try:
        result = subscription_service.cancel_subscription(
            user=current_user,
            db=db,
            reason=reason,
            immediate=immediate
        )
        return result
    except Exception as e:
        logger.error(f"Error cancelling subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/subscription/renew")
async def renew_subscription(
    extend_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """续订用户订阅"""
    try:
        result = subscription_service.renew_subscription(
            user=current_user,
            db=db,
            extend_days=extend_days
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error renewing subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to renew subscription"
        )


@router.get("/subscription/history")
async def get_subscription_history(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户订阅历史"""
    try:
        history = subscription_service.get_subscription_history(
            user_id=current_user.id,
            db=db,
            limit=limit
        )
        return {
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting subscription history for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription history"
        )


@router.get("/subscription/expiring")
async def get_expiring_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查当前用户订阅是否即将过期"""
    if current_user.subscription_tier == SubscriptionTier.FREE:
        return {
            "is_expiring": False,
            "message": "Free subscription does not expire"
        }
    
    if not current_user.subscription_expires_at:
        return {
            "is_expiring": False,
            "message": "No expiration date set"
        }
    
    days_until_expiry = (current_user.subscription_expires_at - datetime.utcnow()).days
    is_expiring = days_until_expiry <= 7
    
    return {
        "is_expiring": is_expiring,
        "days_until_expiry": days_until_expiry,
        "expires_at": current_user.subscription_expires_at,
        "current_tier": current_user.subscription_tier.value,
        "message": f"Subscription expires in {days_until_expiry} days" if is_expiring else "Subscription is not expiring soon"
    }

@router.get("/breakdown", response_model=dict)
async def get_credit_breakdown(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户积分详细分解"""
    breakdown = credit_expiry_service.get_credit_breakdown(current_user.id, db)
    return breakdown

@router.get("/expiring", response_model=List[dict])
async def get_expiring_credits(
    days_ahead: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取即将过期的积分"""
    expiring_credits = credit_expiry_service.get_expiring_credits(
        current_user.id, days_ahead, db
    )
    return expiring_credits

@router.post("/expire", response_model=dict)
async def expire_credits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """手动清理过期积分（管理员功能）"""
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    
    result = credit_expiry_service.expire_credits(db)
    return result

@router.get("/history", response_model=List[dict])
async def get_credit_history(
    skip: int = 0,
    limit: int = 50,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取积分使用历史"""
    query = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == current_user.id
    )
    
    # 按交易类型过滤
    if transaction_type:
        query = query.filter(CreditTransaction.transaction_type == transaction_type)
    
    # 按日期范围过滤
    if start_date:
        query = query.filter(CreditTransaction.created_at >= start_date)
    if end_date:
        query = query.filter(CreditTransaction.created_at <= end_date)
    
    transactions = query.order_by(
        CreditTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    # 转换为字典格式并添加额外信息
    history = []
    for transaction in transactions:
        item = {
            "id": transaction.id,
            "amount": transaction.amount,
            "description": transaction.description,
            "transaction_type": transaction.transaction_type,
            "created_at": transaction.created_at,
            "expires_at": transaction.expires_at,
            "is_expired": transaction.expires_at and transaction.expires_at <= datetime.utcnow() if transaction.expires_at else False
        }
        history.append(item)
    
    return history

@router.get("/usage-statistics")
async def get_credit_usage_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, description="统计天数", ge=1, le=365)
):
    """获取积分使用统计"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, case
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按交易类型统计
    type_stats = db.query(
        CreditTransaction.transaction_type,
        func.sum(case(
            (CreditTransaction.amount > 0, CreditTransaction.amount),
            else_=0
        )).label('total_earned'),
        func.sum(case(
            (CreditTransaction.amount < 0, abs(CreditTransaction.amount)),
            else_=0
        )).label('total_consumed'),
        func.count(CreditTransaction.id).label('transaction_count')
    ).filter(
        and_(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.created_at >= start_date
        )
    ).group_by(CreditTransaction.transaction_type).all()
    
    # 按日期统计（最近7天）
    daily_stats = []
    for i in range(7):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_data = db.query(
            func.sum(case(
                (CreditTransaction.amount > 0, CreditTransaction.amount),
                else_=0
            )).label('earned'),
            func.sum(case(
                (CreditTransaction.amount < 0, abs(CreditTransaction.amount)),
                else_=0
            )).label('consumed')
        ).filter(
            and_(
                CreditTransaction.user_id == current_user.id,
                CreditTransaction.created_at >= day_start,
                CreditTransaction.created_at < day_end
            )
        ).first()
        
        daily_stats.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "earned": day_data.earned or 0,
            "consumed": day_data.consumed or 0
        })
    
    # 获取当前积分状态（使用缓存）
    credit_breakdown = credit_expiry_service.get_cached_breakdown(current_user.id, db)
    
    return {
        "period_days": days,
        "type_statistics": [
            {
                "transaction_type": stat.transaction_type,
                "total_earned": stat.total_earned or 0,
                "total_consumed": stat.total_consumed or 0,
                "transaction_count": stat.transaction_count
            }
            for stat in type_stats
        ],
        "daily_statistics": daily_stats,
        "current_status": {
            "valid_balance": credit_breakdown["valid_balance"],
            "total_earned": credit_breakdown["total_earned"],
            "total_consumed": credit_breakdown["total_consumed"],
            "expired_amount": credit_breakdown["expired_amount"],
            "expiring_soon_count": len(credit_breakdown["expiring_soon"])
        }
    }