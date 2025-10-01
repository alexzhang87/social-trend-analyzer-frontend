from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..services.semantic_analysis_service import SemanticAnalysisService
from ..core.auth import get_current_user, require_subscription
from ..core.database import get_db
from ..utils.logger import logger
from sqlalchemy.orm import Session

router = APIRouter()
semantic_service = SemanticAnalysisService()

class TopicExtractionRequest(BaseModel):
    texts: List[str] = Field(..., description="需要分析的文本列表", min_items=1, max_items=100)
    num_topics: Optional[int] = Field(5, description="主题数量", ge=2, le=20)
    language: Optional[str] = Field("auto", description="文本语言")
    
class EntityRecognitionRequest(BaseModel):
    texts: List[str] = Field(..., description="需要分析的文本列表", min_items=1, max_items=50)
    entity_types: Optional[List[str]] = Field(None, description="实体类型过滤")
    
class ContentQualityRequest(BaseModel):
    texts: List[str] = Field(..., description="需要分析的文本列表", min_items=1, max_items=50)
    criteria: Optional[List[str]] = Field(None, description="质量评估标准")
    
class SemanticSimilarityRequest(BaseModel):
    texts: List[str] = Field(..., description="需要分析的文本列表", min_items=2, max_items=50)
    threshold: Optional[float] = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    
class TopicExtractionResponse(BaseModel):
    topics: List[Dict[str, Any]]
    topic_distribution: List[Dict[str, Any]]
    word_frequencies: Dict[str, int]
    emerging_topics: List[Dict[str, Any]]
    insights: List[str]
    
class EntityRecognitionResponse(BaseModel):
    entities: Dict[str, List[Dict[str, Any]]]
    entity_frequencies: Dict[str, int]
    insights: List[str]
    
class ContentQualityResponse(BaseModel):
    quality_scores: List[Dict[str, Any]]
    overall_quality: Dict[str, Any]
    improvement_suggestions: List[str]
    insights: List[str]
    
class SemanticSimilarityResponse(BaseModel):
    similarity_matrix: List[List[float]]
    similar_pairs: List[Dict[str, Any]]
    diversity_score: float
    uniqueness_scores: List[float]
    insights: List[str]
    
class AnalysisHistoryResponse(BaseModel):
    analyses: List[Dict[str, Any]]
    total_count: int
    
@router.post("/topics/extract", response_model=TopicExtractionResponse)
async def extract_topics(
    request: TopicExtractionRequest,
    current_user = Depends(get_current_user),
    subscription_check = Depends(require_subscription(["premium", "enterprise"])),
    db: Session = Depends(get_db)
):
    """
    主题提取和建模分析
    
    需要Premium或Enterprise订阅
    - 最多支持100个文本
    - 支持2-20个主题数量
    - 提供主题分布和词频统计
    - 识别新兴主题
    """
    try:
        logger.info(f"用户 {current_user.id} 请求主题提取分析，文本数量: {len(request.texts)}")
        
        # 检查用户使用限制
        if current_user.subscription_type == "premium" and len(request.texts) > 50:
            raise HTTPException(
                status_code=403, 
                detail="Premium用户最多支持50个文本的主题分析"
            )
            
        result = await semantic_service.extract_topics(
            texts=request.texts,
            num_topics=request.num_topics,
            language=request.language,
            user_id=current_user.id,
            db=db
        )
        
        logger.info(f"主题提取分析完成，识别到 {len(result['topics'])} 个主题")
        return TopicExtractionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"主题提取分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="主题提取分析失败")
        
@router.post("/entities/recognize", response_model=EntityRecognitionResponse)
async def recognize_entities(
    request: EntityRecognitionRequest,
    current_user = Depends(get_current_user),
    subscription_check = Depends(require_subscription(["premium", "enterprise"])),
    db: Session = Depends(get_db)
):
    """
    实体识别和分析
    
    需要Premium或Enterprise订阅
    - 最多支持50个文本
    - 识别人名、组织、产品、地点等实体
    - 提供实体频率统计
    - 支持实体类型过滤
    """
    try:
        logger.info(f"用户 {current_user.id} 请求实体识别分析，文本数量: {len(request.texts)}")
        
        result = await semantic_service.recognize_entities(
            texts=request.texts,
            entity_types=request.entity_types,
            user_id=current_user.id,
            db=db
        )
        
        total_entities = sum(len(entities) for entities in result['entities'].values())
        logger.info(f"实体识别完成，识别到 {total_entities} 个实体")
        return EntityRecognitionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"实体识别分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="实体识别分析失败")
        
@router.post("/quality/analyze", response_model=ContentQualityResponse)
async def analyze_content_quality(
    request: ContentQualityRequest,
    current_user = Depends(get_current_user),
    subscription_check = Depends(require_subscription(["premium", "enterprise"])),
    db: Session = Depends(get_db)
):
    """
    内容质量分析
    
    需要Premium或Enterprise订阅
    - 最多支持50个文本
    - 评估内容长度、参与度、信息密度等
    - 提供质量评分和改进建议
    - 支持自定义评估标准
    """
    try:
        logger.info(f"用户 {current_user.id} 请求内容质量分析，文本数量: {len(request.texts)}")
        
        result = await semantic_service.analyze_content_quality(
            texts=request.texts,
            criteria=request.criteria,
            user_id=current_user.id,
            db=db
        )
        
        avg_score = result['overall_quality'].get('average_score', 0)
        logger.info(f"内容质量分析完成，平均质量评分: {avg_score:.2f}")
        return ContentQualityResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"内容质量分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内容质量分析失败")
        
@router.post("/similarity/analyze", response_model=SemanticSimilarityResponse)
async def analyze_semantic_similarity(
    request: SemanticSimilarityRequest,
    current_user = Depends(get_current_user),
    subscription_check = Depends(require_subscription(["premium", "enterprise"])),
    db: Session = Depends(get_db)
):
    """
    语义相似度分析
    
    需要Premium或Enterprise订阅
    - 最多支持50个文本
    - 计算文本间相似度矩阵
    - 识别相似文本对
    - 评估内容多样性和独特性
    """
    try:
        logger.info(f"用户 {current_user.id} 请求语义相似度分析，文本数量: {len(request.texts)}")
        
        result = await semantic_service.analyze_semantic_similarity(
            texts=request.texts,
            threshold=request.threshold,
            user_id=current_user.id,
            db=db
        )
        
        similar_pairs_count = len(result['similar_pairs'])
        diversity_score = result['diversity_score']
        logger.info(f"语义相似度分析完成，发现 {similar_pairs_count} 对相似文本，多样性评分: {diversity_score:.2f}")
        return SemanticSimilarityResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语义相似度分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="语义相似度分析失败")
        
@router.get("/history", response_model=AnalysisHistoryResponse)
async def get_semantic_analysis_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=50, description="每页数量")
):
    """
    获取用户语义分析历史记录
    
    - 支持分页查询
    - 返回分析类型、时间、结果摘要等信息
    """
    try:
        logger.info(f"用户 {current_user.id} 请求语义分析历史记录")
        
        result = await semantic_service.get_user_analysis_history(
            user_id=current_user.id,
            db=db,
            page=page,
            limit=limit
        )
        
        logger.info(f"返回 {len(result['analyses'])} 条历史记录")
        return AnalysisHistoryResponse(**result)
        
    except Exception as e:
        logger.error(f"获取语义分析历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")
        
@router.get("/templates")
async def get_analysis_templates(
    current_user = Depends(get_current_user)
):
    """
    获取语义分析预设模板
    
    - 提供不同场景的分析模板
    - 包括参数配置和使用说明
    """
    templates = {
        "social_media_analysis": {
            "name": "社交媒体内容分析",
            "description": "适用于社交媒体帖子的语义分析",
            "recommended_settings": {
                "num_topics": 8,
                "entity_types": ["person", "organization", "hashtag", "mention"],
                "quality_criteria": ["engagement", "originality", "sentiment_consistency"]
            }
        },
        "news_analysis": {
            "name": "新闻内容分析",
            "description": "适用于新闻文章的语义分析",
            "recommended_settings": {
                "num_topics": 10,
                "entity_types": ["person", "organization", "location", "event"],
                "quality_criteria": ["information_density", "objectivity", "completeness"]
            }
        },
        "product_review_analysis": {
            "name": "产品评论分析",
            "description": "适用于产品评论的语义分析",
            "recommended_settings": {
                "num_topics": 6,
                "entity_types": ["product", "feature", "brand"],
                "quality_criteria": ["detail_level", "helpfulness", "authenticity"]
            }
        },
        "academic_analysis": {
            "name": "学术文献分析",
            "description": "适用于学术论文和研究报告的语义分析",
            "recommended_settings": {
                "num_topics": 12,
                "entity_types": ["concept", "methodology", "author", "institution"],
                "quality_criteria": ["academic_rigor", "novelty", "citation_potential"]
            }
        }
    }
    
    return {"templates": templates}
    
@router.get("/stats")
async def get_semantic_analysis_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户语义分析统计信息
    
    - 分析次数统计
    - 常用分析类型
    - 使用趋势等
    """
    try:
        stats = await semantic_service.get_user_analysis_stats(
            user_id=current_user.id,
            db=db
        )
        
        return {"stats": stats}
        
    except Exception as e:
        logger.error(f"获取语义分析统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")