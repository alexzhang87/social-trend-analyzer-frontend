from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..data.models.database import get_db, User, UserFeedback, FeedbackType, FeedbackStatus
from ..core.auth import get_current_active_user, get_admin_user
from ..data.models.schemas import (
    FeedbackCreate, FeedbackResponse, FeedbackUpdate, 
    AdminFeedbackResponse, FeedbackStats
)
from ..utils.logger import logger

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])

@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建用户反馈"""
    try:
        # 验证反馈类型
        feedback_type = FeedbackType(feedback_data.feedback_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback type. Available options: {[t.value for t in FeedbackType]}"
        )
    
    # 验证评分范围
    if feedback_data.rating is not None and (feedback_data.rating < 1 or feedback_data.rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    feedback = UserFeedback(
        user_id=current_user.id,
        analysis_id=feedback_data.analysis_id,
        feedback_type=feedback_type,
        rating=feedback_data.rating,
        title=feedback_data.title,
        content=feedback_data.content
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    logger.info(f"User {current_user.id} created feedback {feedback.id}")
    return feedback

@router.get("/my", response_model=List[FeedbackResponse])
async def get_my_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的反馈列表"""
    feedback_list = db.query(UserFeedback).filter(
        UserFeedback.user_id == current_user.id
    ).order_by(UserFeedback.created_at.desc()).offset(skip).limit(limit).all()
    
    return feedback_list

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取特定反馈详情"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # 检查权限：只有反馈创建者或管理员可以查看
    if feedback.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this feedback"
        )
    
    return feedback

@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新反馈内容（仅限创建者）"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id,
        UserFeedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found or not authorized"
        )
    
    # 只有待处理状态的反馈可以编辑
    if feedback.status != FeedbackStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending feedback can be edited"
        )
    
    # 更新字段
    update_data = feedback_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "feedback_type" and value:
            try:
                value = FeedbackType(value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid feedback type: {value}"
                )
        if field == "rating" and value is not None and (value < 1 or value > 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        setattr(feedback, field, value)
    
    feedback.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(feedback)
    
    return feedback

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除反馈（仅限创建者）"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id,
        UserFeedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found or not authorized"
        )
    
    # 只有待处理状态的反馈可以删除
    if feedback.status != FeedbackStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending feedback can be deleted"
        )
    
    db.delete(feedback)
    db.commit()
    
    return {"message": "Feedback deleted successfully"}

# 管理员接口
@router.get("/admin/all", response_model=List[FeedbackResponse])
async def get_all_feedback(
    status: Optional[str] = Query(None),
    feedback_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """获取所有反馈（管理员）"""
    query = db.query(UserFeedback)
    
    if status:
        try:
            status_enum = FeedbackStatus(status)
            query = query.filter(UserFeedback.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    if feedback_type:
        try:
            type_enum = FeedbackType(feedback_type)
            query = query.filter(UserFeedback.feedback_type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid feedback type: {feedback_type}"
            )
    
    feedback_list = query.order_by(
        UserFeedback.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return feedback_list

@router.post("/admin/{feedback_id}/respond")
async def respond_to_feedback(
    feedback_id: int,
    response_data: AdminFeedbackResponse,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """管理员回复反馈"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    feedback.admin_response = response_data.admin_response
    feedback.admin_id = admin_user.id
    feedback.updated_at = datetime.utcnow()
    
    if response_data.status:
        try:
            feedback.status = FeedbackStatus(response_data.status)
            if feedback.status == FeedbackStatus.RESOLVED:
                feedback.resolved_at = datetime.utcnow()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {response_data.status}"
            )
    else:
        feedback.status = FeedbackStatus.REVIEWED
    
    db.commit()
    db.refresh(feedback)
    
    logger.info(f"Admin {admin_user.id} responded to feedback {feedback_id}")
    return {"message": "Response added successfully", "feedback": feedback}

@router.get("/admin/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """获取反馈统计信息（管理员）"""
    from datetime import timedelta
    from sqlalchemy import func
    
    # 时间范围
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 基础统计
    total_feedback = db.query(UserFeedback).filter(
        UserFeedback.created_at >= start_date
    ).count()
    
    pending_count = db.query(UserFeedback).filter(
        UserFeedback.status == FeedbackStatus.PENDING,
        UserFeedback.created_at >= start_date
    ).count()
    
    resolved_count = db.query(UserFeedback).filter(
        UserFeedback.status == FeedbackStatus.RESOLVED,
        UserFeedback.created_at >= start_date
    ).count()
    
    # 平均评分
    avg_rating = db.query(func.avg(UserFeedback.rating)).filter(
        UserFeedback.rating.isnot(None),
        UserFeedback.created_at >= start_date
    ).scalar()
    
    # 按类型统计
    feedback_by_type = {}
    for feedback_type in FeedbackType:
        count = db.query(UserFeedback).filter(
            UserFeedback.feedback_type == feedback_type,
            UserFeedback.created_at >= start_date
        ).count()
        feedback_by_type[feedback_type.value] = count
    
    # 最近反馈
    recent_feedback = db.query(UserFeedback).filter(
        UserFeedback.created_at >= start_date
    ).order_by(UserFeedback.created_at.desc()).limit(10).all()
    
    return FeedbackStats(
        total_feedback=total_feedback,
        pending_count=pending_count,
        resolved_count=resolved_count,
        average_rating=float(avg_rating) if avg_rating else None,
        feedback_by_type=feedback_by_type,
        recent_feedback=recent_feedback
    )