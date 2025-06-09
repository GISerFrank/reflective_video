# api_health_check.py - 快速验证当前API状态
import requests
import json

def test_all_paths():
    """测试所有可能的路径"""
    base_url = "http://127.0.0.1:8000"

    print("🔍 快速测试所有可能的API路径")
    print("=" * 50)

    # 测试GET端点
    test_paths = [
        # 基础端点
        "/",
        "/health",
        "/docs",

        # 带api前缀的端点
        "/api/videos",
        "/api/videos/",
        "/api/comments",
        "/api/comments/",
        "/api/reflections",
        "/api/reflections/",

        # 不带api前缀的端点
        "/videos",
        "/videos/",
        "/comments",
        "/comments/",
        "/reflections",
        "/reflections/",
    ]

    print("📊 GET端点测试:")
    working_paths = []

    for path in test_paths:
        try:
            url = f"{base_url}{path}"
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                print(f"✅ {path} - 工作正常")
                working_paths.append(path)
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'message' in data:
                        print(f"   💬 {data['message']}")
                except:
                    pass
            elif response.status_code == 404:
                print(f"❌ {path} - 404 未找到")
            else:
                print(f"⚠️ {path} - {response.status_code}")

        except Exception as e:
            print(f"❌ {path} - 异常: {str(e)[:30]}")

    print(f"\n✅ 找到 {len(working_paths)} 个工作的GET端点")

    # 测试POST端点（如果找到了基础端点）
    if working_paths:
        test_post_endpoints(base_url, working_paths)

    return working_paths

def test_post_endpoints(base_url, working_paths):
    """测试POST端点"""
    print(f"\n📝 POST端点测试:")

    # 根据找到的工作路径推断POST端点
    post_tests = []

    for path in working_paths:
        if 'comments' in path:
            base = path.rstrip('/')
            post_tests.extend([
                (f"{base}/preview", {"content": "测试评论内容，需要足够长才能通过验证系统"}, "评论预检测"),
                (f"{base}/similarity/test", {"text1": "第一段文本", "text2": "第二段文本"}, "相似度测试")
            ])
        elif 'reflections' in path:
            base = path.rstrip('/')
            post_tests.append((
                f"{base}/preview",
                {"content": "测试观后感内容，需要足够长才能通过验证系统，至少50个字符", "video_id": 1},
                "观后感预检测"
            ))

    for endpoint, payload, name in post_tests:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 200:
                print(f"✅ {endpoint} - {name}工作正常")
                try:
                    data = response.json()
                    if 'valid' in data:
                        print(f"   ✓ 验证结果: {data['valid']}")
                    if 'similarity_score' in data:
                        print(f"   📊 相似度: {data['similarity_score']}%")
                except:
                    pass
            else:
                print(f"❌ {endpoint} - {name}失败 ({response.status_code})")
                if response.text:
                    print(f"   错误: {response.text[:100]}")

        except Exception as e:
            print(f"❌ {endpoint} - {name}异常: {str(e)[:50]}")

def check_openapi_docs():
    """检查OpenAPI文档"""
    print(f"\n📖 检查OpenAPI文档:")

    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})

            print(f"✅ OpenAPI文档可访问")
            print(f"📊 文档中记录了 {len(paths)} 个端点:")

            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"   🔗 {path} - {', '.join(m.upper() for m in methods)}")

            return paths
        else:
            print(f"❌ 无法访问OpenAPI文档: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 检查OpenAPI文档时出错: {e}")
        return None

def main():
    print("⚡ Smart Video Platform - 快速API状态验证")
    print("=" * 55)

    # 1. 测试所有路径
    working_paths = test_all_paths()

    # 2. 检查OpenAPI文档
    openapi_paths = check_openapi_docs()

    # 3. 总结
    print(f"\n🎯 测试总结:")
    print("=" * 30)

    if working_paths:
        print(f"✅ 找到 {len(working_paths)} 个工作的端点")
        print("🔗 工作的端点:")
        for path in working_paths:
            print(f"   - {path}")
    else:
        print("❌ 没有找到工作的API端点")

    if openapi_paths:
        print(f"\n📖 OpenAPI文档记录了 {len(openapi_paths)} 个端点")
        if len(working_paths) != len(openapi_paths):
            print("⚠️ 工作端点数量与文档不匹配，可能存在问题")
    else:
        print("\n❌ 无法访问OpenAPI文档")

    print(f"\n💡 建议:")
    if not working_paths:
        print("   1. 检查服务是否完全启动")
        print("   2. 检查路由文件是否有语法错误")
        print("   3. 查看uvicorn终端的错误日志")
    else:
        print("   1. API基本工作正常")
        print("   2. 可以使用找到的端点进行测试")
        print("   3. 访问 http://127.0.0.1:8000/docs 查看完整文档")

if __name__ == "__main__":
    main()