from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime
import json
import os

router = APIRouter()
logger = logging.getLogger(__name__)

class FeedbackRequest(BaseModel):
    message_id: str
    session_id: str
    feedback_type: str  # "like", "dislike", "report"
    comment: Optional[str] = None
    rating: Optional[int] = None  # 1-5 stars
    expert_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str

class FeedbackStats(BaseModel):
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    average_rating: float
    expert_ratings: dict

class FeedbackManager:
    def __init__(self):
        self.feedback_file = "app/data/feedback.json"
        self.ensure_feedback_file()
    
    def ensure_feedback_file(self):
        """确保反馈文件存在"""
        if not os.path.exists(self.feedback_file):
            os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump({"feedback": []}, f, ensure_ascii=False, indent=2)
    
    def save_feedback(self, feedback_data: dict) -> str:
        """保存用户反馈"""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            feedback_id = f"fb_{int(datetime.now().timestamp() * 1000)}"
            feedback_entry = {
                "id": feedback_id,
                "timestamp": datetime.now().isoformat(),
                **feedback_data
            }
            
            data["feedback"].append(feedback_entry)
            
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return feedback_id
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            raise HTTPException(status_code=500, detail="Failed to save feedback")
    
    def get_feedback_stats(self) -> dict:
        """获取反馈统计信息"""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            feedback_list = data.get("feedback", [])
            total = len(feedback_list)
            
            if total == 0:
                return {
                    "total_feedback": 0,
                    "positive_feedback": 0,
                    "negative_feedback": 0,
                    "average_rating": 0.0,
                    "expert_ratings": {}
                }
            
            positive = sum(1 for f in feedback_list if f.get("feedback_type") == "like")
            negative = sum(1 for f in feedback_list if f.get("feedback_type") == "dislike")
            
            ratings = [f.get("rating", 0) for f in feedback_list if f.get("rating")]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            # 按专家统计评分
            expert_ratings = {}
            for feedback in feedback_list:
                expert_id = feedback.get("expert_id")
                rating = feedback.get("rating")
                if expert_id and rating:
                    if expert_id not in expert_ratings:
                        expert_ratings[expert_id] = []
                    expert_ratings[expert_id].append(rating)
            
            # 计算每个专家的平均评分
            for expert_id in expert_ratings:
                ratings = expert_ratings[expert_id]
                expert_ratings[expert_id] = sum(ratings) / len(ratings)
            
            return {
                "total_feedback": total,
                "positive_feedback": positive,
                "negative_feedback": negative,
                "average_rating": round(avg_rating, 2),
                "expert_ratings": expert_ratings
            }
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "average_rating": 0.0,
                "expert_ratings": {}
            }

# 初始化反馈管理器
feedback_manager = FeedbackManager()

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """提交用户反馈"""
    try:
        feedback_data = feedback.dict()
        feedback_id = feedback_manager.save_feedback(feedback_data)
        
        logger.info(f"Feedback submitted: {feedback_id} for message {feedback.message_id}")
        
        return FeedbackResponse(
            success=True,
            message="反馈提交成功",
            feedback_id=feedback_id
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="提交反馈失败")

@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats():
    """获取反馈统计信息"""
    try:
        stats = feedback_manager.get_feedback_stats()
        return FeedbackStats(**stats)
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail="获取反馈统计失败")

@router.get("/health")
async def feedback_health():
    """反馈服务健康检查"""
    return {"status": "healthy", "service": "feedback"}