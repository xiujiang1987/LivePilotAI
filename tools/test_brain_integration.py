# -*- coding: utf-8 -*-
"""
LivePilotAI 自主整合測試
驗證 AI Director 與 RealTimeEmotionDetector 的整合性
"""
import sys
import os
import time
import numpy as np
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_integration():
    print("🚀 開始自主整合測試...")
    
    # 1. 測試依賴檢查
    print("\n[1/3] 檢查依賴套件...")
    try:
        import speech_recognition
        import mediapipe
        import pyaudio
        print("  ✅ 關鍵套件 (SpeechRecognition, MediaPipe, PyAudio) 已安裝")
    except ImportError as e:
        print(f"  ❌ 缺少套件: {e}")
        return False

    # 2. 測試 AI Director 初始化 (大腦)
    print("\n[2/3] 初始化 AI Director (大腦)...")
    try:
        from ai_engine.modules.ai_director import AIDirector
        director = AIDirector()
        print("  ✅ AIDirector 初始化成功")
        print(f"  ℹ️  載入規則數: {len(director.rules)}")
    except Exception as e:
        print(f"  ❌ AIDirector 故障: {e}")
        return False

    # 3. 測試偵測器整合 (眼睛 -> 大腦)
    print("\n[3/3] 測試神經整合 (Simulated)...")
    try:
        # Mock frame (black image)
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test processing
        decision, metadata = director.process_frame(mock_frame)
        print(f"  ✅ 處理影格成功 via AIDirector")
        print(f"  ℹ️  Metadata: {metadata.keys()}")
        print(f"  ℹ️  Decision: {decision}")
        
    except Exception as e:
        print(f"  ❌ 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n✨ 測試完成: 系統邏輯核心運作正常")
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
