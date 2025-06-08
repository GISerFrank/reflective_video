# backend/app/models/user_progress.py
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)

    # 观看进度
    watched_time = Column(Integer, default=0)  # 已观看时间（秒）
    completion_percentage = Column(Float, default=0.0)  # 完成百分比
    is_completed = Column(Boolean, default=False)  # 是否完成

    # 观看状态
    last_watched_position = Column(Integer, default=0)  # 最后观看位置
    watch_count = Column(Integer, default=0)  # 观看次数

    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    user = relationship("User", back_populates="progresses")
    video = relationship("Video", back_populates="progresses")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, video_id={self.video_id}, completed={self.is_completed})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "video_id": self.video_id,
            "watched_time": self.watched_time,
            "completion_percentage": self.completion_percentage,
            "is_completed": self.is_completed,
            "last_watched_position": self.last_watched_position,
            "watch_count": self.watch_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }