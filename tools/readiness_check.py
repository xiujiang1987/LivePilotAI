#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI Day 5 準備就緒檢查
確保所有 Day 4 功能正常，為 Day 5 開發做準備
"""

import sys
import os
from pathlib import Path
import time

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def check_system_readiness():
    """檢查系統準備狀態"""
    print("🔍 LivePilotAI Day 5 準備就緒檢查")
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
    
    # 檢查 2: Day 4 核心模組
    print("\n🔧 檢查 2: Day 4 核心模組")
    try:
        from ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        from ai_engine.modules.real_time_detector import RealTimeEmotionDetector, RealTimeConfig
        from ai_engine.emotion_detector import EmotionDetector
        print("  ✅ 所有 Day 4 核心模組導入成功")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ Day 4 模組檢查失敗: {e}")
    
    # 檢查 3: 模組實例化
    print("\n🏗️ 檢查 3: 模組實例化")
    try:
        config = CameraConfig(device_id=0, width=640, height=480, fps=30)
        camera = CameraManager(config)
        
        detection_config = DetectionConfig(detection_method='haar')
        face_detector = FaceDetector(detection_config)
        
        emotion_detector = EmotionDetector()
        
        rt_config = RealTimeConfig(camera_device_id=0)
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
        "test_day4_simple.py",
        "demo_day4.py"
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
    
    # 檢查 6: Day 5 準備目錄
    print("\n📂 檢查 6: Day 5 開發準備")
    day5_dirs = [
        "src/ai_engine/modules",
        "tests",
        "docs",
        "logs"
    ]
    
    for dir_path in day5_dirs:
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
    
    checks_passed += 1  # Day 5 準備總是通過
    
    # 總結報告
    print("\n" + "=" * 60)
    print("📊 Day 5 準備就緒檢查結果")
    print(f"✅ 通過檢查: {checks_passed}/{total_checks}")
    print(f"📈 準備完成度: {checks_passed/total_checks*100:.1f}%")
    
    if checks_passed >= total_checks * 0.8:  # 80% 以上通過
        print("\n🎉 Day 5 開發準備就緒！")
        print("🚀 可以開始 Day 5 高級檢測功能開發")
        print("\n📋 Day 5 主要任務:")
        print("  • 情感強度分析模組")
        print("  • 多人臉追蹤系統")
        print("  • 進階視覺化引擎")
        print("  • 性能基準測試")
        
        print("\n💡 建議開發順序:")
        print("  1. 先實現情感強度分析")
        print("  2. 再開發多人臉追蹤")
        print("  3. 最後整合視覺化")
        print("  4. 進行完整測試驗證")
        
        return True
    else:
        print("\n⚠️ 部分檢查未通過，建議先解決問題")
        print("💬 如有問題，請檢查依賴安裝和檔案完整性")
        return False

def display_day5_roadmap():
    """顯示 Day 5 開發路線圖"""
    print("\n🗺️ Day 5 開發路線圖")
    print("=" * 60)
    
    roadmap = [
        ("09:00-10:30", "情感強度分析模組設計與實現"),
        ("10:30-12:00", "多人臉追蹤系統開發"),
        ("13:00-14:30", "進階視覺化引擎創建"),
        ("14:30-16:00", "模組整合與測試"),
        ("16:00-17:00", "性能優化與基準測試"),
        ("17:00-17:30", "文檔更新與日報撰寫")
    ]
    
    for time_slot, task in roadmap:
        print(f"⏰ {time_slot} - {task}")
    
    print(f"\n🎯 Day 5 預期產出:")
    print("  📄 新增 3-4 個核心模組檔案")
    print("  🧪 完整的測試驗證套件")
    print("  📊 性能基準測試報告")
    print("  📚 技術文檔更新")

if __name__ == "__main__":
    print("🚀 開始 Day 5 準備檢查...")
    time.sleep(1)
    
    readiness = check_system_readiness()
    
    if readiness:
        display_day5_roadmap()
        print(f"\n🎊 Day 4 → Day 5 過渡準備完成！")
        print(f"⭐ LivePilotAI 繼續向前，創造 AI 的未來！")
    else:
        print(f"\n🔧 請先解決上述問題，再進行 Day 5 開發")
    
    print("\n" + "=" * 60)
    print("✨ 感謝使用 LivePilotAI 開發系統！")
