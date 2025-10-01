from datetime import datetime, timedelta
from typing import Optional, Union, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..data.models.database import get_db, User, UserSession, SubscriptionTier, UserRole, CreditTransaction
from .config import settings
from functools import wraps

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# 订阅权限配置
SUBSCRIPTION_LIMITS = {
    SubscriptionTier.FREE: {
        "monthly_credits": 3,
        "credits_per_analysis": 1,
        "daily_requests": 5,
        "features": ["basic_analysis"]
    },
    SubscriptionTier.STARTER: {
        "monthly_credits": 30,
        "credits_per_analysis": 2,
        "daily_requests": 20,
        "features": ["basic_analysis", "advanced_analysis", "email_support"]
    },
    SubscriptionTier.PRO: {
        "monthly_credits": 120,
        "credits_per_analysis": 3,
        "daily_requests": 50,
        "features": ["basic_analysis", "advanced_analysis", "business_insights", 
                    "pdf_reports", "email_support", "priority_support"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def check_subscription_limit(user: User, feature: str, batch_size: int = 1) -> bool:
    """检查用户订阅限制"""
    limits = SUBSCRIPTION_LIMITS.get(user.subscription_tier)
    if not limits:
        return False
    
    # 检查功能权限
    if feature not in limits["features"]:
        return False
    
    # 检查批量大小限制
    if "batch_size" in limits and limits["batch_size"] != -1 and batch_size > limits["batch_size"]:
        return False
    
    return True

def check_credit_balance(user: User, feature: str) -> bool:
    """检查用户积分余额是否足够"""
    required_credits = 0
    
    if feature == "basic_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.FREE]["credits_per_analysis"]
    elif feature == "advanced_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.STARTER]["credits_per_analysis"]
    elif feature in ["business_insights", "pdf_reports"]:
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.PRO]["credits_per_analysis"]
    else:
        return False
        
    return user.credits_balance >= required_credits

def consume_credits(db: Session, user: User, feature: str) -> bool:
    """消耗用户积分"""
    # 确定需要消耗的积分数量
    required_credits = 0
    
    if feature == "basic_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.FREE]["credits_per_analysis"]
    elif feature == "advanced_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.STARTER]["credits_per_analysis"]
    elif feature in ["business_insights", "pdf_reports"]:
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.PRO]["credits_per_analysis"]
    else:
        return False
    
    # 检查余额
    if user.credits_balance < required_credits:
        return False
    
    # 扣除积分
    user.credits_balance -= required_credits
    
    # 记录交易
    transaction = CreditTransaction(
        user_id=user.id,
        amount=-required_credits,
        description=f"Analysis: {feature}",
        transaction_type="consumption"
    )
    
    db.add(transaction)
    db.commit()
    
    return True

def require_credits(feature: str):
    """要求足够积分的装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 current_user 和 db
            current_user = None
            db = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                if isinstance(value, Session):
                    db = value
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # 检查功能权限
            if not check_subscription_limit(current_user, feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature}' not available in your subscription"
                )
                
            # 检查积分余额
            if not check_credit_balance(current_user, feature):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Insufficient credits for {feature}"
                )
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 消耗积分
            consume_credits(db, current_user, feature)
            
            return result
        return wrapper
    return decorator

def require_subscription(min_tier: SubscriptionTier, feature: str = None):
    """订阅权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # 检查订阅等级
            tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER, SubscriptionTier.PRO]
            if tier_order.index(current_user.subscription_tier) < tier_order.index(min_tier):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires {min_tier.value} subscription or higher"
                )
            
            # 检查功能权限
            if feature and not check_subscription_limit(current_user, feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature}' not available in your subscription"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 权限依赖函数
async def require_basic_subscription(current_user: User = Depends(get_current_active_user)):
    if not check_subscription_limit(current_user, "basic_analysis"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Basic subscription required"
        )
    return current_user

async def require_premium_subscription(current_user: User = Depends(get_current_active_user)):
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER, SubscriptionTier.PRO]
    if tier_order.index(current_user.subscription_tier) < tier_order.index(SubscriptionTier.PRO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user

async def require_enterprise_subscription(current_user: User = Depends(get_current_active_user)):
    if current_user.subscription_tier != SubscriptionTier.PRO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required"
        )
    return current_user