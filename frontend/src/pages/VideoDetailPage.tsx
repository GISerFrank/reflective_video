// src/pages/VideoDetailPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Row, Col, Card, Button, Progress, Tag, Space, Statistic, Divider, message } from 'antd';
import {
    PlayCircleOutlined,
    EditOutlined,
    ClockCircleOutlined,
    UserOutlined,
    TrophyOutlined,
    ArrowLeftOutlined,
    ArrowRightOutlined
} from '@ant-design/icons';
import { useVideoStore, useUserStore } from '../store';
import { useRouteNavigation } from '../hooks/useRouteNavigation';
// @ts-ignore
import { Loading, ErrorMessage, VideoPlayer, PageHeader } from '../components/ui';

const VideoDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { user } = useUserStore();
    const {
        currentVideo,
        isLoading,
        error,
        fetchVideoWithProgress,
        updateProgress
    } = useVideoStore();
    const { goToReflection, goToVideoDetail, goBack } = useRouteNavigation();

    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);

    useEffect(() => {
        if (id && user) {
            fetchVideoWithProgress(parseInt(id), user.id);
        }
    }, [id, user, fetchVideoWithProgress]);

    // 处理视频进度更新
    const handleVideoProgress = (time: number, totalDuration: number) => {
        setCurrentTime(time);
        setDuration(totalDuration);

        if (totalDuration > 0 && user && currentVideo) {
            const percentage = Math.floor((time / totalDuration) * 100);
            // 每10%更新一次进度
            if (percentage % 10 === 0 && percentage > (currentVideo.progress?.completion_percentage || 0)) {
                updateProgress(currentVideo.video.id, user.id, percentage);
            }
        }
    };

    // 处理视频播放完成
    const handleVideoEnded = () => {
        if (user && currentVideo) {
            updateProgress(currentVideo.video.id, user.id, 100);
            message.success('恭喜完成视频学习！现在可以写观后感了。');
        }
    };

    const formatDuration = (seconds: number): string => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);

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

    if (isLoading) {
        return <Loading tip="加载视频详情..." />;
    }

    if (!currentVideo) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">视频未找到</h2>
                <Button type="primary" onClick={goBack}>返回视频列表</Button>
            </div>
        );
    }

    const { video, progress, stats, next_video, prev_video } = currentVideo;
    const canWriteReflection = progress && progress.completion_percentage >= 50;

    return (
        <div className="space-y-6">
            <PageHeader
                title={video.title}
                breadcrumbs={[
                    { title: '视频学习', path: '/videos' },
                    { title: video.title }
                ]}
                extra={
                    <Space>
                        {prev_video && (
                            <Button
                                icon={<ArrowLeftOutlined />}
                                onClick={() => goToVideoDetail(prev_video.id)}
                            >
                                上一个
                            </Button>
                        )}
                        {next_video && (
                            <Button
                                type="primary"
                                icon={<ArrowRightOutlined />}
                                onClick={() => goToVideoDetail(next_video.id)}
                            >
                                下一个
                            </Button>
                        )}
                    </Space>
                }
            />

            <ErrorMessage error={error} />

            <Row gutter={[24, 24]}>
                {/* 左侧：视频播放器和信息 */}
                <Col xs={24} lg={16}>
                    <Card className="mb-6">
                        <VideoPlayer
                            src={video.video_url}
                            onProgress={handleVideoProgress}
                            onEnded={handleVideoEnded}
                            startTime={progress?.last_watched_position || 0}
                        />
                    </Card>

                    <Card title="视频信息">
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-xl font-semibold mb-2">{video.title}</h3>
                                <p className="text-gray-600 leading-relaxed">{video.description}</p>
                            </div>

                            <div className="flex flex-wrap gap-2">
                                <Tag color={getDifficultyColor(video.difficulty_level)}>
                                    {video.difficulty_level}
                                </Tag>
                                <Tag>{video.category}</Tag>
                                <Tag icon={<ClockCircleOutlined />}>
                                    {formatDuration(video.duration)}
                                </Tag>
                                <Tag>#{video.order_index}</Tag>
                            </div>

                            {video.prerequisites && (
                                <div>
                                    <h4 className="font-medium mb-2">前置要求：</h4>
                                    <p className="text-gray-600">{video.prerequisites}</p>
                                </div>
                            )}

                            <Divider />

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Statistic
                                    title="观看人数"
                                    value={stats.total_viewers}
                                    prefix={<UserOutlined />}
                                />
                                <Statistic
                                    title="完成人数"
                                    value={stats.completed_viewers}
                                    prefix={<TrophyOutlined />}
                                />
                                <Statistic
                                    title="平均进度"
                                    value={stats.avg_progress}
                                    suffix="%"
                                />
                                <Statistic
                                    title="观后感数"
                                    value={stats.reflection_count}
                                    prefix={<EditOutlined />}
                                />
                            </div>
                        </div>
                    </Card>
                </Col>

                {/* 右侧：学习进度和操作 */}
                <Col xs={24} lg={8}>
                    <Card title="学习进度" className="mb-6">
                        {progress ? (
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <span>观看进度</span>
                                        <span className="font-medium">{progress.completion_percentage}%</span>
                                    </div>
                                    <Progress
                                        percent={progress.completion_percentage}
                                        status={progress.is_completed ? 'success' : 'active'}
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <span>当前播放时间</span>
                                        <span>{formatDuration(currentTime)} / {formatDuration(duration)}</span>
                                    </div>
                                    <Progress
                                        percent={duration > 0 ? (currentTime / duration) * 100 : 0}
                                        showInfo={false}
                                        size="small"
                                    />
                                </div>

                                <div className="text-sm text-gray-500">
                                    开始学习时间：{new Date(progress.created_at).toLocaleDateString()}
                                    {progress.updated_at !== progress.created_at && (
                                        <div>
                                            最近更新：{new Date(progress.updated_at).toLocaleDateString()}
                                        </div>
                                    )}
                                </div>

                                {progress.is_completed && (
                                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                        <div className="flex items-center text-green-700">
                                            <TrophyOutlined className="mr-2" />
                                            <span className="font-medium">恭喜完成学习！</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-6">
                                <PlayCircleOutlined className="text-4xl text-gray-400 mb-2" />
                                <p className="text-gray-500">开始观看视频</p>
                            </div>
                        )}
                    </Card>

                    <Card title="学习操作">
                        <Space direction="vertical" className="w-full">
                            <Button
                                type="primary"
                                icon={<EditOutlined />}
                                disabled={!canWriteReflection}
                                onClick={() => goToReflection(video.id)}
                                block
                            >
                                写观后感
                            </Button>

                            {!canWriteReflection && (
                                <div className="text-sm text-gray-500 text-center">
                                    需要观看至少50%才能写观后感
                                </div>
                            )}

                            <Button block>
                                查看其他观后感
                            </Button>

                            <Button block>
                                添加笔记
                            </Button>
                        </Space>
                    </Card>

                    {/* 学习建议 */}
                    <Card title="学习建议" className="mt-6">
                        <div className="space-y-3 text-sm">
                            <div className="flex items-start space-x-2">
                                <span className="text-blue-600">💡</span>
                                <span>建议多次观看重点内容</span>
                            </div>
                            <div className="flex items-start space-x-2">
                                <span className="text-green-600">✅</span>
                                <span>完成观看后及时写观后感</span>
                            </div>
                            <div className="flex items-start space-x-2">
                                <span className="text-purple-600">🤔</span>
                                <span>思考视频中的关键问题</span>
                            </div>
                        </div>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default VideoDetailPage;
