# backend/app/services/quality_checker.py
import re
import jieba
from typing import Dict, List, Tuple
from ..config import settings

class QualityChecker:
    """
    内容质量检测服务
    检测观后感和评论的质量指标
    """

    def __init__(self):
        # 思考性词汇
        self.thought_words = {
            '思考', '认为', '觉得', '感觉', '理解', '领悟', '体会', '感悟', '反思',
            '意识到', '发现', '注意到', '观察', '分析', '判断', '推测', '猜测',
            '思维', '想法', '观点', '见解', '理念', '概念', '印象', '感受',
            '启发', '启示', '提醒', '警示', '教训', '收获', '得到', '学到',
            '深入', '深刻', '深层', '本质', '核心', '关键', '重要', '意义',
            '价值', '作用', '影响', '效果', '结果', '后果', '原因', '为什么'
        }

        # 情感词汇
        self.emotion_words = {
            '喜欢', '讨厌', '爱', '恨', '开心', '难过', '激动', '平静', '紧张',
            '放松', '惊讶', '震惊', '感动', '愤怒', '恐惧', '害怕', '担心',
            '希望', '失望', '满意', '不满', '欣赏', '赞美', '批评', '质疑'
        }

        # 具体描述性词汇
        self.descriptive_words = {
            '具体', '详细', '清楚', '明确', '准确', '精确', '生动', '形象',
            '比如', '例如', '举例', '实例', '案例', '情况', '场景', '画面',
            '细节', '方面', '角度', '层面', '程度', '范围', '规模', '数量'
        }

        # 质量问题关键词
        self.quality_issues = {
            'too_short': ['字数不足', '内容过短'],
            'repetitive': ['重复内容', '句式单一'],
            'shallow': ['泛泛而谈', '缺乏深度'],
            'off_topic': ['偏离主题', '内容无关'],
            'poor_grammar': ['语法错误', '表达不清'],
            'copy_paste': ['疑似复制', '格式异常']
        }

    def analyze_text_quality(self, text: str, text_type: str = "comment") -> Dict:
        """
        分析文本质量
        text_type: "comment" 或 "reflection"
        """
        if not text or not text.strip():
            return self._create_quality_result(0, ["内容为空"], "内容不能为空")

        text = text.strip()

        # 基础指标
        word_count = len(text)
        sentence_count = len(re.split(r'[。！？\n]', text))

        # 分词分析
        words = jieba.lcut(text)
        unique_words = set(words)

        quality_score = 0
        issues = []
        suggestions = []

        # 1. 长度检查
        min_length = 50 if text_type == "reflection" else 10
        if word_count < min_length:
            issues.append(f"内容过短，至少需要{min_length}个字符")
        else:
            quality_score += 20

        # 2. 思考深度检查
        thought_score = self._check_thought_depth(words)
        quality_score += thought_score
        if thought_score < 10:
            suggestions.append("尝试加入更多个人思考和见解")

        # 3. 具体性检查
        specific_score = self._check_specificity(words, text)
        quality_score += specific_score
        if specific_score < 10:
            suggestions.append("增加具体的例子和细节描述")

        # 4. 表达多样性检查
        diversity_score = self._check_expression_diversity(words, sentence_count)
        quality_score += diversity_score
        if diversity_score < 10:
            suggestions.append("尝试使用更丰富的表达方式")

        # 5. 情感表达检查
        emotion_score = self._check_emotional_expression(words)
        quality_score += emotion_score
        if emotion_score < 5:
            suggestions.append("可以加入更多个人感受和情感体验")

        # 6. 语法和格式检查
        grammar_score = self._check_grammar_and_format(text)
        quality_score += grammar_score
        if grammar_score < 10:
            issues.append("注意语法和标点符号的使用")

        # 特殊检查（根据文本类型）
        if text_type == "reflection":
            reflection_bonus = self._check_reflection_specific(text, words)
            quality_score += reflection_bonus
            if reflection_bonus < 5:
                suggestions.append("观后感应该包含对视频内容的具体反思")

        # 限制分数范围
        quality_score = min(100, max(0, quality_score))

        # 质量等级判定
        quality_level = self._determine_quality_level(quality_score)

        return self._create_quality_result(
            quality_score, issues, suggestions, {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "unique_word_ratio": len(unique_words) / len(words) if words else 0,
                "thought_score": thought_score,
                "specific_score": specific_score,
                "diversity_score": diversity_score,
                "emotion_score": emotion_score,
                "grammar_score": grammar_score,
                "quality_level": quality_level
            }
        )

    def _check_thought_depth(self, words: List[str]) -> int:
        """检查思考深度"""
        thought_count = sum(1 for word in words if word in self.thought_words)

        # 基础分数
        if thought_count == 0:
            return 0
        elif thought_count <= 2:
            return 10
        elif thought_count <= 5:
            return 20
        else:
            return 25

    def _check_specificity(self, words: List[str], text: str) -> int:
        """检查具体性"""
        specific_count = sum(1 for word in words if word in self.descriptive_words)

        # 检查是否包含具体例子
        example_patterns = [r'比如', r'例如', r'举例', r'具体', r'实际']
        has_examples = any(re.search(pattern, text) for pattern in example_patterns)

        # 检查数字和数据
        has_numbers = bool(re.search(r'\d+', text))

        score = 0
        if specific_count > 0:
            score += 10
        if has_examples:
            score += 10
        if has_numbers:
            score += 5

        return min(20, score)

    def _check_expression_diversity(self, words: List[str], sentence_count: int) -> int:
        """检查表达多样性"""
        if not words:
            return 0

        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)

        # 句子长度变化
        avg_sentence_length = len(words) / sentence_count if sentence_count > 0 else 0

        score = 0
        if diversity_ratio > 0.6:
            score += 15
        elif diversity_ratio > 0.4:
            score += 10
        elif diversity_ratio > 0.2:
            score += 5

        if avg_sentence_length > 5:
            score += 5

        return min(20, score)

    def _check_emotional_expression(self, words: List[str]) -> int:
        """检查情感表达"""
        emotion_count = sum(1 for word in words if word in self.emotion_words)

        if emotion_count == 0:
            return 0
        elif emotion_count <= 2:
            return 5
        elif emotion_count <= 4:
            return 10
        else:
            return 15

    def _check_grammar_and_format(self, text: str) -> int:
        """检查语法和格式"""
        score = 15  # 基础分数

        # 检查常见问题
        issues = []

        # 标点符号检查
        if not re.search(r'[。！？]', text):
            issues.append("缺少合适的句号")
            score -= 3

        # 连续重复字符
        if re.search(r'(.)\1{3,}', text):
            issues.append("包含过多重复字符")
            score -= 2

        # 全大写或全小写
        if text.isupper() or text.islower():
            score -= 1

        # 过多的感叹号
        if text.count('！') > 3 or text.count('!') > 3:
            score -= 2

        return max(0, score)

    def _check_reflection_specific(self, text: str, words: List[str]) -> int:
        """观后感特定检查"""
        score = 0

        # 检查是否提到视频内容
        video_keywords = ['视频', '影片', '内容', '讲解', '演示', '案例', '课程']
        has_video_ref = any(keyword in text for keyword in video_keywords)
        if has_video_ref:
            score += 5

        # 检查是否包含疑问
        question_patterns = [r'？', r'\?', r'为什么', r'怎么', r'如何']
        has_questions = any(re.search(pattern, text) for pattern in question_patterns)
        if has_questions:
            score += 3

        # 检查是否有对比或联系
        comparison_words = ['对比', '比较', '相比', '类似', '不同', '联系', '关联']
        has_comparison = any(word in text for word in comparison_words)
        if has_comparison:
            score += 5

        return score

    def _determine_quality_level(self, score: int) -> str:
        """确定质量等级"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "poor"

    def _create_quality_result(self, score: int, issues: List[str], suggestions: List[str], details: Dict = None) -> Dict:
        """创建质量检测结果"""
        return {
            "quality_score": score,
            "quality_passed": score >= settings.quality_threshold,
            "quality_level": self._determine_quality_level(score),
            "issues": issues,
            "suggestions": suggestions,
            "details": details or {}
        }

    def batch_analyze_texts(self, texts: List[str], text_type: str = "comment") -> List[Dict]:
        """批量分析文本质量"""
        return [self.analyze_text_quality(text, text_type) for text in texts]

    def get_quality_stats(self) -> Dict:
        """获取质量检测统计信息"""
        return {
            "threshold": settings.quality_threshold,
            "thought_words_count": len(self.thought_words),
            "emotion_words_count": len(self.emotion_words),
            "descriptive_words_count": len(self.descriptive_words)
        }