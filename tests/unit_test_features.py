# -*- coding: utf-8 -*-
"""
LivePilotAI Day 4 測試腳本
測試即時人臉檢測和情感識別功能
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_camera_manager():
    """測試攝像頭管理器"""
    logger.info("=== 測試攝像頭管理器 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        
        # 創建攝像頭配置
        config = CameraConfig(
            device_id=0,
            width=640,
            height=480,
            fps=30
        )
        
        # 初始化攝像頭管理器
        camera = CameraManager(config)
        
        # 測試初始化
        if camera.initialize_camera():
            logger.info("✓ 攝像頭初始化成功")
            
            # 測試基本讀取
            success, frame = camera.read_frame()
            if success:
                logger.info("✓ 攝像頭讀取測試成功")
                logger.info(f"  - 幀尺寸: {frame.shape}")
            else:
                logger.error("✗ 攝像頭讀取測試失敗")
            
            # 測試攝像頭信息
            info = camera.get_camera_info()
            logger.info(f"✓ 攝像頭信息: {info}")
            
            # 測試即時捕獲
            logger.info("測試即時捕獲模式...")
            frame_count = 0
            
            def frame_callback(frame):
                nonlocal frame_count
                frame_count += 1
                if frame_count <= 5:
                    logger.info(f"  - 接收到第 {frame_count} 幀")
            
            if camera.start_real_time_capture(frame_callback):
                logger.info("✓ 即時捕獲啟動成功")
                time.sleep(3)  # 運行3秒
                camera.stop_real_time_capture()
                logger.info("✓ 即時捕獲停止成功")
                
                # 檢查性能統計
                stats = camera.get_performance_stats()
                logger.info(f"✓ 性能統計: FPS={stats.fps:.1f}, 總幀數={stats.frame_count}")
            else:
                logger.error("✗ 即時捕獲啟動失敗")
            
            camera.release()
            logger.info("✓ 攝像頭資源釋放成功")
            return True
            
        else:
            logger.error("✗ 攝像頭初始化失敗")
            return False
            
    except Exception as e:
        logger.error(f"✗ 攝像頭管理器測試失敗: {e}")
        return False


def test_face_detector():
    """測試人臉檢測器"""
    logger.info("=== 測試人臉檢測器 ===")
    
    try:
        import cv2
        import numpy as np
        from src.ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        
        # 創建檢測配置
        config = DetectionConfig(
            enable_dnn=False,  # 先測試 Haar Cascade
            confidence_threshold=0.5
        )
        
        # 初始化人臉檢測器
        detector = FaceDetector(config)
        
        # 創建測試圖像（包含簡單的人臉特徵）
        test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
        
        # 在圖像中繪製一個簡單的"人臉"
        cv2.circle(test_image, (200, 150), 80, (200, 200, 200), -1)  # 臉
        cv2.circle(test_image, (180, 130), 10, (0, 0, 0), -1)      # 左眼
        cv2.circle(test_image, (220, 130), 10, (0, 0, 0), -1)      # 右眼
        cv2.rectangle(test_image, (195, 160), (205, 170), (0, 0, 0), -1)  # 鼻子
        cv2.ellipse(test_image, (200, 190), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # 嘴
        
        # 測試人臉檢測
        faces = detector.detect_faces(test_image, method="haar")
        logger.info(f"✓ 檢測到 {len(faces)} 張人臉")
        
        if faces:
            for i, face in enumerate(faces):
                logger.info(f"  - 人臉 {i+1}: 位置=({face.x}, {face.y}), 大小={face.width}x{face.height}")
        
        # 測試繪製功能
        result_image = detector.draw_faces(test_image, faces)
        logger.info("✓ 人臉框繪製成功")
        
        # 測試人臉區域提取
        if faces:
            face_roi = detector.get_face_roi(test_image, faces[0])
            if face_roi is not None:
                logger.info(f"✓ 人臉區域提取成功: 大小={face_roi.shape}")
            else:
                logger.warning("✗ 人臉區域提取失敗")
        
        # 獲取性能統計
        stats = detector.get_performance_stats()
        logger.info(f"✓ 檢測器性能統計: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 人臉檢測器測試失敗: {e}")
        return False


def test_emotion_detector():
    """測試情感檢測器"""
    logger.info("=== 測試情感檢測器 ===")
    
    try:
        import cv2
        import numpy as np
        from src.ai_engine.emotion_detector import EmotionDetector
        
        # 初始化情感檢測器
        detector = EmotionDetector()
        
        # 創建測試人臉圖像
        test_face = np.random.randint(0, 255, (48, 48, 3), dtype=np.uint8)
        
        # 測試情感預測
        result = detector.predict_emotion_from_image(test_face)
        
        logger.info("✓ 情感檢測成功")
        logger.info(f"  - 主要情感: {result['dominant_emotion']}")
        logger.info(f"  - 置信度: {result['confidence']:.3f}")
        logger.info(f"  - 所有情感: {list(result['emotions'].keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 情感檢測器測試失敗: {e}")
        return False


def test_integration():
    """測試系統整合"""
    logger.info("=== 測試系統整合 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from src.ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        from src.ai_engine.emotion_detector import EmotionDetector
        
        # 初始化所有組件
        camera_config = CameraConfig(device_id=0, fps=10)  # 降低FPS用於測試
        camera = CameraManager(camera_config)
        
        detection_config = DetectionConfig(enable_dnn=False)  # 使用更快的檢測
        face_detector = FaceDetector(detection_config)
        
        emotion_detector = EmotionDetector()
        
        # 測試初始化
        if not camera.initialize_camera():
            logger.error("✗ 攝像頭初始化失敗")
            return False
        
        logger.info("✓ 所有組件初始化成功")
        
        # 測試端到端流程
        test_frames = 5
        processed_frames = 0
        detected_faces = 0
        detected_emotions = 0
        
        def process_frame(frame):
            nonlocal processed_frames, detected_faces, detected_emotions
            
            try:
                # 檢測人臉
                faces = face_detector.detect_faces(frame)
                detected_faces += len(faces)
                
                # 對每個人臉進行情感檢測
                for face in faces:
                    face_roi = face_detector.get_face_roi(frame, face)
                    if face_roi is not None:
                        emotion_result = emotion_detector.predict_emotion_from_image(face_roi)
                        if emotion_result['dominant_emotion']:
                            detected_emotions += 1
                
                processed_frames += 1
                logger.info(f"  - 處理第 {processed_frames} 幀: {len(faces)} 張人臉")
                
            except Exception as e:
                logger.error(f"  - 幀處理失敗: {e}")
        
        # 啟動處理
        if camera.start_real_time_capture(process_frame):
            logger.info("✓ 開始端到端測試...")
            
            # 運行測試
            start_time = time.time()
            while processed_frames < test_frames and time.time() - start_time < 10:
                time.sleep(0.1)
            
            camera.stop_real_time_capture()
            
            # 統計結果
            runtime = time.time() - start_time
            logger.info(f"✓ 端到端測試完成")
            logger.info(f"  - 處理時間: {runtime:.2f}s")
            logger.info(f"  - 處理幀數: {processed_frames}")
            logger.info(f"  - 檢測人臉: {detected_faces}")
            logger.info(f"  - 情感檢測: {detected_emotions}")
            logger.info(f"  - 平均FPS: {processed_frames/runtime:.2f}")
            
            # 性能驗證
            camera_stats = camera.get_performance_stats()
            detector_stats = face_detector.get_performance_stats()
            
            logger.info(f"✓ 攝像頭性能: FPS={camera_stats.fps:.1f}")
            logger.info(f"✓ 檢測器性能: FPS={detector_stats['detection_fps']:.1f}")
            
            camera.release()
            return True
            
        else:
            logger.error("✗ 無法啟動即時捕獲")
            camera.release()
            return False
            
    except Exception as e:
        logger.error(f"✗ 系統整合測試失敗: {e}")
        return False


def performance_benchmark():
    """性能基準測試"""
    logger.info("=== 性能基準測試 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from src.ai_engine.modules.face_detector import FaceDetector, DetectionConfig
        from src.ai_engine.emotion_detector import EmotionDetector
        
        # 配置
        target_fps = 24
        target_latency = 0.1  # 100ms
        test_duration = 10    # 10秒
        
        # 初始化組件
        camera = CameraManager(CameraConfig(fps=30))
        face_detector = FaceDetector(DetectionConfig(enable_dnn=False))
        emotion_detector = EmotionDetector()
        
        if not camera.initialize_camera():
            logger.error("✗ 攝像頭初始化失敗")
            return False
        
        # 性能統計
        frame_times = []
        detection_times = []
        emotion_times = []
        total_faces = 0
        total_emotions = 0
        
        def benchmark_frame(frame):
            nonlocal total_faces, total_emotions
            
            frame_start = time.time()
            
            # 人臉檢測
            detect_start = time.time()
            faces = face_detector.detect_faces(frame)
            detect_time = time.time() - detect_start
            detection_times.append(detect_time)
            total_faces += len(faces)
            
            # 情感檢測
            for face in faces:
                emotion_start = time.time()
                face_roi = face_detector.get_face_roi(frame, face)
                if face_roi is not None:
                    emotion_detector.predict_emotion_from_image(face_roi)
                    total_emotions += 1
                emotion_time = time.time() - emotion_start
                emotion_times.append(emotion_time)
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
        
        # 執行基準測試
        camera.start_real_time_capture(benchmark_frame)
        logger.info(f"✓ 開始 {test_duration} 秒性能測試...")
        
        time.sleep(test_duration)
        camera.stop_real_time_capture()
        camera.release()
        
        # 分析結果
        if frame_times:
            avg_frame_time = sum(frame_times) / len(frame_times)
            actual_fps = 1.0 / avg_frame_time
            
            avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0
            avg_emotion_time = sum(emotion_times) / len(emotion_times) if emotion_times else 0
            
            logger.info(f"✓ 性能測試結果:")
            logger.info(f"  - 總處理幀數: {len(frame_times)}")
            logger.info(f"  - 平均幀處理時間: {avg_frame_time:.3f}s")
            logger.info(f"  - 實際FPS: {actual_fps:.1f}")
            logger.info(f"  - 人臉檢測時間: {avg_detection_time:.3f}s")
            logger.info(f"  - 情感檢測時間: {avg_emotion_time:.3f}s")
            logger.info(f"  - 總檢測人臉: {total_faces}")
            logger.info(f"  - 總情感檢測: {total_emotions}")
            
            # 性能評估
            fps_ok = actual_fps >= target_fps
            latency_ok = avg_frame_time <= target_latency
            
            logger.info(f"✓ 性能評估:")
            logger.info(f"  - FPS達標: {'✓' if fps_ok else '✗'} (目標: {target_fps}, 實際: {actual_fps:.1f})")
            logger.info(f"  - 延遲達標: {'✓' if latency_ok else '✗'} (目標: {target_latency:.3f}s, 實際: {avg_frame_time:.3f}s)")
            
            return fps_ok and latency_ok
        else:
            logger.error("✗ 沒有收集到性能數據")
            return False
            
    except Exception as e:
        logger.error(f"✗ 性能基準測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    logger.info("LivePilotAI Day 4 功能測試開始")
    logger.info("=" * 50)
    
    test_results = {
        "攝像頭管理器": False,
        "人臉檢測器": False,
        "情感檢測器": False,
        "系統整合": False,
        "性能基準": False
    }
    
    # 執行各項測試
    test_results["攝像頭管理器"] = test_camera_manager()
    test_results["人臉檢測器"] = test_face_detector()
    test_results["情感檢測器"] = test_emotion_detector()
    
    # 只有基礎測試通過才進行整合測試
    if all([test_results["攝像頭管理器"], test_results["人臉檢測器"], test_results["情感檢測器"]]):
        test_results["系統整合"] = test_integration()
        
        # 只有整合測試通過才進行性能測試
        if test_results["系統整合"]:
            test_results["性能基準"] = performance_benchmark()
    
    # 生成測試報告
    logger.info("=" * 50)
    logger.info("Day 4 測試結果總結:")
    
    passed_tests = 0
    for test_name, result in test_results.items():
        status = "✓ 通過" if result else "✗ 失敗"
        logger.info(f"  - {test_name}: {status}")
        if result:
            passed_tests += 1
    
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info(f"總體測試結果: {passed_tests}/{total_tests} 通過 ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 Day 4 任務完成度: 優秀!")
    elif success_rate >= 60:
        logger.info("😊 Day 4 任務完成度: 良好!")
    else:
        logger.info("⚠️  Day 4 任務需要改進")
    
    return success_rate >= 60


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"測試執行失敗: {e}")
        sys.exit(1)
