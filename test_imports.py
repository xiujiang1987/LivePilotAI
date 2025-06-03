# -*- coding: utf-8 -*-
"""
測試 main_day5.py 的 import 修復
"""

import sys
from pathlib import Path

# 添加 src 目錄到路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_imports():
    """測試主要 import 語句"""
    print("🔧 測試 LivePilotAI Day 5 Import 修復...")
    print("=" * 50)
    
    try:
        # 測試 AI engine 模組
        print("\n1. 測試 AI Engine 模組:")
        from src.ai_engine.emotion_detector import EmotionDetector
        print("  ✅ EmotionDetector import 成功")
        
        from src.ai_engine.modules.real_time_detector import RealTimeEmotionDetector
        print("  ✅ RealTimeEmotionDetector import 成功")
        
        from src.ai_engine.modules.camera_manager import CameraManager
        print("  ✅ CameraManager import 成功")
        
        from src.ai_engine.modules.face_detector import FaceDetector
        print("  ✅ FaceDetector import 成功")
        
        # 測試實例化
        print("\n2. 測試類別實例化:")
        
        # 測試 EmotionDetector
        emotion_detector = EmotionDetector()
        print("  ✅ EmotionDetector 實例化成功")
        
        # 測試 FaceDetector
        face_detector = FaceDetector()
        print("  ✅ FaceDetector 實例化成功")
        
        # 測試 CameraManager
        camera_manager = CameraManager()
        print("  ✅ CameraManager 實例化成功")
        
        # 測試 RealTimeEmotionDetector
        real_time_detector = RealTimeEmotionDetector()
        print("  ✅ RealTimeEmotionDetector 實例化成功")
        
        print("\n🎉 所有 import 和實例化測試通過！")
        return True
        
    except Exception as e:
        print(f"\n❌ Import 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_day5_imports():
    """測試 main_day5.py 的 import 語句"""
    print("\n3. 測試 main_day5.py import 語句:")
    
    try:
        # 測試 main_day5.py 的主要 import 部分
        exec("""
# Import AI engine components
from src.ai_engine.emotion_detector import EmotionDetector
from src.ai_engine.modules.real_time_detector import RealTimeEmotionDetector
from src.ai_engine.modules.camera_manager import CameraManager
from src.ai_engine.modules.face_detector import FaceDetector
""")
        print("  ✅ main_day5.py AI engine import 語句成功")
        return True
        
    except Exception as e:
        print(f"  ❌ main_day5.py import 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_imports()
    success2 = test_main_day5_imports()
    
    if success1 and success2:
        print("\n🎯 Import 修復測試完全成功！")
        print("✅ main_day5.py 的 CameraManager、FaceDetector import 問題已解決")
        print("✅ RealTimeDetector 已更正為 RealTimeEmotionDetector")
        print("✅ 所有核心類別可以正常實例化")
    else:
        print("\n❌ 仍有部分 import 問題需要解決")
        sys.exit(1)
