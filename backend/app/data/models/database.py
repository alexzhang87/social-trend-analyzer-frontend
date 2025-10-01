from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import logging
from datetime import datetime
import enum

# Import the central settings object.
# Note: Using a relative path for robustness within the application structure.
from ...core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 数据库连接池和性能优化配置
    engine_kwargs = {
        "pool_size": 20,  # 连接池大小
        "max_overflow": 30,  # 最大溢出连接数
        "pool_timeout": 30,  # 连接超时时间
        "pool_recycle": 3600,  # 连接回收时间（1小时）
        "pool_pre_ping": True,  # 连接前ping检查
        "echo": False,  # 生产环境关闭SQL日志
    }
    
    # SQLite特殊配置
    if settings.DATABASE_URL.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        # SQLite不支持连接池，移除相关配置
        engine_kwargs.pop("pool_size", None)
        engine_kwargs.pop("max_overflow", None)
        engine_kwargs.pop("pool_timeout", None)
        engine_kwargs.pop("pool_recycle", None)
        engine_kwargs.pop("pool_pre_ping", None)
    
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully with optimized configuration")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

Base = declarative_base()

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    author = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    url = Column(String, unique=True, index=True)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)

class SubscriptionTier(enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    PLUS = "plus"
    ENTERPRISE = "enterprise"

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    ANALYST = "analyst"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    credits_balance = Column(Integer, default=10)  # 积分余额，新用户默认10积分
    subscription_expires_at = Column(DateTime, nullable=True)  # 订阅到期时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)  # 正数为增加，负数为消费
    description = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # subscription, purchase, consumption, reward
    expires_at = Column(DateTime, nullable=True)  # 积分过期时间
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token_jti = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)

def get_db():
    """Dependency to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """Creates all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

class FeedbackType(enum.Enum):
    ANALYSIS_QUALITY = "analysis_quality"  # 分析质量反馈
    FEATURE_REQUEST = "feature_request"    # 功能请求
    BUG_REPORT = "bug_report"              # 错误报告
    GENERAL = "general"                    # 一般反馈

class FeedbackStatus(enum.Enum):
    PENDING = "pending"      # 待处理
    REVIEWED = "reviewed"    # 已查看
    RESOLVED = "resolved"    # 已解决
    CLOSED = "closed"        # 已关闭

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(String, nullable=True)  # 关联的分析任务ID
    feedback_type = Column(Enum(FeedbackType), default=FeedbackType.GENERAL)
    rating = Column(Integer, nullable=True)  # 1-5星评分
    title = Column(String(200), nullable=False)  # 反馈标题
    content = Column(Text, nullable=False)  # 反馈内容
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING)
    admin_response = Column(Text, nullable=True)  # 管理员回复
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理的管理员ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)  # 解决时间
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], backref="feedbacks")
    admin = relationship("User", foreign_keys=[admin_id])

class FeedbackAttachment(Base):
    __tablename__ = "feedback_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("user_feedback.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = relationship("UserFeedback", backref="attachments")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expert_id = Column(String, nullable=False)  # Expert identifier
    title = Column(String, nullable=True)  # Session title
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", backref="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    expert_id = Column(String, nullable=True)  # For assistant messages
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")