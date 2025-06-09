# create_react_frontend.sh - React前端项目初始化脚本

echo "🚀 创建Smart Video Platform React前端"
echo "============================================"

# 1. 创建Vite + React + TypeScript项目
echo "📦 创建Vite项目..."
npm create vite@latest frontend -- --template react-ts
cd frontend

# 2. 安装依赖包
echo "📥 安装依赖包..."

# 核心依赖
npm install \
  react-router-dom@6 \
  axios \
  zustand \
  @ant-design/icons \
  antd \
  dayjs \
  classnames

# 开发依赖
npm install -D \
  @types/node \
  tailwindcss \
  autoprefixer \
  postcss \
  eslint-plugin-react-hooks \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser

# 3. 初始化Tailwind CSS
echo "🎨 配置Tailwind CSS..."
npx tailwindcss init -p

# 4. 创建项目目录结构
echo "📁 创建项目目录结构..."

# 创建主要目录
mkdir -p src/{components,pages,hooks,stores,services,types,utils,assets}

# 创建子目录
mkdir -p src/components/{common,video,comment,reflection,layout}
mkdir -p src/pages/{home,video,dashboard,search}
mkdir -p src/assets/{images,icons,styles}

echo "✅ 项目初始化完成！"
echo ""
echo "📁 项目结构："
echo "frontend/"
echo "├── src/"
echo "│   ├── components/          # 可复用组件"
echo "│   │   ├── common/          # 通用组件"
echo "│   │   ├── video/           # 视频相关组件"
echo "│   │   ├── comment/         # 评论相关组件"
echo "│   │   ├── reflection/      # 观后感相关组件"
echo "│   │   └── layout/          # 布局组件"
echo "│   ├── pages/               # 页面组件"
echo "│   │   ├── home/            # 首页"
echo "│   │   ├── video/           # 视频页面"
echo "│   │   ├── dashboard/       # 仪表板"
echo "│   │   └── search/          # 搜索页面"
echo "│   ├── hooks/               # 自定义Hooks"
echo "│   ├── stores/              # 状态管理"
echo "│   ├── services/            # API服务"
echo "│   ├── types/               # TypeScript类型定义"
echo "│   ├── utils/               # 工具函数"
echo "│   └── assets/              # 静态资源"
echo "└── public/                  # 公共文件"
echo ""
echo "🎯 下一步："
echo "1. cd frontend"
echo "2. 配置API服务和类型定义"
echo "3. 创建基础组件和页面"
echo "4. npm run dev 启动开发服务器"