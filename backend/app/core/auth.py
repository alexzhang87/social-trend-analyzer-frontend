from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..data.models.database import get_db, User, UserSession, SubscriptionTier, UserRole, CreditTransaction
from .config import settings
from ..services.session_service import session_service
from functools import wraps
import logging
import re

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

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
                    "pdf_reports", "email_support", "priority_support", "professional_analysis"]
    },
    SubscriptionTier.PLUS: {
        "monthly_credits": 300,
        "credits_per_analysis": 5,
        "daily_requests": 100,
        "features": ["basic_analysis", "advanced_analysis", "business_insights", 
                    "pdf_reports", "email_support", "priority_support", "api_access", "team_collaboration"]
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly_credits": 1000,
        "credits_per_analysis": 10,
        "daily_requests": 500,
        "features": ["basic_analysis", "advanced_analysis", "business_insights", 
                    "pdf_reports", "email_support", "priority_support", "api_access", 
                    "team_collaboration", "custom_models", "dedicated_support"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Dict[str, Union[bool, List[str]]]:
    """验证密码强度"""
    errors = []
    
    # 最小长度检查
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # 最大长度检查
    if len(password) > 128:
        errors.append("Password must be no more than 128 characters long")
    
    # 包含大写字母
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # 包含小写字母
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # 包含数字
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    # 包含特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # 检查常见弱密码
    weak_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    if password.lower() in weak_passwords:
        errors.append("Password is too common and easily guessable")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength_score": calculate_password_strength_score(password)
    }

def calculate_password_strength_score(password: str) -> int:
    """计算密码强度评分（0-100）"""
    score = 0
    
    # 长度评分
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # 字符类型评分
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 15
    
    # 复杂性评分
    unique_chars = len(set(password))
    if unique_chars >= len(password) * 0.7:
        score += 15
    
    return min(score, 100)

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

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db),
    request: Request = None
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        token_jti: str = payload.get("jti")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # 验证会话
        if token_jti:
            session = session_service.validate_session(token_jti, db)
            if not session:
                logger.warning(f"Invalid or expired session for token {token_jti}")
                raise credentials_exception
            
            # 检查会话是否属于正确的用户
            if session.user_id != user_id:
                logger.warning(f"Session user mismatch: session user {session.user_id}, token user {user_id}")
                raise credentials_exception
            
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
    
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User {user_id} not found")
        raise credentials_exception
    
    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
        
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional), db: Session = Depends(get_db)) -> Optional[User]:
    """可选的用户认证，如果没有认证或认证失败则返回None"""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            return None
            
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_admin_user(current_user: User = Depends(get_current_active_user)):
    """要求管理员权限的依赖项"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
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

def check_credit_balance(user: User, feature: str, db: Session) -> bool:
    """检查用户有效积分余额是否足够"""
    from ..services.credit_expiry_service import credit_expiry_service
    
    required_credits = 0
    
    if feature == "basic_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.FREE]["credits_per_analysis"]
    elif feature == "advanced_analysis":
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.STARTER]["credits_per_analysis"]
    elif feature in ["business_insights", "pdf_reports"]:
        required_credits = SUBSCRIPTION_LIMITS[SubscriptionTier.PRO]["credits_per_analysis"]
    else:
        return False
    
    # 使用有效积分余额检查
    valid_balance = credit_expiry_service.get_user_valid_credits(user.id, db)
    return valid_balance >= required_credits

def consume_credits(db: Session, user: User, feature: str) -> bool:
    """消耗用户积分（使用FIFO过期机制）"""
    from ..services.credit_expiry_service import credit_expiry_service
    
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
    
    # 使用FIFO积分消费逻辑
    return credit_expiry_service.consume_credits_fifo(
        user.id, 
        required_credits, 
        db, 
        f"Analysis: {feature}"
    )

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
            if not check_credit_balance(current_user, feature, db):
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
            tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER, SubscriptionTier.PRO, SubscriptionTier.PLUS, SubscriptionTier.ENTERPRISE]
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
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER, SubscriptionTier.PRO, SubscriptionTier.PLUS, SubscriptionTier.ENTERPRISE]
    if tier_order.index(current_user.subscription_tier) < tier_order.index(SubscriptionTier.PRO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user

async def require_enterprise_subscription(current_user: User = Depends(get_current_active_user)):
    if current_user.subscription_tier != SubscriptionTier.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enterprise subscription required"
        )
    return current_user