from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

from ...core.auth import get_current_user
from ...data.models.database import User
from ...services.ai_orchestrator import AIOrchestrator
from ...services.expert_manager import ExpertManager
from ...services.chat_session import ChatSessionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    expert_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    context: Optional[List[Dict[str, Any]]] = Field(default=[])
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    expert_id: str
    session_id: str
    timestamp: str
    processing_time: Optional[float] = None
    model: Optional[str] = None
    tokens: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    session_id: str
    expert_id: str
    created_at: str
    updated_at: str
    message_count: int
    status: str

class ExpertInfo(BaseModel):
    id: str
    name: str
    title: str
    description: str
    expertise: List[str]
    personality: Dict[str, Any]
    is_active: bool

# Initialize services
ai_orchestrator = AIOrchestrator()
expert_manager = ExpertManager()
session_manager = ChatSessionManager()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_request: ChatMessage,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to an AI expert and get a response
    """
    try:
        start_time = datetime.now()
        
        # Validate expert exists and is active
        expert = await expert_manager.get_expert(chat_request.expert_id)
        if not expert or not expert.is_active:
            raise HTTPException(
                status_code=404, 
                detail=f"Expert with ID {chat_request.expert_id} not found or inactive"
            )
        
        # Get or create chat session
        session = await session_manager.get_or_create_session(
            session_id=chat_request.session_id,
            expert_id=chat_request.expert_id,
            user_id=current_user.id
        )
        
        # Process message through AI orchestrator
        response_data = await ai_orchestrator.process_message(
            message=chat_request.message,
            expert=expert,
            session=session,
            context=chat_request.context,
            user=current_user
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Save message and response to database
        background_tasks.add_task(
            session_manager.save_message_pair,
            session_id=chat_request.session_id,
            user_message=chat_request.message,
            assistant_response=response_data["response"],
            expert_id=chat_request.expert_id,
            metadata=response_data.get("metadata", {})
        )
        
        # Update session activity
        background_tasks.add_task(
            session_manager.update_session_activity,
            session_id=chat_request.session_id
        )
        
        return ChatResponse(
            response=response_data["response"],
            expert_id=chat_request.expert_id,
            session_id=chat_request.session_id,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
            model=response_data.get("model"),
            tokens=response_data.get("tokens"),
            metadata=response_data.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing message"
        )

@router.post("/stream")
async def stream_message(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Stream a response from an AI expert
    """
    try:
        # Validate expert exists and is active
        expert = await expert_manager.get_expert(chat_request.expert_id)
        if not expert or not expert.is_active:
            raise HTTPException(
                status_code=404, 
                detail=f"Expert with ID {chat_request.expert_id} not found or inactive"
            )
        
        # Get or create chat session
        session = await session_manager.get_or_create_session(
            session_id=chat_request.session_id,
            expert_id=chat_request.expert_id,
            user_id=current_user.id
        )
        
        async def generate_stream():
            try:
                async for chunk in ai_orchestrator.stream_message(
                    message=chat_request.message,
                    expert=expert,
                    session=session,
                    context=chat_request.context,
                    user=current_user
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send end signal
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up stream: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while setting up stream"
        )

@router.get("/sessions", response_model=List[ChatSession])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get user's chat sessions
    """
    try:
        sessions = await session_manager.get_user_sessions(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        return sessions
        
    except Exception as e:
        logger.error(f"Error fetching user sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching sessions"
        )

@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: User = Depends(get_current_user),
    include_messages: bool = True
):
    """
    Get detailed information about a specific session
    """
    try:
        session = await session_manager.get_session_details(
            session_id=session_id,
            user_id=current_user.id,
            include_messages=include_messages
        )
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching session details"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a chat session
    """
    try:
        success = await session_manager.delete_session(
            session_id=session_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting session"
        )

@router.get("/experts", response_model=List[ExpertInfo])
async def get_available_experts():
    """
    Get list of available AI experts
    """
    try:
        experts = await expert_manager.get_active_experts()
        return experts
        
    except Exception as e:
        logger.error(f"Error fetching experts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching experts"
        )

@router.get("/experts/{expert_id}", response_model=ExpertInfo)
async def get_expert_details(expert_id: str):
    """
    Get detailed information about a specific expert
    """
    try:
        expert = await expert_manager.get_expert(expert_id)
        
        if not expert:
            raise HTTPException(
                status_code=404,
                detail="Expert not found"
            )
        
        return expert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching expert details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching expert details"
        )