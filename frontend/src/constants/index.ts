// src/constants/index.ts
// 应用常量定义

// API 相关常量
export const API_ENDPOINTS = {
    BASE_URL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
    VIDEOS: '/api/videos',
    REFLECTIONS: '/api/reflections',
    COMMENTS: '/api/comments',
    HEALTH: '/health',
} as const;

// 应用配置
export const APP_CONFIG = {
    NAME: 'Smart Video Platform',
    VERSION: '1.0.0',
    DESCRIPTION: '智能视频学习平台',

    // 分页配置
    PAGE_SIZE: 20,

    // 文件上传限制
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_FILE_TYPES: ['mp4', 'webm', 'ogg'],

    // 观后感配置
    REFLECTION: {
        MIN_LENGTH: 50,
        MAX_LENGTH: 2000,
        REQUIRED_WATCH_PERCENTAGE: 50,
    },

    // 评论配置
    COMMENT: {
        MIN_LENGTH: 10,
        MAX_LENGTH: 500,
    },

    // 本地存储键名
    STORAGE_KEYS: {
        USER: 'svp_user',
        SETTINGS: 'svp_settings',
        THEME: 'svp_theme',
    },
} as const;

// 视频难度级别
export const DIFFICULTY_LEVELS = {
    BEGINNER: 'beginner',
    INTERMEDIATE: 'intermediate',
    ADVANCED: 'advanced',
} as const;

export const DIFFICULTY_LABELS = {
    [DIFFICULTY_LEVELS.BEGINNER]: '入门',
    [DIFFICULTY_LEVELS.INTERMEDIATE]: '中级',
    [DIFFICULTY_LEVELS.ADVANCED]: '高级',
} as const;

export const DIFFICULTY_COLORS = {
    [DIFFICULTY_LEVELS.BEGINNER]: 'green',
    [DIFFICULTY_LEVELS.INTERMEDIATE]: 'orange',
    [DIFFICULTY_LEVELS.ADVANCED]: 'red',
} as const;

// 评论状态
export const COMMENT_STATUS = {
    PENDING: 'pending',
    APPROVED: 'approved',
    REJECTED: 'rejected',
} as const;

export const COMMENT_STATUS_LABELS = {
    [COMMENT_STATUS.PENDING]: '待审核',
    [COMMENT_STATUS.APPROVED]: '已通过',
    [COMMENT_STATUS.REJECTED]: '已拒绝',
} as const;

export const COMMENT_STATUS_COLORS = {
    [COMMENT_STATUS.PENDING]: 'orange',
    [COMMENT_STATUS.APPROVED]: 'green',
    [COMMENT_STATUS.REJECTED]: 'red',
} as const;

// 质量分数等级
export const QUALITY_LEVELS = {
    EXCELLENT: 90,
    GOOD: 80,
    FAIR: 60,
    POOR: 0,
} as const;

export const QUALITY_LABELS = {
    [QUALITY_LEVELS.EXCELLENT]: '优秀',
    [QUALITY_LEVELS.GOOD]: '良好',
    [QUALITY_LEVELS.FAIR]: '一般',
    [QUALITY_LEVELS.POOR]: '需改进',
} as const;

export const QUALITY_COLORS = {
    [QUALITY_LEVELS.EXCELLENT]: 'green',
    [QUALITY_LEVELS.GOOD]: 'blue',
    [QUALITY_LEVELS.FAIR]: 'orange',
    [QUALITY_LEVELS.POOR]: 'red',
} as const;

// 路由路径
export const ROUTES = {
    HOME: '/',
    DASHBOARD: '/dashboard',
    VIDEOS: '/videos',
    VIDEO_DETAIL: '/videos/:id',
    REFLECTION: '/videos/:id/reflection',
    REFLECTIONS: '/reflections',
    PROFILE: '/profile',
    SETTINGS: '/settings',
} as const;

// 错误消息
export const ERROR_MESSAGES = {
    NETWORK_ERROR: '网络连接失败，请检查网络设置',
    SERVER_ERROR: '服务器错误，请稍后重试',
    UNAUTHORIZED: '用户未授权，请重新登录',
    NOT_FOUND: '请求的资源不存在',
    VALIDATION_ERROR: '数据验证失败',
    UNKNOWN_ERROR: '未知错误，请联系技术支持',
} as const;

// 成功消息
export const SUCCESS_MESSAGES = {
    REFLECTION_CREATED: '观后感提交成功！',
    COMMENT_CREATED: '评论发布成功！',
    PROGRESS_UPDATED: '学习进度已更新',
    PROFILE_UPDATED: '个人资料更新成功',
} as const;