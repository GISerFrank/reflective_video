// src/pages/ReflectionListPage.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Select, Button, Empty, Space, Statistic, Tag } from 'antd';
import {
    EditOutlined,
    TrophyOutlined,
    FilterOutlined,
    PlusOutlined,
    CheckCircleOutlined,
    ClockCircleOutlined
} from '@ant-design/icons';
import {useReflectionStore, useVideoStore} from '../store';
import { useRouteNavigation } from '../hooks/useRouteNavigation';
// @ts-ignore
import { Loading, ErrorMessage, ReflectionCard, PageHeader } from '../components/ui';
import type {Reflection} from '../types';

const { Option } = Select;

const ReflectionListPage: React.FC = () => {
    const { error, fetchVideos } = useVideoStore();
    // 1. 先获取整个 reflection store 的状态
    const reflectionState = useReflectionStore();
    // 2. 从状态对象中安全地取出 reflections 数组，如果不是数组则提供一个空数组作为备用
    const reflections = Array.isArray(reflectionState.reflections) ? reflectionState.reflections : [];
    // 3. 同样从状态对象中获取 fetchReflections 函数
    const fetchReflections = reflectionState.fetchReflections;

    useEffect(() => {
        fetchVideos();
        fetchReflections();
    }, [fetchVideos, fetchReflections]);
    const { goToVideoList } = useRouteNavigation();

    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [sortBy, setSortBy] = useState<string>('newest');

    useEffect(() => {
        fetchReflections();
    }, [fetchReflections]);

    // 过滤和排序观后感
    const filteredReflections = reflections
        .filter(reflection => {
            if (statusFilter === 'all') return true;
            if (statusFilter === 'approved') return reflection.is_approved;
            if (statusFilter === 'pending') return !reflection.is_approved;
            return true;
        })
        .sort((a, b) => {
            switch (sortBy) {
                case 'newest':
                    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
                case 'oldest':
                    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
                case 'quality':
                    return b.quality_score - a.quality_score;
                default:
                    return 0;
            }
        });

    // 计算统计数据
    const totalReflections = reflections.length;
    const approvedReflections = reflections.filter(r => r.is_approved).length;
    const pendingReflections = totalReflections - approvedReflections;
    const averageQuality = reflections.length > 0
        ? reflections.reduce((sum, r) => sum + r.quality_score, 0) / reflections.length
        : 0;

    const handleReflectionClick = (reflection: Reflection) => {
        // 这里可以添加查看观后感详情的逻辑
        console.log('View reflection:', reflection);
    };

    return (
        <div className="space-y-6">
            <PageHeader
                title="我的观后感"
                subtitle={`共 ${totalReflections} 篇观后感`}
                extra={
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={goToVideoList}
                    >
                        写新观后感
                    </Button>
                }
            />

            <ErrorMessage error={error} />

            {/* 统计卡片 */}
            <Row gutter={[16, 16]}>
                <Col xs={24} sm={6}>
                    <Card>
                        <Statistic
                            title="总观后感"
                            value={totalReflections}
                            prefix={<EditOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={6}>
                    <Card>
                        <Statistic
                            title="已通过"
                            value={approvedReflections}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={6}>
                    <Card>
                        <Statistic
                            title="待审核"
                            value={pendingReflections}
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ color: '#faad14' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={6}>
                    <Card>
                        <Statistic
                            title="平均质量"
                            value={averageQuality.toFixed(1)}
                            prefix={<TrophyOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 筛选和排序 */}
            <Card size="small">
                <Row gutter={[16, 16]} align="middle">
                    <Col xs={24} sm={8}>
                        <Space>
                            <span>状态筛选：</span>
                            <Select
                                value={statusFilter}
                                onChange={setStatusFilter}
                                style={{ width: 120 }}
                            >
                                <Option value="all">全部</Option>
                                <Option value="approved">已通过</Option>
                                <Option value="pending">待审核</Option>
                            </Select>
                        </Space>
                    </Col>
                    <Col xs={24} sm={8}>
                        <Space>
                            <span>排序方式：</span>
                            <Select
                                value={sortBy}
                                onChange={setSortBy}
                                style={{ width: 120 }}
                            >
                                <Option value="newest">最新</Option>
                                <Option value="oldest">最早</Option>
                                <Option value="quality">质量分数</Option>
                            </Select>
                        </Space>
                    </Col>
                    <Col xs={24} sm={8}>
                        <div className="text-right text-sm text-gray-500">
                            显示 {filteredReflections.length} 篇观后感
                        </div>
                    </Col>
                </Row>
            </Card>

            {/* 观后感列表 */}
            {filteredReflections.length > 0 ? (
                <Row gutter={[24, 24]}>
                    {filteredReflections.map(reflection => (
                        <Col key={reflection.id} xs={24}>
                            <ReflectionCard
                                reflection={reflection}
                                onClick={() => handleReflectionClick(reflection)}
                            />
                        </Col>
                    ))}
                </Row>
            ) : (
                <Card>
                    <div className="text-center py-12">
                        {totalReflections === 0 ? (
                            <Empty
                                description="还没有写过观后感"
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                            >
                                <Button type="primary" icon={<PlusOutlined />} onClick={goToVideoList}>
                                    开始写观后感
                                </Button>
                            </Empty>
                        ) : (
                            <Empty
                                description="没有符合条件的观后感"
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                            >
                                <Button onClick={() => {
                                    setStatusFilter('all');
                                    setSortBy('newest');
                                }}>
                                    清除筛选条件
                                </Button>
                            </Empty>
                        )}
                    </div>
                </Card>
            )}

            {/* 成就展示 */}
            {totalReflections > 0 && (
                <Card title="我的成就">
                    <div className="flex flex-wrap gap-2">
                        {totalReflections >= 1 && (
                            <Tag color="blue" className="px-3 py-1">
                                🎉 首次写作
                            </Tag>
                        )}
                        {totalReflections >= 5 && (
                            <Tag color="green" className="px-3 py-1">
                                ✍️ 积极写作者
                            </Tag>
                        )}
                        {totalReflections >= 10 && (
                            <Tag color="purple" className="px-3 py-1">
                                📝 写作达人
                            </Tag>
                        )}
                        {approvedReflections >= 5 && (
                            <Tag color="gold" className="px-3 py-1">
                                ⭐ 质量保证
                            </Tag>
                        )}
                        {averageQuality >= 80 && (
                            <Tag color="red" className="px-3 py-1">
                                🏆 优秀作者
                            </Tag>
                        )}
                    </div>
                </Card>
            )}
        </div>
    );
};

export default ReflectionListPage;
