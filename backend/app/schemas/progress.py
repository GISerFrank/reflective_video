# backend/app/schemas/progress.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProgressBase(BaseModel):
    watched_time: int
    last_watched_position: int


class ProgressCreate(ProgressBase):
    video_id: int


class ProgressUpdate(BaseModel):
    watched_time: Optional[int] = None
    last_watched_position: Optional[int] = None
    completion_percentage: Optional[float] = None
    is_completed: Optional[bool] = None


class ProgressResponse(ProgressBase):
    id: int
    user_id: int
    video_id: int
    completion_percentage: float
    is_completed: bool
    watch_count: int
    started_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True