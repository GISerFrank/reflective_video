# backend/test_services.py - 测试Services层功能
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_comment_services():
    """测试评论服务的完整流程"""
    print("🧪 测试评论服务层")
    print("=" * 60)

    # 1. 测试评论预检测
    print("1️⃣ 测试评论预检测...")

    test_comments = [
        "这个视频很好看！",  # 太简单
        "这个视频讲解得非常详细，我从中学到了很多人工智能的基础知识，特别是机器学习的部分让我印象深刻。",  # 质量良好
        "我觉得这个视频内容很有深度，讲解的人工智能概念很清晰，特别是对于初学者来说很容易理解，建议大家都来看看。",  # 可能重复
    ]

    for i, comment in enumerate(test_comments, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/comments/preview",
                json={"content": comment},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   评论{i}: {comment[:30]}...")
                print(f"   有效性: {result.get('valid', False)}")
                if result.get('valid'):
                    quality = result.get('quality_result', {})
                    similarity = result.get('similarity_result', {})
                    print(f"   质量分数: {quality.get('quality_score', 0)}")
                    print(f"   相似度分数: {similarity.get('similarity_score', 0)}")
                    print(f"   预测状态: {result.get('predicted_status', 'unknown')}")
                else:
                    print(f"   错误: {result.get('error', '未知错误')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")

            print()
        except Exception as e:
            print(f"   ❌ 异常: {e}")

    # 2. 测试创建评论
    print("2️⃣ 测试创建评论...")

    good_comment = {
        "content": "这个AI基础课程讲解得非常棒！我特别喜欢其中关于神经网络的部分，老师用简单易懂的例子说明了复杂的概念。作为一个初学者，我觉得这种循序渐进的教学方式很适合我。希望能有更多这样高质量的教程。",
        "parent_id": None
    }

    try:
        response = requests.post(
            f"{BASE_URL}/comments/",
            json=good_comment,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            result = response.json()
            print("   ✅ 评论创建成功")
            print(f"   评论ID: {result.get('comment', {}).get('id')}")
            print(f"   状态: {result.get('comment', {}).get('status')}")

            quality = result.get('quality_analysis', {})
            similarity = result.get('similarity_analysis', {})

            print(f"   质量分数: {quality.get('quality_score', 0)}")
            print(f"   原创分数: {similarity.get('originality_score', 0)}")
            print(f"   自动决策: {result.get('auto_decision', {}).get('reason', 'N/A')}")
        else:
            print(f"   ❌ 创建失败: {response.status_code}")
            print(f"   错误: {response.text}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    print()

    # 3. 测试相似度检测
    print("3️⃣ 测试相似度检测...")

    try:
        similarity_test = {
            "text1": "这个视频很有趣，内容丰富，讲解清晰",
            "text2": "这个视频挺有意思的，内容很丰富，解释得很清楚"
        }

        response = requests.post(
            f"{BASE_URL}/comments/similarity/test",
            json=similarity_test,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("   ✅ 相似度测试成功")
            print(f"   文本1: {result.get('text1', '')}")
            print(f"   文本2: {result.get('text2', '')}")
            print(f"   相似度分数: {result.get('similarity_score', 0)}%")
            print(f"   是否相似: {result.get('is_similar', False)}")
        else:
            print(f"   ❌ 测试失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    print()

    # 4. 测试质量检测
    print("4️⃣ 测试质量检测...")

    try:
        quality_test_content = "我认为这个人工智能视频非常有价值，它详细解释了机器学习的基本概念。比如，它用简单的例子说明了神经网络是如何工作的。这让我对AI有了更深入的理解。我觉得这种教学方法很有效，因为它将复杂的理论转化为容易理解的实际应用。"

        response = requests.post(
            f"{BASE_URL}/comments/quality/test",
            json={"content": quality_test_content},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("   ✅ 质量测试成功")
            print(f"   质量分数: {result.get('quality_score', 0)}")
            print(f"   质量等级: {result.get('quality_level', 'unknown')}")
            print(f"   是否通过: {result.get('quality_passed', False)}")

            details = result.get('details', {})
            print(f"   字数: {details.get('word_count', 0)}")
            print(f"   思考分数: {details.get('thought_score', 0)}")
            print(f"   具体性分数: {details.get('specific_score', 0)}")

            if result.get('suggestions'):
                print(f"   建议: {'; '.join(result['suggestions'])}")
        else:
            print(f"   ❌ 测试失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")


def test_video_services():
    """测试视频服务层功能"""
    print("\n🎬 测试视频服务层")
    print("=" * 60)

    # 1. 测试获取学习路径
    print("1️⃣ 测试获取学习路径...")

    try:
        response = requests.get(f"{BASE_URL}/videos/learning/path")

        if response.status_code == 200:
            result = response.json()
            print("   ✅ 学习路径获取成功")
            print(f"   总视频数: {result.get('total_videos', 0)}")
            print(f"   已完成: {result.get('completed_videos', 0)}")
            print(f"   完成率: {result.get('completion_rate', 0):.1f}%")

            current_video = result.get('current_video')
            if current_video:
                print(f"   当前建议: {current_video.get('title', 'N/A')}")

            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"   学习建议: {'; '.join(recommendations[:2])}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    # 2. 测试热门视频
    print("\n2️⃣ 测试热门视频...")

    try:
        response = requests.get(f"{BASE_URL}/videos/popular/list?limit=5")

        if response.status_code == 200:
            result = response.json()
            popular_videos = result.get('popular_videos', [])

            print(f"   ✅ 热门视频获取成功 (共{len(popular_videos)}个)")

            for i, video in enumerate(popular_videos[:3], 1):
                print(f"   {i}. {video.get('title', 'N/A')}")
                print(f"      观看人数: {video.get('viewer_count', 0)}")
                print(f"      完成率: {video.get('completion_rate', 0):.1f}%")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    # 3. 测试视频详情
    print("\n3️⃣ 测试视频详情...")

    try:
        response = requests.get(f"{BASE_URL}/videos/1/details")

        if response.status_code == 200:
            result = response.json()
            video = result.get('video', {})
            progress = result.get('progress')
            stats = result.get('stats', {})

            print("   ✅ 视频详情获取成功")
            print(f"   视频标题: {video.get('title', 'N/A')}")
            print(f"   总观看人数: {stats.get('total_viewers', 0)}")
            print(f"   完成人数: {stats.get('completed_viewers', 0)}")
            print(f"   平均进度: {stats.get('average_progress', 0):.1f}%")

            if progress:
                print(f"   用户进度: {progress.get('completion_percentage', 0):.1f}%")
                print(f"   是否完成: {progress.get('is_completed', False)}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")


def test_system_stats():
    """测试系统统计功能"""
    print("\n📊 测试系统统计")
    print("=" * 60)

    # 1. 视频系统统计
    print("1️⃣ 视频系统统计...")

    try:
        response = requests.get(f"{BASE_URL}/videos/stats/overview")

        if response.status_code == 200:
            result = response.json()
            video_stats = result.get('video_stats', {})
            user_stats = result.get('user_stats', {})
            learning_stats = result.get('learning_stats', {})

            print("   ✅ 视频统计获取成功")
            print(f"   总视频数: {video_stats.get('total_videos', 0)}")
            print(f"   总时长: {video_stats.get('total_duration_hours', 0)}小时")
            print(f"   活跃用户: {user_stats.get('active_users', 0)}")
            print(f"   参与率: {user_stats.get('engagement_rate', 0):.1f}%")
            print(f"   学习完成率: {learning_stats.get('completion_rate', 0):.1f}%")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    # 2. 评论系统统计
    print("\n2️⃣ 评论系统统计...")

    try:
        response = requests.get(f"{BASE_URL}/comments/system/stats")

        if response.status_code == 200:
            result = response.json()

            print("   ✅ 评论统计获取成功")
            print(f"   总评论数: {result.get('total_comments', 0)}")
            print(f"   通过率: {result.get('approval_rate', 0):.1f}%")

            similarity_stats = result.get('similarity_stats', {})
            print(f"   相似度拒绝数: {similarity_stats.get('rejected_by_similarity', 0)}")
            print(f"   平均相似度: {similarity_stats.get('average_similarity_score', 0):.1f}")

            thresholds = result.get('thresholds', {})
            print(f"   相似度阈值: {thresholds.get('similarity_threshold', 0)}%")
            print(f"   质量阈值: {thresholds.get('quality_threshold', 0)}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")


def main():
    print("🚀 Smart Video Platform Services层测试")
    print("=" * 80)
    print("请确保后端服务已启动: uvicorn app.main:app --reload")
    print()

    # 等待用户确认
    input("按回车键开始测试...")

    try:
        # 测试基本连接
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code != 200:
            print("❌ 后端服务未运行，请先启动服务")
            return

        print("✅ 后端服务连接正常")
        print()

        # 运行所有测试
        test_comment_services()
        test_video_services()
        test_system_stats()

        print("\n🎉 Services层测试完成！")
        print("\n💡 您可以:")
        print("   1. 访问 http://127.0.0.1:8000/docs 查看完整API文档")
        print("   2. 在文档页面直接测试各个API接口")
        print("   3. 查看相似度检测和质量评估的详细结果")

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("请确保运行: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    main()