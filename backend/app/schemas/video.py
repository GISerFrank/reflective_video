# backend/app/schemas/video.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int
    order_index: int
    category: Optional[str] = None
    difficulty_level: str = "beginner"


class VideoCreate(VideoBase):
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_published: Optional[bool] = None


class VideoResponse(VideoBase):
    id: int
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    is_published: bool
    is_free: bool
    created_at: datetime

    class Config:
        from_attributes = True