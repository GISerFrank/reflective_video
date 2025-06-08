# backend/app/services/reflection_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from ..models.reflection import Reflection
from ..models.video import Video
from ..models.user import User
from ..models.user_progress import UserProgress
from .quality_checker import QualityChecker
from ..config import settings

class ReflectionService:
    """
    观后感业务逻辑服务
    处理观后感的创建、审核和质量评估
    """

    def __init__(self):
        self.quality_checker = QualityChecker()

    def create_reflection(self, content: str, video_id: int, user_id: int, db: Session) -> Dict:
        """
        创建观后感
        包含完整的质量检测和业务逻辑
        """
        # 1. 基础验证
        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "观后感内容至少需要50个字符",
                "code": "CONTENT_TOO_SHORT"
            }

        # 2. 检查视频是否存在
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {
                "success": False,
                "error": "视频不存在",
                "code": "VIDEO_NOT_FOUND"
            }

        # 3. 检查用户是否已经写过观后感
        existing_reflection = db.query(Reflection).filter(
            Reflection.user_id == user_id,
            Reflection.video_id == video_id
        ).first()

        if existing_reflection:
            return {
                "success": False,
                "error": "您已经为这个视频写过观后感了",
                "code": "REFLECTION_EXISTS"
            }

        # 4. 检查用户是否观看过视频
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.video_id == video_id
        ).first()

        if not user_progress or user_progress.completion_percentage < 50:
            return {
                "success": False,
                "error": "请先观看视频至少50%再写观后感",
                "code": "INSUFFICIENT_WATCH_TIME"
            }

        content = content.strip()

        # 5. 质量检测
        quality_result = self.quality_checker.analyze_text_quality(content, "reflection")

        # 6. 创建观后感记录
        new_reflection = Reflection(
            user_id=user_id,
            video_id=video_id,
            content=content,
            word_count=len(content),
            quality_score=quality_result["quality_score"],

            # 从质量检测结果中提取的具体指标
            has_thought_words=self._has_thought_indicators(content),
            has_specific_examples=self._has_specific_examples(content),
            has_questions=self._has_questions(content)
        )

        # 7. 确定审核状态
        approval_result = self._determine_approval_status(quality_result, user_progress)
        new_reflection.is_approved = approval_result["approved"]

        if not approval_result["approved"]:
            new_reflection.feedback = approval_result["feedback"]

        # 8. 保存到数据库
        db.add(new_reflection)
        db.commit()
        db.refresh(new_reflection)

        # 9. 更新用户统计
        if approval_result["approved"]:
            self._update_user_stats(user_id, db)

        return {
            "success": True,
            "reflection": new_reflection,
            "quality_result": quality_result,
            "approval_result": approval_result
        }

    def _has_thought_indicators(self, content: str) -> bool:
        """检查是否包含思考性内容"""
        thought_keywords = [
            '思考', '认为', '觉得', '理解', '感悟', '体会', '反思', '意识到',
            '发现', '学到', '启发', '深刻', '重要', '意义', '为什么', '如何'
        ]
        return any(keyword in content for keyword in thought_keywords)

    def _has_specific_examples(self, content: str) -> bool:
        """检查是否包含具体例子"""
        example_keywords = ['比如', '例如', '具体', '实际', '举例', '比方说']
        return any(keyword in content for keyword in example_keywords)

    def _has_questions(self, content: str) -> bool:
        """检查是否包含问题或疑问"""
        return '？' in content or '?' in content or any(
            keyword in content for keyword in ['为什么', '怎么', '如何', '什么时候', '哪里']
        )

    def _determine_approval_status(self, quality_result: Dict, user_progress: UserProgress) -> Dict:
        """
        确定观后感审核状态
        """
        # 质量分数过低 - 拒绝
        if quality_result["quality_score"] < settings.quality_threshold:
            return {
                "approved": False,
                "feedback": f"观后感质量不达标（分数：{quality_result['quality_score']}）。" +
                            "建议：" + "; ".join(quality_result.get("suggestions", [])),
                "auto_decision": True
            }

        # 观看进度不足 - 拒绝
        if user_progress.completion_percentage < 80:
            return {
                "approved": False,
                "feedback": f"请先完整观看视频（当前进度：{user_progress.completion_percentage:.1f}%）",
                "auto_decision": True
            }

        # 质量优秀 - 自动通过
        if quality_result["quality_score"] >= 85:
            return {
                "approved": True,
                "feedback": "观后感质量优秀，已自动通过审核",
                "auto_decision": True
            }

        # 质量良好 - 自动通过
        if quality_result["quality_score"] >= 70:
            return {
                "approved": True,
                "feedback": "观后感质量良好",
                "auto_decision": True
            }

        # 边界情况 - 需要人工审核（暂时自动通过）
        return {
            "approved": True,
            "feedback": "观后感已提交，感谢分享您的想法",
            "auto_decision": False
        }

    def _update_user_stats(self, user_id: int, db: Session):
        """更新用户统计信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.reflections_written += 1
            db.commit()

    def update_reflection(self, reflection_id: int, new_content: str, db: Session) -> Dict:
        """
        更新观后感内容
        """
        reflection = db.query(Reflection).filter(Reflection.id == reflection_id).first()
        if not reflection:
            return {
                "success": False,
                "error": "观后感不存在",
                "code": "REFLECTION_NOT_FOUND"
            }

        # 检查是否可以编辑（已审核通过的不能修改）
        if reflection.is_approved:
            return {
                "success": False,
                "error": "已通过审核的观后感无法修改",
                "code": "CANNOT_EDIT_APPROVED"
            }

        # 重新检测质量
        quality_result = self.quality_checker.analyze_text_quality(new_content, "reflection")

        # 获取用户进度信息
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == reflection.user_id,
            UserProgress.video_id == reflection.video_id
        ).first()

        # 更新观后感
        reflection.content = new_content.strip()
        reflection.word_count = len(new_content)
        reflection.quality_score = quality_result["quality_score"]
        reflection.has_thought_words = self._has_thought_indicators(new_content)
        reflection.has_specific_examples = self._has_specific_examples(new_content)
        reflection.has_questions = self._has_questions(new_content)

        # 重新确定审核状态
        approval_result = self._determine_approval_status(quality_result, user_progress)
        reflection.is_approved = approval_result["approved"]
        reflection.feedback = approval_result["feedback"] if not approval_result["approved"] else None
        reflection.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(reflection)

        return {
            "success": True,
            "reflection": reflection,
            "quality_result": quality_result,
            "approval_result": approval_result
        }

    def get_user_reflections(self, user_id: int, db: Session) -> List[Reflection]:
        """获取用户的所有观后感"""
        return db.query(Reflection).filter(
            Reflection.user_id == user_id
        ).order_by(Reflection.created_at.desc()).all()

    def get_video_reflections(self, video_id: int, db: Session, approved_only: bool = True) -> List[Dict]:
        """获取视频的所有观后感"""
        query = db.query(Reflection).filter(Reflection.video_id == video_id)

        if approved_only:
            query = query.filter(Reflection.is_approved == True)

        reflections = query.order_by(Reflection.created_at.desc()).all()

        # 添加用户信息
        result = []
        for reflection in reflections:
            user = db.query(User).filter(User.id == reflection.user_id).first()
            result.append({
                "reflection": reflection,
                "user": {
                    "id": user.id,
                    "username": user.username
                } if user else None
            })

        return result

    def get_reflection_stats(self, db: Session) -> Dict:
        """获取观后感统计信息"""
        total_reflections = db.query(Reflection).count()
        approved_reflections = db.query(Reflection).filter(Reflection.is_approved == True).count()

        # 平均质量分数
        avg_quality = db.query(Reflection.quality_score).all()
        avg_score = sum(score[0] for score in avg_quality) / len(avg_quality) if avg_quality else 0

        # 各种质量指标统计
        has_thought_count = db.query(Reflection).filter(Reflection.has_thought_words == True).count()
        has_examples_count = db.query(Reflection).filter(Reflection.has_specific_examples == True).count()
        has_questions_count = db.query(Reflection).filter(Reflection.has_questions == True).count()

        return {
            "total_reflections": total_reflections,
            "approved_reflections": approved_reflections,
            "approval_rate": (approved_reflections / total_reflections * 100) if total_reflections > 0 else 0,
            "average_quality_score": round(avg_score, 2),
            "quality_indicators": {
                "has_thought_words": has_thought_count,
                "has_specific_examples": has_examples_count,
                "has_questions": has_questions_count
            }
        }

    def manual_review_reflection(self, reflection_id: int, approved: bool,
                                 reviewer_feedback: str, db: Session) -> Dict:
        """
        人工审核观后感
        """
        reflection = db.query(Reflection).filter(Reflection.id == reflection_id).first()
        if not reflection:
            return {
                "success": False,
                "error": "观后感不存在"
            }

        # 更新审核状态
        reflection.is_approved = approved
        reflection.feedback = reviewer_feedback
        reflection.reviewed_at = datetime.utcnow()

        # 如果通过审核，更新用户统计
        if approved and not reflection.is_approved:  # 之前未通过，现在通过
            self._update_user_stats(reflection.user_id, db)

        db.commit()

        return {
            "success": True,
            "reflection": reflection,
            "action": "approved" if approved else "rejected"
        }

    def get_top_quality_reflections(self, db: Session, limit: int = 10) -> List[Dict]:
        """获取高质量观后感"""
        reflections = db.query(Reflection).filter(
            Reflection.is_approved == True,
            Reflection.quality_score >= 80
        ).order_by(Reflection.quality_score.desc()).limit(limit).all()

        result = []
        for reflection in reflections:
            user = db.query(User).filter(User.id == reflection.user_id).first()
            video = db.query(Video).filter(Video.id == reflection.video_id).first()

            result.append({
                "reflection": reflection,
                "user": {
                    "id": user.id,
                    "username": user.username
                } if user else None,
                "video": {
                    "id": video.id,
                    "title": video.title
                } if video else None
            })

        return result

    def check_reflection_preview(self, content: str, video_id: int, user_id: int, db: Session) -> Dict:
        """
        观后感预检测（不保存到数据库）
        """
        if not content or len(content.strip()) < 50:
            return {
                "valid": False,
                "error": "观后感内容至少需要50个字符"
            }

        # 检查观看进度
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.video_id == video_id
        ).first()

        if not user_progress or user_progress.completion_percentage < 50:
            return {
                "valid": False,
                "error": "请先观看视频至少50%再写观后感"
            }

        # 质量检测
        quality_result = self.quality_checker.analyze_text_quality(content, "reflection")

        # 预测审核结果
        approval_result = self._determine_approval_status(quality_result, user_progress)

        return {
            "valid": True,
            "quality_result": quality_result,
            "predicted_approval": approval_result["approved"],
            "feedback": approval_result["feedback"],
            "suggestions": quality_result.get("suggestions", [])
        }