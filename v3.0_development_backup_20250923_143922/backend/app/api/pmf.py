from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import tempfile
import os
from sqlalchemy.orm import Session

from ..utils.logger import logger
from ..data.models.database import get_db, User
from ..core.auth import get_current_active_user

router = APIRouter()

class PMFValidationRequest(BaseModel):
    product_name: str
    target_market: str
    value_proposition: str
    user_metrics: Dict[str, Any]
    business_metrics: Dict[str, Any]
    pmf_questions: Dict[str, Any]

class PMFReportResponse(BaseModel):
    id: str
    product_name: str
    pmf_score: int
    created_at: datetime
    status: str  # "generating", "completed", "failed"
    report_url: Optional[str] = None

class PMFValidationResponse(BaseModel):
    id: str
    product_name: str
    pmf_score: int
    validation_results: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]
    created_at: datetime

# 内存存储（实际应用中应使用数据库）
pmf_storage = {
    "reports": {},
    "validations": {}
}

@router.get("/reports", response_model=List[PMFReportResponse])
async def get_pmf_reports(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50)
):
    """获取PMF报告列表"""
    try:
        user_reports = [
            report for report in pmf_storage["reports"].values()
            if report.get("user_id") == current_user.id
        ]
        
        # 按创建时间排序
        user_reports.sort(key=lambda x: x["created_at"], reverse=True)
        
        return [
            PMFReportResponse(
                id=report["id"],
                product_name=report["product_name"],
                pmf_score=report["pmf_score"],
                created_at=report["created_at"],
                status=report["status"],
                report_url=report.get("report_url")
            )
            for report in user_reports[:limit]
        ]
        
    except Exception as e:
        logger.error(f"获取PMF报告列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取PMF报告列表失败: {str(e)}")

@router.post("/validate", response_model=PMFValidationResponse)
async def validate_pmf(
    request: PMFValidationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """执行PMF验证分析"""
    try:
        validation_id = str(uuid.uuid4())
        
        # 计算PMF评分
        pmf_score = calculate_pmf_score(request)
        
        # 生成验证结果
        validation_results = generate_validation_results(request, pmf_score)
        
        # 生成建议和下一步
        recommendations = generate_recommendations(pmf_score, validation_results)
        next_steps = generate_next_steps(pmf_score, validation_results)
        
        validation_record = {
            "id": validation_id,
            "product_name": request.product_name,
            "target_market": request.target_market,
            "value_proposition": request.value_proposition,
            "user_metrics": request.user_metrics,
            "business_metrics": request.business_metrics,
            "pmf_questions": request.pmf_questions,
            "pmf_score": pmf_score,
            "validation_results": validation_results,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "created_at": datetime.now(),
            "user_id": current_user.id
        }
        
        pmf_storage["validations"][validation_id] = validation_record
        
        logger.info(f"完成PMF验证: {validation_id} - {request.product_name}")
        
        return PMFValidationResponse(
            id=validation_id,
            product_name=request.product_name,
            pmf_score=pmf_score,
            validation_results=validation_results,
            recommendations=recommendations,
            next_steps=next_steps,
            created_at=validation_record["created_at"]
        )
        
    except Exception as e:
        logger.error(f"PMF验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"PMF验证失败: {str(e)}")

@router.get("/reports/{report_id}/download")
async def download_pmf_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """下载PMF报告"""
    try:
        if report_id not in pmf_storage["reports"]:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        report = pmf_storage["reports"][report_id]
        
        # 检查权限
        if report.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此报告")
        
        # 生成PDF报告内容
        pdf_content = generate_pmf_pdf_report(report)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pmf_report_{report['product_name']}_{timestamp}.pdf"
        
        logger.info(f"下载PMF报告: {report_id}")
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            background=lambda: os.unlink(tmp_file_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载PMF报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")

def calculate_pmf_score(request: PMFValidationRequest) -> int:
    """计算PMF评分"""
    score = 50  # 基础分数
    
    # 用户指标评分
    user_metrics = request.user_metrics
    if user_metrics.get("retention_rate", 0) > 0.4:
        score += 15
    if user_metrics.get("nps_score", 0) > 50:
        score += 10
    if user_metrics.get("daily_active_users", 0) > 1000:
        score += 10
    
    # 商业指标评分
    business_metrics = request.business_metrics
    if business_metrics.get("revenue_growth", 0) > 0.2:
        score += 10
    if business_metrics.get("customer_acquisition_cost", float('inf')) < 100:
        score += 5
    if business_metrics.get("lifetime_value", 0) > 500:
        score += 5
    
    # PMF关键问题评分
    pmf_questions = request.pmf_questions
    if pmf_questions.get("disappointment_score", 0) > 0.4:
        score += 15
    if pmf_questions.get("recommendation_score", 0) > 0.7:
        score += 10
    
    return min(100, max(0, score))

def generate_validation_results(request: PMFValidationRequest, pmf_score: int) -> Dict[str, Any]:
    """生成验证结果"""
    return {
        "overall_assessment": get_overall_assessment(pmf_score),
        "user_satisfaction": analyze_user_satisfaction(request.user_metrics),
        "market_demand": analyze_market_demand(request.business_metrics),
        "product_value": analyze_product_value(request.pmf_questions),
        "growth_potential": analyze_growth_potential(request.business_metrics),
        "risk_factors": identify_risk_factors(request)
    }

def get_overall_assessment(pmf_score: int) -> str:
    """获取整体评估"""
    if pmf_score >= 80:
        return "强PMF - 产品已达到良好的产品市场匹配"
    elif pmf_score >= 60:
        return "中等PMF - 产品显示出积极的市场匹配信号"
    elif pmf_score >= 40:
        return "弱PMF - 产品需要进一步优化以提高市场匹配度"
    else:
        return "无PMF - 产品尚未找到合适的市场匹配"

def analyze_user_satisfaction(user_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """分析用户满意度"""
    return {
        "retention_analysis": "用户留存率表明产品粘性良好" if user_metrics.get("retention_rate", 0) > 0.4 else "需要提高用户留存率",
        "nps_analysis": "用户推荐意愿较高" if user_metrics.get("nps_score", 0) > 50 else "需要改善用户体验",
        "engagement_level": "高" if user_metrics.get("daily_active_users", 0) > 1000 else "中等"
    }

def analyze_market_demand(business_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """分析市场需求"""
    return {
        "growth_trend": "增长强劲" if business_metrics.get("revenue_growth", 0) > 0.2 else "增长缓慢",
        "acquisition_efficiency": "获客成本合理" if business_metrics.get("customer_acquisition_cost", float('inf')) < 100 else "获客成本偏高",
        "value_realization": "用户价值实现良好" if business_metrics.get("lifetime_value", 0) > 500 else "需要提升用户价值"
    }

def analyze_product_value(pmf_questions: Dict[str, Any]) -> Dict[str, Any]:
    """分析产品价值"""
    return {
        "core_value_delivery": "产品核心价值得到用户认可" if pmf_questions.get("disappointment_score", 0) > 0.4 else "需要强化产品核心价值",
        "recommendation_willingness": "用户推荐意愿强" if pmf_questions.get("recommendation_score", 0) > 0.7 else "需要提升产品推荐度"
    }

def analyze_growth_potential(business_metrics: Dict[str, Any]) -> str:
    """分析增长潜力"""
    if business_metrics.get("revenue_growth", 0) > 0.3:
        return "高增长潜力"
    elif business_metrics.get("revenue_growth", 0) > 0.1:
        return "中等增长潜力"
    else:
        return "增长潜力有限"

def identify_risk_factors(request: PMFValidationRequest) -> List[str]:
    """识别风险因素"""
    risks = []
    
    if request.user_metrics.get("retention_rate", 0) < 0.3:
        risks.append("用户留存率偏低")
    
    if request.business_metrics.get("customer_acquisition_cost", 0) > 200:
        risks.append("获客成本过高")
    
    if request.pmf_questions.get("disappointment_score", 0) < 0.3:
        risks.append("用户对产品依赖度不足")
    
    return risks

def generate_recommendations(pmf_score: int, validation_results: Dict[str, Any]) -> List[str]:
    """生成建议"""
    recommendations = []
    
    if pmf_score < 60:
        recommendations.append("重新审视产品核心价值主张，确保解决真实用户痛点")
        recommendations.append("深入了解目标用户需求，优化产品功能")
    
    if pmf_score < 80:
        recommendations.append("加强用户反馈收集，持续优化产品体验")
        recommendations.append("扩大用户测试范围，验证产品市场适应性")
    
    recommendations.append("建立完善的用户成功体系，提高用户留存")
    recommendations.append("优化营销策略，降低获客成本")
    
    return recommendations

def generate_next_steps(pmf_score: int, validation_results: Dict[str, Any]) -> List[str]:
    """生成下一步行动"""
    next_steps = []
    
    if pmf_score < 40:
        next_steps.append("暂停大规模推广，专注产品优化")
        next_steps.append("进行深度用户访谈，重新定义产品方向")
    elif pmf_score < 70:
        next_steps.append("小规模测试优化方案，验证改进效果")
        next_steps.append("建立用户反馈循环，快速迭代产品")
    else:
        next_steps.append("准备扩大市场推广，加速用户增长")
        next_steps.append("考虑融资计划，支持业务扩张")
    
    next_steps.append("建立PMF监控体系，定期评估产品市场匹配度")
    
    return next_steps

def generate_pmf_pdf_report(report: Dict[str, Any]) -> bytes:
    """生成PMF PDF报告"""
    # 这里应该使用实际的PDF生成库，如reportlab
    # 为了演示，返回模拟的PDF内容
    mock_pdf_content = f"""
    PMF验证报告
    
    产品名称: {report['product_name']}
    PMF评分: {report['pmf_score']}/100
    生成时间: {report['created_at']}
    
    这是一个模拟的PDF报告内容。
    在实际应用中，这里会包含详细的PMF分析结果、图表和建议。
    """.encode('utf-8')
    
    return mock_pdf_content