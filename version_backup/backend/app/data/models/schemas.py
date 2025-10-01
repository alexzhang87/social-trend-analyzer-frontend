from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    platform: str
    author: Optional[str] = None
    text: str
    url: str
    likes: Optional[int] = 0
    created_at: datetime

class PostCreate(PostBase):
    """Schema for creating a post. Used in the seed endpoint."""
    pass

class Post(PostBase):
    """Schema for reading a post from the database."""
    id: int

    class Config:
        from_attributes = True


# --- Request Models ---
class AnalysisRequest(BaseModel):
    keywords: List[str]
    platform: Optional[str] = None
    timeRange: Optional[str] = None
    category: Optional[str] = None


# --- Response Models ---

# Sub-models for the new structured response
class HypeIndex(BaseModel):
    score: int
    reasoning: str

class SentimentSpectrum(BaseModel):
    positive: int
    neutral: int
    negative: int
    questioning: int
    total: int

class KeyTheme(BaseModel):
    theme: str
    summary: str
    isEmerging: bool

class UserPersonaSnapshot(BaseModel):
    personas: List[str]
    coreNeeds: List[str]

class ActionableOpportunity(BaseModel):
    opportunity: str
    description: str
    targetPersona: str

class TopMention(BaseModel):
    platform: str
    author: str
    text: str
    url: str
    likes: int
    sentiment: str

# The main response model, updated to the new structure
class TrendAnalysisResponse(BaseModel):
    title: str
    summary: str
    hypeIndex: HypeIndex
    sentimentSpectrum: SentimentSpectrum
    keyThemes: List[KeyTheme]
    userPersonaSnapshot: UserPersonaSnapshot
    actionableOpportunities: List[ActionableOpportunity]
    top_mentions: List[TopMention]
    keywords: List[str] # This is added by analysis_service, so we keep it

# --- 订阅和积分相关模型 ---

class CreditTransactionBase(BaseModel):
    amount: int
    description: str
    transaction_type: str
    expires_at: Optional[datetime] = None

class CreditTransactionCreate(CreditTransactionBase):
    user_id: int

class CreditTransactionResponse(CreditTransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    tier: str  # "free", "starter", "pro"

class SubscriptionResponse(BaseModel):
    subscription_tier: str
    subscription_expires_at: Optional[datetime] = None
    credits_balance: int


# --- 用户反馈相关模型 ---

class FeedbackBase(BaseModel):
    analysis_id: Optional[str] = None
    feedback_type: str = "general"
    rating: Optional[int] = None
    title: str
    content: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[int] = None
    feedback_type: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: int
    user_id: int
    status: str
    admin_response: Optional[str] = None
    admin_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AdminFeedbackResponse(BaseModel):
    admin_response: str
    status: Optional[str] = None

class FeedbackStats(BaseModel):
    total_feedback: int
    pending_count: int
    resolved_count: int
    average_rating: Optional[float] = None
    feedback_by_type: dict
    recent_feedback: List[FeedbackResponse]