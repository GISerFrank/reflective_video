// src/store/index.ts
// Zustand 状态管理

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
    User,
    Video,
    VideoWithProgress,
    Reflection,
    Comment,
    ReflectionPreviewResponse,
    SimilarityCheckResponse
} from '../types';
import { videoApi, reflectionApi, commentApi } from '../services/api';

// 用户状态管理
interface UserState {
    user: User | null;
    isAuthenticated: boolean;
    setUser: (user: User | null) => void;
    logout: () => void;
}

export const useUserStore = create<UserState>()(
    persist(
        devtools((set) => ({
            user: null,
            isAuthenticated: false,
            setUser: (user) => set({
                user,
                isAuthenticated: !!user
            }, false, 'setUser'),
            logout: () => set({
                user: null,
                isAuthenticated: false
            }, false, 'logout'),
        })),
        { name: 'user-storage' }
    )
);

// 视频状态管理
interface VideoState {
    videos: Video[];
    currentVideo: VideoWithProgress | null;
    isLoading: boolean;
    error: string | null;
    fetchVideos: () => Promise<void>;
    fetchVideoWithProgress: (videoId: number, userId: number) => Promise<void>;
    updateProgress: (videoId: number, userId: number, progress: number) => Promise<void>;
    setCurrentVideo: (video: VideoWithProgress | null) => void;
    clearError: () => void;
}

export const useVideoStore = create<VideoState>()(
    devtools((set, get) => ({
        videos: [],
        currentVideo: null,
        isLoading: false,
        error: null,

        fetchVideos: async () => {
            set({ isLoading: true, error: null }, false, 'fetchVideos:start');
            try {
                const response = await videoApi.getAll();
                if (response.success && response.data) {
                    set({
                        videos: response.data,
                        isLoading: false
                    }, false, 'fetchVideos:success');
                } else {
                    set({
                        error: response.error || '获取视频列表失败',
                        isLoading: false
                    }, false, 'fetchVideos:error');
                }
            } catch (error) {
                set({
                    error: '网络错误',
                    isLoading: false
                }, false, 'fetchVideos:catch');
            }
        },

        fetchVideoWithProgress: async (videoId: number, userId: number) => {
            set({ isLoading: true, error: null }, false, 'fetchVideoWithProgress:start');
            try {
                const response = await videoApi.getWithProgress(videoId, userId);
                if (response.success && response.data) {
                    set({
                        currentVideo: response.data,
                        isLoading: false
                    }, false, 'fetchVideoWithProgress:success');
                } else {
                    set({
                        error: response.error || '获取视频详情失败',
                        isLoading: false
                    }, false, 'fetchVideoWithProgress:error');
                }
            } catch (error) {
                set({
                    error: '网络错误',
                    isLoading: false
                }, false, 'fetchVideoWithProgress:catch');
            }
        },

        updateProgress: async (videoId: number, userId: number, progress: number) => {
            try {
                const response = await videoApi.updateProgress(videoId, userId, progress);
                if (response.success) {
                    // 更新当前视频的进度
                    const { currentVideo } = get();
                    if (currentVideo && currentVideo.video.id === videoId && currentVideo.progress) {
                        set({
                            currentVideo: {
                                ...currentVideo,
                                progress: {
                                    ...currentVideo.progress, // <-- 安全地扩展
                                    completion_percentage: progress,
                                    is_completed: progress >= 100,
                                }
                            }
                        }, false, 'updateProgress:success');
                    }
                }
            } catch (error) {
                console.error('Update progress failed:', error);
            }
        },

        setCurrentVideo: (video) => set({ currentVideo: video }, false, 'setCurrentVideo'),
        clearError: () => set({ error: null }, false, 'clearError'),
    }))
);

// 观后感状态管理
interface ReflectionState {
    reflections: Reflection[];
    currentReflection: Reflection | null;
    isSubmitting: boolean;
    previewResult: ReflectionPreviewResponse | null;
    error: string | null;
    fetchReflections: (videoId?: number) => Promise<void>;
    createReflection: (content: string, videoId: number) => Promise<boolean>;
    previewReflection: (content: string, videoId: number) => Promise<void>;
    clearPreview: () => void;
    clearError: () => void;
}

export const useReflectionStore = create<ReflectionState>()(
    devtools((set, get) => ({
        reflections: [],
        currentReflection: null,
        isSubmitting: false,
        previewResult: null,
        error: null,

        fetchReflections: async (videoId?: number) => {
            try {
                const response = await reflectionApi.getAll(videoId);
                if (response.success && response.data) {
                    set({ reflections: response.data }, false, 'fetchReflections:success');
                } else {
                    set({ error: response.error || '获取观后感失败' , reflections: []}, false, 'fetchReflections:error');
                }
            } catch (error) {
                set({ error: '网络错误' }, false, 'fetchReflections:catch');
            }
        },

        createReflection: async (content: string, videoId: number): Promise<boolean> => {
            set({ isSubmitting: true, error: null }, false, 'createReflection:start');
            try {
                const response = await reflectionApi.create({ content, video_id: videoId });
                if (response.success && response.data) {
                    const { reflections } = get();
                    set({
                        reflections: [response.data, ...reflections],
                        currentReflection: response.data,
                        isSubmitting: false,
                        previewResult: null
                    }, false, 'createReflection:success');
                    return true;
                } else {
                    set({
                        error: response.error || '提交观后感失败',
                        isSubmitting: false
                    }, false, 'createReflection:error');
                    return false;
                }
            } catch (error) {
                set({
                    error: '网络错误',
                    isSubmitting: false
                }, false, 'createReflection:catch');
                return false;
            }
        },

        previewReflection: async (content: string, videoId: number) => {
            try {
                const response = await reflectionApi.preview({ content, video_id: videoId });
                if (response.success && response.data) {
                    set({ previewResult: response.data }, false, 'previewReflection:success');
                } else {
                    set({ error: response.error || '预检测失败' }, false, 'previewReflection:error');
                }
            } catch (error) {
                set({ error: '网络错误' }, false, 'previewReflection:catch');
            }
        },

        clearPreview: () => set({ previewResult: null }, false, 'clearPreview'),
        clearError: () => set({ error: null }, false, 'clearError'),
    }))
);

// 评论状态管理
interface CommentState {
    comments: Comment[];
    isSubmitting: boolean;
    similarityResult: SimilarityCheckResponse | null;
    error: string | null;
    fetchComments: () => Promise<void>;
    createComment: (content: string, parentId?: number) => Promise<boolean>;
    checkSimilarity: (content: string) => Promise<void>;
    clearSimilarityResult: () => void;
    clearError: () => void;
}

export const useCommentStore = create<CommentState>()(
    devtools((set, get) => ({
        comments: [],
        isSubmitting: false,
        similarityResult: null,
        error: null,

        fetchComments: async () => {
            try {
                const response = await commentApi.getAll();
                if (response.success && response.data) {
                    set({ comments: response.data }, false, 'fetchComments:success');
                } else {
                    set({ error: response.error || '获取评论失败' }, false, 'fetchComments:error');
                }
            } catch (error) {
                set({ error: '网络错误' }, false, 'fetchComments:catch');
            }
        },

        createComment: async (content: string, parentId?: number): Promise<boolean> => {
            set({ isSubmitting: true, error: null }, false, 'createComment:start');
            try {
                const response = await commentApi.create({ content, parent_id: parentId });
                if (response.success && response.data) {
                    const { comments } = get();
                    set({
                        comments: [response.data, ...comments],
                        isSubmitting: false,
                        similarityResult: null
                    }, false, 'createComment:success');
                    return true;
                } else {
                    set({
                        error: response.error || '提交评论失败',
                        isSubmitting: false
                    }, false, 'createComment:error');
                    return false;
                }
            } catch (error) {
                set({
                    error: '网络错误',
                    isSubmitting: false
                }, false, 'createComment:catch');
                return false;
            }
        },

        checkSimilarity: async (content: string) => {
            try {
                const response = await commentApi.checkSimilarity({ content });
                if (response.success && response.data) {
                    set({ similarityResult: response.data }, false, 'checkSimilarity:success');
                } else {
                    set({ error: response.error || '相似度检测失败' }, false, 'checkSimilarity:error');
                }
            } catch (error) {
                set({ error: '网络错误' }, false, 'checkSimilarity:catch');
            }
        },

        clearSimilarityResult: () => set({ similarityResult: null }, false, 'clearSimilarityResult'),
        clearError: () => set({ error: null }, false, 'clearError'),
    }))
);

// 全局状态（用于跨组件通信）
interface GlobalState {
    sidebarCollapsed: boolean;
    theme: 'light' | 'dark';
    toggleSidebar: () => void;
    toggleTheme: () => void;
}

export const useGlobalStore = create<GlobalState>()(
    persist(
        devtools((set) => ({
            sidebarCollapsed: false,
            theme: 'light',
            toggleSidebar: () => set((state) => ({
                sidebarCollapsed: !state.sidebarCollapsed
            }), false, 'toggleSidebar'),
            toggleTheme: () => set((state) => ({
                theme: state.theme === 'light' ? 'dark' : 'light'
            }), false, 'toggleTheme'),
        })),
        { name: 'global-settings' }
    )
);