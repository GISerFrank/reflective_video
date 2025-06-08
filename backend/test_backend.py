# backend/diagnose_env.py - 环境诊断脚本
import sys
import os
import subprocess

def check_python_version():
    """检查Python版本"""
    print(f"🐍 Python版本: {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠️  警告: 推荐使用Python 3.8+")
    else:
        print("✅ Python版本符合要求")

def check_virtual_env():
    """检查是否在虚拟环境中"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 当前在虚拟环境中")
        print(f"📁 虚拟环境路径: {sys.prefix}")
    else:
        print("⚠️  警告: 不在虚拟环境中，建议使用虚拟环境")

def check_package(package_name, import_name=None):
    """检查包是否安装"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError as e:
        print(f"❌ {package_name} 未安装或有问题: {e}")
        return False

def check_packages():
    """检查关键包"""
    print("\n🧪 检查Python包...")
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("python-jose", "jose"),
        ("passlib", "passlib"),
        ("scikit-learn", "sklearn"),
        ("jieba", "jieba"),
        ("numpy", "numpy")
    ]

    all_ok = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False

    return all_ok

def install_missing_packages():
    """安装缺失的包"""
    print("\n🔧 尝试安装缺失的包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 包安装失败: {e}")
        return False

def test_basic_imports():
    """测试基本导入"""
    print("\n🧪 测试基本导入...")

    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    tests = [
        ("FastAPI", lambda: __import__("fastapi")),
        ("Pydantic", lambda: __import__("pydantic")),
        ("SQLAlchemy", lambda: __import__("sqlalchemy")),
    ]

    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name} 导入成功")
        except ImportError as e:
            print(f"❌ {name} 导入失败: {e}")
            return False

    return True

def test_app_imports():
    """测试应用模块导入"""
    print("\n🧪 测试应用模块...")

    # 确保app目录存在且有__init__.py
    app_dir = os.path.join(os.path.dirname(__file__), "app")
    init_file = os.path.join(app_dir, "__init__.py")

    if not os.path.exists(app_dir):
        print("❌ app目录不存在")
        return False

    if not os.path.exists(init_file):
        print("❌ app/__init__.py 不存在，正在创建...")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write('# Smart Video Platform Backend\n__version__ = "1.0.0"\n')
        print("✅ 已创建 app/__init__.py")

    try:
        # 测试config导入
        from app.config import settings
        print("✅ app.config 导入成功")

        # 测试models导入
        from app.models.base import Base
        print("✅ app.models.base 导入成功")

        return True
    except ImportError as e:
        print(f"❌ 应用模块导入失败: {e}")
        return False

def main():
    print("🔍 Smart Video Platform 环境诊断")
    print("=" * 50)

    # 检查Python版本
    check_python_version()

    # 检查虚拟环境
    check_virtual_env()

    # 检查包安装
    packages_ok = check_packages()

    if not packages_ok:
        user_input = input("\n❓ 是否尝试自动安装缺失的包？(y/n): ")
        if user_input.lower() == 'y':
            if install_missing_packages():
                packages_ok = check_packages()

    if packages_ok:
        # 测试基本导入
        basic_ok = test_basic_imports()

        if basic_ok:
            # 测试应用导入
            app_ok = test_app_imports()

            if app_ok:
                print("\n🎉 环境诊断完成，一切正常！")
                print("💡 可以运行: uvicorn app.main:app --reload")
            else:
                print("\n❌ 应用模块有问题")
        else:
            print("\n❌ 基础模块导入有问题")
    else:
        print("\n❌ 包安装有问题")

if __name__ == "__main__":
    main()