"""
MonkeyLearn API 路由
提供高级文本分析功能的API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from ..services.monkeylearn_service import monkeylearn_service
from ..services.enhanced_text_analysis_service import enhanced_text_analysis_service
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class TextAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., description="要分析的文本列表", max_items=200)
    include_local_analysis: bool = Field(default=True, description="是否包含本地分析结果")

class MonkeyLearnStatusResponse(BaseModel):
    available: bool
    api_configured: bool
    features: Dict[str, bool]
    note: str

@router.get("/status")
async def get_monkeylearn_status() -> MonkeyLearnStatusResponse:
    """获取MonkeyLearn服务状态"""
    status = monkeylearn_service.get_status()
    return MonkeyLearnStatusResponse(**status)

@router.post("/sentiment-analysis")
async def analyze_sentiment(
    request: TextAnalysisRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    MonkeyLearn情感分析
    
    需要配置MONKEYLEARN_API_TOKEN环境变量
    如果未配置，将使用本地VADER/TextBlob分析
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="文本列表不能为空")
        
        # 执行MonkeyLearn情感分析
        ml_results = await monkeylearn_service.analyze_sentiment(request.texts)
        
        response = {
            "status": "success",
            "monkeylearn_available": monkeylearn_service.available,
            "texts_analyzed": len(request.texts),
            "results": ml_results
        }
        
        # 可选：包含本地分析结果用于对比
        if request.include_local_analysis and len(request.texts) <= 20:
            local_results = []
            for text in request.texts:
                local_result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(text)
                local_results.append({
                    "text": text,
                    "local_sentiment": local_result.get("sentiment", "neutral"),
                    "local_confidence": local_result.get("confidence", 0.0)
                })
            response["local_comparison"] = local_results
        
        return response
        
    except Exception as e:
        logger.error(f"MonkeyLearn情感分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/topic-classification")
async def classify_topics(
    request: TextAnalysisRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    MonkeyLearn主题分类
    
    需要配置MONKEYLEARN_API_TOKEN环境变量
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="文本列表不能为空")
        
        if not monkeylearn_service.available:
            raise HTTPException(
                status_code=503, 
                detail="MonkeyLearn API未配置，请设置MONKEYLEARN_API_TOKEN环境变量"
            )
        
        # 执行主题分类
        results = await monkeylearn_service.classify_topics(request.texts)
        
        return {
            "status": "success",
            "texts_analyzed": len(request.texts),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MonkeyLearn主题分类失败: {e}")
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")

@router.post("/intent-detection")
async def detect_intent(
    request: TextAnalysisRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    MonkeyLearn意图检测
    
    需要配置MONKEYLEARN_API_TOKEN环境变量
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="文本列表不能为空")
        
        if not monkeylearn_service.available:
            raise HTTPException(
                status_code=503, 
                detail="MonkeyLearn API未配置，请设置MONKEYLEARN_API_TOKEN环境变量"
            )
        
        # 执行意图检测
        results = await monkeylearn_service.detect_intent(request.texts)
        
        return {
            "status": "success",
            "texts_analyzed": len(request.texts),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MonkeyLearn意图检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    request: TextAnalysisRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    综合文本分析 (本地分析 + MonkeyLearn分析)
    
    结合本地VADER/TextBlob/NLTK分析和MonkeyLearn高级分析
    即使MonkeyLearn不可用，也会提供本地分析结果
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="文本列表不能为空")
        
        # 执行综合分析
        results = await enhanced_text_analysis_service.comprehensive_analysis_with_monkeylearn(request.texts)
        
        # 统计分析
        sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}
        ml_available_count = 0
        
        for result in results:
            local_sentiment = result.get("local_analysis", {}).get("sentiment", {}).get("sentiment", "neutral")
            sentiment_summary[local_sentiment] = sentiment_summary.get(local_sentiment, 0) + 1
            
            if result.get("monkeylearn_analysis"):
                ml_available_count += 1
        
        return {
            "status": "success",
            "monkeylearn_available": monkeylearn_service.available,
            "texts_analyzed": len(request.texts),
            "monkeylearn_analyses": ml_available_count,
            "sentiment_summary": sentiment_summary,
            "results": results,
            "analysis_info": {
                "local_methods": ["VADER", "TextBlob", "NLTK"],
                "monkeylearn_methods": ["Sentiment", "Topics", "Intent"] if monkeylearn_service.available else [],
                "note": "如果MonkeyLearn未配置，将仅使用本地分析方法"
            }
        }
        
    except Exception as e:
        logger.error(f"综合文本分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/models")
async def get_available_models() -> Dict[str, Any]:
    """获取可用的分析模型信息"""
    return {
        "local_models": {
            "vader": {
                "description": "专门针对社交媒体文本的情感分析",
                "type": "sentiment_analysis",
                "free": True
            },
            "textblob": {
                "description": "通用文本情感分析和语言处理",
                "type": "sentiment_analysis", 
                "free": True
            },
            "nltk": {
                "description": "自然语言处理工具包，支持分词、词性标注、实体识别",
                "type": "nlp_toolkit",
                "free": True
            }
        },
        "monkeylearn_models": {
            "sentiment": {
                "id": "cl_pi3C7JiL",
                "description": "MonkeyLearn预训练情感分析模型",
                "type": "sentiment_analysis",
                "available": monkeylearn_service.available
            },
            "emotion": {
                "id": "cl_Jx8qzYJh", 
                "description": "情绪检测模型",
                "type": "emotion_detection",
                "available": monkeylearn_service.available
            },
            "topics": {
                "id": "cl_5icAVzKR",
                "description": "主题分类模型",
                "type": "topic_classification",
                "available": monkeylearn_service.available
            },
            "intent": {
                "id": "cl_3RnrF5nh",
                "description": "意图分析模型", 
                "type": "intent_detection",
                "available": monkeylearn_service.available
            }
        },
        "note": "MonkeyLearn是付费服务，需要API Token。本地模型完全免费。"
    }