# backend/app/routes/__init__.py
"""
API路由模块
"""

# 条件导入，避免导入错误
__all__ = []

try:
    from . import videos
    __all__.append("videos")
except ImportError as e:
    print(f"❌ 无法导入videos路由: {e}")

try:
    from . import comments
    __all__.append("comments")
except ImportError as e:
    print(f"❌ 无法导入comments路由: {e}")

try:
    from . import reflections
    __all__.append("reflections")
except ImportError as e:
    print(f"❌ 无法导入reflections路由: {e}")

print(f"✅ 成功导入路由模块: {__all__}")
