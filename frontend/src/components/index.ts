// src/components/index.ts
// 所有组件统一导出

// UI 组件
export * from './ui';

// 布局组件
export { MainLayout } from './layout/MainLayout';

// 功能组件
export { default as DashboardPage } from '../pages/DashboardPage';
export { default as VideoListPage } from '../pages/VideoListPage';
export { default as VideoDetailPage } from '../pages/VideoDetailPage';
export { default as ReflectionPage } from '../pages/ReflectionPage';
export { default as ReflectionListPage } from '../pages/ReflectionListPage';
export { default as ProfilePage } from '../pages/ProfilePage';