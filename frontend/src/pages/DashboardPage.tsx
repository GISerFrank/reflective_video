// src/pages/DashboardPage.tsx
import React, { useEffect } from 'react';
import { Row, Col, Card, Statistic, List, Avatar, Tag, Button } from 'antd';
import {
    VideoCameraOutlined,
    EditOutlined,
    TrophyOutlined,
    ClockCircleOutlined,
    UserOutlined,
    ArrowRightOutlined
} from '@ant-design/icons';
import { useVideoStore, useReflectionStore } from '../store';
import { useRouteNavigation } from '../hooks/useRouteNavigation';
// @ts-ignore
import { Loading, ErrorMessage } from '../components/ui';


const DashboardPage: React.FC = () => {
    const { videos, isLoading, error, fetchVideos } = useVideoStore();
    // 1. 先获取整个 reflection store 的状态
    const reflectionState = useReflectionStore();
    // 2. 从状态对象中安全地取出 reflections 数组，如果不是数组则提供一个空数组作为备用
    const reflections = Array.isArray(reflectionState.reflections) ? reflectionState.reflections : [];
    // 3. 同样从状态对象中获取 fetchReflections 函数
    const fetchReflections = reflectionState.fetchReflections;

    const { goToVideoList, goToReflectionList, goToVideoDetail } = useRouteNavigation();

    useEffect(() => {
        fetchVideos();
        fetchReflections();
    }, [fetchVideos, fetchReflections]);

    if (isLoading) {
        return <Loading tip="加载仪表板数据..." />;
    }

    // 计算统计数据
    const totalVideos = videos.length;
    const completedVideos = 0; // 这里需要根据用户进度计算
    const totalReflections = Array.isArray(reflections) ? reflections.length : 0;
    const approvedReflections = Array.isArray(reflections)
        ? reflections.filter(r => r.is_approved)
        : [];
    // 最近的视频
    const recentVideos = videos.slice(0, 3);

    // 最近的观后感
    const recentReflections = reflections.slice(0, 3);

    // @ts-ignore
    return (
        <div className="space-y-6">
            {/* 页面标题 */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">仪表板</h1>
                <p className="text-gray-600">欢迎回到智能视频学习平台</p>
            </div>

            <ErrorMessage error={error} />

            {/* 统计卡片 */}
            <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="总视频数"
                            value={totalVideos}
                            prefix={<VideoCameraOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="已完成视频"
                            value={completedVideos}
                            prefix={<TrophyOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                            suffix={`/ ${totalVideos}`}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="观后感总数"
                            value={totalReflections}
                            prefix={<EditOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="通过的观后感"
                            value={approvedReflections.length}
                            prefix={<TrophyOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                            suffix={`/ ${totalReflections}`}
                        />
                    </Card>
                </Col>
            </Row>

            <Row gutter={[24, 24]}>
                {/* 最近视频 */}
                <Col xs={24} lg={12}>
                    <Card
                        title="推荐视频"
                        extra={
                            <Button
                                type="link"
                                icon={<ArrowRightOutlined />}
                                onClick={goToVideoList}
                            >
                                查看全部
                            </Button>
                        }
                    >
                        {recentVideos.length > 0 ? (
                            <div className="space-y-4">
                                {recentVideos.map(video => (
                                    <div key={video.id} className="p-3 hover:bg-gray-50 rounded cursor-pointer">
                                        <div className="flex items-center space-x-3">
                                            <Avatar
                                                shape="square"
                                                size={64}
                                                src={video.thumbnail_url}
                                                icon={<VideoCameraOutlined />}
                                            />
                                            <div className="flex-1 min-w-0">
                                                <h4 className="font-medium truncate">{video.title}</h4>
                                                <p className="text-sm text-gray-500 truncate">{video.description}</p>
                                                <div className="flex items-center space-x-2 mt-1">
                                                    <Tag size="small">{video.category}</Tag>
                                                    <span className="text-xs text-gray-400 flex items-center">
                            <ClockCircleOutlined className="mr-1" />
                                                        {Math.floor(video.duration / 60)}分钟
                          </span>
                                                </div>
                                            </div>
                                            <Button
                                                type="primary"
                                                size="small"
                                                onClick={() => goToVideoDetail(video.id)}
                                            >
                                                观看
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                暂无视频
                            </div>
                        )}
                    </Card>
                </Col>

                {/* 最近观后感 */}
                <Col xs={24} lg={12}>
                    <Card
                        title="最近观后感"
                        extra={
                            <Button
                                type="link"
                                icon={<ArrowRightOutlined />}
                                onClick={goToReflectionList}
                            >
                                查看全部
                            </Button>
                        }
                    >
                        {recentReflections.length > 0 ? (
                            <List
                                dataSource={recentReflections}
                                renderItem={reflection => (
                                    <List.Item>
                                        <List.Item.Meta
                                            avatar={<Avatar icon={<UserOutlined />} />}
                                            title={
                                                <div className="flex items-center justify-between">
                                                    <span className="text-sm">视频 #{reflection.video_id}</span>
                                                    <div className="flex items-center space-x-2">
                                                        <Tag
                                                            color={reflection.is_approved ? 'green' : 'orange'}
                                                            size="small"
                                                        >
                                                            {reflection.is_approved ? '已通过' : '待审核'}
                                                        </Tag>
                                                        <span className="text-xs text-gray-400">
                              分数: {reflection.quality_score}
                            </span>
                                                    </div>
                                                </div>
                                            }
                                            description={
                                                <div>
                                                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                                        {reflection.content}
                                                    </p>
                                                    <span className="text-xs text-gray-400">
                            {new Date(reflection.created_at).toLocaleDateString()}
                          </span>
                                                </div>
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                还没有写过观后感
                            </div>
                        )}
                    </Card>
                </Col>
            </Row>

            {/* 快速操作 */}
            <Card title="快速操作">
                <Row gutter={[16, 16]}>
                    <Col xs={24} sm={8}>
                        <Button
                            type="primary"
                            size="large"
                            icon={<VideoCameraOutlined />}
                            onClick={goToVideoList}
                            block
                        >
                            开始学习
                        </Button>
                    </Col>
                    <Col xs={24} sm={8}>
                        <Button
                            size="large"
                            icon={<EditOutlined />}
                            onClick={goToReflectionList}
                            block
                        >
                            查看观后感
                        </Button>
                    </Col>
                    <Col xs={24} sm={8}>
                        <Button
                            size="large"
                            icon={<TrophyOutlined />}
                            block
                        >
                            学习成就
                        </Button>
                    </Col>
                </Row>
            </Card>
        </div>
    );
};

export default DashboardPage;