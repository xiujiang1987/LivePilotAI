import cv2
import sys
import os

print("=== LivePilotAI 系統狀態檢查 ===")
print(f"Python: {sys.version}")
print(f"OpenCV: {cv2.__version__}")
print(f"工作目錄: {os.getcwd()}")

# 檢查攝像頭
print("\n--- 攝像頭檢查 ---")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ 攝像頭可用")
    ret, frame = cap.read()
    if ret:
        print(f"✅ 成功捕獲畫面: {frame.shape}")
        # 保存一張測試圖片
        cv2.imwrite("camera_test.jpg", frame)
        print("✅ 測試圖片已保存: camera_test.jpg")
    else:
        print("❌ 無法捕獲畫面")
    cap.release()
else:
    print("❌ 攝像頭不可用")

# 檢查模組
print("\n--- 模組檢查 ---")
sys.path.insert(0, 'src')

try:
    from ai_engine.emotion_detector import EmotionDetector
    print("✅ EmotionDetector 導入成功")
    
    detector = EmotionDetector()
    print("✅ EmotionDetector 實例化成功")
    
    if hasattr(detector, 'predict_emotion_from_image'):
        print("✅ predict_emotion_from_image 方法存在")
    else:
        print("❌ predict_emotion_from_image 方法不存在")
        
except Exception as e:
    print(f"❌ EmotionDetector 錯誤: {e}")

try:
    from ai_engine.modules.face_detector import FaceDetector
    print("✅ FaceDetector 導入成功")
except Exception as e:
    print(f"❌ FaceDetector 錯誤: {e}")

try:
    from ai_engine.modules.camera_manager import CameraManager
    print("✅ CameraManager 導入成功")
except Exception as e:
    print(f"❌ CameraManager 錯誤: {e}")

print("\n=== 檢查完成 ===")
