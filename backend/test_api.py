# test_api.py - 测试API调用
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("🧪 测试Smart Video Platform API")
    print("=" * 40)

    # 测试根路径
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ GET / : {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ GET / 失败: {e}")

    print()

    # 测试健康检查
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ GET /health : {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ GET /health 失败: {e}")

    print()
    print("🌐 在浏览器中访问以下地址:")
    print(f"   📖 API文档: {BASE_URL}/docs")
    print(f"   🔧 健康检查: {BASE_URL}/health")

if __name__ == "__main__":
    test_api()