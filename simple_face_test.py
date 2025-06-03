import cv2
import sys
from pathlib import Path

# 設置路徑
sys.path.insert(0, str(Path.cwd() / 'src'))

print("🎯 LivePilotAI 人臉檢測測試")
print("=" * 40)

try:
    # 導入模組
    from ai_engine.modules.face_detector import FaceDetector, DetectionConfig
    print("✅ 人臉檢測模組導入成功")
    
    # 創建檢測器
    config = DetectionConfig(detection_method='haar')
    detector = FaceDetector(config)
    print("✅ 人臉檢測器初始化成功")
    
    # 檢查攝像頭
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 攝像頭不可用，無法進行實時測試")
        print("💡 但人臉檢測模組已成功初始化")
        exit()
    
    print("✅ 攝像頭已啟動")
    print("\n🎬 開始即時人臉檢測...")
    print("💡 操作說明:")
    print("   - 請將臉部置於攝像頭前")
    print("   - 按 'q' 鍵退出測試")
    print("   - 按 's' 鍵截圖保存")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 無法讀取攝像頭畫面")
            break
        
        frame_count += 1
        
        try:
            # 檢測人臉
            detections = detector.detect_faces(frame)
            
            # 繪製檢測結果
            for detection in detections:
                x, y, w, h = detection.bbox
                confidence = detection.confidence
                
                # 繪製檢測框
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # 顯示信心度
                label = f'Face ({confidence:.2f})'
                cv2.putText(frame, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 顯示統計信息
            info_text = f'Faces: {len(detections)} | Frame: {frame_count}'
            cv2.putText(frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 顯示操作提示
            cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, frame.shape[0]-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        except Exception as e:
            print(f"⚠️ 檢測過程出錯: {e}")
            # 顯示錯誤信息
            cv2.putText(frame, f"Detection Error: {str(e)[:30]}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 顯示結果
        cv2.imshow('LivePilotAI - Face Detection Test', frame)
        
        # 處理按鍵
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 用戶退出測試")
            break
        elif key == ord('s'):
            filename = f'face_detection_test_{frame_count}.jpg'
            cv2.imwrite(filename, frame)
            print(f"📸 截圖已保存: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("🎉 人臉檢測測試完成！")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
finally:
    # 確保資源釋放
    try:
        cap.release()
        cv2.destroyAllWindows()
    except:
        pass
