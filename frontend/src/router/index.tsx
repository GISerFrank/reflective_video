// src/router/index.tsx
import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Loading } from '../components/ui/Loading';
import { MainLayout } from '../components/layout/MainLayout';

// 懒加载页面组件
const VideoListPage = React.lazy(() => import('../pages/VideoListPage'));
const VideoDetailPage = React.lazy(() => import('../pages/VideoDetailPage'));
const ReflectionPage = React.lazy(() => import('../pages/ReflectionPage'));
const ReflectionListPage = React.lazy(() => import('../pages/ReflectionListPage'));
const DashboardPage = React.lazy(() => import('../pages/DashboardPage'));
const ProfilePage = React.lazy(() => import('../pages/ProfilePage'));

// 路由守卫组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // 这里可以添加认证逻辑
    // const { isAuthenticated } = useUserStore();
    // if (!isAuthenticated) {
    //   return <Navigate to="/login" replace />;
    // }
    return <>{children}</>;
};

// 创建路由配置
export const router = createBrowserRouter([
        {
            path: '/',
            element: <MainLayout />,
            children: [
                {
                    index: true,
                    element: <Navigate to="/dashboard" replace />,
        },
        {
            path: 'dashboard',
            element: (
                <Suspense fallback={<Loading tip="加载仪表板..." />}>
        <ProtectedRoute>
            <DashboardPage />
        </ProtectedRoute>
        </Suspense>
    ),
    },
    {
        path: 'videos',
        children: [
            {
                index: true,
                element: (
            <Suspense fallback={<Loading tip="加载视频列表..." />}>
            <ProtectedRoute>
            <VideoListPage />
            </ProtectedRoute>
            </Suspense>
            ),
            },
            {
                path: ':id',
                element: (
            <Suspense fallback={<Loading tip="加载视频详情..." />}>
            <ProtectedRoute>
            <VideoDetailPage />
            </ProtectedRoute>
            </Suspense>
            ),
            },
            {
                path: ':id/reflection',
                element: (
            <Suspense fallback={<Loading tip="加载观后感编辑器..." />}>
            <ProtectedRoute>
            <ReflectionPage />
            </ProtectedRoute>
            </Suspense>
            ),
            },
        ],
    },
    {
        path: 'reflections',
        children: [
            {
                index: true,
                element: (
            <Suspense fallback={<Loading tip="加载观后感列表..." />}>
            <ProtectedRoute>
            <ReflectionListPage />
            </ProtectedRoute>
            </Suspense>
            ),
            },
        ],
    },
    {
        path: 'profile',
        element: (
    <Suspense fallback={<Loading tip="加载个人资料..." />}>
<ProtectedRoute>
    <ProfilePage />
</ProtectedRoute>
</Suspense>
),
},
],
},
{
    path: '*',
        element: (
    <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
        <p className="text-gray-600 mb-8">页面未找到</p>
    <a href="/" className="text-blue-600 hover:text-blue-800">
    返回首页
    </a>
    </div>
    </div>
),
},
]);
