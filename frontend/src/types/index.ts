// src/types/index.ts
// 基于后端模型的TypeScript类型定义

export interface User {
    id: number;
    username: string;
    email: string;
    created_at: string;
}

export interface Video {
    id: number;
    title: string;
    description: string;
    duration: number; // 持续时间（秒）
    order_index: number;
    video_url: string;
    thumbnail_url: string;
    category: string;
    difficulty_level: 'beginner' | 'intermediate' | 'advanced';
    prerequisites?: string;
    is_published: boolean;
    is_free: boolean;
    created_at: string;
}

export interface UserProgress {
    id: number;
    user_id: number;
    video_id: number;
    completion_percentage: number;
    is_completed: boolean;
    last_watched_position: number;
    created_at: string;
    updated_at: string;
}

export interface Reflection {
    id: number;
    user_id: number;
    video_id: number;
    content: string;
    word_count: number;
    quality_score: number;
    has_thought_words: boolean;
    has_specific_examples: boolean;
    has_questions: boolean;
    is_approved: boolean;
    feedback?: string;
    created_at: string;
    reviewed_at?: string;
}

export interface Comment {
    id: number;
    user_id: number;
    content: string;
    word_count: number;
    similarity_score: number;
    original_score: number;
    quality_passed: boolean;
    quality_issues?: string;
    status: CommentStatus;
    reject_reason?: string;
    like_count: number;
    reply_count: number;
    parent_id?: number;
    created_at: string;
}

export enum CommentStatus {
    PENDING = 'pending',
    APPROVED = 'approved',
    REJECTED = 'rejected'
}

// API 请求/响应类型
export interface CreateReflectionRequest {
    content: string;
    video_id: number;
}

export interface ReflectionPreviewRequest {
    content: string;
    video_id: number;
}

export interface ReflectionPreviewResponse {
    valid: boolean;
    error?: string;
    quality_result?: {
        quality_score: number;
        quality_passed: boolean;
    };
    predicted_approval: boolean;
}

export interface CreateCommentRequest {
    content: string;
    parent_id?: number;
}

export interface SimilarityCheckRequest {
    content: string;
}

export interface SimilarityCheckResponse {
    similarity_score: number;
    original_score: number;
    quality_passed: boolean;
    quality_issues?: string;
    recommendation: string;
}

// 组件状态类型
export interface VideoWithProgress {
    video: Video;
    progress?: UserProgress;
    stats: {
        total_viewers: number;
        completed_viewers: number;
        avg_progress: number;
        reflection_count: number;
        comment_count: number;
    };
    next_video?: Video;
    prev_video?: Video;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

// 全局状态类型
export interface AppState {
    user: User | null;
    currentVideo: VideoWithProgress | null;
    isLoading: boolean;
    error: string | null;
}

export interface VideoState {
    videos: Video[];
    currentVideo: VideoWithProgress | null;
    isLoading: boolean;
    error: string | null;
}

export interface ReflectionState {
    reflections: Reflection[];
    currentReflection: Reflection | null;
    isSubmitting: boolean;
    previewResult: ReflectionPreviewResponse | null;
    error: string | null;
}

export interface CommentState {
    comments: Comment[];
    isSubmitting: boolean;
    similarityResult: SimilarityCheckResponse | null;
    error: string | null;
}