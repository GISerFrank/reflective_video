# backend/app/routes/reflections.py - 最小功能版本
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

@router.get("/")
async def get_reflections():
    """获取观后感列表"""
    return {"reflections": [], "total": 0, "message": "观后感功能正常运行"}

@router.post("/")
async def create_reflection(content: str = Body(...), video_id: int = Body(...)):
    """创建观后感"""
    if not content or len(content.strip()) < 50:
        raise HTTPException(status_code=400, detail="观后感内容至少需要50个字符")
    
    quality_score = min(len(content) * 1.0, 100)
    
    return {
        "success": True,
        "reflection": {
            "id": 1,
            "content": content.strip(),
            "video_id": video_id,
            "quality_score": round(quality_score, 2),
            "is_approved": quality_score >= 60
        }
    }

@router.post("/preview")
async def preview_reflection(content: str = Body(...), video_id: int = Body(...)):
    """观后感预检测"""
    if not content or len(content.strip()) < 50:
        return {"valid": False, "error": "观后感内容至少需要50个字符"}
    
    quality_score = min(len(content) * 1.0, 100)
    return {
        "valid": True,
        "quality_result": {"quality_score": round(quality_score, 2), "quality_passed": quality_score >= 60},
        "predicted_approval": quality_score >= 60
    }

@router.get("/stats/overview")
async def get_reflection_stats():
    """获取观后感统计"""
    return {"total_reflections": 0, "approved_reflections": 0, "approval_rate": 0.0}

@router.get("/featured/top")
async def get_top_quality_reflections():
    """获取精选高质量观后感"""
    return {"featured_reflections": [], "count": 0, "message": "暂无精选观后感"}
