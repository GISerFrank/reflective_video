# backend/app/schemas/comment.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.comment import CommentStatus


class CommentBase(BaseModel):
    content: str

    @validator('content')
    def content_length(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('评论内容至少需要10个字符')
        return v.strip()


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentResponse(CommentBase):
    id: int
    user_id: int
    word_count: int
    similarity_score: float
    original_score: float
    quality_passed: bool
    quality_issues: Optional[str]
    status: CommentStatus
    reject_reason: Optional[str]
    like_count: int
    reply_count: int
    parent_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class SimilarityCheckRequest(BaseModel):
    content: str


class SimilarityCheckResponse(BaseModel):
    similarity_score: float
    original_score: float
    quality_passed: bool
    quality_issues: Optional[str]
    recommendation: str