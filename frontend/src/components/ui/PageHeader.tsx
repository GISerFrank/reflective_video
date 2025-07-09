// src/components/ui/PageHeader.tsx
import React from 'react';
import { Typography, Breadcrumb, Space, Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    breadcrumbs?: Array<{ title: string; path?: string }>;
    extra?: React.ReactNode;
    onBack?: () => void;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
                                                          title,
                                                          subtitle,
                                                          breadcrumbs,
                                                          extra,
                                                          onBack
                                                      }) => {
    const navigate = useNavigate();

    const handleBack = () => {
        if (onBack) {
            onBack();
        } else {
            navigate(-1);
        }
    };

    return (
        <div className="mb-6">
            {breadcrumbs && (
                <Breadcrumb className="mb-4">
                    {breadcrumbs.map((item, index) => (
                        <Breadcrumb.Item key={index}>
                            {item.path ? (
                                <a onClick={() => navigate(item.path!)}>{item.title}</a>
                            ) : (
                                item.title
                            )}
                        </Breadcrumb.Item>
                    ))}
                </Breadcrumb>
            )}

            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    {onBack && (
                        <Button
                            type="text"
                            icon={<ArrowLeftOutlined />}
                            onClick={handleBack}
                            className="flex items-center justify-center w-8 h-8"
                        />
                    )}
                    <div>
                        <Title level={2} className="!mb-0">
                            {title}
                        </Title>
                        {subtitle && (
                            <div className="text-gray-500 mt-1">{subtitle}</div>
                        )}
                    </div>
                </div>

                {extra && (
                    <Space>{extra}</Space>
                )}
            </div>
        </div>
    );
};