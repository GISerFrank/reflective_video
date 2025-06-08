# backend/app/services/comment_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from ..models.comment import Comment, CommentStatus
from ..models.user import User
from .similarity_detector import SimilarityDetector
from .quality_checker import QualityChecker
from ..config import settings

class CommentService:
    """
    评论业务逻辑服务
    集成相似度检测和质量检测
    """

    def __init__(self):
        self.similarity_detector = SimilarityDetector()
        self.quality_checker = QualityChecker()

    def create_comment(self, content: str, user_id: int, parent_id: Optional[int], db: Session) -> Dict:
        """
        创建新评论，包含完整的检测流程
        """
        # 1. 基础验证
        if not content or len(content.strip()) < 10:
            return {
                "success": False,
                "error": "评论内容至少需要10个字符",
                "code": "CONTENT_TOO_SHORT"
            }

        content = content.strip()

        # 2. 质量检测
        quality_result = self.quality_checker.analyze_text_quality(content, "comment")

        # 3. 相似度检测
        similarity_result = self.similarity_detector.check_comment_originality(content, db)

        # 4. 创建评论记录
        new_comment = Comment(
            user_id=user_id,
            content=content,
            word_count=len(content),
            parent_id=parent_id,

            # 质量指标
            quality_passed=quality_result["quality_passed"],
            quality_issues="; ".join(quality_result["issues"]) if quality_result["issues"] else None,

            # 相似度指标
            similarity_score=similarity_result["similarity_score"],
            original_score=similarity_result["originality_score"]
        )

        # 5. 确定审核状态
        approval_result = self._determine_approval_status(quality_result, similarity_result)
        new_comment.status = CommentStatus(approval_result["status"])

        if approval_result["status"] == "rejected":
            new_comment.reject_reason = approval_result["reason"]

        # 6. 保存到数据库
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        # 7. 更新用户统计
        if approval_result["status"] == "approved":
            self._update_user_stats(user_id, similarity_result["originality_score"], db)

        return {
            "success": True,
            "comment": new_comment,
            "quality_result": quality_result,
            "similarity_result": similarity_result,
            "approval_result": approval_result
        }

    def _determine_approval_status(self, quality_result: Dict, similarity_result: Dict) -> Dict:
        """
        根据质量和相似度检测结果确定审核状态
        """
        # 相似度过高 - 直接拒绝
        if similarity_result["similarity_score"] >= settings.similarity_threshold:
            return {
                "status": "rejected",
                "reason": f"与已有评论相似度过高 ({similarity_result['similarity_score']:.1f}%)",
                "auto_decision": True
            }

        # 质量不达标 - 直接拒绝
        if not quality_result["quality_passed"]:
            return {
                "status": "rejected",
                "reason": f"内容质量不达标 (分数: {quality_result['quality_score']})",
                "auto_decision": True
            }

        # 质量很高且原创性好 - 自动通过
        if (quality_result["quality_score"] >= 80 and
                similarity_result["similarity_score"] < 20):
            return {
                "status": "approved",
                "reason": "内容质量优秀且原创性高",
                "auto_decision": True
            }

        # 边界情况 - 人工审核
        if (quality_result["quality_score"] >= 60 and
                similarity_result["similarity_score"] < 40):
            return {
                "status": "pending",
                "reason": "需要人工审核确认",
                "auto_decision": False
            }

        # 其他情况 - 默认拒绝
        return {
            "status": "rejected",
            "reason": "内容质量或原创性不足",
            "auto_decision": True
        }

    def _update_user_stats(self, user_id: int, originality_score: float, db: Session):
        """更新用户统计信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # 增加通过的评论数
        user.comments_approved += 1

        # 更新原创度分数
        self.similarity_detector.update_user_originality_score(user_id, originality_score, db)

    def update_comment(self, comment_id: int, new_content: str, db: Session) -> Dict:
        """
        更新评论内容并重新检测
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return {
                "success": False,
                "error": "评论不存在",
                "code": "COMMENT_NOT_FOUND"
            }

        # 检查是否可以编辑
        if comment.status == CommentStatus.APPROVED:
            return {
                "success": False,
                "error": "已通过审核的评论无法修改",
                "code": "CANNOT_EDIT_APPROVED"
            }

        # 重新检测
        quality_result = self.quality_checker.analyze_text_quality(new_content, "comment")
        similarity_result = self.similarity_detector.check_comment_originality(
            new_content, db, exclude_id=comment_id
        )

        # 更新评论
        comment.content = new_content.strip()
        comment.word_count = len(new_content)
        comment.quality_passed = quality_result["quality_passed"]
        comment.quality_issues = "; ".join(quality_result["issues"]) if quality_result["issues"] else None
        comment.similarity_score = similarity_result["similarity_score"]
        comment.original_score = similarity_result["originality_score"]

        # 重新确定状态
        approval_result = self._determine_approval_status(quality_result, similarity_result)
        comment.status = CommentStatus(approval_result["status"])
        comment.reject_reason = approval_result["reason"] if approval_result["status"] == "rejected" else None
        comment.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(comment)

        return {
            "success": True,
            "comment": comment,
            "quality_result": quality_result,
            "similarity_result": similarity_result,
            "approval_result": approval_result
        }

    def get_comments_by_status(self, status: CommentStatus, db: Session, limit: int = 50) -> List[Comment]:
        """获取指定状态的评论"""
        return db.query(Comment).filter(
            Comment.status == status
        ).order_by(Comment.created_at.desc()).limit(limit).all()

    def manual_review_comment(self, comment_id: int, approved: bool, reviewer_feedback: str, db: Session) -> Dict:
        """
        人工审核评论
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return {
                "success": False,
                "error": "评论不存在"
            }

        if comment.status != CommentStatus.PENDING:
            return {
                "success": False,
                "error": "只能审核待审核状态的评论"
            }

        # 更新状态
        comment.status = CommentStatus.APPROVED if approved else CommentStatus.REJECTED
        if not approved:
            comment.reject_reason = reviewer_feedback
        comment.reviewed_at = datetime.utcnow()

        # 如果通过，更新用户统计
        if approved:
            self._update_user_stats(comment.user_id, comment.original_score, db)

        db.commit()

        return {
            "success": True,
            "comment": comment,
            "action": "approved" if approved else "rejected"
        }

    def get_user_comment_stats(self, user_id: int, db: Session) -> Dict:
        """获取用户评论统计"""
        total_comments = db.query(Comment).filter(Comment.user_id == user_id).count()
        approved_comments = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.status == CommentStatus.APPROVED
        ).count()
        pending_comments = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.status == CommentStatus.PENDING
        ).count()
        rejected_comments = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.status == CommentStatus.REJECTED
        ).count()

        # 计算平均分数
        user_comments = db.query(Comment).filter(Comment.user_id == user_id).all()
        avg_quality = sum(c.quality_passed for c in user_comments) / len(user_comments) * 100 if user_comments else 0
        avg_originality = sum(c.original_score for c in user_comments) / len(user_comments) if user_comments else 0

        return {
            "total_comments": total_comments,
            "approved_comments": approved_comments,
            "pending_comments": pending_comments,
            "rejected_comments": rejected_comments,
            "approval_rate": (approved_comments / total_comments * 100) if total_comments > 0 else 0,
            "average_quality_score": round(avg_quality, 2),
            "average_originality_score": round(avg_originality, 2)
        }

    def check_comment_preview(self, content: str, db: Session) -> Dict:
        """
        评论预检测（不保存到数据库）
        用于给用户实时反馈
        """
        if not content or len(content.strip()) < 10:
            return {
                "valid": False,
                "error": "评论内容至少需要10个字符"
            }

        content = content.strip()

        # 质量检测
        quality_result = self.quality_checker.analyze_text_quality(content, "comment")

        # 相似度检测
        similarity_result = self.similarity_detector.check_comment_originality(content, db)

        # 预测审核结果
        approval_result = self._determine_approval_status(quality_result, similarity_result)

        return {
            "valid": True,
            "quality_result": quality_result,
            "similarity_result": similarity_result,
            "predicted_status": approval_result["status"],
            "predicted_reason": approval_result["reason"],
            "recommendations": quality_result.get("suggestions", []) + [similarity_result.get("recommendation", "")]
        }

    def get_system_stats(self, db: Session) -> Dict:
        """获取系统评论统计"""
        total_comments = db.query(Comment).count()
        approved_rate = db.query(Comment).filter(Comment.status == CommentStatus.APPROVED).count() / total_comments * 100 if total_comments > 0 else 0

        # 相似度统计
        similarity_stats = self.similarity_detector.get_similarity_stats(db)

        # 质量统计
        quality_stats = self.quality_checker.get_quality_stats()

        return {
            "total_comments": total_comments,
            "approval_rate": round(approved_rate, 2),
            "similarity_stats": similarity_stats,
            "quality_stats": quality_stats,
            "thresholds": {
                "similarity_threshold": settings.similarity_threshold,
                "quality_threshold": settings.quality_threshold
            }
        }