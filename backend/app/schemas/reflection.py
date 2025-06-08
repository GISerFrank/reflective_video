# backend/app/schemas/reflection.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ReflectionBase(BaseModel):
    content: str

    @validator('content')
    def content_length(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('观后感内容至少需要50个字符')
        return v.strip()


class ReflectionCreate(ReflectionBase):
    video_id: int


class ReflectionUpdate(BaseModel):
    content: Optional[str] = None


class ReflectionResponse(ReflectionBase):
    id: int
    user_id: int
    video_id: int
    word_count: int
    quality_score: float
    has_thought_words: bool
    has_specific_examples: bool
    has_questions: bool
    is_approved: bool
    feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True