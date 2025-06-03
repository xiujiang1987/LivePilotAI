#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 調試版啟動器
Debug version launcher to identify issues
"""

import sys
import os
import subprocess
from pathlib import Path

def debug_system():
    """調試系統狀況"""
    print("=" * 50)
    print("LivePilotAI 系統調試報告")
    print("=" * 50)
    
    # 檢查 Python 版本
    print(f"Python 版本: {sys.version}")
    print(f"當前工作目錄: {os.getcwd()}")
    
    # 檢查關鍵檔案
    key_files = [
        "main_day5.py",
        "main_fixed.py", 
        "launcher_fixed.py",
        "basic_test.py",
        "diagnose.py"
    ]
    
    print("\n檔案檢查:")
    for file in key_files:
        if Path(file).exists():
            print(f"[PASS] {file} - 存在")
        else:
            print(f"[FAIL] {file} - 不存在")
    
    # 檢查模組導入
    print("\n模組導入檢查:")
    modules = ["tkinter", "subprocess", "threading", "pathlib"]
    for module in modules:
        try:
            __import__(module)
            print(f"[PASS] {module} - 可導入")
        except ImportError as e:
            print(f"[FAIL] {module} - 導入失敗: {e}")
    
    # 嘗試執行基本命令
    print("\n命令執行測試:")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[PASS] Python 命令執行成功: {result.stdout.strip()}")
        else:
            print(f"[FAIL] Python 命令執行失敗")
    except Exception as e:
        print(f"[FAIL] 命令執行錯誤: {e}")
    
    # 檢查檔案權限
    print("\n檔案權限檢查:")
    for file in key_files:
        if Path(file).exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    f.read(100)  # 嘗試讀取前100個字符
                print(f"[PASS] {file} - 可讀取")
            except Exception as e:
                print(f"[FAIL] {file} - 讀取失敗: {e}")

def test_launcher_components():
    """測試啟動器組件"""
    print("\n" + "=" * 50)
    print("啟動器組件測試")
    print("=" * 50)
    
    # 測試主應用程式啟動
    print("\n1. 測試主應用程式啟動:")
    if Path("main_day5.py").exists():
        try:
            result = subprocess.run([sys.executable, "main_day5.py", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("[PASS] main_day5.py 可以執行")
                print(f"輸出: {result.stdout[:200]}...")
            else:
                print(f"[FAIL] main_day5.py 執行失敗")
                print(f"錯誤: {result.stderr}")
        except Exception as e:
            print(f"[FAIL] 執行錯誤: {e}")
    else:
        print("[FAIL] main_day5.py 不存在")
    
    # 測試系統測試
    print("\n2. 測試系統測試:")
    test_files = ["basic_test.py", "day5_simple_test.py", "simple_test.py"]
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    print(f"[PASS] {test_file} 執行成功")
                else:
                    print(f"[FAIL] {test_file} 執行失敗")
                    print(f"錯誤: {result.stderr[:200]}")
                break
            except Exception as e:
                print(f"[FAIL] {test_file} 執行錯誤: {e}")
        else:
            print(f"[SKIP] {test_file} 不存在")
    
    # 測試 OBS 整合
    print("\n3. 測試 OBS 整合:")
    if Path("obs_test_simple.py").exists():
        try:
            result = subprocess.run([sys.executable, "obs_test_simple.py"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("[PASS] OBS 測試執行成功")
            else:
                print(f"[FAIL] OBS 測試執行失敗")
                print(f"錯誤: {result.stderr[:200]}")
        except Exception as e:
            print(f"[FAIL] OBS 測試執行錯誤: {e}")
    else:
        print("[FAIL] obs_test_simple.py 不存在")

if __name__ == "__main__":
    try:
        debug_system()
        test_launcher_components()
        
        print("\n" + "=" * 50)
        print("調試完成！")
        print("如果看到這條消息，說明基本功能正常")
        print("請檢查上面的測試結果找出問題所在")
        print("=" * 50)
        
    except Exception as e:
        print(f"調試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
