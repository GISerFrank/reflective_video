// src/utils/index.ts
// 工具函数集合

/**
 * 格式化时间戳为可读字符串
 */
export const formatDate = (date: string | Date, format: 'date' | 'datetime' | 'relative' = 'date'): string => {
    const d = new Date(date);

    if (format === 'relative') {
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

        if (diffInSeconds < 60) return '刚刚';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}分钟前`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}小时前`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}天前`;
        return d.toLocaleDateString('zh-CN');
    }

    if (format === 'datetime') {
        return d.toLocaleString('zh-CN');
    }

    return d.toLocaleDateString('zh-CN');
};

/**
 * 格式化视频时长（秒 -> HH:MM:SS 或 MM:SS）
 */
export const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * 防抖函数
 */
export const debounce = <T extends (...args: any[]) => any>(
    func: T,
    wait: number
): ((...args: Parameters<T>) => void) => {
    let timeout: NodeJS.Timeout;

    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};

/**
 * 节流函数
 */
export const throttle = <T extends (...args: any[]) => any>(
    func: T,
    limit: number
): ((...args: Parameters<T>) => void) => {
    let inThrottle: boolean;

    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

/**
 * 生成随机ID
 */
export const generateId = (): string => {
    return Math.random().toString(36).substr(2, 9);
};

/**
 * 深拷贝对象
 */
export const deepClone = <T>(obj: T): T => {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }

    if (obj instanceof Date) {
        return new Date(obj.getTime()) as unknown as T;
    }

    if (obj instanceof Array) {
        return obj.map(item => deepClone(item)) as unknown as T;
    }

    if (typeof obj === 'object') {
        const copy = {} as { [K in keyof T]: T[K] };
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                copy[key] = deepClone(obj[key]);
            }
        }
        return copy;
    }

    return obj;
};

/**
 * 检查是否为移动设备
 */
export const isMobile = (): boolean => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );
};

/**
 * 获取URL参数
 */
export const getUrlParams = (url?: string): Record<string, string> => {
    const params: Record<string, string> = {};
    const urlSearchParams = new URLSearchParams(url || window.location.search);

    for (const [key, value] of urlSearchParams) {
        params[key] = value;
    }

    return params;
};

/**
 * 设置URL参数
 */
export const setUrlParams = (params: Record<string, string>): void => {
    const url = new URL(window.location.href);

    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });

    window.history.replaceState({}, '', url.toString());
};

/**
 * 本地存储工具
 */
export const storage = {
    get: <T>(key: string, defaultValue?: T): T | null => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue || null;
        } catch {
            return defaultValue || null;
        }
    },

    set: <T>(key: string, value: T): void => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    },

    remove: (key: string): void => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
        }
    },

    clear: (): void => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Failed to clear localStorage:', error);
        }
    }
};

/**
 * 验证工具
 */
export const validation = {
    email: (email: string): boolean => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    phone: (phone: string): boolean => {
        const phoneRegex = /^1[3-9]\d{9}$/;
        return phoneRegex.test(phone);
    },

    password: (password: string): { valid: boolean; message?: string } => {
        if (password.length < 6) {
            return { valid: false, message: '密码长度至少6位' };
        }
        if (password.length > 20) {
            return { valid: false, message: '密码长度不能超过20位' };
        }
        return { valid: true };
    },

    required: (value: any): boolean => {
        if (typeof value === 'string') return value.trim().length > 0;
        if (Array.isArray(value)) return value.length > 0;
        return value !== null && value !== undefined;
    }
};