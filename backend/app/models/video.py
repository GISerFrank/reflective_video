# backend/app/models/video.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # 视频属性
    duration = Column(Integer, nullable=False)  # 持续时间（秒）
    order_index = Column(Integer, nullable=False, unique=True)  # 播放顺序
    video_url = Column(String(500))  # 视频文件URL
    thumbnail_url = Column(String(500))  # 缩略图URL

    # 课程信息
    category = Column(String(100))  # 分类
    difficulty_level = Column(String(20), default="beginner")  # 难度级别
    prerequisites = Column(Text)  # 前置要求

    # 状态管理
    is_published = Column(Boolean, default=True)
    is_free = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    progresses = relationship("UserProgress", back_populates="video", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', order={self.order_index})>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "order_index": self.order_index,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "category": self.category,
            "difficulty_level": self.difficulty_level,
            "is_published": self.is_published,
            "is_free": self.is_free,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }