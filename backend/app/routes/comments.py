# backend/app/routes/comments.py - 最小功能版本
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def get_comments():
    """获取评论列表"""
    return {
        "comments": [],
        "total": 0,
        "message": "评论功能正常运行"
    }

@router.post("/")
async def create_comment(content: str = Body(..., embed=True)):
    """创建评论"""
    if not content or len(content.strip()) < 10:
        raise HTTPException(
            status_code=400, 
            detail="评论内容至少需要10个字符"
        )
    
    return {
        "success": True,
        "comment": {
            "id": 1,
            "content": content.strip(),
            "status": "approved",
            "quality_score": len(content) * 2,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "message": "评论创建成功"
    }

@router.post("/preview")
async def preview_comment(content: str = Body(..., embed=True)):
    """评论预检测"""
    if not content or len(content.strip()) < 10:
        return {
            "valid": False,
            "error": "评论内容至少需要10个字符"
        }
    
    content = content.strip()
    quality_score = min(len(content) * 1.5, 100)
    
    return {
        "valid": True,
        "quality_result": {
            "quality_score": round(quality_score, 2),
            "quality_passed": quality_score >= 60,
            "quality_level": "good" if quality_score >= 80 else "fair"
        },
        "similarity_result": {
            "similarity_score": 15.0,
            "originality_score": 85.0,
            "status": "approved"
        },
        "predicted_status": "approved" if quality_score >= 60 else "rejected",
        "recommendations": [
            "内容质量良好" if quality_score >= 80 else "建议增加更多详细内容"
        ]
    }

@router.post("/similarity/test")
async def test_similarity(text1: str = Body(...), text2: str = Body(...)):
    """相似度测试"""
    # 简单的相似度计算
    set1, set2 = set(text1.lower()), set(text2.lower())
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    similarity = (intersection / union * 100) if union > 0 else 0
    
    return {
        "text1": text1[:50] + "..." if len(text1) > 50 else text1,
        "text2": text2[:50] + "..." if len(text2) > 50 else text2,
        "similarity_score": round(similarity, 2),
        "is_similar": similarity > 50
    }

@router.post("/quality/test")
async def test_quality(content: str = Body(..., embed=True)):
    """质量测试"""
    word_count = len(content)
    
    # 简单的质量评分
    base_score = min(word_count * 1.2, 60)
    
    # 加分项
    bonus = 0
    if any(word in content for word in ["认为", "觉得", "思考", "理解"]):
        bonus += 15
    if any(word in content for word in ["比如", "例如", "具体"]):
        bonus += 10
    if "？" in content or "?" in content:
        bonus += 5
    
    quality_score = min(base_score + bonus, 100)
    
    return {
        "quality_score": round(quality_score, 2),
        "quality_passed": quality_score >= 60,
        "quality_level": "excellent" if quality_score >= 90 else "good" if quality_score >= 75 else "fair" if quality_score >= 60 else "poor",
        "details": {
            "word_count": word_count,
            "thought_score": 15 if bonus >= 15 else 5,
            "specific_score": 10 if "比如" in content or "例如" in content else 5,
            "emotion_score": 5 if any(word in content for word in ["喜欢", "讨厌", "感动"]) else 0
        },
        "issues": ["内容过短"] if word_count < 30 else [],
        "suggestions": [
            "增加更多个人见解",
            "提供具体例子"
        ] if quality_score < 80 else ["内容质量良好"]
    }

@router.get("/system/stats")
async def get_system_stats():
    """系统统计"""
    return {
        "total_comments": 0,
        "approval_rate": 0.0,
        "similarity_stats": {
            "average_similarity_score": 0.0,
            "rejected_by_similarity": 0,
            "rejection_rate": 0.0,
            "threshold": 70.0
        },
        "quality_stats": {
            "threshold": 60,
            "thought_words_count": 20,
            "emotion_words_count": 15
        },
        "thresholds": {
            "similarity_threshold": 70.0,
            "quality_threshold": 60
        }
    }
