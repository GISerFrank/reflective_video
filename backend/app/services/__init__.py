# backend/app/services/__init__.py
"""
业务逻辑服务层
包含核心算法和复杂业务逻辑处理
"""

from .similarity_detector import SimilarityDetector
from .quality_checker import QualityChecker
from .video_service import VideoService
from .comment_service import CommentService
from .reflection_service import ReflectionService
from .auth_service import AuthService

__all__ = [
    "SimilarityDetector",
    "QualityChecker",
    "VideoService",
    "CommentService",
    "ReflectionService",
    "AuthService"
]