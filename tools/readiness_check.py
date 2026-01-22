#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 專案健康檢查 (v1.1.0)
確保專案環境完整，包含核心模組與模型
"""

import sys
import os
from pathlib import Path
import time

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def check_system_readiness():
    """檢查系統狀態"""
    print("🔍 LivePilotAI 專案健康檢查 (v1.1.0)")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 6
    
    # 檢查 1: 基礎環境
    print("\n📚 檢查 1: 基礎環境")
    try:
        import cv2
        import numpy as np
        import tensorflow as tf
        print(f"  ✅ OpenCV: {cv2.__version__}")
        print(f"  ✅ NumPy: {np.__version__}")
        print(f"  ✅ TensorFlow: {tf.__version__}")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ 基礎環境檢查失敗: {e}")
    
    # 檢查 2: 核心模組 (v1.0)
    print("\n🔧 檢查 2: 核心模組 (v1.0)")
    try:
        from ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        from ai_engine.modules.real_time_detector import RealTimeEmotionDetector, RealTimeConfig
        from ai_engine.emotion_detector import EmotionDetector
        print("  ✅ 所有核心模組導入成功")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ 模組檢查失敗: {e}")
    
    # 檢查 3: 模組實例化
    print("\n🏗️ 檢查 3: 模組實例化")
    try:
        config = CameraConfig(device_id=0, width=640, height=480, fps=30)
        camera = CameraManager(config)
        
        detection_config = DetectionConfig(enable_dnn=False)
        face_detector = FaceDetector(detection_config)
        
        emotion_detector = EmotionDetector()
        
        rt_config = RealTimeConfig(camera_config=config)
        rt_detector = RealTimeEmotionDetector(rt_config)
        
        print("  ✅ 所有模組實例化成功")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ 模組實例化失敗: {e}")
    
    # 檢查 4: 攝像頭硬體
    print("\n📹 檢查 4: 攝像頭硬體")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"  ✅ 攝像頭正常工作，解析度: {w}x{h}")
                checks_passed += 1
            else:
                print("  ⚠️ 攝像頭無法讀取影像")
            cap.release()
        else:
            print("  ⚠️ 攝像頭設備不可用")
    except Exception as e:
        print(f"  ❌ 攝像頭檢查失敗: {e}")
    
    # 檢查 5: 檔案完整性
    print("\n📁 檢查 5: 關鍵檔案完整性")
    required_files = [
        "src/ai_engine/modules/camera_manager.py",
        "src/ai_engine/modules/face_detector.py",
        "src/ai_engine/modules/real_time_detector.py",
        "src/ai_engine/emotion_detector.py",
        "tests/simple_face_test.py",
        "demos/demo_basic.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 檔案不存在")
            missing_files.append(file_path)
    
    if not missing_files:
        print("  ✅ 所有關鍵檔案完整")
        checks_passed += 1
    else:
        print(f"  ❌ 缺少 {len(missing_files)} 個關鍵檔案")
    
    # 檢查 6: 專案目錄結構
    print("\n📂 檢查 6: 專案目錄結構")
    
    required_dirs = [
        "src/ai_engine/modules",
        "tests",
        "docs",
        "logs"
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}/ 目錄存在")
        else:
            print(f"  ⚠️ {dir_path}/ 目錄不存在，將自動創建")
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ 已創建 {dir_path}/ 目錄")
            except Exception as e:
                print(f"  ❌ 創建目錄失敗: {e}")
    
    checks_passed += 1
    
    # 總結報告
    print("\n" + "=" * 60)
    print("📊 檢查結果總結")
    print(f"✅ 通過檢查: {checks_passed}/{total_checks}")
    print(f"📈 系統健康度: {checks_passed/total_checks*100:.1f}%")
    
    if checks_passed >= total_checks * 0.8:
        print("\n🎉 系統檢查通過！")
        print("🚀 v1.1.0 核心功能就緒")
        return True
    else:
        print("\n⚠️ 部分檢查未通過，建議先解決問題")
        print("💬 如有問題，請檢查依賴安裝和檔案完整性")
        return False

if __name__ == "__main__":
    print("🚀 啟動系統檢查程序...")
    time.sleep(1)
    
    readiness = check_system_readiness()
    
    if readiness:
        print(f"\n🎊 系統狀態良好！ (v1.1.0 Ready)")
        print(f"⭐ LivePilotAI 可以正常運行")
    else:
        print(f"\n🔧 請先解決上述問題")
    
    print("\n" + "=" * 60)
    print("✨ LivePilotAI System Check Complete")
