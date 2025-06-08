# backend/app/models/comment.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
import enum


class CommentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 评论内容
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)

    # 相似度检测
    similarity_score = Column(Float, default=0.0)  # 与已有评论的最高相似度
    original_score = Column(Float, default=100.0)  # 原创度分数

    # 质量检测
    quality_passed = Column(Boolean, default=False)
    quality_issues = Column(Text)  # 质量问题描述

    # 审核状态
    status = Column(Enum(CommentStatus), default=CommentStatus.PENDING)
    reject_reason = Column(String(200))  # 拒绝原因

    # 互动数据
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # 回复的父评论

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)

    # 关系定义
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, status={self.status.value})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "word_count": self.word_count,
            "similarity_score": self.similarity_score,
            "original_score": self.original_score,
            "quality_passed": self.quality_passed,
            "quality_issues": self.quality_issues,
            "status": self.status.value,
            "reject_reason": self.reject_reason,
            "like_count": self.like_count,
            "reply_count": self.reply_count,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "user": self.user.to_dict() if self.user else None
        }