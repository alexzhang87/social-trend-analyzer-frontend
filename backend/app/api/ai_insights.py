from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..services.ai_insights_service import AIInsightsService
from ..core.auth import get_current_user
from ..data.models.database import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-insights", tags=["AI Insights"])

@router.get("/market-intelligence")
async def get_market_intelligence(
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取市场情报和趋势洞察"""
    try:
        ai_insights_service = AIInsightsService()
        intelligence = await ai_insights_service.get_market_intelligence(keyword)
        return {
            "success": True,
            "data": intelligence,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取市场情报失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场情报失败: {str(e)}")

@router.get("/strategic-recommendations")
async def get_strategic_recommendations(
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取战略建议和商业机会"""
    try:
        ai_insights_service = AIInsightsService()
        recommendations = await ai_insights_service.get_strategic_recommendations(keyword)
        return {
            "success": True,
            "data": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取战略建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取战略建议失败: {str(e)}")

@router.get("/growth-predictions")
async def get_growth_predictions(
    keyword: Optional[str] = None,
    time_range: str = "3months",
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取增长预测和市场趋势"""
    try:
        ai_insights_service = AIInsightsService()
        predictions = await ai_insights_service.get_growth_predictions(keyword, time_range)
        return {
            "success": True,
            "data": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取增长预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取增长预测失败: {str(e)}")

@router.get("/competitive-analysis")
async def get_competitive_analysis(
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取竞争分析和风险评估"""
    try:
        ai_insights_service = AIInsightsService()
        analysis = await ai_insights_service.get_competitive_analysis(keyword)
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取竞争分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取竞争分析失败: {str(e)}")

@router.get("/dashboard")
async def get_insights_dashboard(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取AI洞察仪表板数据"""
    try:
        ai_insights_service = AIInsightsService()
        dashboard_data = await ai_insights_service.get_dashboard_data()
        return {
            "success": True,
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取仪表板数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")

@router.post("/refresh")
async def refresh_insights(
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """刷新AI洞察数据"""
    try:
        ai_insights_service = AIInsightsService()
        result = await ai_insights_service.refresh_insights(keyword)
        return {
            "success": True,
            "data": result,
            "message": "洞察数据已刷新",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"刷新洞察数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"刷新洞察数据失败: {str(e)}")