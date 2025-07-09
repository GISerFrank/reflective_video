// src/pages/ProfilePage.tsx
import React, {useEffect} from 'react';
import { Card, Row, Col, Avatar, Descriptions, Button, Progress, Tag } from 'antd';
import { UserOutlined, EditOutlined, SettingOutlined } from '@ant-design/icons';
import { useUserStore, useVideoStore, useReflectionStore } from '../store';
// @ts-ignore
import { PageHeader } from '../components/ui';

const ProfilePage: React.FC = () => {
    const { user } = useUserStore();
    const { videos } = useVideoStore();

    const reflectionState = useReflectionStore();
    // 2. 从状态对象中安全地取出 reflections 数组，如果不是数组则提供一个空数组作为备用
    const reflections = Array.isArray(reflectionState.reflections) ? reflectionState.reflections : [];

    // 计算学习统计
    const totalVideos = videos.length;
    const completedVideos = 0; // 这里需要根据实际进度计算
    const totalReflections = reflections.length;
    const approvedReflections = reflections.filter(r => r.is_approved).length;

    return (
        <div className="space-y-6">
            <PageHeader title="个人资料" />

            <Row gutter={[24, 24]}>
                <Col xs={24} lg={8}>
                    <Card title="基本信息">
                        <div className="text-center mb-6">
                            <Avatar size={100} icon={<UserOutlined />} className="mb-4" />
                            <h3 className="text-xl font-semibold">{user?.username || '用户'}</h3>
                            <p className="text-gray-500">{user?.email || 'user@example.com'}</p>
                        </div>

                        <Descriptions column={1} size="small">
                            <Descriptions.Item label="用户ID">
                                {user?.id || 1}
                            </Descriptions.Item>
                            <Descriptions.Item label="注册时间">
                                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '2024-01-01'}
                            </Descriptions.Item>
                            <Descriptions.Item label="学习等级">
                                <Tag color="blue">初学者</Tag>
                            </Descriptions.Item>
                        </Descriptions>

                        <div className="mt-6 space-y-2">
                            <Button icon={<EditOutlined />} block>
                                编辑资料
                            </Button>
                            <Button icon={<SettingOutlined />} block>
                                账户设置
                            </Button>
                        </div>
                    </Card>
                </Col>

                <Col xs={24} lg={16}>
                    <div className="space-y-6">
                        {/* 学习统计 */}
                        <Card title="学习统计">
                            <Row gutter={[16, 16]}>
                                <Col xs={24} sm={12}>
                                    <div className="text-center p-4">
                                        <div className="text-2xl font-bold text-blue-600">{totalVideos}</div>
                                        <div className="text-gray-500">可学习视频</div>
                                    </div>
                                </Col>
                                <Col xs={24} sm={12}>
                                    <div className="text-center p-4">
                                        <div className="text-2xl font-bold text-green-600">{completedVideos}</div>
                                        <div className="text-gray-500">已完成视频</div>
                                    </div>
                                </Col>
                            </Row>

                            <div className="mt-4">
                                <div className="flex justify-between items-center mb-2">
                                    <span>总体学习进度</span>
                                    <span>{totalVideos > 0 ? Math.round((completedVideos / totalVideos) * 100) : 0}%</span>
                                </div>
                                <Progress
                                    percent={totalVideos > 0 ? (completedVideos / totalVideos) * 100 : 0}
                                    strokeColor={{
                                        '0%': '#108ee9',
                                        '100%': '#87d068',
                                    }}
                                />
                            </div>
                        </Card>

                        {/* 观后感统计 */}
                        <Card title="观后感统计">
                            <Row gutter={[16, 16]}>
                                <Col xs={24} sm={8}>
                                    <div className="text-center p-4">
                                        <div className="text-2xl font-bold text-purple-600">{totalReflections}</div>
                                        <div className="text-gray-500">总观后感</div>
                                    </div>
                                </Col>
                                <Col xs={24} sm={8}>
                                    <div className="text-center p-4">
                                        <div className="text-2xl font-bold text-green-600">{approvedReflections}</div>
                                        <div className="text-gray-500">已通过</div>
                                    </div>
                                </Col>
                                <Col xs={24} sm={8}>
                                    <div className="text-center p-4">
                                        <div className="text-2xl font-bold text-orange-600">
                                            {totalReflections > 0 ? Math.round((approvedReflections / totalReflections) * 100) : 0}%
                                        </div>
                                        <div className="text-gray-500">通过率</div>
                                    </div>
                                </Col>
                            </Row>
                        </Card>

                        {/* 学习成就 */}
                        <Card title="学习成就">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">🎯</div>
                                        <div>
                                            <div className="font-medium">学习新手</div>
                                            <div className="text-sm text-gray-500">完成第一个视频学习</div>
                                        </div>
                                    </div>
                                    <Tag color="blue">已获得</Tag>
                                </div>

                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">📝</div>
                                        <div>
                                            <div className="font-medium">思考者</div>
                                            <div className="text-sm text-gray-500">写出第一篇高质量观后感</div>
                                        </div>
                                    </div>
                                    <Tag>未获得</Tag>
                                </div>

                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">🏆</div>
                                        <div>
                                            <div className="font-medium">学习达人</div>
                                            <div className="text-sm text-gray-500">完成10个视频学习</div>
                                        </div>
                                    </div>
                                    <Tag>未获得</Tag>
                                </div>
                            </div>
                        </Card>
                    </div>
                </Col>
            </Row>
        </div>
    );
};

export default ProfilePage;