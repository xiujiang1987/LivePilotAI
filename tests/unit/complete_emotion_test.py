import cv2
import sys
import time
from pathlib import Path

# 設置路徑
sys.path.insert(0, str(Path.cwd() / 'src'))

print("🎭 LivePilotAI 完整情感檢測測試")
print("=" * 50)

try:
    # 導入所有模組
    from ai_engine.modules.camera_manager import CameraManager, CameraConfig
    from ai_engine.modules.face_detector import FaceDetector, DetectionConfig
    from ai_engine.emotion_detector import EmotionDetector
    print("✅ 所有模組導入成功")
    
    # 創建配置
    camera_config = CameraConfig(
        device_id=0,
        width=640,
        height=480,
        fps=30
    )
    
    detection_config = DetectionConfig(
        detection_method='haar',
        min_face_size=(30, 30),
        scale_factor=1.1,
        min_neighbors=5
    )
    
    # 初始化組件
    camera_manager = CameraManager(camera_config)
    face_detector = FaceDetector(detection_config)
    emotion_detector = EmotionDetector()
    
    print("✅ 所有組件初始化成功")
    
    # 檢查攝像頭
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 攝像頭不可用")
        exit()
    
    print("✅ 攝像頭已啟動")
    print("\n🎬 開始完整情感檢測測試...")
    print("💡 功能說明:")
    print("   - 即時人臉檢測")
    print("   - 7種情感識別 (快樂、悲傷、憤怒、恐懼、驚訝、厭惡、中性)")
    print("   - 實時性能監控")
    print("\n⌨️ 操作說明:")
    print("   - 按 'q' 鍵退出")
    print("   - 按 's' 鍵截圖")
    print("   - 按 'SPACE' 鍵暫停/恢復")
    
    # 性能統計
    frame_count = 0
    start_time = time.time()
    paused = False
    
    # 情感標籤映射
    emotion_labels = {
        0: '😠 Angry',
        1: '🤢 Disgust', 
        2: '😨 Fear',
        3: '😊 Happy',
        4: '😐 Neutral',
        5: '😢 Sad',
        6: '😮 Surprise'
    }
    
    # 顏色映射 (BGR)
    emotion_colors = {
        0: (0, 0, 255),      # 憤怒 - 紅色
        1: (0, 128, 128),    # 厭惡 - 青色
        2: (128, 0, 128),    # 恐懼 - 紫色
        3: (0, 255, 0),      # 快樂 - 綠色
        4: (128, 128, 128),  # 中性 - 灰色
        5: (255, 0, 0),      # 悲傷 - 藍色
        6: (0, 255, 255)     # 驚訝 - 黃色
    }
    
    print(f"\n⏰ 3秒後開始檢測...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("🚀 開始檢測！")
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("❌ 無法讀取攝像頭畫面")
                break
            
            frame_count += 1
            current_time = time.time()
            fps = frame_count / (current_time - start_time) if current_time > start_time else 0
            
            try:
                # 檢測人臉
                face_detections = face_detector.detect_faces(frame)
                
                # 處理每個檢測到的人臉
                for detection in face_detections:
                    x, y, w, h = detection.bbox
                    confidence = detection.confidence
                    
                    # 提取人臉區域
                    face_roi = frame[y:y+h, x:x+w]
                    
                    if face_roi.size > 0:
                        # 情感檢測
                        try:
                            emotion_result = emotion_detector.predict_emotion_from_image(face_roi)
                            emotion_idx = emotion_result['predicted_emotion']
                            emotion_confidence = emotion_result['confidence']
                            
                            # 獲取顏色和標籤
                            color = emotion_colors.get(emotion_idx, (255, 255, 255))
                            label = emotion_labels.get(emotion_idx, f'Unknown ({emotion_idx})')
                            
                            # 繪製人臉框
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                            
                            # 顯示情感標籤和信心度
                            emotion_text = f'{label} ({emotion_confidence:.2f})'
                            cv2.putText(frame, emotion_text, (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            
                            # 顯示人臉檢測信心度
                            face_text = f'Face: {confidence:.2f}'
                            cv2.putText(frame, face_text, (x, y+h+20), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                            
                        except Exception as e:
                            # 如果情感檢測失敗，只顯示人臉框
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, f'Face ({confidence:.2f})', (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(frame, f'Emotion Error: {str(e)[:20]}', (x, y+h+20), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
                
                # 顯示統計信息
                stats_y = 30
                cv2.putText(frame, f'Faces: {len(face_detections)}', (10, stats_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f'FPS: {fps:.1f}', (10, stats_y + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f'Frame: {frame_count}', (10, stats_y + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
            except Exception as e:
                print(f"⚠️ 檢測過程出錯: {e}")
                cv2.putText(frame, f"Detection Error", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        else:
            # 暫停狀態
            cv2.putText(frame, "PAUSED - Press SPACE to resume", 
                       (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # 顯示操作提示
        help_y = frame.shape[0] - 60
        cv2.putText(frame, "q:Quit | s:Save | SPACE:Pause", (10, help_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "LivePilotAI - Emotion Detection Test", (10, help_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 顯示結果
        cv2.imshow('LivePilotAI - Complete Emotion Detection Test', frame)
        
        # 處理按鍵
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 用戶退出測試")
            break
        elif key == ord('s'):
            filename = f'emotion_test_{int(time.time())}.jpg'
            cv2.imwrite(filename, frame)
            print(f"📸 截圖已保存: {filename}")
        elif key == ord(' '):  # 空格鍵
            paused = not paused
            print(f"⏸️ 測試{'暫停' if paused else '恢復'}")
    
    # 顯示最終統計
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print(f"\n📊 測試統計:")
    print(f"   總幀數: {frame_count}")
    print(f"   總時間: {total_time:.1f} 秒")
    print(f"   平均 FPS: {avg_fps:.1f}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("🎉 完整情感檢測測試完成！")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        cap.release()
        cv2.destroyAllWindows()
    except:
        pass
