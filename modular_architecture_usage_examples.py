#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 模組化架構使用範例
展示如何使用重構後的模組化情感檢測引擎
"""

import sys
import asyncio
import logging
from typing import Optional

# 添加專案根目錄到路徑
sys.path.insert(0, '.')

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_basic_state_machine():
    """範例1: 基礎狀態機使用"""
    print("\n" + "="*60)
    print("📋 範例1: 基礎狀態機使用")
    print("="*60)
    
    try:
        # 導入必要模組
        from src.ai_engine.simple_emotion_state_machine import (
            SimpleEmotionDetectorStateMachine, 
            SimpleEmotionDetectorConfig
        )
        from src.ai_engine.states import EmotionDetectorState
        
        # 創建配置
        config = SimpleEmotionDetectorConfig()
        config.max_consecutive_failures = 3
        config.auto_retry = True
        config.retry_delay = 2.0
        
        # 創建狀態機
        state_machine = SimpleEmotionDetectorStateMachine(config)
        
        print(f"✅ 狀態機創建成功")
        print(f"   - 初始狀態: {state_machine.state.name}")
        print(f"   - 運行狀態: {state_machine.is_running}")
        print(f"   - 配置: 最大失敗次數={config.max_consecutive_failures}")
        
        # 顯示統計資訊
        stats = state_machine.stats
        print(f"   - 統計資訊: {stats}")
        
        return state_machine
        
    except Exception as e:
        print(f"❌ 基礎狀態機範例失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def example_2_dependency_check():
    """範例2: 依賴檢查"""
    print("\n" + "="*60)
    print("🔍 範例2: 系統依賴檢查")
    print("="*60)
    
    try:
        from src.ai_engine.modules.dependency_manager import DependencyManager
        
        # 執行依賴檢查
        installed, missing = DependencyManager.check_dependencies()
        
        print(f"✅ 依賴檢查完成")
        print(f"   - 已安裝套件: {len(installed)} 個")
        for pkg in installed:
            print(f"     ✓ {pkg}")
            
        print(f"   - 缺失套件: {len(missing)} 個")
        for pkg in missing:
            print(f"     ✗ {pkg}")
            
        if missing:
            print(f"\n💡 建議安裝命令:")
            for pkg in missing:
                print(f"   pip install {pkg}")
        else:
            print(f"\n🎉 所有必要依賴都已安裝！")
            
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ 依賴檢查範例失敗: {e}")
        return False


def example_3_emotion_detector():
    """範例3: 情感檢測器配置"""
    print("\n" + "="*60)
    print("🧠 範例3: 情感檢測器配置")
    print("="*60)
    
    try:
        from src.ai_engine.modules.emotion_detector import (
            EmotionDetector, 
            DetectionConfig
        )
        
        # 創建自定義配置
        config = DetectionConfig()
        config.model_confidence_threshold = 0.8
        config.enable_gpu = False  # 使用CPU模式
        
        # 創建檢測器
        detector = EmotionDetector(config)
        
        print(f"✅ 情感檢測器創建成功")
        print(f"   - 信心閾值: {config.model_confidence_threshold}")
        print(f"   - GPU模式: {config.enable_gpu}")
        print(f"   - 檢測器狀態: 已初始化")
        
        return detector
        
    except Exception as e:
        print(f"❌ 情感檢測器範例失敗: {e}")
        return None


def example_4_camera_manager():
    """範例4: 攝像頭管理"""
    print("\n" + "="*60)
    print("📷 範例4: 攝像頭管理器")
    print("="*60)
    
    try:
        from src.ai_engine.modules.camera_manager import (
            CameraManager, 
            CameraConfig
        )
        
        # 創建攝像頭配置
        config = CameraConfig()
        config.device_id = 0
        config.width = 1280
        config.height = 720
        config.fps = 30
        
        # 創建攝像頭管理器
        camera_manager = CameraManager(config)
        
        print(f"✅ 攝像頭管理器創建成功")
        print(f"   - 設備ID: {config.device_id}")
        print(f"   - 解析度: {config.width}x{config.height}")
        print(f"   - 幀率: {config.fps} FPS")
        
        # 獲取攝像頭資訊（不實際開啟）
        camera_info = camera_manager.get_camera_info()
        print(f"   - 攝像頭資訊: {camera_info}")
        
        return camera_manager
        
    except Exception as e:
        print(f"❌ 攝像頭管理器範例失敗: {e}")
        return None


def example_5_integrated_workflow():
    """範例5: 整合工作流程"""
    print("\n" + "="*60)
    print("🔄 範例5: 整合工作流程展示")
    print("="*60)
    
    try:
        # 步驟1: 依賴檢查
        print("步驟1: 檢查系統依賴...")
        dependencies_ok = example_2_dependency_check()
        
        if not dependencies_ok:
            print("⚠️ 部分依賴缺失，但繼續展示流程...")
        
        # 步驟2: 創建各個模組
        print("\n步驟2: 初始化各個模組...")
        
        # 狀態機
        state_machine = example_1_basic_state_machine()
        
        # 情感檢測器  
        emotion_detector = example_3_emotion_detector()
        
        # 攝像頭管理器
        camera_manager = example_4_camera_manager()
        
        # 步驟3: 檢查整合狀態
        print("\n步驟3: 檢查整合狀態...")
        
        modules_status = {
            '狀態機': state_machine is not None,
            '情感檢測器': emotion_detector is not None,
            '攝像頭管理器': camera_manager is not None,
        }
        
        print("模組狀態:")
        for module_name, status in modules_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {module_name}: {'正常' if status else '異常'}")
        
        success_count = sum(modules_status.values())
        total_count = len(modules_status)
        
        print(f"\n📊 整合結果: {success_count}/{total_count} 模組正常")
        
        if success_count == total_count:
            print("🎉 所有模組整合成功！架構可以正常運行")
            return True
        else:
            print("⚠️ 部分模組需要檢查，但基礎架構可用")
            return False
            
    except Exception as e:
        print(f"❌ 整合工作流程失敗: {e}")
        return False


def main():
    """主函數 - 運行所有範例"""
    print("🚀 LivePilotAI 模組化架構使用範例")
    print("展示重構後的情感檢測引擎如何使用")
    print("="*60)
    
    examples = [
        ("基礎狀態機", example_1_basic_state_machine),
        ("依賴檢查", example_2_dependency_check),
        ("情感檢測器", example_3_emotion_detector),
        ("攝像頭管理", example_4_camera_manager),
        ("整合工作流程", example_5_integrated_workflow),
    ]
    
    results = []
    
    for example_name, example_func in examples:
        try:
            print(f"\n🔄 運行範例: {example_name}")
            result = example_func()
            results.append((example_name, result is not None and result is not False))
        except Exception as e:
            print(f"❌ 範例 {example_name} 執行失敗: {e}")
            results.append((example_name, False))
    
    # 總結報告
    print("\n" + "="*60)
    print("📊 範例執行總結")
    print("="*60)
    
    success_count = 0
    for example_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{example_name:<20} {status}")
        if success:
            success_count += 1
    
    total_examples = len(results)
    success_rate = success_count / total_examples * 100
    
    print("-" * 40)
    print(f"成功範例: {success_count}/{total_examples}")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_count >= 3:  # 至少3個範例成功
        print("\n🎉 模組化架構展示成功！")
        print("💡 LivePilotAI 情感檢測引擎已成功重構為模組化架構")
        print("🚀 可以開始使用新的模組化架構進行開發")
    else:
        print("\n⚠️ 部分範例需要檢查")
        print("💡 請檢查依賴安裝和模組配置")
    
    print("\n📝 使用說明:")
    print("1. 根據需要導入相應的模組")
    print("2. 創建適當的配置對象")
    print("3. 初始化所需的管理器或檢測器")
    print("4. 根據狀態機流程執行情感檢測")
    
    return success_count >= 3


if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("✅ 模組化架構範例展示完成")
    else:
        print("⚠️ 部分功能需要進一步配置")
    print("="*60)
