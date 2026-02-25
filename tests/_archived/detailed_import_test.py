#!/usr/bin/env python3
import sys
import traceback
sys.path.insert(0, '.')

print("=== 模組導入測試 ===")

# 測試 1: States 模組
print("\n1. 測試 states 模組...")
try:
    from src.ai_engine.states import EmotionDetectorState
    print("✓ SUCCESS: States import OK")
except Exception as e:
    print(f"✗ ERROR in states: {e}")
    traceback.print_exc()

# 測試 2: DependencyManager
print("\n2. 測試 dependency_manager 模組...")
try:
    from src.ai_engine.modules.dependency_manager import DependencyManager
    print("✓ SUCCESS: DependencyManager import OK")
except Exception as e:
    print(f"✗ ERROR in dependency_manager: {e}")
    traceback.print_exc()

# 測試 3: CameraManager  
print("\n3. 測試 camera_manager 模組...")
try:
    from src.ai_engine.modules.camera_manager import CameraManager
    print("✓ SUCCESS: CameraManager import OK")
except Exception as e:
    print(f"✗ ERROR in camera_manager: {e}")
    traceback.print_exc()

# 測試 4: EmotionDetector
print("\n4. 測試 emotion_detector 模組...")
try:
    from src.ai_engine.modules.emotion_detector import EmotionDetector
    print("✓ SUCCESS: EmotionDetector import OK")
except Exception as e:
    print(f"✗ ERROR in emotion_detector: {e}")
    traceback.print_exc()

# 測試 5: 模組包導入
print("\n5. 測試 modules 包導入...")
try:
    from src.ai_engine.modules import DependencyManager, CameraManager, EmotionDetector
    print("✓ SUCCESS: Modules package import OK")
except Exception as e:
    print(f"✗ ERROR in modules package: {e}")
    traceback.print_exc()

# 測試 6: 狀態機導入
print("\n6. 測試狀態機導入...")
try:
    from src.ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
    print("✓ SUCCESS: Simple state machine import OK")
except Exception as e:
    print(f"✗ ERROR in simple state machine: {e}")
    traceback.print_exc()

print("\n=== 測試完成 ===")
