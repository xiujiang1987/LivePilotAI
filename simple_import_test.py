#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from src.ai_engine.states import EmotionDetectorState
    print("SUCCESS: States import OK")
except Exception as e:
    print(f"ERROR in states: {e}")

try:
    from src.ai_engine.modules.dependency_manager import DependencyManager
    print("SUCCESS: DependencyManager import OK")
except Exception as e:
    print(f"ERROR in dependency_manager: {e}")

try:
    from src.ai_engine.modules.camera_manager import CameraManager
    print("SUCCESS: CameraManager import OK")
except Exception as e:
    print(f"ERROR in camera_manager: {e}")
