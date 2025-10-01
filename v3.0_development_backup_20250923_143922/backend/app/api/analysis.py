from fastapi import APIRouter, Body, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from ..services.analysis_service import AnalysisService
from ..utils.logger import logger
from ..data.models.database import get_db, User
from ..core.auth import get_current_active_user

router = APIRouter()
analysis_service = AnalysisService()

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    text: str
    sentiment: str

class TrendAnalysisRequest(BaseModel):
    keywords: List[str]
    platform_filter: Optional[str] = None
    time_range: Optional[str] = None

class TrendAnalysisResponse(BaseModel):
    id: str
    keywords: List[str]
    status: str
    created_at: datetime
    results: Optional[Dict[str, Any]] = None

class AnalysisListItem(BaseModel):
    id: str
    keywords: List[str]
    status: str
    created_at: datetime
    platform_filter: Optional[str] = None

class AnalysisDetailResponse(BaseModel):
    id: str
    keywords: List[str]
    status: str
    created_at: datetime
    platform_filter: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

# 内存存储（实际应用中应使用数据库）
analysis_storage = {}

@router.post("/", response_model=AnalysisResponse)
def analyze_text(request: AnalysisRequest):
    """
    对给定的文本进行情感分析。

    - **text**: 需要进行情感分析的文本。
    """
    logger.info(f"收到对文本的情感分析请求: '{request.text[:50]}...'")
    
    if not request.text:
        raise HTTPException(status_code=400, detail="文本内容不能为空。")
        
    try:
        sentiment = analysis_service.analyze_sentiment(request.text)
        logger.info(f"文本分析完成，情感: {sentiment}")
        
        return AnalysisResponse(
            text=request.text,
            sentiment=sentiment
        )
        
    except Exception as e:
        logger.error(f"处理情感分析请求时发生错误: {e}")
        raise HTTPException(status_code=500, detail="处理请求时发生内部错误。")

@router.post("/analyze", response_model=TrendAnalysisResponse)
async def create_trend_analysis(
    request: TrendAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的趋势分析任务
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # 创建分析记录
        analysis_record = {
            "id": analysis_id,
            "keywords": request.keywords,
            "platform_filter": request.platform_filter,
            "time_range": request.time_range,
            "status": "processing",
            "created_at": datetime.now(),
            "user_id": current_user.id,
            "results": None
        }
        
        analysis_storage[analysis_id] = analysis_record
        
        # 这里应该启动后台分析任务
        # 为了演示，我们直接返回一个模拟结果
        mock_results = {
            "summary": f"对关键词 {', '.join(request.keywords)} 的分析已完成",
            "hypeIndex": {"score": 75, "reasoning": "基于社交媒体数据分析"},
            "sentimentSpectrum": {"positive": 60, "neutral": 30, "negative": 10},
            "keyThemes": [
                {"theme": "用户反馈", "summary": "用户对产品功能的积极反馈", "isEmerging": True}
            ],
            "userPersonaSnapshot": {
                "personas": ["科技爱好者 (40%)", "早期采用者 (35%)", "普通用户 (25%)"],
                "coreNeeds": ["了解产品功能", "获取使用指南", "参与社区讨论"]
            },
            "actionableOpportunities": [
                {
                    "opportunity": "内容营销机会",
                    "description": "基于用户兴趣创建相关内容",
                    "targetPersona": "科技爱好者"
                }
            ]
        }
        
        # 更新状态为完成
        analysis_record["status"] = "completed"
        analysis_record["results"] = mock_results
        
        logger.info(f"创建趋势分析任务: {analysis_id}")
        
        return TrendAnalysisResponse(
            id=analysis_id,
            keywords=request.keywords,
            status="completed",
            created_at=analysis_record["created_at"],
            results=mock_results
        )
        
    except Exception as e:
        logger.error(f"创建趋势分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建分析失败: {str(e)}")

@router.get("/list", response_model=List[AnalysisListItem])
async def get_analysis_list(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取用户的分析列表
    """
    try:
        # 过滤当前用户的分析记录
        user_analyses = [
            analysis for analysis in analysis_storage.values()
            if analysis.get("user_id") == current_user.id
        ]
        
        # 按创建时间排序
        user_analyses.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 分页
        paginated_analyses = user_analyses[offset:offset + limit]
        
        return [
            AnalysisListItem(
                id=analysis["id"],
                keywords=analysis["keywords"],
                status=analysis["status"],
                created_at=analysis["created_at"],
                platform_filter=analysis.get("platform_filter")
            )
            for analysis in paginated_analyses
        ]
        
    except Exception as e:
        logger.error(f"获取分析列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析列表失败: {str(e)}")

@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取分析详情
    """
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="分析记录不存在")
        
        analysis = analysis_storage[analysis_id]
        
        # 检查权限
        if analysis.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此分析记录")
        
        return AnalysisDetailResponse(
            id=analysis["id"],
            keywords=analysis["keywords"],
            status=analysis["status"],
            created_at=analysis["created_at"],
            platform_filter=analysis.get("platform_filter"),
            results=analysis.get("results")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析详情失败: {str(e)}")