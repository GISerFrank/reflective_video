# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    videos_completed: int
    reflections_written: int
    comments_approved: int
    originality_score: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    videos_completed: int
    reflections_written: int
    comments_approved: int
    originality_score: float