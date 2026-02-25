import cv2
import sys
import os
import time
from pathlib import Path

# 測試報告文件
report_file = "test_report.txt"

def write_report(message):
    """寫入測試報告"""
    with open(report_file, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

# 清空舊報告
with open(report_file, "w", encoding="utf-8") as f:
    f.write("LivePilotAI 實例測試報告\n")
    f.write("="*50 + "\n")

write_report("🎭 開始 LivePilotAI 實例測試")

# 環境檢查
write_report(f"Python 版本: {sys.version.split()[0]}")
write_report(f"OpenCV 版本: {cv2.__version__}")
write_report(f"工作目錄: {os.getcwd()}")

# 攝像頭檢查
write_report("\n📷 攝像頭測試:")
cap = cv2.VideoCapture(0)
camera_ok = False

if cap.isOpened():
    write_report("✅ 攝像頭初始化成功")
    ret, frame = cap.read()
    if ret:
        write_report(f"✅ 成功捕獲畫面，尺寸: {frame.shape}")
        cv2.imwrite("test_frame.jpg", frame)
        write_report("✅ 測試圖片已保存: test_frame.jpg")
        camera_ok = True
    else:
        write_report("❌ 無法捕獲畫面")
    cap.release()
else:
    write_report("❌ 攝像頭初始化失敗")

# 模組測試
write_report("\n📦 模組測試:")
sys.path.insert(0, str(Path.cwd() / 'src'))

modules_ok = True

try:
    from ai_engine.emotion_detector import EmotionDetector
    write_report("✅ EmotionDetector 導入成功")
    
    detector = EmotionDetector()
    write_report("✅ EmotionDetector 實例化成功")
    
    if hasattr(detector, 'predict_emotion_from_image'):
        write_report("✅ predict_emotion_from_image 方法可用")
    else:
        write_report("❌ predict_emotion_from_image 方法不可用")
        modules_ok = False
        
except Exception as e:
    write_report(f"❌ EmotionDetector 錯誤: {e}")
    modules_ok = False

try:
    from ai_engine.modules.face_detector import FaceDetector
    write_report("✅ FaceDetector 導入成功")
except Exception as e:
    write_report(f"❌ FaceDetector 錯誤: {e}")
    modules_ok = False

try:
    from ai_engine.modules.camera_manager import CameraManager
    write_report("✅ CameraManager 導入成功")
except Exception as e:
    write_report(f"❌ CameraManager 錯誤: {e}")
    modules_ok = False

# 簡單人臉檢測測試
if camera_ok:
    write_report("\n👤 人臉檢測測試:")
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        cap = cv2.VideoCapture(0)
        frame_count = 0
        face_detected = 0
        
        start_time = time.time()
        while time.time() - start_time < 3:  # 測試3秒
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    face_detected += 1
                    write_report(f"✅ 幀 {frame_count}: 檢測到 {len(faces)} 個人臉")
        
        cap.release()
        write_report(f"📊 人臉檢測統計: {face_detected}/{frame_count} 幀檢測到人臉")
        
    except Exception as e:
        write_report(f"❌ 人臉檢測測試失敗: {e}")

# 總結
write_report("\n📊 測試總結:")
write_report(f"攝像頭: {'✅ 正常' if camera_ok else '❌ 異常'}")
write_report(f"模組系統: {'✅ 正常' if modules_ok else '❌ 異常'}")

if camera_ok and modules_ok:
    write_report("🎉 系統已就緒，可進行完整測試！")
else:
    write_report("⚠️ 系統存在問題，需要修復")

write_report("📝 詳細報告已保存至: test_report.txt")
write_report("測試完成！")

print(f"\n請查看測試報告: {report_file}")
