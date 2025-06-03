#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 模組化架構使用示例
展示如何使用新的模組化情感檢測系統
"""

import sys
import asyncio
import logging

# 設置路徑
sys.path.insert(0, '.')

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_1_basic_usage():
    """示例 1: 基本使用方法"""
    
    print("\n=== 示例 1: 基本使用方法 ===")
    
    # 導入所需模組
    from src.ai_engine.states import EmotionDetectorState
    from src.ai_engine.modules.dependency_manager import DependencyManager
    from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
    from src.ai_engine.modules.emotion_detector import EmotionDetector, DetectionConfig
    
    print("1. 創建依賴管理器")
    dep_manager = DependencyManager()
    
    print("2. 創建攝像頭配置")
    camera_config = CameraConfig(
        device_id=0,
        width=640,
        height=480,
        fps=30
    )
    
    print("3. 創建情感檢測配置")
    detection_config = DetectionConfig(
        confidence_threshold=0.7,
        enable_face_detection=True,
        enable_emotion_detection=True
    )
    
    print("4. 創建管理器實例")
    camera_manager = CameraManager(camera_config)
    emotion_detector = EmotionDetector(detection_config)
    
    print("✓ 基本組件創建成功")

def example_2_simple_state_machine():
    """示例 2: 使用簡化狀態機"""
    
    print("\n=== 示例 2: 使用簡化狀態機 ===")
    
    from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine, SimpleEmotionDetectorConfig
    from src.ai_engine.modules.emotion_detector import DetectionConfig
    
    print("1. 創建配置")
    detection_config = DetectionConfig(confidence_threshold=0.8)
    config = SimpleEmotionDetectorConfig(
        detection_config=detection_config,
        max_consecutive_failures=3,
        auto_retry=True
    )
    
    print("2. 創建狀態機")
    state_machine = SimpleEmotionDetectorStateMachine(config)
    
    print(f"3. 初始狀態: {state_machine.state.name}")
    print(f"4. 配置: {state_machine.config}")
    
    print("✓ 簡化狀態機創建成功")

async def example_3_async_operations():
    """示例 3: 異步操作"""
    
    print("\n=== 示例 3: 異步操作示例 ===")
    
    from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
    
    print("1. 創建異步狀態機")
    state_machine = SimpleEmotionDetectorStateMachine()
    
    print("2. 執行異步初始化")
    # 這裡只是演示，實際的異步方法需要在狀態機中實現
    await asyncio.sleep(0.1)  # 模擬異步操作
    
    print("✓ 異步操作完成")

def example_4_error_handling():
    """示例 4: 錯誤處理"""
    
    print("\n=== 示例 4: 錯誤處理示例 ===")
    
    from src.ai_engine.states import StateTransitionError, EmotionDetectorError
    from src.ai_engine.modules.camera_manager import CameraSetupError
    
    try:
        # 模擬可能的錯誤情況
        print("1. 測試錯誤處理機制")
        
        # 這些是異常類別的演示
        print(f"   - StateTransitionError: {StateTransitionError}")
        print(f"   - EmotionDetectorError: {EmotionDetectorError}")
        print(f"   - CameraSetupError: {CameraSetupError}")
        
        print("✓ 錯誤處理類別正常")
        
    except Exception as e:
        print(f"✗ 錯誤處理測試失敗: {e}")

def example_5_modular_benefits():
    """示例 5: 模組化的優勢展示"""
    
    print("\n=== 示例 5: 模組化架構優勢 ===")
    
    print("🔧 模組化架構的優勢:")
    print("  1. 清晰的責任分離")
    print("     - states.py: 狀態定義")
    print("     - modules/dependency_manager.py: 依賴管理")
    print("     - modules/camera_manager.py: 攝像頭管理")
    print("     - modules/emotion_detector.py: 情感檢測核心")
    print("     - simple_emotion_state_machine.py: 簡化狀態機")
    print("     - emotion_state_machine.py: 完整狀態機")
    
    print("\n  2. 易於測試和維護")
    print("     - 每個模組可以獨立測試")
    print("     - 減少模組間的耦合")
    print("     - 清晰的接口定義")
    
    print("\n  3. 可擴展性")
    print("     - 可以輕鬆添加新的狀態")
    print("     - 可以擴展檢測功能")
    print("     - 支持不同的配置方案")
    
    print("\n  4. 性能優化")
    print("     - 避免了單體架構的龐大文件")
    print("     - 支持延遲加載")
    print("     - 更好的記憶體管理")

async def main():
    """主函數"""
    
    print("LivePilotAI 模組化架構使用示例")
    print("=" * 50)
    
    try:
        # 執行各個示例
        example_1_basic_usage()
        example_2_simple_state_machine()
        await example_3_async_operations()
        example_4_error_handling()
        example_5_modular_benefits()
        
        print("\n" + "=" * 50)
        print("🎉 所有示例執行成功！")
        print("\n📚 接下來可以:")
        print("  1. 查看 MODULAR_REFACTORING_COMPLETION_REPORT.md")
        print("  2. 運行完整的測試套件")
        print("  3. 開始集成到主應用程序")
        
    except Exception as e:
        print(f"\n❌ 示例執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
