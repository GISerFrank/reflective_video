// src/components/ui/Loading.tsx
import React from 'react';
import { Spin } from 'antd';

interface LoadingProps {
    size?: 'small' | 'default' | 'large';
    tip?: string;
    spinning?: boolean;
    children?: React.ReactNode;
}

export const Loading: React.FC<LoadingProps> = ({
                                                    size = 'default',
                                                    tip,
                                                    spinning = true,
                                                    children
                                                }) => {
    if (children) {
        return (
            <Spin spinning={spinning} tip={tip} size={size}>
                {children}
            </Spin>
        );
    }

    // 修复：在没有 children 的情况下，需要包装内容才能使用 tip
    return (
        <div className="flex justify-center items-center p-8">
            <Spin size={size} tip={tip} spinning={spinning}>
                <div className="w-20 h-20" /> {/* 占位内容 */}
            </Spin>
        </div>
    );
};
