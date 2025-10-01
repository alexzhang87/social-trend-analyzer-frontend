from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import uuid

from ..data.models.database import User
from ..services.competitive_analysis_service import CompetitiveAnalysisService
from ..core.auth import (
    get_current_active_user, 
    require_premium_subscription,
    check_subscription_limit
)
from ..core.usage_tracker import usage_tracker

logger = logging.getLogger("trend-analyzer")
router = APIRouter()

# 请求模型
class CompetitiveAnalysisRequest(BaseModel):
    brand_keywords: List[List[str]]  # [["Apple", "iPhone"], ["Samsung", "Galaxy"]]
    analysis_type: str = "competitive"  # competitive, positioning, swot

class CompetitiveAnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: str

# 初始化服务
competitive_service = CompetitiveAnalysisService()

@router.post("/compare", response_model=CompetitiveAnalysisResponse)
def compare_competitors(
    request: CompetitiveAnalysisRequest,
    current_user: User = Depends(require_premium_subscription)
):
    """
    竞品对比分析
    
    需要Premium订阅权限
    """
    try:
        # 检查订阅限制
        if not check_subscription_limit(current_user, "competitive_analysis"):
            raise HTTPException(
                status_code=403, 
                detail="已达到竞品分析次数限制，请升级订阅"
            )
        
        # 验证输入
        if len(request.brand_keywords) < 2:
            raise HTTPException(
                status_code=400,
                detail="至少需要2个品牌进行对比分析"
            )
        
        if len(request.brand_keywords) > 5:
            raise HTTPException(
                status_code=400,
                detail="最多支持5个品牌的对比分析"
            )
        
        # 记录使用情况
        usage_tracker.track_api_usage(
            user_id=current_user.id,
            endpoint="competitive_analysis",
            subscription_tier=current_user.subscription_tier.value
        )
        
        logger.info(f"用户 {current_user.id} 开始竞品对比分析: {request.brand_keywords}")
        
        # 执行分析
        result = competitive_service.compare_brands(
            brand_keywords=request.brand_keywords,
            user_id=current_user.id
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return CompetitiveAnalysisResponse(
            task_id=str(uuid.uuid4()),
            status="completed",
            message="竞品对比分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"竞品对比分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/history")
def get_competitive_analysis_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户的竞品分析历史
    """
    try:
        analyses = competitive_service.get_user_analyses(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "analyses": analyses,
            "total": len(analyses),
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"获取竞品分析历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.get("/templates")
def get_analysis_templates(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取竞品分析模板
    """
    templates = {
        "tech_companies": {
            "name": "科技公司对比",
            "description": "适用于科技公司和产品的对比分析",
            "example_brands": [
                ["Apple", "iPhone"],
                ["Samsung", "Galaxy"],
                ["Google", "Pixel"]
            ]
        },
        "social_media": {
            "name": "社交媒体平台",
            "description": "社交媒体平台的竞争分析",
            "example_brands": [
                ["TikTok"],
                ["Instagram"],
                ["YouTube"]
            ]
        },
        "automotive": {
            "name": "汽车品牌",
            "description": "汽车品牌和车型对比",
            "example_brands": [
                ["Tesla", "Model 3"],
                ["BMW", "i3"],
                ["Mercedes", "EQS"]
            ]
        },
        "streaming": {
            "name": "流媒体服务",
            "description": "流媒体平台竞争分析",
            "example_brands": [
                ["Netflix"],
                ["Disney+"],
                ["Amazon Prime"]
            ]
        }
    }
    
    return {
        "templates": templates,
        "usage_tips": [
            "选择2-5个相关品牌进行对比",
            "使用具体的产品名称获得更准确的结果",
            "定期进行分析以跟踪竞争态势变化"
        ]
    }