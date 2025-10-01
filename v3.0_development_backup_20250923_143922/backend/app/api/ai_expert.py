from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from sqlalchemy.orm import Session

from ..services.ai_expert_service import AIExpertService
from ..utils.logger import logger
from ..data.models.database import get_db, User
from ..core.auth import get_current_active_user

router = APIRouter()
ai_expert_service = AIExpertService()

class ExpertConsultationRequest(BaseModel):
    idea_text: str = Field(..., description="User's business idea or concept")
    pmf_data: Optional[Dict[str, Any]] = Field(None, description="PMF evaluation data from previous analysis")
    analysis_data: Optional[Dict[str, Any]] = Field(None, description="Previous analysis results")
    consultation_type: str = Field("general", description="Type of consultation: general, technical, market, business")
    
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)

class ExpertChatRequest(BaseModel):
    session_id: str = Field(..., description="Chat session ID")
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class ExpertChatResponse(BaseModel):
    session_id: str
    message_id: str
    response: str
    expert_type: str
    confidence_score: float
    sources: List[Dict[str, Any]]
    follow_up_questions: List[str]
    timestamp: datetime

class ConsultationSession(BaseModel):
    session_id: str
    user_id: str
    idea_summary: str
    expert_type: str
    status: str  # active, completed, paused
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage]
    context_data: Dict[str, Any]

class ExpertRecommendation(BaseModel):
    expert_type: str
    confidence: float
    reasoning: str
    estimated_session_length: int  # minutes

class SessionListResponse(BaseModel):
    sessions: List[ConsultationSession]
    total_count: int
    has_more: bool

# In-memory storage for demo (should use database in production)
consultation_sessions = {}
chat_history = {}

@router.post("/recommend-expert", response_model=List[ExpertRecommendation])
async def recommend_expert(
    request: ExpertConsultationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Recommend the most suitable AI expert based on user's idea and context
    """
    try:
        recommendations = await ai_expert_service.recommend_expert(
            idea_text=request.idea_text,
            pmf_data=request.pmf_data,
            analysis_data=request.analysis_data,
            user_id=current_user.id
        )
        
        logger.info(f"Generated expert recommendations for user {current_user.id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error recommending expert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to recommend expert: {str(e)}")

@router.post("/start-consultation", response_model=ConsultationSession)
async def start_consultation(
    request: ExpertConsultationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start a new AI expert consultation session
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Create consultation session
        session = await ai_expert_service.create_consultation_session(
            session_id=session_id,
            user_id=current_user.id,
            idea_text=request.idea_text,
            pmf_data=request.pmf_data,
            analysis_data=request.analysis_data,
            consultation_type=request.consultation_type
        )
        
        # Store session in memory (should use database)
        consultation_sessions[session_id] = session
        
        logger.info(f"Started consultation session {session_id} for user {current_user.id}")
        return session
        
    except Exception as e:
        logger.error(f"Error starting consultation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start consultation: {str(e)}")

@router.post("/chat", response_model=ExpertChatResponse)
async def chat_with_expert(
    request: ExpertChatRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = None
):
    """
    Send a message to AI expert and get response
    """
    try:
        # Verify session exists and belongs to user
        if request.session_id not in consultation_sessions:
            raise HTTPException(status_code=404, detail="Consultation session not found")
        
        session = consultation_sessions[request.session_id]
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Generate AI expert response
        response = await ai_expert_service.generate_expert_response(
            session_id=request.session_id,
            user_message=request.message,
            context=request.context,
            session_data=session
        )
        
        # Update session with new messages
        user_message = ChatMessage(role="user", content=request.message)
        assistant_message = ChatMessage(role="assistant", content=response.response)
        
        session.messages.extend([user_message, assistant_message])
        session.updated_at = datetime.now()
        
        # Store chat history
        if request.session_id not in chat_history:
            chat_history[request.session_id] = []
        chat_history[request.session_id].extend([user_message, assistant_message])
        
        logger.info(f"Generated expert response for session {request.session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in expert chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate expert response: {str(e)}")

@router.get("/sessions", response_model=SessionListResponse)
async def get_consultation_sessions(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by session status")
):
    """
    Get user's consultation sessions
    """
    try:
        user_sessions = [
            session for session in consultation_sessions.values()
            if session.user_id == current_user.id
        ]
        
        # Filter by status if provided
        if status:
            user_sessions = [s for s in user_sessions if s.status == status]
        
        # Sort by updated_at descending
        user_sessions.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Apply pagination
        total_count = len(user_sessions)
        paginated_sessions = user_sessions[offset:offset + limit]
        has_more = offset + limit < total_count
        
        return SessionListResponse(
            sessions=paginated_sessions,
            total_count=total_count,
            has_more=has_more
        )
        
    except Exception as e:
        logger.error(f"Error getting consultation sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@router.get("/sessions/{session_id}", response_model=ConsultationSession)
async def get_consultation_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific consultation session details
    """
    try:
        if session_id not in consultation_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = consultation_sessions[session_id]
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.put("/sessions/{session_id}/status")
async def update_session_status(
    session_id: str,
    status: str = Query(..., description="New session status"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update consultation session status
    """
    try:
        if session_id not in consultation_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = consultation_sessions[session_id]
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        valid_statuses = ["active", "completed", "paused"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        session.status = status
        session.updated_at = datetime.now()
        
        return {"message": "Session status updated successfully", "status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session status: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_consultation_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a consultation session
    """
    try:
        if session_id not in consultation_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = consultation_sessions[session_id]
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Delete session and chat history
        del consultation_sessions[session_id]
        if session_id in chat_history:
            del chat_history[session_id]
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")