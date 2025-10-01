# 积分和订阅管理API

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..data.models.database import get_db, User, CreditTransaction, SubscriptionTier
from ..core.auth import get_current_active_user, SUBSCRIPTION_LIMITS
from ..data.models.schemas import CreditTransactionCreate, CreditTransactionResponse
from ..data.models.schemas import SubscriptionUpdate, SubscriptionResponse

router = APIRouter(prefix="/api/v1/credits", tags=["credits"])

@router.get("/balance", response_model=dict)
async def get_credit_balance(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的积分余额"""
    subscription_tier = current_user.subscription_tier
    monthly_credits = SUBSCRIPTION_LIMITS[subscription_tier]["monthly_credits"]
    
    return {
        "credits_balance": current_user.credits_balance,
        "subscription_tier": subscription_tier.value,
        "monthly_credits": monthly_credits,
        "subscription_expires_at": current_user.subscription_expires_at
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