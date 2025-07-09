// src/pages/VideoListPage.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Input, Select, Button, Empty, Space } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';
import { useVideoStore } from '../store';
import { useRouteNavigation } from '../hooks/useRouteNavigation';
// @ts-ignore
import { Loading, ErrorMessage, VideoCard, PageHeader } from '../components/ui';

const { Search } = Input;
const { Option } = Select;

const VideoListPage: React.FC = () => {
    const { videos, isLoading, error, fetchVideos } = useVideoStore();
    const { goToVideoDetail } = useRouteNavigation();

    const [searchText, setSearchText] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

    useEffect(() => {
        fetchVideos();
    }, [fetchVideos]);

    // 获取所有分类
    const categories = Array.from(new Set(videos.map(video => video.category).filter(Boolean)));

    // 过滤视频
    const filteredVideos = videos.filter(video => {
        const matchesSearch = video.title.toLowerCase().includes(searchText.toLowerCase()) ||
            video.description.toLowerCase().includes(searchText.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || video.category === selectedCategory;
        const matchesDifficulty = selectedDifficulty === 'all' || video.difficulty_level === selectedDifficulty;

        return matchesSearch && matchesCategory && matchesDifficulty;
    });

    // 按顺序排序
    const sortedVideos = filteredVideos.sort((a, b) => a.order_index - b.order_index);

    if (isLoading) {
        return <Loading tip="加载视频列表..." />;
    }

    return (
        <div className="space-y-6">
            <PageHeader
                title="视频学习"
                subtitle={`共 ${videos.length} 个视频`}
            />

            <ErrorMessage error={error} />

            {/* 搜索和筛选 */}
            <div className="bg-white p-4 rounded-lg shadow-sm">
                <Space direction="vertical" size="middle" className="w-full">
                    <Row gutter={[16, 16]} align="middle">
                        <Col xs={24} md={8}>
                            <Search
                                placeholder="搜索视频标题或描述..."
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                onSearch={setSearchText}
                                enterButton={<SearchOutlined />}
                                allowClear
                            />
                        </Col>
                        <Col xs={12} md={4}>
                            <Select
                                value={selectedCategory}
                                onChange={setSelectedCategory}
                                placeholder="选择分类"
                                className="w-full"
                            >
                                <Option value="all">全部分类</Option>
                                {categories.map(category => (
                                    <Option key={category} value={category}>{category}</Option>
                                ))}
                            </Select>
                        </Col>
                        <Col xs={12} md={4}>
                            <Select
                                value={selectedDifficulty}
                                onChange={setSelectedDifficulty}
                                placeholder="选择难度"
                                className="w-full"
                            >
                                <Option value="all">全部难度</Option>
                                <Option value="beginner">入门</Option>
                                <Option value="intermediate">中级</Option>
                                <Option value="advanced">高级</Option>
                            </Select>
                        </Col>
                        <Col xs={24} md={8}>
                            <div className="text-sm text-gray-500">
                                找到 {filteredVideos.length} 个视频
                            </div>
                        </Col>
                    </Row>
                </Space>
            </div>

            {/* 视频列表 */}
            {sortedVideos.length > 0 ? (
                <Row gutter={[24, 24]}>
                    {sortedVideos.map(video => (
                        <Col key={video.id} xs={24} sm={12} lg={8} xl={6}>
                            <VideoCard
                                video={video}
                                onClick={() => goToVideoDetail(video.id)}
                            />
                        </Col>
                    ))}
                </Row>
            ) : (
                <div className="text-center py-12">
                    <Empty
                        description="没有找到符合条件的视频"
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    >
                        <Button type="primary" onClick={() => {
                            setSearchText('');
                            setSelectedCategory('all');
                            setSelectedDifficulty('all');
                        }}>
                            清除筛选条件
                        </Button>
                    </Empty>
                </div>
            )}
        </div>
    );
};

export default VideoListPage;