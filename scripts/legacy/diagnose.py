#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 診斷工具
用於診斷啟動失敗的具體原因
"""

import sys
import os
import traceback
from pathlib import Path

def diagnose_main_app():
    """診斷主應用程式"""
    print("=== 診斷主應用程式 ===")
    
    try:
        # 檢查檔案是否存在
        if not Path("main_day5.py").exists():
            print("❌ main_day5.py 檔案不存在")
            return False
            
        print("✅ main_day5.py 檔案存在")
        
        # 檢查基本導入
        try:
            import tkinter
            print("✅ tkinter 可用")
        except ImportError as e:
            print(f"❌ tkinter 導入失敗: {e}")
            return False
            
        # 嘗試導入模組
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        try:
            from ui import MainControlPanel
            print("✅ UI 模組可導入")
        except ImportError as e:
            print(f"❌ UI 模組導入失敗: {e}")
            print(f"   檢查路徑: {src_path}")
            return False
            
        try:
            from obs_integration import OBSManager
            print("✅ OBS 整合模組可導入")
        except ImportError as e:
            print(f"❌ OBS 整合模組導入失敗: {e}")
            return False
            
        print("✅ 主應用程式基本診斷通過")
        return True
        
    except Exception as e:
        print(f"❌ 主應用程式診斷失敗: {e}")
        traceback.print_exc()
        return False

def diagnose_dependencies():
    """診斷依賴套件"""
    print("\n=== 診斷依賴套件 ===")
    
    required_packages = [
        'tkinter',
        'cv2',
        'numpy', 
        'PIL',
        'asyncio',
        'threading',
        'json',
        'pathlib'
    ]
    
    available_count = 0
    for package in required_packages:
        try:
            if package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"✅ {package}")
            available_count += 1
        except ImportError:
            print(f"❌ {package} - 需要安裝")
            
    print(f"\n套件可用性: {available_count}/{len(required_packages)}")
    return available_count >= len(required_packages) * 0.8

def diagnose_file_structure():
    """診斷檔案結構"""
    print("\n=== 診斷檔案結構 ===")
    
    required_files = [
        "main_day5.py",
        "src/ui/__init__.py",
        "src/obs_integration/__init__.py", 
        "src/ai_engine/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
            
    return len(missing_files) == 0

def diagnose_encoding():
    """診斷編碼問題"""
    print("\n=== 診斷編碼問題 ===")
    
    try:
        # 測試 Unicode 字符
        test_chars = ['🚀', '✅', '❌', '🧪', '📺']
        for char in test_chars:
            print(f"Unicode 測試: {char}")
        print("✅ Unicode 字符支援正常")
        return True
    except UnicodeEncodeError:
        print("❌ Unicode 編碼問題")
        return False

def run_simple_test():
    """執行簡單測試"""
    print("\n=== 執行簡單測試 ===")
    
    try:
        # 測試 tkinter
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隱藏視窗
        root.destroy()
        print("✅ tkinter 基本功能正常")
        
        # 測試檔案讀取
        with open("main_day5.py", 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 檔案讀取正常 (長度: {len(content)})")
        
        return True
    except Exception as e:
        print(f"❌ 簡單測試失敗: {e}")
        return False

def main():
    """主診斷函數"""
    print("LivePilotAI 診斷工具")
    print("=" * 50)
    
    # 執行所有診斷
    results = {
        'main_app': diagnose_main_app(),
        'dependencies': diagnose_dependencies(), 
        'file_structure': diagnose_file_structure(),
        'encoding': diagnose_encoding(),
        'simple_test': run_simple_test()
    }
    
    # 總結
    print("\n" + "=" * 50)
    print("診斷結果總結")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} {test_name}")
    
    print(f"\n總體狀況: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有診斷都通過！系統應該可以正常運行。")
    elif passed >= total * 0.8:
        print("⚠️ 大部分功能正常，可能有小問題需要修復。")
    else:
        print("❌ 系統有重大問題，需要修復後才能正常使用。")
    
    # 提供修復建議
    print("\n修復建議:")
    
    if not results['dependencies']:
        print("- 安裝缺失的依賴套件: pip install -r requirements.txt")
        
    if not results['file_structure']:
        print("- 檢查檔案結構，確保所有必要檔案都存在")
        
    if not results['encoding']:
        print("- 設定正確的終端編碼: chcp 65001")
        
    if not results['main_app']:
        print("- 檢查模組導入路徑和檔案權限")

if __name__ == "__main__":
    main()
