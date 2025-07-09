// src/components/ui/ErrorMessage.tsx
import React from 'react';
import { Alert } from 'antd';

interface ErrorMessageProps {
    error: string | null;
    onClose?: () => void;
    showIcon?: boolean;
    type?: 'error' | 'warning';
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
                                                              error,
                                                              onClose,
                                                              showIcon = true,
                                                              type = 'error'
                                                          }) => {
    if (!error) return null;

    return (
        <Alert
            message="错误"
            description={error}
            type={type}
            showIcon={showIcon}
            closable={!!onClose}
            onClose={onClose}
            className="mb-4"
        />
    );
};