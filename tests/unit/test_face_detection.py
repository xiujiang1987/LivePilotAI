import cv2
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from ai_engine.modules.face_detector import FaceDetector, DetectionConfig

print("🎯 簡單人臉檢測測試")
print("按 'q' 退出")

# 創建檢測器
config = DetectionConfig(detection_method='haar')
detector = FaceDetector(config)

# 啟動攝像頭
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 攝像頭不可用")
    exit()

print("✅ 攝像頭已啟動，開始人臉檢測...")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 檢測人臉
    detections = detector.detect_faces(frame)
    
    # 繪製檢測框
    for detection in detections:
        x, y, w, h = detection.bbox
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f'Face ({detection.confidence:.2f})', 
                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # 顯示結果
    cv2.putText(frame, f'Faces: {len(detections)}', (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('LivePilotAI - Face Detection Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🎉 人臉檢測測試完成！")
