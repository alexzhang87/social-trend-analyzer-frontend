import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..data.models.database import SessionLocal, ChatSession, ChatMessage, User

logger = logging.getLogger(__name__)

class ChatSessionManager:
    """
    Chat Session Manager handles chat sessions and message persistence
    """
    
    def __init__(self):
        self.session_cache = {}  # In-memory cache for active sessions
        self.cache_ttl = timedelta(hours=1)  # Cache TTL
    
    async def get_or_create_session(
        self,
        session_id: str,
        expert_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get existing session or create a new one
        """
        try:
            # Check cache first
            cache_key = f"{session_id}_{user_id}"
            if cache_key in self.session_cache:
                cached_session = self.session_cache[cache_key]
                if datetime.now() - cached_session["cached_at"] < self.cache_ttl:
                    return cached_session["data"]
            
            db = SessionLocal()
            try:
                # Try to get existing session
                session = db.query(ChatSession).filter(
                    and_(
                        ChatSession.session_id == session_id,
                        ChatSession.user_id == user_id
                    )
                ).first()
                
                if session:
                    session_data = {
                        "id": session.id,
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "expert_id": session.expert_id,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "message_count": session.message_count,
                        "status": session.status,
                        "metadata": json.loads(session.metadata) if session.metadata else {}
                    }
                else:
                    # Create new session
                    new_session = ChatSession(
                        session_id=session_id,
                        user_id=user_id,
                        expert_id=expert_id,
                        status="active",
                        message_count=0,
                        metadata=json.dumps({
                            "created_by": "chat_interface",
                            "initial_expert": expert_id
                        })
                    )
                    
                    db.add(new_session)
                    db.commit()
                    db.refresh(new_session)
                    
                    session_data = {
                        "id": new_session.id,
                        "session_id": new_session.session_id,
                        "user_id": new_session.user_id,
                        "expert_id": new_session.expert_id,
                        "created_at": new_session.created_at.isoformat(),
                        "updated_at": new_session.updated_at.isoformat(),
                        "message_count": new_session.message_count,
                        "status": new_session.status,
                        "metadata": json.loads(new_session.metadata) if new_session.metadata else {}
                    }
                
                # Cache the session
                self.session_cache[cache_key] = {
                    "data": session_data,
                    "cached_at": datetime.now()
                }
                
                return session_data
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting/creating session {session_id}: {str(e)}")
            # Return a minimal session object for fallback
            return {
                "session_id": session_id,
                "user_id": user_id,
                "expert_id": expert_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "message_count": 0,
                "status": "active",
                "metadata": {}
            }
    
    async def save_message_pair(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        expert_id: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Save a user message and assistant response pair
        """
        try:
            db = SessionLocal()
            try:
                # Get session
                session = db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                
                if not session:
                    logger.warning(f"Session {session_id} not found when saving messages")
                    return False
                
                # Save user message
                user_msg = ChatMessage(
                    session_id=session.id,
                    role="user",
                    content=user_message,
                    expert_id=expert_id,
                    metadata=json.dumps(metadata or {})
                )
                db.add(user_msg)
                
                # Save assistant response
                assistant_msg = ChatMessage(
                    session_id=session.id,
                    role="assistant",
                    content=assistant_response,
                    expert_id=expert_id,
                    metadata=json.dumps(metadata or {})
                )
                db.add(assistant_msg)
                
                # Update session message count and timestamp
                session.message_count += 2
                session.updated_at = datetime.now()
                
                db.commit()
                
                # Update cache
                cache_key = f"{session_id}_{session.user_id}"
                if cache_key in self.session_cache:
                    self.session_cache[cache_key]["data"]["message_count"] = session.message_count
                    self.session_cache[cache_key]["data"]["updated_at"] = session.updated_at.isoformat()
                
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error saving message pair for session {session_id}: {str(e)}")
            return False
    
    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp
        """
        try:
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                
                if session:
                    session.updated_at = datetime.now()
                    db.commit()
                    
                    # Update cache
                    cache_key = f"{session_id}_{session.user_id}"
                    if cache_key in self.session_cache:
                        self.session_cache[cache_key]["data"]["updated_at"] = session.updated_at.isoformat()
                    
                    return True
                
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error updating session activity for {session_id}: {str(e)}")
            return False
    
    async def get_user_sessions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's chat sessions
        """
        try:
            db = SessionLocal()
            try:
                sessions = db.query(ChatSession).filter(
                    ChatSession.user_id == user_id
                ).order_by(desc(ChatSession.updated_at)).offset(offset).limit(limit).all()
                
                session_list = []
                for session in sessions:
                    session_data = {
                        "session_id": session.session_id,
                        "expert_id": session.expert_id,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "message_count": session.message_count,
                        "status": session.status
                    }
                    session_list.append(session_data)
                
                return session_list
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting user sessions for user {user_id}: {str(e)}")
            return []
    
    async def get_session_details(
        self,
        session_id: str,
        user_id: int,
        include_messages: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information including messages
        """
        try:
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(
                    and_(
                        ChatSession.session_id == session_id,
                        ChatSession.user_id == user_id
                    )
                ).first()
                
                if not session:
                    return None
                
                session_data = {
                    "session_id": session.session_id,
                    "expert_id": session.expert_id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": session.message_count,
                    "status": session.status,
                    "metadata": json.loads(session.metadata) if session.metadata else {}
                }
                
                if include_messages:
                    messages = db.query(ChatMessage).filter(
                        ChatMessage.session_id == session.id
                    ).order_by(ChatMessage.created_at).all()
                    
                    message_list = []
                    for msg in messages:
                        message_data = {
                            "id": msg.id,
                            "role": msg.role,
                            "content": msg.content,
                            "expert_id": msg.expert_id,
                            "created_at": msg.created_at.isoformat(),
                            "metadata": json.loads(msg.metadata) if msg.metadata else {}
                        }
                        message_list.append(message_data)
                    
                    session_data["messages"] = message_list
                
                return session_data
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting session details for {session_id}: {str(e)}")
            return None
    
    async def delete_session(self, session_id: str, user_id: int) -> bool:
        """
        Delete a chat session and all its messages
        """
        try:
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(
                    and_(
                        ChatSession.session_id == session_id,
                        ChatSession.user_id == user_id
                    )
                ).first()
                
                if not session:
                    return False
                
                # Delete all messages in the session
                db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.id
                ).delete()
                
                # Delete the session
                db.delete(session)
                db.commit()
                
                # Remove from cache
                cache_key = f"{session_id}_{user_id}"
                if cache_key in self.session_cache:
                    del self.session_cache[cache_key]
                
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    async def get_session_messages(
        self,
        session_id: str,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a specific session
        """
        try:
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(
                    and_(
                        ChatSession.session_id == session_id,
                        ChatSession.user_id == user_id
                    )
                ).first()
                
                if not session:
                    return []
                
                messages = db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.id
                ).order_by(ChatMessage.created_at).offset(offset).limit(limit).all()
                
                message_list = []
                for msg in messages:
                    message_data = {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "expert_id": msg.expert_id,
                        "created_at": msg.created_at.isoformat(),
                        "metadata": json.loads(msg.metadata) if msg.metadata else {}
                    }
                    message_list.append(message_data)
                
                return message_list
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting session messages for {session_id}: {str(e)}")
            return []
    
    def cleanup_cache(self):
        """
        Clean up expired cache entries
        """
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key, cached_item in self.session_cache.items():
                if current_time - cached_item["cached_at"] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.session_cache[key]
                
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")