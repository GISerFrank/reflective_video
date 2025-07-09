// src/components/ui/VideoPlayer.tsx
import React, { useRef, useEffect } from 'react';
import { message } from 'antd';

interface VideoPlayerProps {
    src: string;
    onProgress?: (currentTime: number, duration: number) => void;
    onEnded?: () => void;
    startTime?: number;
    className?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
                                                            src,
                                                            onProgress,
                                                            onEnded,
                                                            startTime = 0,
                                                            className = ''
                                                        }) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        // 设置起始时间
        if (startTime > 0) {
            video.currentTime = startTime;
        }

        const handleTimeUpdate = () => {
            if (onProgress) {
                onProgress(video.currentTime, video.duration);
            }
        };

        const handleEnded = () => {
            message.success('视频播放完成！');
            if (onEnded) {
                onEnded();
            }
        };

        const handleError = () => {
            message.error('视频加载失败，请刷新页面重试');
        };

        video.addEventListener('timeupdate', handleTimeUpdate);
        video.addEventListener('ended', handleEnded);
        video.addEventListener('error', handleError);

        return () => {
            video.removeEventListener('timeupdate', handleTimeUpdate);
            video.removeEventListener('ended', handleEnded);
            video.removeEventListener('error', handleError);
        };
    }, [onProgress, onEnded, startTime]);

    return (
        <video
            ref={videoRef}
            src={src}
            controls
            className={`w-full h-auto rounded-lg shadow-lg ${className}`}
            preload="metadata"
        >
            您的浏览器不支持视频播放。
        </video>
    );
};