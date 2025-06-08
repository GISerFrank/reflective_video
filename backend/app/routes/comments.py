# backend/app/routes/comments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.base import get_db
from ..models.comment import Comment, CommentStatus
from ..schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from ..services.comment_service import CommentService

router = APIRouter()
comment_service = CommentService()

# 创建评论（集成相似度和质量检测）
@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        comment_data: CommentCreate,
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """
    创建新评论
    - 自动进行相似度检测
    - 自动进行质量评估
    - 智能审核决策
    """
    # TODO: 从认证中获取用户ID
    user_id = 1  # 临时固定值

    # 使用服务层创建评论
    result = comment_service.create_comment(
        content=comment_data.content,
        user_id=user_id,
        parent_id=comment_data.parent_id,
        db=db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # 返回完整的创建结果
    return {
        "comment": result["comment"],
        "quality_analysis": result["quality_result"],
        "similarity_analysis": result["similarity_result"],
        "auto_decision": result["approval_result"]
    }


# 评论预检测（实时反馈）
@router.post("/preview")
async def preview_comment(
        content: str = Body(..., embed=True),
        db: Session = Depends(get_db)
):
    """
    评论预检测 - 不保存到数据库
    用于给用户实时反馈和建议
    """
    # 使用服务层进行预检测
    result = comment_service.check_comment_preview(content, db)

    return result


# 获取评论列表
@router.get("/", response_model=List[CommentResponse])
async def get_comments(
        status_filter: Optional[CommentStatus] = Query(None, description="按状态筛选"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """获取评论列表，支持按状态筛选"""

    query = db.query(Comment)

    if status_filter:
        query = query.filter(Comment.status == status_filter)

    comments = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

    return comments


# 获取单个评论详情
@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
        comment_id: int,
        db: Session = Depends(get_db)
):
    """获取评论详情，包含检测结果"""

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    return comment


# 更新评论内容
@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        comment_update: CommentUpdate,
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """
    更新评论内容
    - 重新进行质量和相似度检测
    - 重新审核
    """
    # 使用服务层更新评论
    result = comment_service.update_comment(comment_id, comment_update.content, db)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {
        "comment": result["comment"],
        "quality_analysis": result["quality_result"],
        "similarity_analysis": result["similarity_result"],
        "approval_result": result["approval_result"]
    }


# 人工审核评论
@router.post("/{comment_id}/review")
async def manual_review_comment(
        comment_id: int,
        approved: bool = Body(...),
        feedback: str = Body(...),
        db: Session = Depends(get_db)
        # TODO: current_admin: User = Depends(get_current_admin)
):
    """
    人工审核评论
    需要管理员权限
    """
    result = comment_service.manual_review_comment(
        comment_id=comment_id,
        approved=approved,
        reviewer_feedback=feedback,
        db=db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


# 获取待审核评论
@router.get("/pending/list")
async def get_pending_comments(
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
        # TODO: current_admin: User = Depends(get_current_admin)
):
    """获取待人工审核的评论列表"""

    pending_comments = comment_service.get_comments_by_status(
        CommentStatus.PENDING, db, limit
    )

    return {"pending_comments": pending_comments, "count": len(pending_comments)}


# 获取用户评论统计
@router.get("/users/{user_id}/stats")
async def get_user_comment_stats(
        user_id: int,
        db: Session = Depends(get_db)
):
    """获取指定用户的评论统计信息"""

    stats = comment_service.get_user_comment_stats(user_id, db)
    return stats


# 获取系统评论统计
@router.get("/system/stats")
async def get_system_comment_stats(
        db: Session = Depends(get_db)
):
    """获取系统评论统计概览"""

    stats = comment_service.get_system_stats(db)
    return stats


# 测试相似度检测
@router.post("/similarity/test")
async def test_similarity_detection(
        text1: str = Body(...),
        text2: str = Body(...),
        db: Session = Depends(get_db)
):
    """
    测试接口：比较两段文本的相似度
    用于调试和演示相似度算法
    """
    similarity_score = comment_service.similarity_detector.calculate_similarity(text1, text2)

    return {
        "text1": text1[:100] + "..." if len(text1) > 100 else text1,
        "text2": text2[:100] + "..." if len(text2) > 100 else text2,
        "similarity_score": round(similarity_score, 2),
        "is_similar": similarity_score >= comment_service.similarity_detector.chinese_stopwords
    }


# 测试质量检测
@router.post("/quality/test")
async def test_quality_check(
        content: str = Body(..., embed=True),
):
    """
    测试接口：检测文本质量
    返回详细的质量分析报告
    """
    quality_result = comment_service.quality_checker.analyze_text_quality(content, "comment")

    return quality_result