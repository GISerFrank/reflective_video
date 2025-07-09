// src/components/ui/ReflectionCard.tsx
import React from 'react';
import { Card, Tag, Rate, Space } from 'antd';
import { UserOutlined, CalendarOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type {Reflection} from '../../types';

interface ReflectionCardProps {
    reflection: Reflection;
    showVideo?: boolean;
    onClick?: () => void;
}

export const ReflectionCard: React.FC<ReflectionCardProps> = ({
                                                                  reflection,
                                                                  showVideo = false,
                                                                  onClick
                                                              }) => {
    const getScoreColor = (score: number) => {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'error';
    };

    return (
        <Card
            hoverable
            className="mb-4"
            onClick={onClick}
            extra={
                <Space>
                    <Tag color={getScoreColor(reflection.quality_score)}>
                        质量分数: {reflection.quality_score}
                    </Tag>
                    {reflection.is_approved && (
                        <Tag color="green" icon={<CheckCircleOutlined />}>
                            已通过
                        </Tag>
                    )}
                </Space>
            }
        >
            <div className="mb-3">
                <Space className="text-sm text-gray-500">
                    <UserOutlined />
                    <span>用户 #{reflection.user_id}</span>
                    <CalendarOutlined />
                    <span>{new Date(reflection.created_at).toLocaleDateString()}</span>
                    <span>字数: {reflection.word_count}</span>
                </Space>
            </div>

            <div className="mb-3">
                <p className="text-gray-800 leading-relaxed line-clamp-3">
                    {reflection.content}
                </p>
            </div>

            <div className="flex flex-wrap gap-2">
                {reflection.has_thought_words && (
                    <Tag color="blue">包含思考性词汇</Tag>
                )}
                {reflection.has_specific_examples && (
                    <Tag color="green">包含具体例子</Tag>
                )}
                {reflection.has_questions && (
                    <Tag color="purple">包含疑问</Tag>
                )}
            </div>

            {reflection.feedback && (
                <div className="mt-3 p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">反馈: {reflection.feedback}</span>
                </div>
            )}
        </Card>
    );
};