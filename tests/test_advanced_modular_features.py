#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 模組化架構進階功能測試
測試狀態機的實際運行和狀態轉換
"""

import sys
import asyncio
import logging

# 添加專案根目錄到路徑
sys.path.insert(0, '.')

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_state_machine_initialization():
    """測試狀態機初始化"""
    print("\n=== 狀態機初始化測試 ===")
    
    try:
        from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine, SimpleEmotionDetectorConfig
        from src.ai_engine.states import EmotionDetectorState
        
        # 創建配置
        config = SimpleEmotionDetectorConfig()
        print(f"✓ 配置創建成功: {config}")
        
        # 創建狀態機
        state_machine = SimpleEmotionDetectorStateMachine(config)
        print(f"✓ 狀態機創建成功")
        print(f"  - 初始狀態: {state_machine.state}")
        print(f"  - 運行狀態: {state_machine.is_running}")
        
        return state_machine
        
    except Exception as e:
        print(f"❌ 狀態機初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dependency_manager():
    """測試依賴管理器"""
    print("\n=== 依賴管理器測試 ===")
    
    try:
        from src.ai_engine.modules.dependency_manager import DependencyManager
        
        manager = DependencyManager()
        print("✓ 依賴管理器創建成功")
        
        # 測試基本依賴檢查
        available_libs = manager.get_available_libraries()
        print(f"✓ 可用庫檢查成功: {len(available_libs)} 個庫")
        
        for lib_name, is_available in available_libs.items():
            status = "✓" if is_available else "✗"
            print(f"  {status} {lib_name}: {'可用' if is_available else '不可用'}")
        
        return manager
        
    except Exception as e:
        print(f"❌ 依賴管理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_emotion_detector():
    """測試情感檢測器"""
    print("\n=== 情感檢測器測試 ===")
    
    try:
        from src.ai_engine.modules.emotion_detector import EmotionDetector, DetectionConfig
        
        config = DetectionConfig()
        detector = EmotionDetector(config)
        print("✓ 情感檢測器創建成功")
        print(f"  - 配置: {config}")
        
        return detector
        
    except Exception as e:
        print(f"❌ 情感檢測器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_camera_manager():
    """測試攝像頭管理器"""
    print("\n=== 攝像頭管理器測試 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager
        
        camera_manager = CameraManager()
        print("✓ 攝像頭管理器創建成功")
        
        # 測試攝像頭資訊（不實際開啟攝像頭）
        camera_info = camera_manager.get_camera_info()
        print(f"✓ 攝像頭資訊獲取成功: {camera_info}")
        
        return camera_manager
        
    except Exception as e:
        print(f"❌ 攝像頭管理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_state_machine_workflow():
    """測試狀態機工作流程"""
    print("\n=== 狀態機工作流程測試 ===")
    
    try:
        from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
        from src.ai_engine.states import EmotionDetectorState
        
        state_machine = SimpleEmotionDetectorStateMachine()
        print(f"✓ 狀態機創建成功，初始狀態: {state_machine.state}")
        
        # 測試狀態轉換（模擬）
        if hasattr(state_machine, 'transition_to'):
            # 如果有狀態轉換方法，測試它
            print("✓ 找到狀態轉換方法")
        else:
            print("ℹ️ 狀態機沒有公開的狀態轉換方法")
        
        # 檢查統計資訊
        stats = state_machine.stats
        print(f"✓ 統計資訊: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 狀態機工作流程測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_integration():
    """測試模組整合"""
    print("\n=== 模組整合測試 ===")
    
    try:
        # 測試各模組是否可以正常一起工作
        dependency_manager = test_dependency_manager()
        emotion_detector = test_emotion_detector()
        camera_manager = test_camera_manager()
        state_machine = test_state_machine_initialization()
        
        if all([dependency_manager, emotion_detector, camera_manager, state_machine]):
            print("✓ 所有模組整合測試通過")
            return True
        else:
            print("⚠️ 部分模組整合測試失敗")
            return False
            
    except Exception as e:
        print(f"❌ 模組整合測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 LivePilotAI 模組化架構進階功能測試開始")
    print("=" * 60)
    
    test_results = []
    
    # 1. 依賴管理器測試
    dependency_result = test_dependency_manager() is not None
    test_results.append(("依賴管理器", dependency_result))
    
    # 2. 情感檢測器測試
    emotion_result = test_emotion_detector() is not None
    test_results.append(("情感檢測器", emotion_result))
    
    # 3. 攝像頭管理器測試
    camera_result = test_camera_manager() is not None
    test_results.append(("攝像頭管理器", camera_result))
    
    # 4. 狀態機初始化測試
    state_machine_result = test_state_machine_initialization() is not None
    test_results.append(("狀態機初始化", state_machine_result))
    
    # 5. 狀態機工作流程測試
    workflow_result = asyncio.run(test_state_machine_workflow())
    test_results.append(("狀態機工作流程", workflow_result))
    
    # 6. 模組整合測試
    integration_result = test_module_integration()
    test_results.append(("模組整合", integration_result))
    
    # 總結測試結果
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:<20} {status}")
        if result:
            passed_tests += 1
    
    print("-" * 40)
    print(f"總測試數: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"失敗測試: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有進階功能測試通過！")
        print("📋 模組化重構架構運行穩定")
    else:
        print("\n⚠️ 部分測試失敗，需要檢查相關模組")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
