// src/hooks/useVideoProgress.ts
import { useState, useEffect, useCallback } from 'react';
import { useVideoStore, useUserStore } from '../store';

interface VideoProgressHook {
    currentTime: number;
    duration: number;
    progress: number;
    isPlaying: boolean;
    updateProgress: (time: number, total: number) => void;
    saveProgress: () => void;
}

export const useVideoProgress = (videoId: number): VideoProgressHook => {
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const { updateProgress: updateVideoProgress } = useVideoStore();
    const { user } = useUserStore();

    const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

    const updateProgress = useCallback((time: number, total: number) => {
        setCurrentTime(time);
        setDuration(total);
    }, []);

    const saveProgress = useCallback(() => {
        if (user && progress > 0) {
            updateVideoProgress(videoId, user.id, Math.floor(progress));
        }
    }, [user, videoId, progress, updateVideoProgress]);

    // 自动保存进度（每30秒或进度变化超过5%时）
    useEffect(() => {
        const interval = setInterval(() => {
            if (isPlaying) {
                saveProgress();
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [isPlaying, saveProgress]);

    return {
        currentTime,
        duration,
        progress,
        isPlaying,
        updateProgress,
        saveProgress,
    };
};