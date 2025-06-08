# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./database.db"

    # JWT配置
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 应用配置
    app_name: str = "Smart Video Platform"
    app_version: str = "1.0.0"
    debug: bool = True

    # 文件配置
    upload_dir: str = "./uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB

    # 检测算法配置
    similarity_threshold: float = 60.0
    quality_threshold: float = 60.0

    # CORS配置
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()