// src/services/api.ts
// API 服务层 - 与后端 FastAPI 通信

// src/services/api.ts
// API 服务层 - 与后端 FastAPI 通信
import type {
    Video,
    VideoWithProgress,
    Reflection,
    Comment,
    CreateReflectionRequest,
    ReflectionPreviewRequest,
    ReflectionPreviewResponse,
    CreateCommentRequest,
    SimilarityCheckRequest,
    SimilarityCheckResponse,
    ApiResponse
} from '../types';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
        const url = `${this.baseURL}${endpoint}`;

        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return {
                success: true,
                data: data,
            };
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            return {
                success: false,
                error: error instanceof Error ? error.message : '未知错误',
            };
        }
    }

    // 健康检查
    async healthCheck(): Promise<ApiResponse<{ status: string; message: string }>> {
        return this.request('/health');
    }

    // 视频相关API
    async getVideos(): Promise<ApiResponse<Video[]>> {
        return this.request('/api/videos/');
    }

    async getVideoWithProgress(
        videoId: number,
        userId: number
    ): Promise<ApiResponse<VideoWithProgress>> {
        return this.request(`/api/videos/${videoId}/progress?user_id=${userId}`);
    }

    async updateVideoProgress(
        videoId: number,
        userId: number,
        completionPercentage: number
    ): Promise<ApiResponse<any>> {
        return this.request(`/api/videos/${videoId}/progress`, {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                completion_percentage: completionPercentage,
            }),
        });
    }

    // 观后感相关API
    async getReflections(videoId?: number): Promise<ApiResponse<Reflection[]>> {
        const endpoint = videoId
            ? `/api/reflections/?video_id=${videoId}`
            : '/api/reflections/';
        return this.request(endpoint);
    }

    async createReflection(
        reflection: CreateReflectionRequest
    ): Promise<ApiResponse<Reflection>> {
        return this.request('/api/reflections/', {
            method: 'POST',
            body: JSON.stringify(reflection),
        });
    }

    async previewReflection(
        request: ReflectionPreviewRequest
    ): Promise<ApiResponse<ReflectionPreviewResponse>> {
        return this.request('/api/reflections/preview', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async getReflectionStats(): Promise<ApiResponse<{
        total_reflections: number;
        approved_reflections: number;
        approval_rate: number;
    }>> {
        return this.request('/api/reflections/stats/overview');
    }

    async getFeaturedReflections(): Promise<ApiResponse<{
        featured_reflections: Reflection[];
        count: number;
        message?: string;
    }>> {
        return this.request('/api/reflections/featured/top');
    }

    // 评论相关API
    async getComments(): Promise<ApiResponse<Comment[]>> {
        return this.request('/api/comments/');
    }

    async createComment(
        comment: CreateCommentRequest
    ): Promise<ApiResponse<Comment>> {
        return this.request('/api/comments/', {
            method: 'POST',
            body: JSON.stringify(comment),
        });
    }

    async previewComment(content: string): Promise<ApiResponse<any>> {
        return this.request('/api/comments/preview', {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    }

    async checkSimilarity(
        request: SimilarityCheckRequest
    ): Promise<ApiResponse<SimilarityCheckResponse>> {
        return this.request('/api/comments/similarity/test', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }
}

// 创建API客户端实例
export const apiClient = new ApiClient();

// 导出具体的API函数，便于在组件中使用
export const videoApi = {
    getAll: () => apiClient.getVideos(),
    getWithProgress: (videoId: number, userId: number) =>
        apiClient.getVideoWithProgress(videoId, userId),
    updateProgress: (videoId: number, userId: number, progress: number) =>
        apiClient.updateVideoProgress(videoId, userId, progress),
};

export const reflectionApi = {
    getAll: (videoId?: number) => apiClient.getReflections(videoId),
    create: (reflection: CreateReflectionRequest) =>
        apiClient.createReflection(reflection),
    preview: (request: ReflectionPreviewRequest) =>
        apiClient.previewReflection(request),
    getStats: () => apiClient.getReflectionStats(),
    getFeatured: () => apiClient.getFeaturedReflections(),
};

export const commentApi = {
    getAll: () => apiClient.getComments(),
    create: (comment: CreateCommentRequest) => apiClient.createComment(comment),
    preview: (content: string) => apiClient.previewComment(content),
    checkSimilarity: (request: SimilarityCheckRequest) =>
        apiClient.checkSimilarity(request),
};

export default apiClient;