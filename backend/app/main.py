# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ FastAPI内置CORS
from .config import settings
from .models.database_setup import init_database

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# ✅ 配置CORS (FastAPI内置)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 允许的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_database()

# 根路径测试
@app.get("/")
async def root():
    return {
        "message": "Smart Video Platform API",
        "version": settings.app_version,
        "status": "running"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 注册路由
from .routes import videos, comments, reflections

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(reflections.router, prefix="/api/reflections", tags=["reflections"])