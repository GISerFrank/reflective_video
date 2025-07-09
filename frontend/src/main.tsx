// src/main.tsx - Vite 项目的入口文件
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// 导入 store 用于初始化数据
import { useUserStore } from './store'

// 模拟用户登录 - 初始化用户数据
const initializeApp = () => {
    const { setUser } = useUserStore.getState()

    // 临时用户数据，实际项目中应该：
    // 1. 检查 localStorage 中是否有 token
    // 2. 如果有 token，调用 API 获取用户信息
    // 3. 如果没有 token，跳转到登录页
    const mockUser = {
        id: 1,
        username: '测试用户',
        email: 'test@example.com',
        created_at: new Date().toISOString(),
    }

    // 设置用户信息
    setUser(mockUser)

    console.log('🚀 Smart Video Platform 初始化完成')
}

// 应用初始化
initializeApp()

// 创建根节点并渲染应用
const container = document.getElementById('root')
if (!container) {
    throw new Error('Root element not found')
}

const root = ReactDOM.createRoot(container)

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
)