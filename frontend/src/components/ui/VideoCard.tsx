// src/components/ui/VideoCard.tsx
import React from 'react';
import { Card, Tag, Progress } from 'antd';
import { PlayCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import type {Video, UserProgress} from '../../types';

const { Meta } = Card;

interface VideoCardProps {
    video: Video;
    progress?: UserProgress;
    onClick?: () => void;
}

const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const getDifficultyColor = (level: string) => {
    switch (level) {
        case 'beginner': return 'green';
        case 'intermediate': return 'orange';
        case 'advanced': return 'red';
        default: return 'blue';
    }
};

export const VideoCard: React.FC<VideoCardProps> = ({ video, progress, onClick }) => {
    return (
        <Card
            hoverable
            className="w-full"
            cover={
                <div className="relative">
                    <img
                        alt={video.title}
                        src={video.thumbnail_url || '/placeholder-video.jpg'}
                        className="h-48 w-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
                        <PlayCircleOutlined className="text-white text-4xl opacity-0 hover:opacity-100 transition-opacity duration-200" />
                    </div>
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-sm flex items-center">
                        <ClockCircleOutlined className="mr-1" />
                        {formatDuration(video.duration)}
                    </div>
                </div>
            }
            actions={[
                <div key="difficulty" className="px-4">
                    <Tag color={getDifficultyColor(video.difficulty_level)}>
                        {video.difficulty_level}
                    </Tag>
                </div>,
                <div key="category" className="px-4">
                    <Tag>{video.category}</Tag>
                </div>
            ]}
            onClick={onClick}
        >
            <Meta
                title={
                    <div className="flex items-center justify-between">
                        <span className="text-lg font-semibold truncate">{video.title}</span>
                        <span className="text-sm text-gray-500 ml-2">#{video.order_index}</span>
                    </div>
                }
                description={
                    <div>
                        <p className="text-gray-600 mb-3 line-clamp-2">{video.description}</p>
                        {progress && (
                            <div>
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-500">学习进度</span>
                                    <span className="text-sm font-medium">{progress.completion_percentage}%</span>
                                </div>
                                <Progress
                                    percent={progress.completion_percentage}
                                    size="small"
                                    status={progress.is_completed ? 'success' : 'active'}
                                />
                            </div>
                        )}
                    </div>
                }
            />
        </Card>
    );
};