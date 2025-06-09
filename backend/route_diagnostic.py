# route_diagnostic.py - 路由注册问题诊断工具
import os
import sys
import traceback
from pathlib import Path

def check_file_structure():
    """检查文件结构"""
    print("🔍 检查项目文件结构...")
    print("=" * 40)

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/routes/__init__.py",
        "app/routes/videos.py",
        "app/routes/comments.py",
        "app/routes/reflections.py"
    ]

    missing_files = []
    existing_files = []

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            existing_files.append(file_path)
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️ 缺少 {len(missing_files)} 个必需文件")
        print("💡 请确保以下文件存在:")
        for file in missing_files:
            print(f"   - {file}")

    return existing_files, missing_files

def test_import_routes():
    """测试路由模块导入"""
    print("\n🧪 测试路由模块导入...")
    print("=" * 40)

    # 添加当前目录到Python路径
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    import_results = {}

    route_modules = ['videos', 'comments', 'reflections']

    for module_name in route_modules:
        print(f"\n📦 测试导入 {module_name}...")

        try:
            # 尝试不同的导入方式
            import_methods = [
                f"from app.routes import {module_name}",
                f"import app.routes.{module_name}",
                f"from .routes import {module_name}",  # 这个在脚本中不会工作，但我们可以模拟
            ]

            for method in import_methods:
                try:
                    print(f"   尝试: {method}")

                    if method.startswith("from app.routes"):
                        exec(f"from app.routes import {module_name}")
                        module = eval(module_name)
                    elif method.startswith("import app.routes"):
                        exec(f"import app.routes.{module_name}")
                        module = eval(f"app.routes.{module_name}")
                    else:
                        print(f"      ⚠️ 跳过相对导入测试")
                        continue

                    # 检查router属性
                    if hasattr(module, 'router'):
                        router = module.router
                        print(f"      ✅ 导入成功，找到router对象")
                        print(f"      📊 Router类型: {type(router)}")

                        # 检查路由数量
                        if hasattr(router, 'routes'):
                            route_count = len(router.routes)
                            print(f"      🔗 包含 {route_count} 个路由")

                            # 显示路由详情
                            for i, route in enumerate(router.routes[:3]):  # 只显示前3个
                                if hasattr(route, 'path') and hasattr(route, 'methods'):
                                    methods = list(route.methods) if route.methods else ['?']
                                    print(f"         {i+1}. {route.path} - {methods}")

                        import_results[module_name] = {
                            'success': True,
                            'router': router,
                            'method': method
                        }
                        break
                    else:
                        print(f"      ❌ 导入成功但没有找到router属性")
                        import_results[module_name] = {
                            'success': False,
                            'error': 'No router attribute'
                        }

                except Exception as e:
                    print(f"      ❌ {method} 失败: {str(e)}")
                    import_results[module_name] = {
                        'success': False,
                        'error': str(e)
                    }

        except Exception as e:
            print(f"   ❌ 模块 {module_name} 导入完全失败: {e}")
            import_results[module_name] = {
                'success': False,
                'error': f"Complete import failure: {e}"
            }

    return import_results

def check_route_syntax():
    """检查路由文件语法"""
    print("\n🔍 检查路由文件语法...")
    print("=" * 40)

    route_files = [
        "app/routes/videos.py",
        "app/routes/comments.py",
        "app/routes/reflections.py"
    ]

    syntax_results = {}

    for file_path in route_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} - 文件不存在")
            continue

        try:
            print(f"📄 检查 {file_path}...")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试编译代码
            compile(content, file_path, 'exec')
            print(f"   ✅ 语法检查通过")

            # 检查关键内容
            if 'router = APIRouter()' in content:
                print(f"   ✅ 找到router定义")
            else:
                print(f"   ⚠️ 没有找到标准的router定义")

            # 统计路由定义
            route_count = content.count('@router.')
            print(f"   📊 包含 {route_count} 个路由定义")

            syntax_results[file_path] = {
                'valid': True,
                'route_count': route_count
            }

        except SyntaxError as e:
            print(f"   ❌ 语法错误: {e}")
            print(f"      行 {e.lineno}: {e.text}")
            syntax_results[file_path] = {
                'valid': False,
                'error': str(e)
            }
        except Exception as e:
            print(f"   ❌ 其他错误: {e}")
            syntax_results[file_path] = {
                'valid': False,
                'error': str(e)
            }

    return syntax_results

def check_dependencies():
    """检查依赖项"""
    print("\n📦 检查依赖项...")
    print("=" * 40)

    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic'
    ]

    missing_deps = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_deps.append(package)

    return missing_deps

def create_minimal_test_app():
    """创建一个最小测试应用"""
    print("\n🧪 创建最小测试应用...")
    print("=" * 40)

    try:
        from fastapi import FastAPI, APIRouter

        # 创建测试应用
        test_app = FastAPI(title="Test App")

        # 创建测试路由
        test_router = APIRouter()

        @test_router.get("/")
        async def test_endpoint():
            return {"message": "测试路由工作正常"}

        # 注册路由
        test_app.include_router(test_router, prefix="/test", tags=["test"])

        print("✅ 最小测试应用创建成功")
        print("📊 包含路由数量:", len(test_app.routes))

        # 显示路由信息
        for route in test_app.routes:
            if hasattr(route, 'path'):
                print(f"   🔗 {route.path}")

        return True

    except Exception as e:
        print(f"❌ 创建测试应用失败: {e}")
        traceback.print_exc()
        return False

def generate_fixed_main_py():
    """生成修复版的main.py"""
    print("\n🛠️ 生成修复版main.py...")
    print("=" * 40)

    fixed_content = '''# app/main.py - 修复版本
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Smart Video Platform",
    description="智能视频学习平台",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {
        "message": "Smart Video Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 安全的路由注册函数
def safe_include_router(app, module_name, prefix, tags):
    """安全地注册路由"""
    try:
        logger.info(f"尝试导入路由模块: {module_name}")
        
        if module_name == "videos":
            from .routes import videos as module
        elif module_name == "comments":
            from .routes import comments as module
        elif module_name == "reflections":
            from .routes import reflections as module
        else:
            raise ImportError(f"未知模块: {module_name}")
        
        if not hasattr(module, 'router'):
            raise AttributeError(f"模块 {module_name} 没有 router 属性")
        
        app.include_router(module.router, prefix=prefix, tags=tags)
        logger.info(f"✅ {module_name.title()}路由注册成功")
        logger.info(f"   前缀: {prefix}")
        logger.info(f"   路由数量: {len(module.router.routes)}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ {module_name}路由导入失败: {e}")
        return False
    except AttributeError as e:
        logger.error(f"❌ {module_name}路由属性错误: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {module_name}路由注册失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 注册路由
registered_routes = []

if safe_include_router(app, "videos", "/api/videos", ["videos"]):
    registered_routes.append("videos")

if safe_include_router(app, "comments", "/api/comments", ["comments"]):
    registered_routes.append("comments")

if safe_include_router(app, "reflections", "/api/reflections", ["reflections"]):
    registered_routes.append("reflections")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Smart Video Platform API启动完成")
    logger.info(f"📊 成功注册路由: {registered_routes}")
    logger.info("📖 API文档: http://127.0.0.1:8000/docs")
    
    # 显示所有路由
    logger.info("🔗 所有可用路由:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', {''})
            method_str = ','.join(methods) if methods else 'GET'
            logger.info(f"   {method_str} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    return fixed_content

def main():
    print("🔬 Smart Video Platform - 路由注册问题诊断工具")
    print("=" * 60)

    # 1. 检查文件结构
    existing, missing = check_file_structure()

    # 2. 检查依赖项
    missing_deps = check_dependencies()

    if missing_deps:
        print(f"\n⚠️ 缺少依赖包，请安装:")
        print(f"   pip install {' '.join(missing_deps)}")
        return

    # 3. 检查语法
    syntax_results = check_route_syntax()

    # 4. 测试导入
    import_results = test_import_routes()

    # 5. 创建测试应用
    test_app_ok = create_minimal_test_app()

    # 6. 总结和建议
    print(f"\n🎯 诊断总结:")
    print("=" * 30)

    issues_found = []

    if missing:
        issues_found.append(f"缺少 {len(missing)} 个必需文件")

    for file, result in syntax_results.items():
        if not result['valid']:
            issues_found.append(f"{file} 语法错误")

    failed_imports = [name for name, result in import_results.items() if not result['success']]
    if failed_imports:
        issues_found.append(f"{len(failed_imports)} 个模块导入失败")

    if issues_found:
        print("❌ 发现以下问题:")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("✅ 文件结构和语法检查通过")

    # 7. 提供解决方案
    print(f"\n💡 解决方案建议:")
    print("=" * 30)

    if failed_imports:
        print("1. 主要问题是路由导入失败，建议:")
        for name, result in import_results.items():
            if not result['success']:
                print(f"   - {name}: {result['error']}")

        print(f"\n2. 生成修复版main.py:")
        choice = input("是否生成修复版的main.py文件? (y/n): ").strip().lower()

        if choice in ['y', 'yes', '是']:
            fixed_content = generate_fixed_main_py()

            try:
                with open("app/main_fixed.py", 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print("✅ 已生成 app/main_fixed.py")
                print("💡 请将其重命名为 main.py 并重启服务")
            except Exception as e:
                print(f"❌ 生成文件失败: {e}")
    else:
        print("所有导入测试通过，问题可能在其他地方")
        print("建议检查数据库连接或其他依赖项")

if __name__ == "__main__":
    main()