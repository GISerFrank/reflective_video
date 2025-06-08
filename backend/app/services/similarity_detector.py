# backend/app/services/similarity_detector.py
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional
import re
from sqlalchemy.orm import Session
from ..models.comment import Comment
from ..config import settings

class SimilarityDetector:
    """
    相似度检测服务
    使用TF-IDF + 余弦相似度检测文本相似性
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,          # 最大特征数
            stop_words=None,            # 中文停用词需要自定义
            ngram_range=(1, 2),         # 1-2gram特征
            min_df=1,                   # 最小文档频率
            max_df=0.8                  # 最大文档频率
        )
        self.chinese_stopwords = self._load_chinese_stopwords()

    def _load_chinese_stopwords(self) -> set:
        """加载中文停用词"""
        # 基础中文停用词
        stopwords = {
            '的', '了', '是', '我', '你', '他', '她', '它', '我们', '你们', '他们',
            '这', '那', '这个', '那个', '这里', '那里', '这样', '那样',
            '有', '没有', '还', '就', '都', '也', '很', '更', '最',
            '在', '从', '到', '为', '和', '与', '及', '以及',
            '但是', '然而', '不过', '可是', '虽然', '尽管',
            '因为', '所以', '如果', '那么', '然后', '接着',
            '什么', '怎么', '为什么', '哪里', '哪个', '多少',
            '一个', '一些', '许多', '很多', '大量', '少量',
            '非常', '特别', '尤其', '特殊', '普通', '一般'
        }
        return stopwords

    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        1. 清理特殊字符
        2. 中文分词
        3. 去除停用词
        """
        # 清理特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？、；：""''（）【】\s]', '', text)

        # 中文分词
        words = jieba.lcut(text)

        # 去除停用词和短词
        filtered_words = [
            word.strip() for word in words
            if len(word.strip()) > 1 and word.strip() not in self.chinese_stopwords
        ]

        return ' '.join(filtered_words)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        返回值：0-100的相似度分数
        """
        if not text1 or not text2:
            return 0.0

        # 预处理文本
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)

        if not processed_text1 or not processed_text2:
            return 0.0

        try:
            # 计算TF-IDF向量
            tfidf_matrix = self.vectorizer.fit_transform([processed_text1, processed_text2])

            # 计算余弦相似度
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity = similarity_matrix[0][0]

            # 转换为百分比
            return float(similarity * 100)

        except Exception as e:
            print(f"相似度计算错误: {e}")
            return 0.0

    def find_most_similar_comment(self, new_text: str, db: Session, exclude_id: Optional[int] = None) -> Tuple[float, Optional[Comment]]:
        """
        找到数据库中与新文本最相似的评论
        返回：(最高相似度, 最相似的评论对象)
        """
        if not new_text or len(new_text.strip()) < 10:
            return 0.0, None

        # 查询已有评论（排除自己）
        query = db.query(Comment).filter(Comment.content.isnot(None))
        if exclude_id:
            query = query.filter(Comment.id != exclude_id)

        existing_comments = query.all()

        if not existing_comments:
            return 0.0, None

        max_similarity = 0.0
        most_similar_comment = None

        # 批量计算相似度（优化性能）
        if len(existing_comments) > 50:  # 如果评论太多，采用批量处理
            return self._batch_similarity_check(new_text, existing_comments)

        # 逐一比较
        for comment in existing_comments:
            similarity = self.calculate_similarity(new_text, comment.content)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_comment = comment

        return max_similarity, most_similar_comment

    def _batch_similarity_check(self, new_text: str, comments: List[Comment]) -> Tuple[float, Optional[Comment]]:
        """
        批量相似度检测（适用于大量评论的情况）
        """
        try:
            # 预处理所有文本
            processed_new = self.preprocess_text(new_text)
            processed_comments = [self.preprocess_text(comment.content) for comment in comments]

            # 过滤空文本
            valid_pairs = [(i, text) for i, text in enumerate(processed_comments) if text]
            if not valid_pairs:
                return 0.0, None

            valid_indices = [pair[0] for pair in valid_pairs]
            valid_texts = [pair[1] for pair in valid_pairs]

            # 构建文档列表
            all_texts = [processed_new] + valid_texts

            # 计算TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)

            # 计算相似度矩阵
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

            # 找到最高相似度
            similarities = similarity_matrix[0]
            max_idx = np.argmax(similarities)
            max_similarity = float(similarities[max_idx] * 100)

            # 返回结果
            original_idx = valid_indices[max_idx]
            most_similar_comment = comments[original_idx]

            return max_similarity, most_similar_comment

        except Exception as e:
            print(f"批量相似度检测错误: {e}")
            # 降级到逐一比较
            return self.find_most_similar_comment(new_text, None)

    def check_comment_originality(self, text: str, db: Session, exclude_id: Optional[int] = None) -> Dict:
        """
        检查评论原创性
        返回检测结果和建议
        """
        similarity_score, similar_comment = self.find_most_similar_comment(text, db, exclude_id)

        # 计算原创度分数 (100 - 相似度)
        originality_score = max(0, 100 - similarity_score)

        # 根据相似度给出判断
        if similarity_score >= settings.similarity_threshold:
            status = "rejected"
            reason = f"与已有评论相似度过高 ({similarity_score:.1f}%)"
            recommendation = "请尝试用自己的话表达独特的观点"
        elif similarity_score >= 40:
            status = "warning"
            reason = f"与已有评论有一定相似性 ({similarity_score:.1f}%)"
            recommendation = "建议增加更多个人见解和独特观点"
        else:
            status = "approved"
            reason = "原创性良好"
            recommendation = "继续保持独特的表达"

        return {
            "similarity_score": round(similarity_score, 2),
            "originality_score": round(originality_score, 2),
            "status": status,
            "reason": reason,
            "recommendation": recommendation,
            "similar_comment_id": similar_comment.id if similar_comment else None,
            "similar_comment_content": similar_comment.content[:100] + "..." if similar_comment and len(similar_comment.content) > 100 else similar_comment.content if similar_comment else None
        }

    def update_user_originality_score(self, user_id: int, new_score: float, db: Session):
        """
        更新用户的原创度分数
        采用加权平均的方式
        """
        from ..models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # 获取用户的评论数量
        comment_count = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.status == "approved"
        ).count()

        if comment_count == 0:
            # 第一个评论
            user.originality_score = new_score
        else:
            # 加权平均：新评论权重20%，历史平均权重80%
            user.originality_score = user.originality_score * 0.8 + new_score * 0.2

        db.commit()

    def get_similarity_stats(self, db: Session) -> Dict:
        """
        获取相似度检测统计信息
        """
        total_comments = db.query(Comment).count()
        rejected_comments = db.query(Comment).filter(
            Comment.reject_reason.like("%相似度%")
        ).count()

        avg_similarity = db.query(Comment.similarity_score).filter(
            Comment.similarity_score > 0
        ).all()

        avg_score = np.mean([score[0] for score in avg_similarity]) if avg_similarity else 0

        return {
            "total_comments": total_comments,
            "rejected_by_similarity": rejected_comments,
            "rejection_rate": (rejected_comments / total_comments * 100) if total_comments > 0 else 0,
            "average_similarity_score": round(avg_score, 2),
            "threshold": settings.similarity_threshold
        }