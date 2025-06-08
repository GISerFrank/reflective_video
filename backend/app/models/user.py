# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)

    # 用户统计信息
    videos_completed = Column(Integer, default=0)
    reflections_written = Column(Integer, default=0)
    comments_approved = Column(Integer, default=0)
    originality_score = Column(Float, default=100.0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # 用户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 关系定义
    progresses = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "videos_completed": self.videos_completed,
            "reflections_written": self.reflections_written,
            "comments_approved": self.comments_approved,
            "originality_score": self.originality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }