# backend/app/routes/reflections.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.base import get_db
from ..models.reflection import Reflection
from ..schemas.reflection import ReflectionCreate, ReflectionResponse, ReflectionUpdate
from ..services.reflection_service import ReflectionService

router = APIRouter()
reflection_service = ReflectionService()

# 创建观后感
@router.post("/", response_model=ReflectionResponse, status_code=status.HTTP_201_CREATED)
async def create_reflection(
        reflection_data: ReflectionCreate,
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """
    创建观后感
    - 自动质量评估
    - 检查观看进度要求
    - 智能审核决策
    """
    # TODO: 从认证中获取用户ID
    user_id = 1  # 临时固定值

    # 使用服务层创建观后感
    result = reflection_service.create_reflection(
        content=reflection_data.content,
        video_id=reflection_data.video_id,
        user_id=user_id,
        db=db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {
        "reflection": result["reflection"],
        "quality_analysis": result["quality_result"],
        "approval_result": result["approval_result"]
    }


# 观后感预检测
@router.post("/preview")
async def preview_reflection(
        content: str = Body(...),
        video_id: int = Body(...),
        db: Session = Depends(get_db)
):
    """
    观后感预检测 - 不保存到数据库
    检查质量和观看要求
    """
    # TODO: 从认证中获取用户ID
    user_id = 1

    result = reflection_service.check_reflection_preview(content, video_id, user_id, db)
    return result


# 获取用户的观后感列表
@router.get("/my", response_model=List[ReflectionResponse])
async def get_my_reflections(
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有观后感"""
    # TODO: 从认证中获取用户ID
    user_id = 1

    reflections = reflection_service.get_user_reflections(user_id, db)
    return reflections


# 获取指定视频的观后感
@router.get("/video/{video_id}")
async def get_video_reflections(
        video_id: int,
        approved_only: bool = Query(True, description="只显示已审核通过的"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """获取指定视频的观后感列表"""

    reflections = reflection_service.get_video_reflections(video_id, db, approved_only)

    # 分页
    paginated_reflections = reflections[skip:skip + limit]

    return {
        "reflections": paginated_reflections,
        "total": len(reflections),
        "showing": len(paginated_reflections)
    }


# 获取单个观后感详情
@router.get("/{reflection_id}", response_model=ReflectionResponse)
async def get_reflection(
        reflection_id: int,
        db: Session = Depends(get_db)
):
    """获取观后感详情"""

    reflection = db.query(Reflection).filter(Reflection.id == reflection_id).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="观后感不存在"
        )

    return reflection


# 更新观后感
@router.put("/{reflection_id}", response_model=ReflectionResponse)
async def update_reflection(
        reflection_id: int,
        reflection_update: ReflectionUpdate,
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """
    更新观后感内容
    - 重新进行质量检测
    - 重新审核
    """
    result = reflection_service.update_reflection(
        reflection_id, reflection_update.content, db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {
        "reflection": result["reflection"],
        "quality_analysis": result["quality_result"],
        "approval_result": result["approval_result"]
    }


# 人工审核观后感
@router.post("/{reflection_id}/review")
async def manual_review_reflection(
        reflection_id: int,
        approved: bool = Body(...),
        feedback: str = Body(...),
        db: Session = Depends(get_db)
        # TODO: current_admin: User = Depends(get_current_admin)
):
    """
    人工审核观后感
    需要管理员权限
    """
    result = reflection_service.manual_review_reflection(
        reflection_id=reflection_id,
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


# 获取高质量观后感
@router.get("/featured/top")
async def get_top_quality_reflections(
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)
):
    """获取精选高质量观后感"""

    top_reflections = reflection_service.get_top_quality_reflections(db, limit)

    return {
        "featured_reflections": top_reflections,
        "count": len(top_reflections)
    }


# 获取观后感统计
@router.get("/stats/overview")
async def get_reflection_stats(
        db: Session = Depends(get_db)
):
    """获取观后感系统统计"""

    stats = reflection_service.get_reflection_stats(db)
    return stats


# 删除观后感
@router.delete("/{reflection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reflection(
        reflection_id: int,
        db: Session = Depends(get_db)
        # TODO: current_user: User = Depends(get_current_user)
):
    """删除观后感（仅限作者本人或管理员）"""

    reflection = db.query(Reflection).filter(Reflection.id == reflection_id).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="观后感不存在"
        )

    # TODO: 检查权限 - 只有作者或管理员可以删除
    # if reflection.user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="无权限删除此观后感"
    #     )

    db.delete(reflection)
    db.commit()