# backend/app/models/reflection.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)

    # 观后感内容
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)

    # 质量评估
    quality_score = Column(Float, default=0.0)  # 质量分数 (0-100)
    has_thought_words = Column(Boolean, default=False)  # 是否包含思考性词汇
    has_specific_examples = Column(Boolean, default=False)  # 是否包含具体例子
    has_questions = Column(Boolean, default=False)  # 是否包含疑问

    # 审核状态
    is_approved = Column(Boolean, default=False)
    reviewed_at = Column(DateTime)
    feedback = Column(Text)  # 反馈意见

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    user = relationship("User", back_populates="reflections")
    video = relationship("Video", back_populates="reflections")

    def __repr__(self):
        return f"<Reflection(id={self.id}, user_id={self.user_id}, video_id={self.video_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "video_id": self.video_id,
            "content": self.content,
            "word_count": self.word_count,
            "quality_score": self.quality_score,
            "has_thought_words": self.has_thought_words,
            "has_specific_examples": self.has_specific_examples,
            "has_questions": self.has_questions,
            "is_approved": self.is_approved,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None
        }