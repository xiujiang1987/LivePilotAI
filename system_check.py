#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 系統狀態檢查
Simple System Status Check
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 8):
        print("[OK] Python 版本符合要求 (>= 3.8)")
        return True
    else:
        print("[ERROR] Python 版本過低，需要 3.8 或更高版本")
        return False

def check_files():
    """檢查必要文件"""
    print("\n檢查系統文件:")
    
    required_files = [
        "main_day5.py",
        "src/ui/__init__.py",
        "src/obs_integration/__init__.py",
        "src/ai_engine/__init__.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            all_exist = False
    
    return all_exist

def check_imports():
    """檢查模組導入"""
    print("\n檢查模組導入:")
    
    # Add src to path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    modules_to_test = [
        ("tkinter", "GUI 框架"),
        ("cv2", "OpenCV (視覺處理)"),
        ("numpy", "數值計算"),
        ("PIL", "圖像處理"),
    ]
    
    imported_count = 0
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"[OK] {module_name} - {description}")
            imported_count += 1
        except ImportError:
            print(f"[MISSING] {module_name} - {description}")
    
    return imported_count

def check_system_status():
    """檢查整體系統狀態"""
    print("=" * 60)
    print("LivePilotAI 系統狀態檢查")
    print("=" * 60)
    
    # 檢查 Python 版本
    python_ok = check_python_version()
    
    # 檢查文件
    files_ok = check_files()
    
    # 檢查導入
    import_count = check_imports()
    
    # 總結
    print("\n" + "=" * 60)
    print("系統狀態摘要")
    print("=" * 60)
    
    if python_ok:
        print("[OK] Python 環境")
    else:
        print("[ERROR] Python 環境")
    
    if files_ok:
        print("[OK] 系統文件")
    else:
        print("[WARNING] 部分文件缺失")
    
    print(f"[INFO] 可用模組: {import_count}/4")
    
    if python_ok and import_count >= 2:
        print("\n[STATUS] 系統基本可用")
        print("建議執行: python main_day5.py")
    else:
        print("\n[STATUS] 系統需要修復")
        print("建議安裝依賴: pip install -r requirements.txt")

if __name__ == "__main__":
    check_system_status()
