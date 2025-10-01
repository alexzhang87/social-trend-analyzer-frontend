from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..data.models.database import (
    get_db, User, UserSession, SubscriptionTier, UserRole, CreditTransaction
)
from ..core.auth import get_admin_user, get_password_hash
from ..core.usage_tracker import usage_tracker
from ..core.config import settings

router = APIRouter()

# Pydantic模型
class UserListResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    role: str
    subscription_tier: str
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    subscription_tier: Optional[SubscriptionTier] = None
    password: Optional[str] = None

class UserCreateRequest(BaseModel):
    email: EmailStr  # 这里需要 email-validator 库
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE

class UsageStatsResponse(BaseModel):
    user_id: int
    username: str
    email: str
    subscription_tier: str
    daily_usage: Dict[str, int]
    monthly_usage: Dict[str, int]
    remaining_requests: Dict[str, Any]

class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    users_by_tier: Dict[str, int]
    total_requests_today: int
    total_requests_month: int
    top_users: List[Dict[str, Any]]

# 用户管理API
@router.get("/users", response_model=List[UserListResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    subscription_tier: Optional[SubscriptionTier] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（分页、搜索、筛选）"""
    query = db.query(User)
    
    # 搜索功能
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )
    
    # 筛选功能
    if role:
        query = query.filter(User.role == role)
    if subscription_tier:
        query = query.filter(User.subscription_tier == subscription_tier)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 分页
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserListResponse)
async def get_user_by_id(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取特定用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/users", response_model=UserListResponse)
async def create_user(
    user_data: UserCreateRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建新用户"""
    # 检查邮箱和用户名是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        subscription_tier=user_data.subscription_tier,
        is_active=True,
        is_verified=True  # 管理员创建的用户默认已验证
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/users/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 防止管理员修改自己的角色
    if user.id == admin_user.id and user_data.role and user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    # 更新字段
    update_data = user_data.dict(exclude_unset=True)
    
    # 特殊处理密码
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # 检查邮箱和用户名唯一性
    if "email" in update_data and update_data["email"] != user.email:
        if db.query(User).filter(User.email == update_data["email"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if "username" in update_data and update_data["username"] != user.username:
        if db.query(User).filter(User.username == update_data["username"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # 应用更新
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 防止管理员删除自己
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # 删除用户会话
    db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

# 使用统计API
@router.get("/users/{user_id}/usage", response_model=UsageStatsResponse)
async def get_user_usage(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户使用统计"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    stats = usage_tracker.get_usage_stats(user)
    
    return UsageStatsResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        subscription_tier=user.subscription_tier.value,
        daily_usage=stats["daily_usage"],
        monthly_usage=stats["monthly_usage"],
        remaining_requests=stats["remaining_requests"]
    )

@router.post("/users/{user_id}/reset-usage")
async def reset_user_usage(
    user_id: int,
    period: str = Query("daily", regex="^(daily|monthly)$"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """重置用户使用量"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = usage_tracker.reset_user_usage(user_id, period)
    
    if success:
        return {"message": f"User {user.username} {period} usage reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset usage"
        )

# 系统统计API
# 添加新的统计响应模型
class DetailedSystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    users_by_tier: Dict[str, int]
    total_requests_today: int
    total_requests_month: int
    active_users_today: int
    active_users_month: int
    daily_stats: List[Dict[str, Any]]
    feature_stats_daily: Dict[str, int]
    feature_stats_monthly: Dict[str, int]
    top_users: List[Dict[str, Any]]

# 更新系统统计API
@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取系统统计信息"""
    # 基础统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 按订阅等级统计
    users_by_tier = {}
    for tier in SubscriptionTier:
        count = db.query(User).filter(User.subscription_tier == tier).count()
        users_by_tier[tier.value] = count
    
    # 获取活跃用户（最近7天有登录）
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_active_users = db.query(User).filter(
        User.last_login >= week_ago
    ).order_by(desc(User.last_login)).limit(10).all()
    
    top_users = []
    for user in recent_active_users:
        stats = usage_tracker.get_usage_stats(user)
        top_users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "subscription_tier": user.subscription_tier.value,
            "last_login": user.last_login,
            "daily_usage": sum(stats["daily_usage"].values()),
            "monthly_usage": sum(stats["monthly_usage"].values())
        })
    
    # 获取系统使用统计
    system_stats = usage_tracker.get_system_usage_stats()
    
    return SystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        users_by_tier=users_by_tier,
        total_requests_today=system_stats["total_requests_today"],
        total_requests_month=system_stats["total_requests_month"],
        top_users=top_users
    )

# 添加详细统计API
@router.get("/stats/detailed", response_model=DetailedSystemStatsResponse)
async def get_detailed_system_stats(
    days: int = Query(7, ge=1, le=30),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取详细系统统计信息"""
    # 基础统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 按订阅等级统计
    users_by_tier = {}
    for tier in SubscriptionTier:
        count = db.query(User).filter(User.subscription_tier == tier).count()
        users_by_tier[tier.value] = count
    
    # 获取活跃用户
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_active_users = db.query(User).filter(
        User.last_login >= week_ago
    ).order_by(desc(User.last_login)).limit(10).all()
    
    top_users = []
    for user in recent_active_users:
        stats = usage_tracker.get_usage_stats(user)
        top_users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "subscription_tier": user.subscription_tier.value,
            "last_login": user.last_login,
            "daily_usage": sum(stats["daily_usage"].values()),
            "monthly_usage": sum(stats["monthly_usage"].values())
        })
    
    # 获取详细系统统计
    system_stats = usage_tracker.get_system_usage_stats(days)
    
    return DetailedSystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        users_by_tier=users_by_tier,
        total_requests_today=system_stats["total_requests_today"],
        total_requests_month=system_stats["total_requests_month"],
        active_users_today=system_stats["active_users_today"],
        active_users_month=system_stats["active_users_month"],
        daily_stats=system_stats["daily_stats"],
        feature_stats_daily=system_stats["feature_stats_daily"],
        feature_stats_monthly=system_stats["feature_stats_monthly"],
        top_users=top_users
    )

# 添加用户活动统计API
@router.get("/stats/activity")
async def get_user_activity_stats(
    days: int = Query(30, ge=1, le=90),
    admin_user: User = Depends(get_admin_user)
):
    """获取用户活动统计"""
    return usage_tracker.get_user_activity_stats(days)

# 订阅管理API
@router.post("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    subscription_tier: SubscriptionTier,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新用户订阅等级"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_tier = user.subscription_tier
    user.subscription_tier = subscription_tier
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.username} subscription updated from {old_tier.value} to {subscription_tier.value}",
        "user_id": user.id,
        "old_tier": old_tier.value,
        "new_tier": subscription_tier.value
    }

# 系统配置API
@router.get("/config")
async def get_system_config(
    admin_user: User = Depends(get_admin_user)
):
    """获取系统配置信息"""
    from ..core.auth import SUBSCRIPTION_LIMITS
    
    return {
        "subscription_limits": {
            tier.value: limits for tier, limits in SUBSCRIPTION_LIMITS.items()
        },
        "system_info": {
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "SQLite",
            "redis_available": usage_tracker.redis_client is not None,
            "admin_count": len([u for u in [admin_user] if u.role == UserRole.ADMIN])
        }
    }

@router.get("/health")
async def admin_health_check(
    admin_user: User = Depends(get_admin_user)
):
    """管理员健康检查"""
    return {
        "status": "healthy",
        "admin_user": admin_user.username,
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "redis": "connected" if usage_tracker.redis_client else "disconnected",
            "auth": "active"
        }
    }

# 扩展订阅管理功能

# 新增Pydantic模型
class BatchSubscriptionUpdateRequest(BaseModel):
    user_ids: List[int]
    subscription_tier: SubscriptionTier
    reason: Optional[str] = None

class SubscriptionPlanResponse(BaseModel):
    tier: str
    name: str
    description: str
    daily_limits: Dict[str, int]
    monthly_limits: Dict[str, int]
    features: List[str]
    price: Optional[float] = None

class SubscriptionStatsResponse(BaseModel):
    total_subscriptions: int
    subscriptions_by_tier: Dict[str, int]
    revenue_by_tier: Dict[str, float]
    recent_upgrades: List[Dict[str, Any]]
    recent_downgrades: List[Dict[str, Any]]
    churn_rate: float
    upgrade_rate: float

class SubscriptionHistoryResponse(BaseModel):
    id: int
    user_id: int
    username: str
    old_tier: str
    new_tier: str
    changed_by: str
    reason: Optional[str]
    timestamp: datetime

# 批量订阅管理API
@router.post("/subscriptions/batch-update")
async def batch_update_subscriptions(
    request: BatchSubscriptionUpdateRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """批量更新用户订阅等级"""
    updated_users = []
    failed_users = []
    
    for user_id in request.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            failed_users.append({"user_id": user_id, "reason": "User not found"})
            continue
        
        old_tier = user.subscription_tier
        user.subscription_tier = request.subscription_tier
        user.updated_at = datetime.utcnow()
        
        updated_users.append({
            "user_id": user.id,
            "username": user.username,
            "old_tier": old_tier.value,
            "new_tier": request.subscription_tier.value
        })
    
    db.commit()
    
    return {
        "message": f"Updated {len(updated_users)} users to {request.subscription_tier.value}",
        "updated_users": updated_users,
        "failed_users": failed_users,
        "total_requested": len(request.user_ids),
        "successful": len(updated_users),
        "failed": len(failed_users)
    }

# 订阅计划管理API
@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    admin_user: User = Depends(get_admin_user)
):
    """获取所有订阅计划信息"""
    from ..core.auth import SUBSCRIPTION_LIMITS
    
    plans = []
    plan_details = {
        SubscriptionTier.FREE: {
            "name": "免费版",
            "description": "基础功能，适合个人用户",
            "features": ["基础分析", "有限API调用", "社区支持"],
            "price": 0.0
        },
        SubscriptionTier.BASIC: {
            "name": "基础版",
            "description": "增强功能，适合小团队",
            "features": ["高级分析", "更多API调用", "邮件支持", "数据导出"],
            "price": 9.99
        },
        SubscriptionTier.PREMIUM: {
            "name": "高级版",
            "description": "全功能版本，适合企业用户",
            "features": ["无限分析", "优先API调用", "专属支持", "高级报告", "API集成"],
            "price": 29.99
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "企业版",
            "description": "定制化解决方案",
            "features": ["定制功能", "无限制使用", "专属客户经理", "SLA保证", "私有部署"],
            "price": 99.99
        }
    }
    
    for tier in SubscriptionTier:
        limits = SUBSCRIPTION_LIMITS.get(tier, {})
        details = plan_details.get(tier, {})
        
        plans.append(SubscriptionPlanResponse(
            tier=tier.value,
            name=details.get("name", tier.value.title()),
            description=details.get("description", f"{tier.value} subscription plan"),
            daily_limits=limits.get("daily", {}),
            monthly_limits=limits.get("monthly", {}),
            features=details.get("features", []),
            price=details.get("price")
        ))
    
    return plans

# 订阅统计API
@router.get("/subscriptions/stats", response_model=SubscriptionStatsResponse)
async def get_subscription_stats(
    days: int = Query(30, ge=1, le=90),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取订阅统计信息"""
    # 基础统计
    total_subscriptions = db.query(User).count()
    
    # 按订阅等级统计
    subscriptions_by_tier = {}
    revenue_by_tier = {}
    
    plan_prices = {
        SubscriptionTier.FREE: 0.0,
        SubscriptionTier.STARTER: 19.99,
        SubscriptionTier.PRO: 199.0,
        SubscriptionTier.PLUS: 599.0,
        SubscriptionTier.ENTERPRISE: 999.0
    }
    
    for tier in SubscriptionTier:
        count = db.query(User).filter(User.subscription_tier == tier).count()
        subscriptions_by_tier[tier.value] = count
        revenue_by_tier[tier.value] = count * plan_prices.get(tier, 0.0)
    
    # 计算转换率（简化版本）
    total_paid = sum(count for tier, count in subscriptions_by_tier.items() if tier != "free")
    upgrade_rate = (total_paid / total_subscriptions * 100) if total_subscriptions > 0 else 0
    churn_rate = 5.0  # 模拟数据，实际应该从历史数据计算
    
    return SubscriptionStatsResponse(
        total_subscriptions=total_subscriptions,
        subscriptions_by_tier=subscriptions_by_tier,
        revenue_by_tier=revenue_by_tier,
        recent_upgrades=[],  # 需要订阅历史表来实现
        recent_downgrades=[],  # 需要订阅历史表来实现
        churn_rate=churn_rate,
        upgrade_rate=upgrade_rate
    )

# 订阅历史查询API
@router.get("/subscriptions/history")
async def get_subscription_history(
    user_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=90),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取订阅变更历史"""
    # 注意：这需要一个订阅历史表来完整实现
    # 这里返回模拟数据作为示例
    return {
        "message": "Subscription history feature requires a subscription_history table",
        "note": "This would track all subscription tier changes with timestamps, reasons, and admin info",
        "suggested_implementation": {
            "table_structure": {
                "id": "Primary key",
                "user_id": "Foreign key to users",
                "old_tier": "Previous subscription tier",
                "new_tier": "New subscription tier",
                "changed_by": "Admin user who made the change",
                "reason": "Optional reason for change",
                "timestamp": "When the change occurred"
            }
        }
    }

# 订阅分析API
@router.get("/subscriptions/analytics")
async def get_subscription_analytics(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取订阅分析数据"""
    # 基础统计
    total_users = db.query(User).count()
    
    # 按订阅等级分组统计
    tier_stats = {}
    for tier in SubscriptionTier:
        count = db.query(User).filter(User.subscription_tier == tier).count()
        percentage = (count / total_users * 100) if total_users > 0 else 0
        tier_stats[tier.value] = {
            "count": count,
            "percentage": round(percentage, 2)
        }
    
    # 收入分析
    plan_prices = {
        SubscriptionTier.FREE: 0.0,
        SubscriptionTier.BASIC: 9.99,
        SubscriptionTier.PREMIUM: 29.99,
        SubscriptionTier.ENTERPRISE: 99.99
    }
    
    total_revenue = 0
    revenue_breakdown = {}
    
    for tier in SubscriptionTier:
        count = tier_stats[tier.value]["count"]
        price = plan_prices.get(tier, 0.0)
        revenue = count * price
        total_revenue += revenue
        revenue_breakdown[tier.value] = revenue
    
    return {
        "period": period,
        "total_users": total_users,
        "tier_distribution": tier_stats,
        "revenue_analysis": {
            "total_monthly_revenue": total_revenue,
            "revenue_by_tier": revenue_breakdown,
            "average_revenue_per_user": round(total_revenue / total_users, 2) if total_users > 0 else 0
        },
        "growth_metrics": {
            "note": "Growth metrics require historical data tracking",
            "suggested_metrics": [
                "Monthly Recurring Revenue (MRR)",
                "Customer Lifetime Value (CLV)",
                "Churn Rate",
                "Upgrade/Downgrade Rates",
                "New Subscriber Growth"
            ]
        }
    }

# 订阅操作日志API
@router.get("/subscriptions/logs")
async def get_subscription_logs(
    days: int = Query(7, ge=1, le=30),
    action: Optional[str] = Query(None, regex="^(upgrade|downgrade|create|cancel)$"),
    admin_user: User = Depends(get_admin_user)
):
    """获取订阅操作日志"""
    # 这需要一个专门的日志系统来实现
    return {
        "message": "Subscription logging system not yet implemented",
        "note": "This would track all subscription-related operations",
        "suggested_log_structure": {
            "timestamp": "When the action occurred",
            "action": "Type of action (upgrade, downgrade, etc.)",
            "user_id": "Affected user",
            "admin_id": "Admin who performed the action",
            "old_value": "Previous state",
            "new_value": "New state",
            "metadata": "Additional context"
        }
    }

class CreditAdjustRequest(BaseModel):
    amount: int
    description: Optional[str] = "Admin manual adjustment"

@router.post("/users/{user_id}/credits/adjust")
async def adjust_user_credits(
    user_id: int,
    request: CreditAdjustRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """按用户ID调整积分（正数为充值，负数为扣减）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新余额
    user.credits_balance = user.credits_balance + request.amount
    
    # 记录交易
    tx = CreditTransaction(
        user_id=user.id,
        amount=request.amount,
        description=request.description or "Admin manual adjustment",
        transaction_type="admin_adjustment"
    )
    db.add(tx)
    db.commit()
    db.refresh(user)
    db.refresh(tx)
    
    return {
        "user_id": user.id,
        "email": user.email,
        "amount": request.amount,
        "new_balance": user.credits_balance,
        "transaction_id": tx.id,
        "description": tx.description
    }

@router.post("/users/by-email/{email}/credits/adjust")
async def adjust_user_credits_by_email(
    email: EmailStr,
    request: CreditAdjustRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """按用户邮箱调整积分（正数为充值，负数为扣减）"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新余额
    user.credits_balance = user.credits_balance + request.amount
    
    # 记录交易
    tx = CreditTransaction(
        user_id=user.id,
        amount=request.amount,
        description=request.description or "Admin manual adjustment",
        transaction_type="admin_adjustment"
    )
    db.add(tx)
    db.commit()
    db.refresh(user)
    db.refresh(tx)
    
    return {
        "user_id": user.id,
        "email": user.email,
        "amount": request.amount,
        "new_balance": user.credits_balance,
        "transaction_id": tx.id,
        "description": tx.description
    }