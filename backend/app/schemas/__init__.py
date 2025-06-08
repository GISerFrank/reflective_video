# backend/app/schemas/__init__.py
# Pydantic模式定义，用于API输入输出验证

from .user import UserCreate, UserUpdate, UserResponse, UserStats
from .video import VideoCreate, VideoUpdate, VideoResponse
from .reflection import ReflectionCreate, ReflectionUpdate, ReflectionResponse
from .comment import CommentCreate, CommentUpdate, CommentResponse, SimilarityCheckRequest, SimilarityCheckResponse
from .progress import ProgressCreate, ProgressUpdate, ProgressResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserStats",
    "VideoCreate", "VideoUpdate", "VideoResponse",
    "ReflectionCreate", "ReflectionUpdate", "ReflectionResponse",
    "CommentCreate", "CommentUpdate", "CommentResponse", "SimilarityCheckRequest", "SimilarityCheckResponse",
    "ProgressCreate", "ProgressUpdate", "ProgressResponse"
]