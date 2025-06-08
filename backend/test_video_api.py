# backend/test_video_api.py - 测试视频API
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/videos"

def test_video_apis():
    print("🧪 测试视频管理API")
    print("=" * 50)

    # 1. 测试获取视频列表
    print("1️⃣ 测试获取视频列表...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            videos = response.json()
            print(f"   找到 {len(videos)} 个视频")
            if videos:
                print(f"   第一个视频: {videos[0]['title']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print()

    # 2. 测试获取视频统计
    print("2️⃣ 测试获取视频统计...")
    try:
        response = requests.get(f"{BASE_URL}/stats/overview")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   总视频数: {stats.get('total_videos', 0)}")
            print(f"   总时长: {stats.get('total_duration_formatted', 'N/A')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print()

    # 3. 测试获取分类列表
    print("3️⃣ 测试获取分类列表...")
    try:
        response = requests.get(f"{BASE_URL}/categories/list")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"   分类: {categories.get('categories', [])}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print()

    # 4. 测试获取单个视频 (如果有视频的话)
    print("4️⃣ 测试获取单个视频...")
    try:
        # 先获取视频列表
        list_response = requests.get(f"{BASE_URL}/")
        if list_response.status_code == 200:
            videos = list_response.json()
            if videos:
                video_id = videos[0]['id']
                response = requests.get(f"{BASE_URL}/{video_id}")
                print(f"   状态码: {response.status_code}")
                if response.status_code == 200:
                    video = response.json()
                    print(f"   视频标题: {video['title']}")
                    print(f"   视频时长: {video['duration']}秒")
                else:
                    print(f"   错误: {response.text}")
            else:
                print("   ⚠️ 没有视频数据进行测试")
        else:
            print("   ⚠️ 无法获取视频列表")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print()

    # 5. 测试创建视频 (演示用)
    print("5️⃣ 测试创建视频...")
    try:
        video_data = {
            "title": "测试视频 - API创建",
            "description": "这是通过API创建的测试视频",
            "duration": 600,  # 10分钟
            "order_index": 999,  # 使用一个不会冲突的序号
            "category": "测试分类",
            "difficulty_level": "beginner"
        }

        response = requests.post(
            f"{BASE_URL}/",
            json=video_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 201:
            video = response.json()
            print(f"   ✅ 创建成功: {video['title']}")
            print(f"   视频ID: {video['id']}")

            # 测试删除刚创建的视频
            delete_response = requests.delete(f"{BASE_URL}/{video['id']}")
            if delete_response.status_code == 204:
                print(f"   ✅ 测试视频已清理")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

    print()
    print("🌐 访问以下链接查看API文档:")
    print("   📖 http://127.0.0.1:8000/docs")
    print("   🔧 http://127.0.0.1:8000/docs#/videos")

if __name__ == "__main__":
    test_video_apis()