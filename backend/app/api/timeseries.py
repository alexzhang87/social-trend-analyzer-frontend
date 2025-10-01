from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from ..services.time_series_service import TimeSeriesAnalysisService
def get_database_models():
    from ..data.models.database import User
    return User
from ..core.auth import (
    get_current_active_user,
    require_premium_subscription,
    check_subscription_limit
)
from ..core.usage_tracker import usage_tracker

logger = logging.getLogger("trend-analyzer")
router = APIRouter(prefix="/timeseries", tags=["时间序列分析"])

# 初始化服务
timeseries_service = TimeSeriesAnalysisService()

# Pydantic 模型
class TimeSeriesAnalysisRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=5, description="关键词列表")
    time_range: str = Field(default="30d", description="时间范围: 7d, 30d, 90d, 1y")
    
    class Config:
        schema_extra = {
            "example": {
                "keywords": ["Vision Pro", "VR"],
                "time_range": "30d"
            }
        }

class TrendForecastRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=5, description="关键词列表")
    forecast_days: int = Field(default=7, ge=1, le=30, description="预测天数")
    
    class Config:
        schema_extra = {
            "example": {
                "keywords": ["Vision Pro"],
                "forecast_days": 7
            }
        }

class TimeSeriesAnalysisResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    processing_time: float
    user_tier: str
    remaining_requests: Optional[int] = None

@router.post("/analyze", response_model=TimeSeriesAnalysisResponse, status_code=200)
def analyze_trend_evolution(
    request: TimeSeriesAnalysisRequest,
    current_user = Depends(require_premium_subscription)
):
    """时间序列趋势演变分析 - 需要Premium订阅"""
    try:
        # 检查使用限制
        if not usage_tracker.check_rate_limit(current_user, "timeseries_analysis", 1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily usage limit exceeded for timeseries analysis"
            )
        
        # 检查订阅限制
        if not check_subscription_limit(current_user, "timeseries_analysis", len(request.keywords)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keywords count exceeds subscription limit"
            )
        
        # 验证时间范围
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if request.time_range not in valid_ranges:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid time_range. Must be one of: {valid_ranges}"
            )
        
        import time
        start_time = time.time()
        
        # 执行时间序列分析
        result = timeseries_service.analyze_trend_evolution(
            keywords=request.keywords,
            time_range=request.time_range,
            user_id=current_user.id
        )
        
        # 记录使用量
        usage_tracker.increment_usage(current_user.id, "timeseries_analysis", 1)
        
        processing_time = round(time.time() - start_time, 2)
        
        return TimeSeriesAnalysisResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            user_tier=current_user.subscription_tier.value,
            remaining_requests=usage_tracker.get_remaining_requests(current_user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"时间序列分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"时间序列分析失败: {str(e)}"
        )

@router.post("/forecast", response_model=TimeSeriesAnalysisResponse, status_code=200)
def predict_future_trends(
    request: TrendForecastRequest,
    current_user = Depends(require_premium_subscription)
):
    """未来趋势预测 - 需要Premium订阅"""
    try:
        # 检查使用限制
        if not usage_tracker.check_rate_limit(current_user, "trend_forecast", 1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily usage limit exceeded for trend forecast"
            )
        
        # 检查订阅限制
        if not check_subscription_limit(current_user, "trend_forecast", len(request.keywords)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keywords count exceeds subscription limit"
            )
        
        import time
        start_time = time.time()
        
        # 执行趋势预测
        result = timeseries_service.predict_future_trends(
            keywords=request.keywords,
            forecast_days=request.forecast_days,
            user_id=current_user.id
        )
        
        # 记录使用量
        usage_tracker.increment_usage(current_user.id, "trend_forecast", 1)
        
        processing_time = round(time.time() - start_time, 2)
        
        return TimeSeriesAnalysisResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            user_tier=current_user.subscription_tier.value,
            remaining_requests=usage_tracker.get_remaining_requests(current_user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"趋势预测失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"趋势预测失败: {str(e)}"
        )

@router.get("/history", status_code=200)
def get_timeseries_history(
    limit: int = 10,
    current_user = Depends(require_premium_subscription)
):
    """获取用户时间序列分析历史"""
    try:
        if limit > 50:
            limit = 50  # 限制最大返回数量
        
        history = timeseries_service.get_user_timeseries_history(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "history": history,
                "total_count": len(history)
            },
            "user_tier": current_user.subscription_tier.value
        }
        
    except Exception as e:
        logger.error(f"获取时间序列分析历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录失败: {str(e)}"
        )

@router.get("/templates", status_code=200)
def get_analysis_templates():
    """获取预设的时间序列分析模板"""
    templates = [
        {
            "id": "tech_trend",
            "name": "科技趋势分析",
            "description": "分析科技产品和技术的发展趋势",
            "keywords": ["AI", "人工智能", "机器学习"],
            "time_range": "90d",
            "forecast_days": 14
        },
        {
            "id": "brand_monitoring",
            "name": "品牌监控",
            "description": "监控品牌提及度和情感变化",
            "keywords": ["Apple", "iPhone"],
            "time_range": "30d",
            "forecast_days": 7
        },
        {
            "id": "market_analysis",
            "name": "市场分析",
            "description": "分析市场热点和投资机会",
            "keywords": ["股市", "投资", "基金"],
            "time_range": "30d",
            "forecast_days": 10
        },
        {
            "id": "social_trend",
            "name": "社会趋势",
            "description": "分析社会热点和文化趋势",
            "keywords": ["环保", "可持续发展"],
            "time_range": "90d",
            "forecast_days": 21
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "templates": templates
        }
    }

@router.get("/stats", status_code=200)
def get_timeseries_stats(
    current_user = Depends(require_premium_subscription)
):
    """获取用户时间序列分析统计信息"""
    try:
        # 获取用户分析历史
        history = timeseries_service.get_user_timeseries_history(
            user_id=current_user.id,
            limit=100
        )
        
        # 计算统计信息
        total_analyses = len(history)
        completed_analyses = len([h for h in history if h['status'] == 'completed'])
        
        # 分析时间范围分布
        time_range_stats = {}
        for analysis in history:
            time_range = analysis.get('time_range', 'unknown')
            time_range_stats[time_range] = time_range_stats.get(time_range, 0) + 1
        
        # 趋势评分分布
        trend_scores = [h.get('trend_score', 0) for h in history if h.get('trend_score') is not None]
        avg_trend_score = sum(trend_scores) / len(trend_scores) if trend_scores else 0
        
        return {
            "status": "success",
            "data": {
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "success_rate": round(completed_analyses / total_analyses * 100, 1) if total_analyses > 0 else 0,
                "time_range_distribution": time_range_stats,
                "average_trend_score": round(avg_trend_score, 2),
                "recent_analyses": history[:5]  # 最近5次分析
            },
            "user_tier": current_user.subscription_tier.value
        }
        
    except Exception as e:
        logger.error(f"获取时间序列分析统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )