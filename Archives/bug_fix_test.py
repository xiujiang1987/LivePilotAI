#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI BUG 修復測試工具
測試所有已知的 BUG 修復是否成功
"""

import sys
import os
import traceback
import logging
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """測試所有關鍵模組的匯入"""
    print("\n=== 測試模組匯入 ===")
    
    tests = [
        # UI 模組測試
        ("UI 狀態管理", "from src.ui import SystemStatusManager, StatusLevel"),
        ("UI 主面板", "from src.ui.main_panel import MainPanel"),
        ("UI 狀態指示器", "from src.ui.status_indicators import StatusIndicator, StatusPanel"),
        
        # OBS 整合測試
        ("OBS 管理器", "from src.obs_integration.obs_manager import OBSManager, OBSConfig"),
        ("OBS WebSocket", "from src.obs_integration.websocket_client import OBSWebSocketClient"),
        
        # AI 引擎測試
        ("情感檢測器", "from src.ai_engine.emotion_detector import EmotionDetector"),
        ("攝像頭管理", "from src.ai_engine.modules.camera_manager import CameraManager"),
        ("即時檢測器", "from src.ai_engine.modules.real_time_detector import RealTimeEmotionDetector"),
        
        # 核心模組測試
        ("配置管理", "from src.core.config_manager import ConfigManager"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}: 成功")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: 失敗 - {e}")
            failed += 1
    
    print(f"\n匯入測試結果: {passed} 成功, {failed} 失敗")
    return failed == 0

def test_dataclass_issues():
    """測試 dataclass 相關問題"""
    print("\n=== 測試 Dataclass 問題 ===")
    
    try:
        from src.ai_engine.modules.real_time_detector import RealTimeConfig
        config = RealTimeConfig()
        print("✅ RealTimeConfig 創建成功")
        
        # 測試預設值
        assert config.camera_config is not None
        assert config.detection_config is not None
        print("✅ 預設值設置正確")
        
        return True
    except Exception as e:
        print(f"❌ Dataclass 測試失敗: {e}")
        traceback.print_exc()
        return False

def test_websocket_compatibility():
    """測試 WebSocket 兼容性"""
    print("\n=== 測試 WebSocket 兼容性 ===")
    
    try:
        import websockets
        print(f"✅ WebSockets 版本: {websockets.__version__}")
        
        # 檢查是否為兼容版本
        if websockets.__version__.startswith("11.0"):
            print("✅ 使用兼容版本")
            return True
        else:
            print(f"⚠️ 版本可能不兼容: {websockets.__version__}")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket 測試失敗: {e}")
        return False

def test_dependencies():
    """測試必要依賴是否安裝"""
    print("\n=== 測試依賴套件 ===")
    
    dependencies = [
        ("tkinter", "GUI 框架"),
        ("cv2", "OpenCV"),
        ("numpy", "數值計算"),
        ("PIL", "圖像處理"),
        ("websockets", "WebSocket 客戶端"),
        ("psutil", "系統監控"),
    ]
    
    passed = 0
    failed = 0
    
    for module, description in dependencies:
        try:
            if module == "cv2":
                import cv2
            elif module == "PIL":
                from PIL import Image
            else:
                __import__(module)
            print(f"✅ {module}: {description}")
            passed += 1
        except ImportError:
            print(f"❌ {module}: {description} - 未安裝")
            failed += 1
    
    print(f"\n依賴測試結果: {passed} 成功, {failed} 失敗")
    return failed == 0

def test_file_structure():
    """測試關鍵檔案是否存在"""
    print("\n=== 測試檔案結構 ===")
    
    critical_files = [
        "main.py",
        "src/ui/__init__.py",
        "src/ui/status_indicators.py",
        "src/ui/main_panel.py",
        "src/obs_integration/obs_manager.py",
        "src/ai_engine/emotion_detector.py",
        "src/core/config_manager.py",
        "requirements.txt",
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 缺失")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺失檔案: {len(missing_files)}")
        return False
    else:
        print("\n✅ 所有關鍵檔案都存在")
        return True

def test_main_startup():
    """測試主程式是否能正常匯入"""
    print("\n=== 測試主程式啟動 ===")
    
    try:
        # 設置路徑
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        # 測試主程式類別
        from main import LivePilotAIApp
        print("✅ 主程式類別匯入成功")
        
        # 測試實例化 (不啟動 GUI)
        app = LivePilotAIApp()
        print("✅ 主程式實例化成功")
        
        return True
    except Exception as e:
        print(f"❌ 主程式測試失敗: {e}")
        traceback.print_exc()
        return False

def create_bug_fix_report():
    """創建 BUG 修復報告"""
    print("\n" + "="*60)
    print("LivePilotAI BUG 修復測試報告")
    print("="*60)
    
    tests = [
        ("模組匯入", test_imports),
        ("Dataclass 問題", test_dataclass_issues),
        ("WebSocket 兼容性", test_websocket_compatibility),
        ("依賴套件", test_dependencies),
        ("檔案結構", test_file_structure),
        ("主程式啟動", test_main_startup),
    ]
    
    results = {}
    total_passed = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                total_passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試執行失敗: {e}")
            results[test_name] = False
    
    # 總結報告
    print("\n" + "="*60)
    print("總結報告")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20} : {status}")
    
    print(f"\n整體結果: {total_passed}/{total_tests} 測試通過")
    
    if total_passed == total_tests:
        print("\n🎉 所有 BUG 修復測試都通過！")
        success_level = "EXCELLENT"
    elif total_passed >= total_tests * 0.8:
        print("\n✅ 大部分 BUG 已修復，系統基本可用")
        success_level = "GOOD"
    elif total_passed >= total_tests * 0.5:
        print("\n⚠️ 部分 BUG 已修復，仍需要進一步工作")
        success_level = "PARTIAL"
    else:
        print("\n❌ 多數測試失敗，需要更多修復工作")
        success_level = "POOR"
    
    # 保存報告
    report_data = {
        'timestamp': __import__('time').time(),
        'total_tests': total_tests,
        'passed_tests': total_passed,
        'success_rate': total_passed / total_tests,
        'success_level': success_level,
        'test_results': results
    }
    
    try:
        import json
        with open('bug_fix_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n📊 詳細報告已保存到: bug_fix_report.json")
    except Exception as e:
        print(f"⚠️ 無法保存報告: {e}")
    
    return success_level

def main():
    """主執行函數"""
    print("LivePilotAI BUG 修復驗證工具")
    print("開始執行全面測試...")
    
    try:
        result = create_bug_fix_report()
        
        # 根據結果給出建議
        if result == "EXCELLENT":
            print("\n🚀 建議: 系統已準備好正常使用！")
        elif result == "GOOD":
            print("\n👍 建議: 可以開始基本使用，注意觀察剩餘問題")
        elif result == "PARTIAL":
            print("\n🔧 建議: 需要解決剩餘的關鍵問題後再使用")
        else:
            print("\n🆘 建議: 需要全面檢查和修復後再使用")
            
    except Exception as e:
        print(f"\n💥 測試工具執行失敗: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
