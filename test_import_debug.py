#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模組導入測試除錯
"""

import sys
import traceback

# 添加專案根目錄到路徑
sys.path.insert(0, '.')

def test_individual_imports():
    """測試各個模組的單獨導入"""
    
    print("=== 測試各個模組的單獨導入 ===")
    
    # 測試 states 模組
    try:
        from src.ai_engine.states import EmotionDetectorState
        print("✓ states 模組導入成功")
    except Exception as e:
        print(f"✗ states 模組導入失敗: {e}")
        traceback.print_exc()
    
    # 測試 dependency_manager 模組
    try:
        from src.ai_engine.modules.dependency_manager import DependencyManager
        print("✓ dependency_manager 模組導入成功")
    except Exception as e:
        print(f"✗ dependency_manager 模組導入失敗: {e}")
        traceback.print_exc()
    
    # 測試 camera_manager 模組
    try:
        from src.ai_engine.modules.camera_manager import CameraManager
        print("✓ camera_manager 模組導入成功")
    except Exception as e:
        print(f"✗ camera_manager 模組導入失敗: {e}")
        traceback.print_exc()
    
    # 測試 emotion_detector 模組
    try:
        from src.ai_engine.modules.emotion_detector import EmotionDetector
        print("✓ emotion_detector 模組導入成功")
    except Exception as e:
        print(f"✗ emotion_detector 模組導入失敗: {e}")
        traceback.print_exc()

def test_modules_init():
    """測試 modules 包的 __init__.py 導入"""
    
    print("\n=== 測試 modules 包導入 ===")
    
    try:
        from src.ai_engine.modules import DependencyManager, CameraManager, EmotionDetector
        print("✓ modules 包導入成功")
    except Exception as e:
        print(f"✗ modules 包導入失敗: {e}")
        traceback.print_exc()

def test_state_machine():
    """測試狀態機導入"""
    
    print("\n=== 測試狀態機導入 ===")
    
    try:
        from src.ai_engine.emotion_state_machine import EmotionDetectorStateMachine
        print("✓ 完整狀態機導入成功")
    except Exception as e:
        print(f"✗ 完整狀態機導入失敗: {e}")
        traceback.print_exc()
    
    try:
        from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
        print("✓ 簡化狀態機導入成功")
    except Exception as e:
        print(f"✗ 簡化狀態機導入失敗: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_individual_imports()
    test_modules_init()
    test_state_machine()
    print("\n=== 導入測試完成 ===")
