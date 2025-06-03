#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 核心功能實時測試
簡化版本，專注於驗證核心功能是否正常運作
"""

import cv2
import sys
import time
from pathlib import Path

# 設置路徑
sys.path.insert(0, str(Path.cwd() / 'src'))

print("🎭 LivePilotAI 核心功能實時測試")
print("=" * 40)

def test_basic_camera():
    """基本攝像頭測試"""
    print("📷 基本攝像頭測試...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 攝像頭無法開啟")
        return False
    
    print("✅ 攝像頭已開啟")
    
    # 讀取幾幀測試
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"✅ 成功讀取第 {i+1} 幀，尺寸: {frame.shape}")
        else:
            print(f"❌ 無法讀取第 {i+1} 幀")
            cap.release()
            return False
    
    cap.release()
    print("✅ 基本攝像頭測試通過")
    return True

def test_face_detection():
    """基本人臉檢測測試"""
    print("\n👤 基本人臉檢測測試...")
    
    try:
        # 使用 OpenCV 內建的人臉檢測
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ 攝像頭無法開啟")
            return False
        
        print("✅ 人臉檢測器已載入")
        print("🎥 開始 5 秒人臉檢測測試...")
        
        start_time = time.time()
        frame_count = 0
        face_count = 0
        
        while time.time() - start_time < 5:  # 測試 5 秒
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 檢測人臉
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                face_count += 1
                print(f"✅ 幀 {frame_count}: 檢測到 {len(faces)} 個人臉")
            
            # 繪製人臉框
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # 顯示統計
            cv2.putText(frame, f'Frames: {frame_count}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f'Faces: {len(faces)}', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f'Test: {5-(time.time()-start_time):.1f}s', (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"📊 測試結果:")
        print(f"   總幀數: {frame_count}")
        print(f"   檢測到人臉的幀數: {face_count}")
        print(f"   檢測率: {(face_count/frame_count*100):.1f}%" if frame_count > 0 else "N/A")
        
        return True
        
    except Exception as e:
        print(f"❌ 人臉檢測測試失敗: {e}")
        return False

def test_emotion_modules():
    """測試情感檢測模組"""
    print("\n🎭 情感檢測模組測試...")
    
    try:
        from ai_engine.emotion_detector import EmotionDetector
        emotion_detector = EmotionDetector()
        print("✅ EmotionDetector 模組載入成功")
        
        # 測試模組方法
        if hasattr(emotion_detector, 'predict_emotion_from_image'):
            print("✅ predict_emotion_from_image 方法可用")
        else:
            print("❌ predict_emotion_from_image 方法不可用")
            
        return True
        
    except Exception as e:
        print(f"❌ 情感檢測模組測試失敗: {e}")
        return False

def main():
    """主測試流程"""
    print("開始核心功能測試...")
    
    # 1. 基本攝像頭測試
    camera_ok = test_basic_camera()
    
    # 2. 人臉檢測測試
    face_ok = test_face_detection() if camera_ok else False
    
    # 3. 情感檢測模組測試
    emotion_ok = test_emotion_modules()
    
    # 總結
    print(f"\n📊 測試總結:")
    print(f"   攝像頭: {'✅ 通過' if camera_ok else '❌ 失敗'}")
    print(f"   人臉檢測: {'✅ 通過' if face_ok else '❌ 失敗'}")
    print(f"   情感模組: {'✅ 通過' if emotion_ok else '❌ 失敗'}")
    
    if all([camera_ok, face_ok, emotion_ok]):
        print("\n🎉 所有核心功能測試通過！")
        print("💡 系統已就緒，可以運行完整測試")
    else:
        print("\n⚠️ 部分功能測試失敗")
    
    return all([camera_ok, face_ok, emotion_ok])

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'='*40}")
        print("測試完成！" if success else "測試發現問題！")
    except KeyboardInterrupt:
        print("\n👋 用戶中斷測試")
    except Exception as e:
        print(f"\n❌ 測試過程出錯: {e}")
        import traceback
        traceback.print_exc()
