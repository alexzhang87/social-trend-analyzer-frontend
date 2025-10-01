from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import httpx
import secrets
import urllib.parse

# 延迟导入以避免循环依赖
def get_database_models():
    from ..data.models.database import get_db, User, UserSession
    return get_db, User, UserSession
from ..core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    get_current_active_user
)
from ..core.config import settings
from ..services.email_service import email_service
from ..services.session_service import session_service
from ..services.login_limiter import login_limiter

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr  # 这里也需要 email-validator 库
    username: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    role: str
    subscription_tier: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

# Email verification models
class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationConfirm(BaseModel):
    email: EmailStr
    code: str
    username: str
    password: str
    full_name: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class MessageResponse(BaseModel):
    message: str

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(lambda: get_database_models()[0]())):
    get_db, User, UserSession = get_database_models()
    
    # Check if user already exists
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
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        credits_balance=10  # 为新用户设置初始积分
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(lambda: get_database_models()[0]())):
    get_db, User, UserSession = get_database_models()
    
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    return current_user

@router.post("/logout")
async def logout(current_user = Depends(get_current_active_user)):
    return {"message": "Successfully logged out"}


# Email verification endpoints
@router.post("/send-verification-code", response_model=MessageResponse)
async def send_verification_code(request: EmailVerificationRequest, db: Session = Depends(lambda: get_database_models()[0]())):
    """Send email verification code for registration"""
    get_db, User, UserSession = get_database_models()
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate and store verification code
    code = email_service.generate_verification_code()
    if not email_service.store_verification_code(request.email, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store verification code"
        )
    
    # Send email
    if not email_service.send_verification_email(request.email, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return MessageResponse(message="Verification code sent successfully")

@router.post("/verify-email-and-register", response_model=UserResponse)
async def verify_email_and_register(request: EmailVerificationConfirm, db: Session = Depends(lambda: get_database_models()[0]())):
    """Verify email code and complete registration"""
    get_db, User, UserSession = get_database_models()
    
    # Verify the code
    if not email_service.verify_code(request.email, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Check if email already exists (double check)
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    db_user = User(
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        full_name=request.full_name,
        credits_balance=10,  # Initial credits for new users
        is_active=True  # Email verified, so activate immediately
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(lambda: get_database_models()[0]())):
    """Send password reset email"""
    get_db, User, UserSession = get_database_models()
    
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return MessageResponse(message="If the email exists, a password reset link has been sent")
    
    # Generate and store reset token
    reset_token = email_service.generate_reset_token()
    if not email_service.store_reset_token(request.email, reset_token):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reset token"
        )
    
    # Send reset email
    if not email_service.send_password_reset_email(request.email, reset_token):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )
    
    return MessageResponse(message="If the email exists, a password reset link has been sent")

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(lambda: get_database_models()[0]())):
    """Reset password using token"""
    get_db, User, UserSession = get_database_models()
    
    # Verify reset token
    if not email_service.verify_reset_token(request.email, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    # Clean up the reset token
    email_service._cleanup_expired_code(f"password_reset:{request.email}")
    
    return MessageResponse(message="Password reset successfully")


# OAuth相关模型
class OAuthState(BaseModel):
    state: str
    redirect_url: Optional[str] = None


@router.get("/github")
async def github_login():
    """GitHub OAuth登录 - 重定向到GitHub授权页面"""
    state = secrets.token_urlsafe(32)
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(settings.GITHUB_REDIRECT_URI)}&"
        f"scope=user:email&"
        f"state={state}"
    )
    
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: str, db: Session = Depends(lambda: get_database_models()[0]())):
    """GitHub OAuth回调处理"""
    get_db, User, UserSession = get_database_models()
    
    try:
        # 1. 使用授权码获取访问令牌
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                # 记录详细的错误信息
                error_detail = token_data.get("error_description", token_data.get("error", "Unknown error"))
                raise HTTPException(status_code=400, detail=f"Failed to get access token: {error_detail}")
            
            access_token = token_data["access_token"]
            
            # 2. 使用访问令牌获取用户信息
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"}
            )
            user_data = user_response.json()
            
            # 3. 获取用户邮箱
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {access_token}"}
            )
            emails_data = email_response.json()
            primary_email = next((email["email"] for email in emails_data if email["primary"]), None)
            
            if not primary_email:
                raise HTTPException(status_code=400, detail="No primary email found")
            
            # 4. 检查用户是否已存在
            existing_user = db.query(User).filter(User.email == primary_email).first()
            
            if existing_user:
                # 更新最后登录时间
                existing_user.last_login = datetime.utcnow()
                db.commit()
                user = existing_user
            else:
                # 创建新用户
                user = User(
                    email=primary_email,
                    username=user_data.get("login", primary_email.split("@")[0]),
                    hashed_password="",  # OAuth用户不需要密码
                    is_active=True,
                    credits_balance=100,  # 新用户初始积分
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # 5. 生成JWT令牌
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
            
            # 6. 创建用户会话
            session = UserSession(
                user_id=user.id,
                token_jti=access_token,
                expires_at=datetime.utcnow() + access_token_expires
            )
            db.add(session)
            db.commit()
            
            # 7. 重定向到前端首页，携带token
            frontend_url = f"{settings.FRONTEND_URL}/?token={access_token}"
            return RedirectResponse(url=frontend_url)
            
    except HTTPException as e:
        # 透传业务性错误（如400），不要包成500
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth authentication failed: {str(e)}")


# 会话管理API
class SessionResponse(BaseModel):
    id: str
    device_info: str
    ip_address: str
    location: Optional[str]
    created_at: datetime
    last_activity: datetime
    is_current: bool
    
    class Config:
        from_attributes = True

@router.get("/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user = Depends(get_current_active_user)
):
    """获取用户的所有活跃会话"""
    try:
        sessions = session_service.get_user_sessions(current_user.id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user = Depends(get_current_active_user)
):
    """撤销指定会话"""
    try:
        success = session_service.revoke_session(session_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return {"message": "Session revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke session: {str(e)}"
        )

@router.delete("/sessions")
async def revoke_all_sessions(
    current_user = Depends(get_current_active_user)
):
    """撤销用户的所有其他会话（除当前会话外）"""
    try:
        revoked_count = session_service.revoke_all_user_sessions(current_user.id, exclude_current=True)
        return {"message": f"Revoked {revoked_count} sessions"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke sessions: {str(e)}"
        )

@router.get("/sessions/stats")
async def get_session_stats(
    current_user = Depends(get_current_active_user)
):
    """获取用户会话统计"""
    try:
        stats = session_service.get_user_session_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session stats: {str(e)}"
        )


@router.get("/google")
async def google_login():
    """Google OAuth登录 - 重定向到Google授权页面"""
    state = secrets.token_urlsafe(32)
    
    # 不对redirect_uri进行编码，因为Google OAuth期望原始URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    print(f"Google auth URL: {google_auth_url}")
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(lambda: get_database_models()[0]())):
    """Google OAuth回调处理"""
    get_db, User, UserSession = get_database_models()
    
    try:
        # 1. 使用授权码获取访问令牌
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # 添加调试日志
            print(f"Google token response status: {token_response.status_code}")
            print(f"Google token response headers: {dict(token_response.headers)}")
            print(f"Google token response text: {token_response.text}")
            
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                # 记录详细的错误信息
                error_detail = token_data.get("error_description", token_data.get("error", "Unknown error"))
                raise HTTPException(status_code=400, detail=f"Failed to get access token: {error_detail}")
            
            access_token = token_data["access_token"]
            
            # 2. 使用访问令牌获取用户信息
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_data = user_response.json()
            
            # 添加调试日志
            print(f"Google user response status: {user_response.status_code}")
            print(f"Google user data: {user_data}")
            
            email = user_data.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="No email found")
            
            # 3. 检查用户是否已存在
            existing_user = db.query(User).filter(User.email == email).first()
            
            if existing_user:
                # 更新最后登录时间
                existing_user.last_login = datetime.utcnow()
                db.commit()
                user = existing_user
            else:
                # 创建新用户
                user = User(
                    email=email,
                    username=user_data.get("name", email.split("@")[0]),
                    hashed_password="",  # OAuth用户不需要密码
                    is_active=True,
                    credits_balance=100,  # 新用户初始积分
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # 4. 生成JWT令牌
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            jwt_token = create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
            
            # 5. 创建用户会话
            session = UserSession(
                user_id=user.id,
                token_jti=jwt_token,
                expires_at=datetime.utcnow() + access_token_expires,
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            
            # 6. 重定向到前端回调页面，携带token
            frontend_url = f"{settings.FRONTEND_URL}?token={jwt_token}"
            print(f"Redirecting to: {frontend_url}")
            return RedirectResponse(url=frontend_url)
            
    except HTTPException as e:
        print(f"Google OAuth HTTP error: {str(e)}")
        raise e
    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth authentication failed: {str(e)}")