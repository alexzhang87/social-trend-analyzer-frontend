from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from sqlalchemy.orm import Session

from ..services.enhanced_startup_consultant_service import EnhancedStartupConsultantService
from ..utils.logger import logger
from ..data.models.database import get_db, User
from ..core.auth import get_current_active_user

router = APIRouter()
enhanced_consultant_service = EnhancedStartupConsultantService()

class StartupAdviceRequest(BaseModel):
    idea_description: str = Field(..., description="Detailed description of the startup idea")
    industry: Optional[str] = Field(None, description="Target industry")
    target_market: Optional[str] = Field(None, description="Target market description")
    business_stage: str = Field("idea", description="Current business stage: idea, mvp, early, growth")
    budget_range: Optional[str] = Field(None, description="Available budget range")
    team_size: Optional[int] = Field(None, description="Current team size")
    specific_questions: Optional[List[str]] = Field(None, description="Specific questions to address")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class StartupAdviceResponse(BaseModel):
    advice_id: str
    market_analysis: Dict[str, Any]
    business_model_suggestions: List[Dict[str, Any]]
    technical_roadmap: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    next_steps: List[str]
    confidence_score: float
    generated_at: datetime
    follow_up_questions: List[str]
    sources: List[Dict[str, Any]]

class ModelStatusResponse(BaseModel):
    model_loaded: bool
    model_path: str
    model_type: str
    vocab_size: int
    last_loaded: Optional[datetime]
    performance_metrics: Dict[str, Any]

class AdviceHistoryResponse(BaseModel):
    advice_history: List[Dict[str, Any]]
    total_count: int
    has_more: bool

class BatchAdviceRequest(BaseModel):
    ideas: List[StartupAdviceRequest] = Field(..., description="List of startup ideas to analyze")
    analysis_type: str = Field("comprehensive", description="Type of analysis: quick, comprehensive, detailed")

class BatchAdviceResponse(BaseModel):
    batch_id: str
    results: List[StartupAdviceResponse]
    summary: Dict[str, Any]
    processing_time: float
    generated_at: datetime

# In-memory storage for advice history (should use database in production)
advice_history = {}

@router.post("/generate-advice", response_model=StartupAdviceResponse)
async def generate_startup_advice(
    request: StartupAdviceRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = None
):
    """
    Generate comprehensive startup advice using the enhanced model
    """
    try:
        advice_id = str(uuid.uuid4())
        
        # Generate startup advice using enhanced model
        advice = enhanced_consultant_service.generate_startup_advice(
            idea_description=request.idea_description,
            industry=request.industry,
            target_market=request.target_market,
            business_stage=request.business_stage,
            budget_range=request.budget_range,
            team_size=request.team_size,
            specific_questions=request.specific_questions,
            context_data=request.context_data
        )
        
        # Create response
        response = StartupAdviceResponse(
            advice_id=advice_id,
            market_analysis=advice.get("market_analysis", {}),
            business_model_suggestions=advice.get("business_model_suggestions", []),
            technical_roadmap=advice.get("technical_roadmap", {}),
            risk_assessment=advice.get("risk_assessment", {}),
            next_steps=advice.get("next_steps", []),
            confidence_score=advice.get("confidence_score", 0.8),
            generated_at=datetime.now(),
            follow_up_questions=advice.get("follow_up_questions", []),
            sources=advice.get("sources", [])
        )
        
        # Store in history
        if current_user.id not in advice_history:
            advice_history[current_user.id] = []
        
        advice_history[current_user.id].append({
            "advice_id": advice_id,
            "request": request.dict(),
            "response": response.dict(),
            "timestamp": datetime.now()
        })
        
        logger.info(f"Generated startup advice {advice_id} for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating startup advice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate advice: {str(e)}")

@router.post("/batch-advice", response_model=BatchAdviceResponse)
async def generate_batch_advice(
    request: BatchAdviceRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = None
):
    """
    Generate advice for multiple startup ideas in batch
    """
    try:
        batch_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        results = []
        for idea_request in request.ideas:
            advice = enhanced_consultant_service.generate_startup_advice(
                idea_description=idea_request.idea_description,
                industry=idea_request.industry,
                target_market=idea_request.target_market,
                business_stage=idea_request.business_stage,
                budget_range=idea_request.budget_range,
                team_size=idea_request.team_size,
                specific_questions=idea_request.specific_questions,
                context_data=idea_request.context_data
            )
            
            advice_id = str(uuid.uuid4())
            response = StartupAdviceResponse(
                advice_id=advice_id,
                market_analysis=advice.get("market_analysis", {}),
                business_model_suggestions=advice.get("business_model_suggestions", []),
                technical_roadmap=advice.get("technical_roadmap", {}),
                risk_assessment=advice.get("risk_assessment", {}),
                next_steps=advice.get("next_steps", []),
                confidence_score=advice.get("confidence_score", 0.8),
                generated_at=datetime.now(),
                follow_up_questions=advice.get("follow_up_questions", []),
                sources=advice.get("sources", [])
            )
            results.append(response)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = {
            "total_ideas": len(request.ideas),
            "avg_confidence": sum(r.confidence_score for r in results) / len(results),
            "common_industries": list(set(r.industry for r in request.ideas if r.industry)),
            "processing_time": processing_time
        }
        
        batch_response = BatchAdviceResponse(
            batch_id=batch_id,
            results=results,
            summary=summary,
            processing_time=processing_time,
            generated_at=datetime.now()
        )
        
        logger.info(f"Generated batch advice {batch_id} for {len(request.ideas)} ideas")
        return batch_response
        
    except Exception as e:
        logger.error(f"Error generating batch advice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate batch advice: {str(e)}")

@router.get("/model-status", response_model=ModelStatusResponse)
async def get_model_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the status of the enhanced startup consultant model
    """
    try:
        status = enhanced_consultant_service.get_model_status()
        
        return ModelStatusResponse(
            model_loaded=status.get("is_loaded", False),
            model_path=status.get("model_path", ""),
            model_type=status.get("model_type", "enhanced_consultant"),
            vocab_size=status.get("vocab_size", 1000),
            last_loaded=status.get("last_loaded"),
            performance_metrics=status.get("performance_metrics", {})
        )
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.get("/advice-history", response_model=AdviceHistoryResponse)
async def get_advice_history(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    business_stage: Optional[str] = Query(None, description="Filter by business stage")
):
    """
    Get user's advice generation history
    """
    try:
        user_history = advice_history.get(current_user.id, [])
        
        # Filter by business stage if provided
        if business_stage:
            user_history = [
                h for h in user_history 
                if h["request"].get("business_stage") == business_stage
            ]
        
        # Sort by timestamp descending
        user_history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total_count = len(user_history)
        paginated_history = user_history[offset:offset + limit]
        has_more = offset + limit < total_count
        
        return AdviceHistoryResponse(
            advice_history=paginated_history,
            total_count=total_count,
            has_more=has_more
        )
        
    except Exception as e:
        logger.error(f"Error getting advice history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get advice history: {str(e)}")

@router.get("/advice/{advice_id}")
async def get_advice_details(
    advice_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific advice details by ID
    """
    try:
        user_history = advice_history.get(current_user.id, [])
        
        for advice_record in user_history:
            if advice_record["advice_id"] == advice_id:
                return advice_record
        
        raise HTTPException(status_code=404, detail="Advice not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting advice details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get advice details: {str(e)}")

@router.post("/reload-model")
async def reload_model(
    current_user: User = Depends(get_current_active_user)
):
    """
    Reload the enhanced startup consultant model
    """
    try:
        # Check if user has admin privileges (simplified check)
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        success = enhanced_consultant_service.reload_model()
        
        if success:
            return {"message": "Model reloaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reload model")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the enhanced consultant service
    """
    try:
        status = enhanced_consultant_service.get_model_status()
        
        return {
            "status": "healthy" if status.get("is_loaded", False) else "degraded",
            "model_loaded": status.get("is_loaded", False),
            "timestamp": datetime.now(),
            "service": "enhanced_startup_consultant"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(),
            "service": "enhanced_startup_consultant"
        }

@router.get("/templates")
async def get_advice_templates():
    """
    Get predefined advice templates for different business stages
    """
    try:
        templates = {
            "idea": {
                "name": "Idea Stage Template",
                "description": "For early-stage ideas and concepts",
                "suggested_questions": [
                    "What is the core problem you're solving?",
                    "Who is your target customer?",
                    "What makes your solution unique?",
                    "How will you validate your idea?"
                ],
                "focus_areas": ["market_validation", "problem_definition", "target_audience"]
            },
            "mvp": {
                "name": "MVP Stage Template", 
                "description": "For minimum viable product development",
                "suggested_questions": [
                    "What features are essential for your MVP?",
                    "How will you measure product-market fit?",
                    "What is your go-to-market strategy?",
                    "How will you gather user feedback?"
                ],
                "focus_areas": ["product_development", "user_testing", "market_entry"]
            },
            "early": {
                "name": "Early Stage Template",
                "description": "For early-stage startups with initial traction",
                "suggested_questions": [
                    "How can you scale your current operations?",
                    "What are your key growth metrics?",
                    "How will you expand your customer base?",
                    "What funding options should you consider?"
                ],
                "focus_areas": ["scaling", "growth_metrics", "funding"]
            },
            "growth": {
                "name": "Growth Stage Template",
                "description": "For growing startups looking to scale",
                "suggested_questions": [
                    "How can you optimize your business model?",
                    "What new markets should you enter?",
                    "How will you manage rapid growth?",
                    "What strategic partnerships make sense?"
                ],
                "focus_areas": ["optimization", "expansion", "partnerships"]
            }
        }
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")