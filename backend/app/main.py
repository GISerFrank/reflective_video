# backend/app/main.py - 修复版本
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="Smart Video Platform",
    description="智能视频学习平台 - 集成相似度检测和质量评估的观后感系统",
    version="1.0.0"
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {
        "message": "欢迎使用Smart Video Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Smart Video Platform API运行正常"
    }

# 条件导入和注册路由 - 避免导入错误
try:
    from .routes import videos
    app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
    print("✅ Videos路由注册成功")
except ImportError as e:
    print(f"❌ Videos路由导入失败: {e}")

try:
    from .routes import comments
    app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
    print("✅ Comments路由注册成功")
except ImportError as e:
    print(f"❌ Comments路由导入失败: {e}")

try:
    from .routes import reflections
    app.include_router(reflections.router, prefix="/api/reflections", tags=["reflections"])
    print("✅ Reflections路由注册成功")
except ImportError as e:
    print(f"❌ Reflections路由导入失败: {e}")

# 启动事件
@app.on_event("startup")
async def startup_event():
    print("🚀 Smart Video Platform API启动完成")
    print("📖 API文档: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
