# backend/app/services/video_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

from ..models.video import Video
from ..models.user_progress import UserProgress
from ..models.user import User
from ..models.reflection import Reflection
from ..models.comment import Comment, CommentStatus

class VideoService:
    """
    视频业务逻辑服务
    处理视频相关的复杂业务逻辑
    """

    def get_video_with_progress(self, video_id: int, user_id: int, db: Session) -> Optional[Dict]:
        """
        获取视频详情及用户进度
        """
        # 获取视频信息
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.is_published == True
        ).first()

        if not video:
            return None

        # 获取用户进度
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.video_id == video_id
        ).first()

        # 获取相关统计
        stats = self._get_video_stats(video_id, db)

        return {
            "video": video,
            "progress": progress,
            "stats": stats,
            "next_video": self._get_next_video(video.order_index, db),
            "prev_video": self._get_prev_video(video.order_index, db)
        }

    def _get_video_stats(self, video_id: int, db: Session) -> Dict:
        """获取视频统计信息"""
        # 总观看人数
        total_viewers = db.query(UserProgress.user_id).filter(
            UserProgress.video_id == video_id
        ).distinct().count()

        # 完成人数
        completed_viewers = db.query(UserProgress).filter(
            UserProgress.video_id == video_id,
            UserProgress.is_completed == True
        ).count()

        # 平均观看进度
        avg_progress = db.query(func.avg(UserProgress.completion_percentage)).filter(
            UserProgress.video_id == video_id
        ).scalar() or 0

        # 观后感数量
        reflection_count = db.query(Reflection).filter(
            Reflection.video_id == video_id,
            Reflection.is_approved == True
        ).count()

        # 评论数量
        comment_count = db.query(Comment).filter(
            Comment.status == CommentStatus.APPROVED
        ).count()  # 这里假设评论是全局的，如果需要按视频分类需要调整模型

        return {
            "total_viewers": total_viewers,
            "completed_viewers": completed_viewers,
            "completion_rate": (completed_viewers / total_viewers * 100) if total_viewers > 0 else 0,
            "average_progress": round(avg_progress, 2),
            "reflection_count": reflection_count,
            "comment_count": comment_count
        }

    def _get_next_video(self, current_order: int, db: Session) -> Optional[Video]:
        """获取下一个视频"""
        return db.query(Video).filter(
            Video.order_index > current_order,
            Video.is_published == True
        ).order_by(Video.order_index).first()

    def _get_prev_video(self, current_order: int, db: Session) -> Optional[Video]:
        """获取上一个视频"""
        return db.query(Video).filter(
            Video.order_index < current_order,
            Video.is_published == True
        ).order_by(desc(Video.order_index)).first()

    def update_watch_progress(self, video_id: int, user_id: int,
                              watched_time: int, current_position: int, db: Session) -> Dict:
        """
        更新观看进度的智能算法
        """
        # 获取视频信息
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {"success": False, "error": "视频不存在"}

        # 查找或创建进度记录
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.video_id == video_id
        ).first()

        if not progress:
            progress = UserProgress(
                user_id=user_id,
                video_id=video_id,
                watched_time=0,
                last_watched_position=0,
                watch_count=0
            )
            db.add(progress)

        # 智能更新逻辑
        old_watched_time = progress.watched_time
        old_position = progress.last_watched_position

        # 更新观看时间（只有前进时才增加）
        if watched_time > old_watched_time:
            progress.watched_time = watched_time

        # 更新当前位置
        progress.last_watched_position = current_position

        # 检测是否是新的观看会话（位置倒退很多表示重新开始）
        if current_position < old_position - 30:  # 倒退超过30秒
            progress.watch_count += 1

        # 计算完成百分比
        completion_percentage = min((watched_time / video.duration) * 100, 100.0)
        progress.completion_percentage = completion_percentage

        # 判断是否完成（90%以上且观看时间足够）
        if (completion_percentage >= 90 and
                watched_time >= video.duration * 0.8 and
                not progress.is_completed):

            progress.is_completed = True
            progress.completed_at = datetime.utcnow()

            # 更新用户统计
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.videos_completed += 1

        progress.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(progress)

        return {
            "success": True,
            "progress": progress,
            "newly_completed": progress.is_completed and completion_percentage >= 90,
            "next_video_recommended": self._should_recommend_next_video(progress, db)
        }

    def _should_recommend_next_video(self, progress: UserProgress, db: Session) -> bool:
        """判断是否应该推荐下一个视频"""
        if not progress.is_completed:
            return False

        # 检查是否已经开始下一个视频
        video = db.query(Video).filter(Video.id == progress.video_id).first()
        if not video:
            return False

        next_video = self._get_next_video(video.order_index, db)
        if not next_video:
            return False

        # 检查是否已经有下一个视频的进度
        next_progress = db.query(UserProgress).filter(
            UserProgress.user_id == progress.user_id,
            UserProgress.video_id == next_video.id
        ).first()

        return next_progress is None  # 如果没有进度记录，则推荐

    def get_user_learning_path(self, user_id: int, db: Session) -> Dict:
        """
        获取用户学习路径和建议
        """
        # 获取用户所有进度
        user_progresses = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).join(Video).order_by(Video.order_index).all()

        # 获取所有发布的视频
        all_videos = db.query(Video).filter(
            Video.is_published == True
        ).order_by(Video.order_index).all()

        # 构建学习路径
        learning_path = []
        completed_count = 0
        current_video = None

        for video in all_videos:
            progress = next((p for p in user_progresses if p.video_id == video.id), None)

            video_info = {
                "video": video,
                "progress": progress,
                "status": self._get_video_status(video, progress),
                "can_access": self._can_access_video(video, user_progresses, all_videos)
            }

            learning_path.append(video_info)

            if progress and progress.is_completed:
                completed_count += 1
            elif not current_video and (not progress or progress.completion_percentage < 90):
                current_video = video

        # 生成学习建议
        recommendations = self._generate_learning_recommendations(
            user_id, learning_path, db
        )

        return {
            "learning_path": learning_path,
            "total_videos": len(all_videos),
            "completed_videos": completed_count,
            "completion_rate": (completed_count / len(all_videos) * 100) if all_videos else 0,
            "current_video": current_video,
            "recommendations": recommendations
        }

    def _get_video_status(self, video: Video, progress: Optional[UserProgress]) -> str:
        """获取视频状态"""
        if not progress:
            return "not_started"
        elif progress.is_completed:
            return "completed"
        elif progress.completion_percentage > 0:
            return "in_progress"
        else:
            return "not_started"

    def _can_access_video(self, video: Video, user_progresses: List[UserProgress],
                          all_videos: List[Video]) -> bool:
        """判断用户是否可以访问该视频"""
        # 第一个视频总是可以访问
        if video.order_index == 1:
            return True

        # 检查前置视频是否完成
        prev_video = next((v for v in all_videos if v.order_index == video.order_index - 1), None)
        if not prev_video:
            return True

        prev_progress = next((p for p in user_progresses if p.video_id == prev_video.id), None)
        return prev_progress and prev_progress.is_completed

    def _generate_learning_recommendations(self, user_id: int, learning_path: List[Dict],
                                           db: Session) -> List[str]:
        """生成个性化学习建议"""
        recommendations = []

        # 分析学习模式
        completed_videos = [item for item in learning_path if item["status"] == "completed"]
        in_progress_videos = [item for item in learning_path if item["status"] == "in_progress"]

        # 如果没有开始学习
        if not completed_videos and not in_progress_videos:
            recommendations.append("建议从第一个视频开始学习")
            return recommendations

        # 如果有未完成的视频
        if in_progress_videos:
            video_title = in_progress_videos[0]["video"].title
            progress = in_progress_videos[0]["progress"].completion_percentage
            recommendations.append(f"继续学习《{video_title}》(已完成{progress:.1f}%)")

        # 分析学习效率
        if completed_videos:
            # 计算平均观看时间
            total_watch_time = sum(p["progress"].watched_time for p in completed_videos)
            avg_efficiency = total_watch_time / len(completed_videos) if completed_videos else 0

            if avg_efficiency > 0:
                recommendations.append("保持良好的学习节奏")

        # 检查是否需要写观后感
        user_reflections = db.query(Reflection).filter(Reflection.user_id == user_id).count()
        if len(completed_videos) > user_reflections:
            recommendations.append("建议为已完成的视频写观后感，加深理解")

        return recommendations

    def get_popular_videos(self, db: Session, limit: int = 10) -> List[Dict]:
        """获取热门视频（按观看人数和完成率排序）"""
        # 子查询：计算每个视频的统计数据
        video_stats = db.query(
            Video.id,
            Video.title,
            Video.description,
            Video.duration,
            Video.category,
            func.count(UserProgress.user_id).label('viewer_count'),
            func.sum(func.cast(UserProgress.is_completed, db.bind.dialect.name == 'sqlite' and 'INTEGER' or 'INT')).label('completion_count'),
            func.avg(UserProgress.completion_percentage).label('avg_progress')
        ).outerjoin(UserProgress).filter(
            Video.is_published == True
        ).group_by(Video.id).subquery()

        # 主查询：排序和限制
        popular_videos = db.query(video_stats).order_by(
            desc(video_stats.c.viewer_count),
            desc(video_stats.c.avg_progress)
        ).limit(limit).all()

        result = []
        for video_stat in popular_videos:
            completion_rate = 0
            if video_stat.viewer_count > 0 and video_stat.completion_count:
                completion_rate = (video_stat.completion_count / video_stat.viewer_count) * 100

            result.append({
                "id": video_stat.id,
                "title": video_stat.title,
                "description": video_stat.description,
                "duration": video_stat.duration,
                "category": video_stat.category,
                "viewer_count": video_stat.viewer_count or 0,
                "completion_rate": round(completion_rate, 2),
                "average_progress": round(video_stat.avg_progress or 0, 2)
            })

        return result

    def get_system_overview(self, db: Session) -> Dict:
        """获取系统概览统计"""
        # 视频统计
        total_videos = db.query(Video).filter(Video.is_published == True).count()
        total_duration = db.query(func.sum(Video.duration)).filter(Video.is_published == True).scalar() or 0

        # 用户统计
        total_users = db.query(User).count()
        active_users = db.query(UserProgress.user_id).distinct().count()

        # 学习统计
        total_views = db.query(UserProgress).count()
        completed_views = db.query(UserProgress).filter(UserProgress.is_completed == True).count()

        # 最近7天的活跃度
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = db.query(UserProgress).filter(
            UserProgress.updated_at >= week_ago
        ).count()

        return {
            "video_stats": {
                "total_videos": total_videos,
                "total_duration_hours": round(total_duration / 3600, 2),
                "categories": db.query(Video.category).filter(
                    Video.category.isnot(None),
                    Video.is_published == True
                ).distinct().count()
            },
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "engagement_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
            },
            "learning_stats": {
                "total_views": total_views,
                "completed_views": completed_views,
                "completion_rate": round((completed_views / total_views * 100) if total_views > 0 else 0, 2),
                "recent_activity": recent_activity
            }
        }