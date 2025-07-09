// src/App.tsx
import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { router } from './router';
import { useGlobalStore } from './store';
import './App.css';

const App: React.FC = () => {
    const { theme } = useGlobalStore();

    return (
        <ConfigProvider
            locale={zhCN}
            theme={{
                token: {
                    colorPrimary: '#1890ff',
                    borderRadius: 6,
                },
                algorithm: theme === 'dark' ? undefined : undefined, // 可以在这里配置暗色主题
            }}
        >
            <div className={`app ${theme}`}>
                <RouterProvider router={router} />
            </div>
        </ConfigProvider>
    );
};

export default App;