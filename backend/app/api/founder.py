from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from ..utils.logger import logger
from ..data.models.database import get_db, User
from ..core.auth import get_current_active_user

router = APIRouter()

class PMFMetricsResponse(BaseModel):
    total_assessments: int
    average_score: float
    latest_score: Optional[int] = None
    trend: str  # "improving", "declining", "stable"

class BusinessIdeaRequest(BaseModel):
    title: str
    description: str
    target_market: str
    problem_statement: str
    solution_approach: str

class BusinessIdeaResponse(BaseModel):
    id: str
    title: str
    description: str
    target_market: str
    problem_statement: str
    solution_approach: str
    created_at: datetime
    pmf_score: Optional[int] = None
    status: str  # "draft", "analyzing", "completed"

class CompetitorResponse(BaseModel):
    id: str
    name: str
    description: str
    strengths: List[str]
    weaknesses: List[str]
    market_position: str
    website: Optional[str] = None

class PMFAssessmentRequest(BaseModel):
    product_name: str
    target_audience: str
    core_value_proposition: str
    key_metrics: Dict[str, Any]
    user_feedback: List[str]
    market_indicators: Dict[str, Any]

class PMFAssessmentResponse(BaseModel):
    id: str
    product_name: str
    pmf_score: int
    assessment_date: datetime
    key_findings: List[str]
    recommendations: List[str]
    next_steps: List[str]

# 内存存储（实际应用中应使用数据库）
founder_storage = {
    "business_ideas": {},
    "pmf_assessments": {},
    "competitors": {}
}

@router.get("/pmf-metrics", response_model=PMFMetricsResponse)
async def get_pmf_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """获取PMF指标概览"""
    try:
        user_assessments = [
            assessment for assessment in founder_storage["pmf_assessments"].values()
            if assessment.get("user_id") == current_user.id
        ]
        
        if not user_assessments:
            return PMFMetricsResponse(
                total_assessments=0,
                average_score=0.0,
                latest_score=None,
                trend="stable"
            )
        
        scores = [assessment["pmf_score"] for assessment in user_assessments]
        latest_score = scores[-1] if scores else None
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        # 简单趋势计算
        trend = "stable"
        if len(scores) >= 2:
            if scores[-1] > scores[-2]:
                trend = "improving"
            elif scores[-1] < scores[-2]:
                trend = "declining"
        
        return PMFMetricsResponse(
            total_assessments=len(user_assessments),
            average_score=round(average_score, 1),
            latest_score=latest_score,
            trend=trend
        )
        
    except Exception as e:
        logger.error(f"获取PMF指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PMF指标失败: {str(e)}")

@router.get("/business-ideas", response_model=List[BusinessIdeaResponse])
async def get_business_ideas(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50)
):
    """获取商业想法列表"""
    try:
        user_ideas = [
            idea for idea in founder_storage["business_ideas"].values()
            if idea.get("user_id") == current_user.id
        ]
        
        # 按创建时间排序
        user_ideas.sort(key=lambda x: x["created_at"], reverse=True)
        
        return [
            BusinessIdeaResponse(
                id=idea["id"],
                title=idea["title"],
                description=idea["description"],
                target_market=idea["target_market"],
                problem_statement=idea["problem_statement"],
                solution_approach=idea["solution_approach"],
                created_at=idea["created_at"],
                pmf_score=idea.get("pmf_score"),
                status=idea.get("status", "draft")
            )
            for idea in user_ideas[:limit]
        ]
        
    except Exception as e:
        logger.error(f"获取商业想法列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取商业想法列表失败: {str(e)}")

@router.post("/business-ideas", response_model=BusinessIdeaResponse)
async def create_business_idea(
    request: BusinessIdeaRequest,
    current_user: User = Depends(get_current_active_user)
):
    """创建新的商业想法"""
    try:
        idea_id = str(uuid.uuid4())
        
        idea_record = {
            "id": idea_id,
            "title": request.title,
            "description": request.description,
            "target_market": request.target_market,
            "problem_statement": request.problem_statement,
            "solution_approach": request.solution_approach,
            "created_at": datetime.now(),
            "user_id": current_user.id,
            "status": "draft",
            "pmf_score": None
        }
        
        founder_storage["business_ideas"][idea_id] = idea_record
        
        logger.info(f"创建商业想法: {idea_id} - {request.title}")
        
        return BusinessIdeaResponse(
            id=idea_id,
            title=request.title,
            description=request.description,
            target_market=request.target_market,
            problem_statement=request.problem_statement,
            solution_approach=request.solution_approach,
            created_at=idea_record["created_at"],
            pmf_score=None,
            status="draft"
        )
        
    except Exception as e:
        logger.error(f"创建商业想法失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建商业想法失败: {str(e)}")

@router.get("/competitors", response_model=List[CompetitorResponse])
async def get_competitors(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50)
):
    """获取竞争对手分析"""
    try:
        # 返回模拟的竞争对手数据
        mock_competitors = [
            {
                "id": "comp_1",
                "name": "TrendScope",
                "description": "专业的社交媒体趋势分析平台",
                "strengths": ["强大的数据源", "实时分析", "企业级功能"],
                "weaknesses": ["价格昂贵", "学习曲线陡峭"],
                "market_position": "高端市场领导者",
                "website": "https://trendscope.com"
            },
            {
                "id": "comp_2",
                "name": "SocialInsight",
                "description": "面向中小企业的社交媒体分析工具",
                "strengths": ["易于使用", "价格合理", "良好的客户支持"],
                "weaknesses": ["功能有限", "数据深度不足"],
                "market_position": "中端市场竞争者",
                "website": "https://socialinsight.com"
            },
            {
                "id": "comp_3",
                "name": "ViralTracker",
                "description": "专注于病毒式传播内容的分析平台",
                "strengths": ["独特的病毒式分析", "创新的可视化"],
                "weaknesses": ["功能单一", "市场覆盖有限"],
                "market_position": "细分市场专家",
                "website": "https://viraltracker.com"
            }
        ]
        
        return [
            CompetitorResponse(
                id=comp["id"],
                name=comp["name"],
                description=comp["description"],
                strengths=comp["strengths"],
                weaknesses=comp["weaknesses"],
                market_position=comp["market_position"],
                website=comp.get("website")
            )
            for comp in mock_competitors[:limit]
        ]
        
    except Exception as e:
        logger.error(f"获取竞争对手分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取竞争对手分析失败: {str(e)}")

@router.post("/pmf-assessment", response_model=PMFAssessmentResponse)
async def create_pmf_assessment(
    request: PMFAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """创建PMF评估"""
    try:
        assessment_id = str(uuid.uuid4())
        
        # 模拟PMF评分计算
        pmf_score = 75  # 基础分数
        
        # 根据关键指标调整分数
        if request.key_metrics.get("user_retention", 0) > 0.6:
            pmf_score += 10
        if request.key_metrics.get("nps_score", 0) > 50:
            pmf_score += 10
        if len(request.user_feedback) > 5:
            pmf_score += 5
        
        pmf_score = min(100, pmf_score)  # 确保不超过100
        
        assessment_record = {
            "id": assessment_id,
            "product_name": request.product_name,
            "target_audience": request.target_audience,
            "core_value_proposition": request.core_value_proposition,
            "key_metrics": request.key_metrics,
            "user_feedback": request.user_feedback,
            "market_indicators": request.market_indicators,
            "pmf_score": pmf_score,
            "assessment_date": datetime.now(),
            "user_id": current_user.id
        }
        
        founder_storage["pmf_assessments"][assessment_id] = assessment_record
        
        # 生成关键发现和建议
        key_findings = [
            f"产品'{request.product_name}'的PMF评分为{pmf_score}分",
            "用户反馈显示产品解决了核心痛点",
            "市场指标表明存在增长潜力"
        ]
        
        recommendations = [
            "继续收集用户反馈，优化产品功能",
            "扩大目标用户群体的市场验证",
            "建立更完善的用户留存机制"
        ]
        
        next_steps = [
            "制定详细的产品路线图",
            "启动A/B测试验证关键假设",
            "准备下一轮融资材料"
        ]
        
        logger.info(f"创建PMF评估: {assessment_id} - {request.product_name}")
        
        return PMFAssessmentResponse(
            id=assessment_id,
            product_name=request.product_name,
            pmf_score=pmf_score,
            assessment_date=assessment_record["assessment_date"],
            key_findings=key_findings,
            recommendations=recommendations,
            next_steps=next_steps
        )
        
    except Exception as e:
        logger.error(f"创建PMF评估失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建PMF评估失败: {str(e)}")