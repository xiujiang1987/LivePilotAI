import os
import sys
import subprocess
import time

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    import io
    # Set console code page to UTF-8
    os.system('chcp 65001 >nul')
    # Reconfigure stdout/stderr to use utf-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("================================================")
    print("         LivePilotAI 專案快速啟動")
    print("================================================")
    print("")
    print(f"當前目錄: {os.getcwd()}")
    print(f"Python: {sys.executable}")
    print("")

def run_command(cmd):
    print(f"\n🚀 執行: {cmd} ...\n")
    subprocess.run(cmd, shell=True)
    input("\n按 Enter 鍵繼續...")

def main():
    # Ensure we are in the project root
    # This script is in scripts/, so project root is one level up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    while True:
        clear_screen()
        print_header()
        print("[3] 可用操作:")
        print("   1. 啟動主程式 (Main Panel)")
        print("   2. 測試場景管理器")
        print("   3. 運行完整系統測試")
        print("   4. 安裝依賴包")
        print("   5. 查看專案狀態")
        print("   6. 打開專案資料夾")
        print("   0. 退出")
        print("")

        choice = input("請選擇操作 (1-6, 0): ").strip()

        if choice == '1':
            run_command(f'"{sys.executable}" main.py')
        elif choice == '2':
            run_command(f'"{sys.executable}" src/obs_integration/scene_manager.py')
        elif choice == '3':
            run_command(f'"{sys.executable}" test_system.py')
        elif choice == '4':
            run_command(f'"{sys.executable}" -m pip install -r requirements.txt')
        elif choice == '5':
            print("\n📋 專案狀態:")
            print(f"   專案位置: {os.getcwd()}")
            print("   Git狀態:")
            subprocess.run("git status --porcelain", shell=True)
            input("\n按 Enter 鍵繼續...")
        elif choice == '6':
            print("\n📂 打開專案資料夾...")
            os.startfile('.')
        elif choice == '0':
            print("\n👋 感謝使用 LivePilotAI！")
            time.sleep(1)
            sys.exit(0)
        else:
            print("\n❌ 無效選擇，請重新輸入")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已終止")
        sys.exit(0)
