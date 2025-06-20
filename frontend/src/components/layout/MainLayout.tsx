// src/components/layout/MainLayout.tsx
import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, Space } from 'antd';
import {
    HomeOutlined,
    VideoCameraOutlined,
    EditOutlined,
    UserOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    BellOutlined,
    SettingOutlined,
    LogoutOutlined
} from '@ant-design/icons';
import { Outlet, useLocation } from 'react-router-dom';
import { useRouteNavigation } from '../../hooks/useRouteNavigation';
import { useGlobalStore } from '../../store';

const { Header, Sider, Content } = Layout;

export const MainLayout: React.FC = () => {
    const location = useLocation();
    const { goToDashboard, goToVideoList, goToReflectionList, goToProfile } = useRouteNavigation();
    const { sidebarCollapsed, toggleSidebar } = useGlobalStore();

    // 根据当前路径确定选中的菜单项
    const getSelectedKey = () => {
        const path = location.pathname;
        if (path.startsWith('/videos')) return 'videos';
        if (path.startsWith('/reflections')) return 'reflections';
        if (path.startsWith('/profile')) return 'profile';
        return 'dashboard';
    };

    // 侧边栏菜单项
    const menuItems = [
        {
            key: 'dashboard',
            icon: <HomeOutlined />,
            label: '仪表板',
            onClick: goToDashboard,
        },
        {
            key: 'videos',
            icon: <VideoCameraOutlined />,
            label: '视频学习',
            onClick: goToVideoList,
        },
        {
            key: 'reflections',
            icon: <EditOutlined />,
            label: '我的观后感',
            onClick: goToReflectionList,
        },
        {
            key: 'profile',
            icon: <UserOutlined />,
            label: '个人资料',
            onClick: goToProfile,
        },
    ];

    // 用户下拉菜单
    const userMenuItems = [
        {
            key: 'profile',
            icon: <UserOutlined />,
            label: '个人资料',
            onClick: goToProfile,
        },
        {
            key: 'settings',
            icon: <SettingOutlined />,
            label: '设置',
        },
        {
            type: 'divider' as const,
        },
        {
            key: 'logout',
            icon: <LogoutOutlined />,
            label: '退出登录',
            danger: true,
        },
    ];

    return (
        <Layout className="min-h-screen">
            <Sider
                trigger={null}
                collapsible
                collapsed={sidebarCollapsed}
                className="shadow-lg"
                theme="light"
            >
                <div className="flex items-center justify-center h-16 border-b">
                    <div className="text-xl font-bold text-blue-600">
                        {sidebarCollapsed ? 'SVP' : 'Smart Video Platform'}
                    </div>
                </div>

                <Menu
                    theme="light"
                    mode="inline"
                    selectedKeys={[getSelectedKey()]}
                    items={menuItems}
                    className="border-r-0"
                />
            </Sider>

            <Layout>
                <Header className="bg-white shadow-sm px-4 flex items-center justify-between">
                    <Button
                        type="text"
                        icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={toggleSidebar}
                        className="text-lg"
                    />

                    <Space size="middle">
                        <Button type="text" icon={<BellOutlined />} />

                        <Dropdown
                            menu={{ items: userMenuItems }}
                            placement="bottomRight"
                            arrow
                        >
                            <Space className="cursor-pointer hover:bg-gray-50 px-2 py-1 rounded">
                                <Avatar icon={<UserOutlined />} />
                                <span className="font-medium">用户</span>
                            </Space>
                        </Dropdown>
                    </Space>
                </Header>

                <Content className="p-6 bg-gray-50 overflow-auto">
                    <div className="max-w-7xl mx-auto">
                        <Outlet />
                    </div>
                </Content>
            </Layout>
        </Layout>
    );
};