# backend/app/routes/videos.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.base import get_db
from ..models.video import Video
from ..schemas.video import VideoCreate, VideoUpdate, VideoResponse
from ..schemas.progress import ProgressResponse, ProgressUpdate
from ..services.video_service import VideoService

router = APIRouter()
video_service = VideoService()

# 获取视频列表
@router.get("/", response_model=List[VideoResponse])
async def get_videos(
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
        category: Optional[str] = Query(None, description="按分类筛选"),
        difficulty: Optional[str] = Query(None, description="按难度筛选"),
        published_only: bool = Query(True, description="只显示已发布的视频"),
        db: Session = Depends(get_db)
):
    """
    获取视频列表
    - 支持分页、筛选
    - 按播放顺序排序
    """
    query = db.query(Video)

    # 筛选条件
    if published_only:
        query = query.filter(Video.is_published == True)

    if category:
        query = query.filter(Video.category == category)

    if difficulty:
        query = query.filter(Video.difficulty_level == difficulty)

    # 排序和分页
    videos = query.order_by(Video.order_index).offset(skip).limit(limit).all()

    return videos


# 获取单个视频详情（使用服务层）
@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
        video_id: int,
        db: Session = Depends(get_db)
):
    """获取指定视频的详细信息"""
    # TODO: 从认证中获取用户ID
    user_id = 1  # 临时固定值

    # 使用服务层获取详情
    video_data = video_service.get_video_with_progress(video_id, user_id, db)

    if not video_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在或未发布"
        )

    return video_data["video"]


# 获取视频详情和进度（新接口）
@router.get("/{video_id}/details")
async def get_video_details(
        video_id: int,
        db: Session = Depends(get_db)
):
    """获取视频详情、用户进度和相关统计"""
    # TODO: 从认证中获取用户ID
    user_id = 1

    video_data = video_service.get_video_with_progress(video_id, user_id, db)

    if not video_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在或未发布"
        )

    return video_data


# 更新观看进度（使用服务层）
@router.post("/{video_id}/progress", response_model=ProgressResponse)
async def update_video_progress(
        video_id: int,
        progress_update: ProgressUpdate,
        db: Session = Depends(get_db)
):
    """更新观看进度（使用智能算法）"""
    # TODO: 从认证中获取用户ID
    user_id = 1

    # 使用服务层的智能进度更新
    result = video_service.update_watch_progress(
        video_id=video_id,
        user_id=user_id,
        watched_time=progress_update.watched_time,
        current_position=progress_update.last_watched_position,
        db=db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result["progress"]


# 获取用户学习路径
@router.get("/learning/path")
async def get_learning_path(
        db: Session = Depends(get_db)
):
    """获取用户的个性化学习路径"""
    # TODO: 从认证中获取用户ID
    user_id = 1

    learning_data = video_service.get_user_learning_path(user_id, db)
    return learning_data


# 获取热门视频
@router.get("/popular/list")
async def get_popular_videos(
        limit: int = Query(10, ge=1, le=50, description="返回数量"),
        db: Session = Depends(get_db)
):
    """获取热门视频排行"""
    popular_videos = video_service.get_popular_videos(db, limit)
    return {"popular_videos": popular_videos}


# 获取系统统计概览
@router.get("/stats/overview")
async def get_video_stats(db: Session = Depends(get_db)):
    """获取视频系统统计概览"""
    stats = video_service.get_system_overview(db)
    return stats