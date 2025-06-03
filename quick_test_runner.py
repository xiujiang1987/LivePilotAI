#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 快速測試執行器
用於驗證系統狀態並運行基本測試
"""

import sys
import cv2
import numpy as np
from pathlib import Path

def test_environment():
    """測試環境"""
    print("🔍 環境檢測:")
    print(f"   Python 版本: {sys.version.split()[0]}")
    print(f"   OpenCV 版本: {cv2.__version__}")
    print(f"   NumPy 版本: {np.__version__}")
    print(f"   工作目錄: {Path.cwd()}")
    return True

def test_camera():
    """測試攝像頭"""
    print("\n📷 攝像頭測試:")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"   ✅ 攝像頭正常 - 分辨率: {frame.shape[1]}x{frame.shape[0]}")
            cap.release()
            return True
        else:
            print("   ❌ 無法讀取攝像頭畫面")
            cap.release()
            return False
    else:
        print("   ❌ 無法開啟攝像頭")
        return False

def test_modules():
    """測試模組導入"""
    print("\n📦 模組測試:")
    try:
        sys.path.insert(0, str(Path.cwd() / 'src'))
        
        from ai_engine.modules.camera_manager import CameraManager
        print("   ✅ CameraManager 導入成功")
        
        from ai_engine.modules.face_detector import FaceDetector
        print("   ✅ FaceDetector 導入成功")
        
        from ai_engine.emotion_detector import EmotionDetector
        print("   ✅ EmotionDetector 導入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 模組導入失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🎭 LivePilotAI 快速測試執行器")
    print("=" * 50)
    
    # 環境測試
    env_ok = test_environment()
    
    # 攝像頭測試
    camera_ok = test_camera()
    
    # 模組測試
    modules_ok = test_modules()
    
    # 總結
    print("\n📊 測試結果:")
    print(f"   環境檢測: {'✅ 通過' if env_ok else '❌ 失敗'}")
    print(f"   攝像頭: {'✅ 通過' if camera_ok else '❌ 失敗'}")
    print(f"   模組導入: {'✅ 通過' if modules_ok else '❌ 失敗'}")
    
    if all([env_ok, camera_ok, modules_ok]):
        print("\n🎉 所有測試通過！系統已就緒")
        print("💡 可以運行完整的情感檢測測試")
        return True
    else:
        print("\n⚠️ 部分測試失敗，請檢查系統配置")
        return False

if __name__ == "__main__":
    main()
