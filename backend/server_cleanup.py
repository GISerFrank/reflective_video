# force_cleanup.py - 强力清理端口8000的所有进程
import subprocess
import time
import requests
import os
import sys

def run_command(cmd, shell=True):
    """运行系统命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"
    except Exception as e:
        return False, "", str(e)

def force_kill_port_8000():
    """强制杀死所有占用端口8000的进程"""
    print("💀 强力清理端口8000...")
    print("=" * 40)

    # Windows命令：查找占用端口8000的进程
    print("🔍 查找占用端口8000的进程...")
    success, output, error = run_command("netstat -ano | findstr :8000")

    if not success or not output.strip():
        print("✅ 没有进程占用端口8000")
        return True

    print("📋 发现以下进程占用端口8000:")
    print(output.strip())

    # 提取PID
    pids = set()
    for line in output.strip().split('\n'):
        parts = line.strip().split()
        if len(parts) >= 5 and ':8000' in parts[1]:
            try:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)
            except:
                continue

    if not pids:
        print("❌ 无法提取PID信息")
        return False

    print(f"🎯 找到 {len(pids)} 个占用端口的进程PID: {', '.join(pids)}")

    # 逐个杀死进程
    killed_count = 0
    for pid in pids:
        print(f"💀 尝试杀死进程 PID {pid}...")

        # 先尝试温和终止
        success, _, _ = run_command(f"taskkill /PID {pid}")
        if success:
            print(f"   ✅ 温和终止 PID {pid}")
            killed_count += 1
        else:
            # 强制杀死
            success, _, _ = run_command(f"taskkill /F /PID {pid}")
            if success:
                print(f"   💀 强制杀死 PID {pid}")
                killed_count += 1
            else:
                print(f"   ❌ 无法杀死 PID {pid}")

    print(f"\n📊 成功清理了 {killed_count}/{len(pids)} 个进程")
    return killed_count > 0

def kill_all_python_uvicorn():
    """杀死所有Python uvicorn进程"""
    print("\n🐍 清理所有Python uvicorn进程...")
    print("=" * 40)

    # 查找所有包含uvicorn的python进程
    success, output, error = run_command('wmic process where "CommandLine like \'%uvicorn%\'" get ProcessId,CommandLine /format:csv')

    if success and output.strip():
        lines = output.strip().split('\n')
        pids = []

        for line in lines[1:]:  # 跳过标题行
            if 'uvicorn' in line and line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        pid = parts[-1].strip()
                        if pid.isdigit():
                            pids.append(pid)
                    except:
                        continue

        if pids:
            print(f"🎯 找到 {len(pids)} 个uvicorn进程: {', '.join(pids)}")

            for pid in pids:
                success, _, _ = run_command(f"taskkill /F /PID {pid}")
                if success:
                    print(f"   ✅ 已杀死 PID {pid}")
                else:
                    print(f"   ❌ 无法杀死 PID {pid}")
        else:
            print("✅ 没有找到uvicorn进程")
    else:
        print("⚠️ 无法查询Python进程")

def nuclear_option():
    """核选项：杀死所有Python进程（谨慎使用）"""
    print("\n☢️ 核选项：清理所有Python进程...")
    print("=" * 40)
    print("⚠️ 警告：这将关闭所有Python程序！")

    choice = input("❓ 确定要继续吗？这可能影响其他Python程序 (y/n): ").strip().lower()

    if choice not in ['y', 'yes', '是']:
        print("❌ 已取消核选项")
        return False

    # 杀死所有python.exe进程（除了当前脚本）
    current_pid = os.getpid()

    success, output, error = run_command("tasklist /FI \"IMAGENAME eq python.exe\" /FO CSV")

    if success and output.strip():
        lines = output.strip().split('\n')
        for line in lines[1:]:  # 跳过标题
            if 'python.exe' in line:
                try:
                    parts = [p.strip('"') for p in line.split('","')]
                    if len(parts) >= 2:
                        pid = parts[1]
                        if pid.isdigit() and int(pid) != current_pid:
                            success, _, _ = run_command(f"taskkill /F /PID {pid}")
                            if success:
                                print(f"   💀 已杀死Python进程 PID {pid}")
                except:
                    continue

    return True

def wait_for_port_release():
    """等待端口释放"""
    print("\n⏳ 等待端口8000释放...")
    print("=" * 40)

    for i in range(10, 0, -1):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=1)
            print(f"   ⏳ 端口仍被占用，等待 {i} 秒...")
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print("   ✅ 端口8000已释放！")
            return True
        except:
            print(f"   ❓ 端口状态不明，等待 {i} 秒...")
            time.sleep(1)

    print("   ⚠️ 端口可能仍被占用，但继续尝试...")
    return False

def verify_cleanup():
    """验证清理结果"""
    print("\n🔍 验证清理结果...")
    print("=" * 40)

    # 检查端口占用
    success, output, error = run_command("netstat -ano | findstr :8000")

    if not success or not output.strip():
        print("✅ 端口8000已完全释放")
        return True
    else:
        print("❌ 端口8000仍有进程占用:")
        print(output.strip())
        return False

def start_clean_server():
    """启动干净的服务器"""
    print("\n🚀 启动全新服务器...")
    print("=" * 40)

    print("📁 当前目录:", os.getcwd())

    # 检查必需文件
    if not os.path.exists("app/main.py"):
        print("❌ 未找到 app/main.py，请确保在backend目录中运行")
        return False

    print("✅ 找到app/main.py，准备启动...")
    print("\n" + "="*50)
    print("🎯 观察启动日志，确认路由注册成功：")
    print("="*50)

    try:
        # 启动uvicorn
        subprocess.run(["uvicorn", "app.main:app", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        return True
    except FileNotFoundError:
        print("❌ 找不到uvicorn命令，请安装: pip install uvicorn")
        return False

def main():
    print("☢️ Smart Video Platform - 强力端口清理工具")
    print("=" * 55)
    print("这个工具将强制清理端口8000上的所有进程")
    print("⚠️ 警告：可能会影响其他使用该端口的程序")

    choice = input(f"\n❓ 是否继续强力清理? (y/n): ").strip().lower()
    if choice not in ['y', 'yes', '是']:
        print("❌ 操作已取消")
        return

    # 步骤1：强制清理端口8000
    force_kill_port_8000()

    # 步骤2：清理Python uvicorn进程
    kill_all_python_uvicorn()

    # 步骤3：等待端口释放
    wait_for_port_release()

    # 步骤4：验证清理结果
    clean = verify_cleanup()

    if not clean:
        print("\n⚠️ 常规清理不完全，是否使用核选项？")
        nuclear_option()
        time.sleep(2)
        verify_cleanup()

    # 步骤5：启动服务器
    print(f"\n🎯 清理完成！")
    choice = input("❓ 是否立即启动新服务器? (y/n): ").strip().lower()

    if choice in ['y', 'yes', '是']:
        start_clean_server()
    else:
        print("\n📋 手动启动命令:")
        print("   cd D:\\reflective_video\\backend")
        print("   uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()