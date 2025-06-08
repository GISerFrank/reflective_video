# backend/app/models/database_setup.py
from .base import Base, engine, create_tables
from .user import User
from .video import Video
from .reflection import Reflection
from .comment import Comment
from .user_progress import UserProgress
from sqlalchemy.orm import Session
from datetime import datetime


def init_database():
    """初始化数据库并创建示例数据"""
    # 创建所有表
    create_tables()

    # 创建示例数据
    create_sample_data()


def create_sample_data():
    """创建示例数据"""
    from .base import SessionLocal

    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(Video).count() > 0:
            return

        # 创建示例视频
        videos = [
            Video(
                title="第1课：人工智能基础",
                description="介绍人工智能的基本概念和发展历史",
                duration=900,  # 15分钟
                order_index=1,
                category="AI基础",
                difficulty_level="beginner"
            ),
            Video(
                title="第2课：机器学习原理",
                description="深入理解机器学习的核心算法和原理",
                duration=1080,  # 18分钟
                order_index=2,
                category="机器学习",
                difficulty_level="intermediate"
            ),
            Video(
                title="第3课：深度学习应用",
                description="探索深度学习在实际项目中的应用案例",
                duration=1200,  # 20分钟
                order_index=3,
                category="深度学习",
                difficulty_level="advanced"
            )
        ]

        for video in videos:
            db.add(video)

        # 创建示例用户
        sample_user = User(
            username="demo_user",
            email="demo@example.com",
            hashed_password="fake_hashed_password"
        )
        db.add(sample_user)

        # 需要先提交用户，才能创建进度记录
        db.commit()

        # 创建一些观看进度示例
        user_id = sample_user.id
        for i, video in enumerate(videos, 1):
            if i <= 2:  # 前两个视频有观看记录
                progress = UserProgress(
                    user_id=user_id,
                    video_id=video.id,
                    watched_time=video.duration // 2,  # 看了一半
                    completion_percentage=50.0,
                    last_watched_position=video.duration // 2,
                    watch_count=1
                )
                db.add(progress)

        db.commit()
        print("示例数据创建完成")

    except Exception as e:
        print(f"创建示例数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()