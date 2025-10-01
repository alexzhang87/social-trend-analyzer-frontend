"""
AI智能分析API端点
提供情感分析、趋势预测、个性化推荐等AI增强功能的REST接口
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...data.models.database import get_db, User
from ...core.auth import get_current_user
from ...services.ai_analysis_service import (
    ai_analysis_service,
    SentimentResult,
    TrendPrediction,
    PersonalizedRecommendations,
    SentimentType,
    TrendDirection
)

router = APIRouter()

# Pydantic模型定义

class SentimentAnalysisRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., description="待分析的文本")
    use_advanced: bool = Field(True, description="是否使用高级模型")

class BatchSentimentRequest(BaseModel):
    """批量情感分析请求"""
    texts: List[str] = Field(..., description="文本列表")
    use_advanced: bool = Field(True, description="是否使用高级模型")

class TrendPredictionRequest(BaseModel):
    """趋势预测请求"""
    data: List[Dict[str, Any]] = Field(..., description="历史数据")
    target_column: str = Field(..., description="目标列名")
    time_horizon: int = Field(30, description="预测时间范围（天）")

class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_profile: Dict[str, Any] = Field(..., description="用户画像")
    items: List[Dict[str, Any]] = Field(..., description="候选项目列表")
    num_recommendations: int = Field(10, description="推荐数量")

class TextInsightsRequest(BaseModel):
    """文本洞察请求"""
    texts: List[str] = Field(..., description="文本列表")

class SentimentResponse(BaseModel):
    """情感分析响应"""
    sentiment: str
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float
    emotions: Dict[str, float]

class TrendResponse(BaseModel):
    """趋势预测响应"""
    direction: str
    confidence: float
    predicted_values: List[float]
    time_horizon: int
    factors: List[str]
    accuracy_score: float

class RecommendationItemResponse(BaseModel):
    """推荐项目响应"""
    item_id: str
    title: str
    description: str
    score: float
    reason: str
    category: str
    metadata: Dict[str, Any]

class RecommendationResponse(BaseModel):
    """推荐响应"""
    user_id: str
    recommendations: List[RecommendationItemResponse]
    total_score: float
    diversity_score: float
    novelty_score: float
    explanation: str

# API端点

@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析文本情感
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 10000 characters allowed.")
        
        result = await ai_analysis_service.analyze_sentiment(
            request.text,
            request.use_advanced
        )
        
        return SentimentResponse(
            sentiment=result.sentiment.value,
            confidence=result.confidence,
            positive_score=result.positive_score,
            negative_score=result.negative_score,
            neutral_score=result.neutral_score,
            compound_score=result.compound_score,
            emotions=result.emotions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.post("/sentiment/batch")
async def batch_sentiment_analysis(
    request: BatchSentimentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量情感分析
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Text list cannot be empty")
        
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="Too many texts. Maximum 100 texts allowed.")
        
        # 检查每个文本的长度
        for i, text in enumerate(request.texts):
            if len(text) > 5000:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Text {i+1} too long. Maximum 5000 characters allowed per text."
                )
        
        # 并发处理
        import asyncio
        tasks = [
            ai_analysis_service.analyze_sentiment(text, request.use_advanced)
            for text in request.texts
        ]
        results = await asyncio.gather(*tasks)
        
        # 转换为响应格式
        sentiment_responses = [
            SentimentResponse(
                sentiment=result.sentiment.value,
                confidence=result.confidence,
                positive_score=result.positive_score,
                negative_score=result.negative_score,
                neutral_score=result.neutral_score,
                compound_score=result.compound_score,
                emotions=result.emotions
            )
            for result in results
        ]
        
        # 聚合统计
        positive_count = sum(1 for r in results if r.sentiment == SentimentType.POSITIVE)
        negative_count = sum(1 for r in results if r.sentiment == SentimentType.NEGATIVE)
        neutral_count = sum(1 for r in results if r.sentiment == SentimentType.NEUTRAL)
        
        avg_compound = sum(r.compound_score for r in results) / len(results)
        
        return {
            "results": sentiment_responses,
            "summary": {
                "total_texts": len(request.texts),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": positive_count / len(results),
                "negative_ratio": negative_count / len(results),
                "neutral_ratio": neutral_count / len(results),
                "average_compound_score": avg_compound
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch sentiment analysis: {str(e)}")

@router.post("/trends/predict", response_model=TrendResponse)
async def predict_trends(
    request: TrendPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    预测趋势
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Data cannot be empty")
        
        if len(request.data) > 10000:
            raise HTTPException(status_code=400, detail="Too much data. Maximum 10000 records allowed.")
        
        if request.time_horizon <= 0 or request.time_horizon > 365:
            raise HTTPException(status_code=400, detail="Time horizon must be between 1 and 365 days")
        
        result = await ai_analysis_service.predict_trends(
            request.data,
            request.target_column,
            request.time_horizon
        )
        
        return TrendResponse(
            direction=result.direction.value,
            confidence=result.confidence,
            predicted_values=result.predicted_values,
            time_horizon=result.time_horizon,
            factors=result.factors,
            accuracy_score=result.accuracy_score
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting trends: {str(e)}")

@router.post("/recommendations", response_model=RecommendationResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成个性化推荐
    """
    try:
        if not request.items:
            raise HTTPException(status_code=400, detail="Items list cannot be empty")
        
        if len(request.items) > 1000:
            raise HTTPException(status_code=400, detail="Too many items. Maximum 1000 items allowed.")
        
        if request.num_recommendations <= 0 or request.num_recommendations > 50:
            raise HTTPException(status_code=400, detail="Number of recommendations must be between 1 and 50")
        
        result = await ai_analysis_service.generate_personalized_recommendations(
            current_user.id,
            request.user_profile,
            request.items,
            request.num_recommendations
        )
        
        recommendation_items = [
            RecommendationItemResponse(
                item_id=rec.item_id,
                title=rec.title,
                description=rec.description,
                score=rec.score,
                reason=rec.reason,
                category=rec.category,
                metadata=rec.metadata
            )
            for rec in result.recommendations
        ]
        
        return RecommendationResponse(
            user_id=result.user_id,
            recommendations=recommendation_items,
            total_score=result.total_score,
            diversity_score=result.diversity_score,
            novelty_score=result.novelty_score,
            explanation=result.explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/insights/text")
async def analyze_text_insights(
    request: TextInsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析文本洞察
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Text list cannot be empty")
        
        if len(request.texts) > 500:
            raise HTTPException(status_code=400, detail="Too many texts. Maximum 500 texts allowed.")
        
        # 检查文本长度
        for i, text in enumerate(request.texts):
            if len(text) > 5000:
                raise HTTPException(
                    status_code=400,
                    detail=f"Text {i+1} too long. Maximum 5000 characters allowed per text."
                )
        
        result = await ai_analysis_service.analyze_text_insights(request.texts)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text insights: {str(e)}")

@router.get("/models/status")
async def get_model_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取AI模型状态
    """
    try:
        return {
            "sentiment_analyzer": ai_analysis_service.sentiment_analyzer is not None,
            "emotion_classifier": ai_analysis_service.emotion_classifier is not None,
            "vectorizer": ai_analysis_service.vectorizer is not None,
            "cache_ttl": ai_analysis_service.cache_ttl,
            "status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")

@router.post("/models/reload")
async def reload_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重新加载AI模型（仅管理员）
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only administrators can reload models")
        
        # 重新初始化模型
        ai_analysis_service._initialize_models()
        
        return {
            "message": "AI models reloaded successfully",
            "timestamp": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading models: {str(e)}")

@router.get("/analytics/usage")
async def get_usage_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取使用分析（仅管理员）
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only administrators can view usage analytics")
        
        # 这里可以实现使用统计逻辑
        # 暂时返回模拟数据
        return {
            "sentiment_analysis_requests": 1250,
            "trend_prediction_requests": 340,
            "recommendation_requests": 890,
            "text_insights_requests": 560,
            "total_requests": 3040,
            "average_response_time": 0.85,
            "cache_hit_rate": 0.72,
            "error_rate": 0.02
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage analytics: {str(e)}")

@router.post("/feedback")
async def submit_analysis_feedback(
    analysis_type: str,
    analysis_id: str,
    feedback_score: int,
    feedback_text: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交分析反馈
    """
    try:
        if feedback_score < 1 or feedback_score > 5:
            raise HTTPException(status_code=400, detail="Feedback score must be between 1 and 5")
        
        valid_types = ["sentiment", "trend", "recommendation", "insights"]
        if analysis_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid analysis type. Must be one of: {valid_types}")
        
        # 这里可以实现反馈存储逻辑
        # 暂时返回成功响应
        return {
            "message": "Feedback submitted successfully",
            "analysis_type": analysis_type,
            "analysis_id": analysis_id,
            "feedback_score": feedback_score,
            "user_id": current_user.id,
            "timestamp": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/health")
async def health_check():
    """
    AI分析服务健康检查
    """
    try:
        # 简单的健康检查
        test_text = "This is a test."
        result = await ai_analysis_service.analyze_sentiment(test_text, use_advanced=False)
        
        return {
            "status": "healthy",
            "sentiment_analyzer": "working",
            "test_result": {
                "sentiment": result.sentiment.value,
                "confidence": result.confidence
            },
            "timestamp": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00"
        }