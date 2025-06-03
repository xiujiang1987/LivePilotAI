# -*- coding: utf-8 -*-
"""
LivePilotAI Day 4 演示腳本
展示即時人臉檢測和情感識別功能
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simple_demo():
    """簡單演示"""
    logger.info("LivePilotAI 即時情感檢測演示")
    logger.info("=" * 40)
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from src.ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        from src.ai_engine.emotion_detector import EmotionDetector
        import cv2
        import numpy as np
        
        # 初始化組件
        logger.info("正在初始化系統組件...")
        
        camera_config = CameraConfig(
            device_id=0,
            width=640,
            height=480,
            fps=24
        )
        camera = CameraManager(camera_config)
        
        detection_config = DetectionConfig(
            enable_dnn=False,  # 使用較快的 Haar Cascade
            confidence_threshold=0.5
        )
        face_detector = FaceDetector(detection_config)
        emotion_detector = EmotionDetector()
        
        # 初始化攝像頭
        if not camera.initialize_camera():
            logger.error("攝像頭初始化失敗")
            return False
        
        logger.info("✓ 系統初始化成功")
        logger.info("正在啟動即時檢測...")
        
        # 統計變數
        frame_count = 0
        face_count = 0
        emotion_count = 0
        start_time = time.time()
        
        # 創建顯示窗口
        window_name = "LivePilotAI - 即時情感檢測 (按 'q' 退出, 'p' 暫停)"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        
        def process_frame(frame):
            nonlocal frame_count, face_count, emotion_count
            
            try:
                frame_count += 1
                display_frame = frame.copy()
                
                # 檢測人臉
                faces = face_detector.detect_faces(frame)
                face_count += len(faces)
                
                # 處理每個檢測到的人臉
                for i, face in enumerate(faces):
                    # 繪製人臉框
                    cv2.rectangle(
                        display_frame,
                        (face.x, face.y),
                        (face.x + face.width, face.y + face.height),
                        (0, 255, 0), 2
                    )
                    
                    # 提取人臉區域進行情感檢測
                    face_roi = face_detector.get_face_roi(frame, face)
                    if face_roi is not None:
                        try:
                            emotion_result = emotion_detector.predict_emotion_from_image(face_roi)
                            emotion_count += 1
                            
                            # 顯示情感標籤
                            emotion = emotion_result['dominant_emotion']
                            confidence = emotion_result['confidence']
                            
                            # 選擇顏色
                            color = get_emotion_color(emotion)
                            
                            # 更新邊框顏色
                            cv2.rectangle(
                                display_frame,
                                (face.x, face.y),
                                (face.x + face.width, face.y + face.height),
                                color, 2
                            )
                            
                            # 繪製情感標籤
                            label = f"{emotion} ({confidence:.2f})"
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                            
                            # 標籤背景
                            cv2.rectangle(
                                display_frame,
                                (face.x, face.y - 25),
                                (face.x + label_size[0] + 10, face.y),
                                color, -1
                            )
                            
                            # 標籤文字
                            cv2.putText(
                                display_frame, label,
                                (face.x + 5, face.y - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                            )
                            
                        except Exception as e:
                            logger.warning(f"情感檢測失敗: {e}")
                
                # 添加系統信息
                runtime = time.time() - start_time
                fps = frame_count / runtime if runtime > 0 else 0
                
                info_text = [
                    f"FPS: {fps:.1f}",
                    f"Frames: {frame_count}",
                    f"Faces: {face_count}",
                    f"Emotions: {emotion_count}",
                    f"Runtime: {runtime:.1f}s"
                ]
                
                for i, text in enumerate(info_text):
                    cv2.putText(
                        display_frame, text,
                        (10, 30 + i * 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                    )
                
                # 顯示幀
                cv2.imshow(window_name, display_frame)
                
                # 處理按鍵
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    return "quit"
                elif key == ord('p'):
                    logger.info("演示已暫停，按任意鍵繼續...")
                    cv2.waitKey(0)
                    logger.info("演示已恢復")
                
            except Exception as e:
                logger.error(f"幀處理錯誤: {e}")
        
        # 啟動即時捕獲
        success = camera.start_real_time_capture(process_frame)
        if not success:
            logger.error("無法啟動即時捕獲")
            return False
        
        logger.info("✓ 即時檢測已啟動")
        logger.info("按 'q' 退出演示，按 'p' 暫停/恢復")
        
        # 主循環
        try:
            while True:
                time.sleep(0.1)
                # 檢查窗口是否還存在
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
        except KeyboardInterrupt:
            logger.info("用戶中斷演示")
        
        # 清理資源
        camera.stop_real_time_capture()
        camera.release()
        cv2.destroyAllWindows()
        
        # 生成演示報告
        runtime = time.time() - start_time
        logger.info("=" * 40)
        logger.info("演示統計:")
        logger.info(f"  - 運行時間: {runtime:.1f}s")
        logger.info(f"  - 處理幀數: {frame_count}")
        logger.info(f"  - 檢測人臉: {face_count}")
        logger.info(f"  - 情感檢測: {emotion_count}")
        logger.info(f"  - 平均FPS: {frame_count/runtime:.1f}")
        logger.info(f"  - 人臉檢測率: {face_count/frame_count:.2f} 人臉/幀")
        
        return True
        
    except Exception as e:
        logger.error(f"演示失敗: {e}")
        return False


def get_emotion_color(emotion):
    """獲取情感對應的顏色"""
    color_map = {
        'Happy': (0, 255, 0),      # 綠色
        'Sad': (255, 0, 0),        # 藍色
        'Angry': (0, 0, 255),      # 紅色
        'Surprise': (0, 255, 255), # 黃色
        'Fear': (128, 0, 128),     # 紫色
        'Disgust': (0, 128, 255),  # 橙色
        'Neutral': (128, 128, 128) # 灰色
    }
    return color_map.get(emotion, (255, 255, 255))


def advanced_demo():
    """進階演示 - 使用完整的 RealTimeEmotionDetector"""
    logger.info("LivePilotAI 進階即時檢測演示")
    logger.info("=" * 40)
    
    try:
        from src.ai_engine.modules.real_time_detector import (
            RealTimeEmotionDetector, RealTimeConfig, CameraConfig, DetectionConfig
        )
        
        # 創建配置
        config = RealTimeConfig()
        config.camera_config = CameraConfig(
            device_id=0,
            width=640,
            height=480,
            fps=24
        )
        config.detection_config = DetectionConfig(
            enable_dnn=False,
            confidence_threshold=0.5
        )
        config.show_video = True
        config.show_emotions = True
        config.show_confidence = True
        
        # 創建檢測器
        detector = RealTimeEmotionDetector(config)
        
        # 設置結果回調
        def result_callback(frame, results):
            if results:
                emotions = [r.emotion for r in results]
                logger.info(f"檢測到情感: {emotions}")
        
        # 啟動檢測
        if detector.start(result_callback):
            logger.info("✓ 進階檢測系統已啟動")
            logger.info("系統將自動顯示檢測窗口")
            logger.info("按 'q' 退出，'p' 暫停/恢復，'s' 截圖")
            
            try:
                # 運行直到用戶停止
                while detector.is_running:
                    time.sleep(1)
                    
                    # 顯示統計信息
                    stats = detector.get_performance_stats()
                    logger.info(f"統計: FPS={stats['current_fps']:.1f}, "
                              f"幀數={stats['total_frames']}, "
                              f"人臉={stats['total_faces']}")
                    
            except KeyboardInterrupt:
                logger.info("用戶中斷檢測")
            
            # 停止檢測
            detector.stop()
            
            # 生成性能報告
            report_path = f"performance_report_{int(time.time())}.txt"
            detector.save_performance_report(report_path)
            logger.info(f"性能報告已保存: {report_path}")
            
            return True
        else:
            logger.error("無法啟動進階檢測系統")
            return False
            
    except Exception as e:
        logger.error(f"進階演示失敗: {e}")
        return False


def main():
    """主函數"""
    print("LivePilotAI Day 4 即時檢測演示")
    print("=" * 40)
    print("請選擇演示模式:")
    print("1. 簡單演示 (基本功能)")
    print("2. 進階演示 (完整系統)")
    print("0. 退出")
    print("=" * 40)
    
    try:
        choice = input("請輸入選擇 (0-2): ").strip()
        
        if choice == "1":
            return simple_demo()
        elif choice == "2":
            return advanced_demo()
        elif choice == "0":
            logger.info("用戶選擇退出")
            return True
        else:
            logger.error("無效選擇")
            return False
            
    except KeyboardInterrupt:
        logger.info("演示被中斷")
        return False
    except Exception as e:
        logger.error(f"演示執行失敗: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        print("=" * 40)
        if success:
            print("✓ 演示完成")
        else:
            print("✗ 演示失敗")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"演示執行錯誤: {e}")
        sys.exit(1)
