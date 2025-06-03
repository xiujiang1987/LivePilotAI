# -*- coding: utf-8 -*-
"""
LivePilotAI Day 4 簡化測試腳本
驗證基本組件功能
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

def test_basic_imports():
    """測試基本模組導入"""
    logger.info("=== 測試基本模組導入 ===")
    
    try:
        # 測試 OpenCV
        import cv2
        logger.info(f"✓ OpenCV 版本: {cv2.__version__}")
        
        # 測試 NumPy
        import numpy as np
        logger.info(f"✓ NumPy 版本: {np.__version__}")
        
        # 測試專案模組
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        logger.info("✓ CameraManager 導入成功")
        
        from src.ai_engine.modules.face_detector import FaceDetector
        logger.info("✓ FaceDetector 導入成功")
        
        # 創建基本對象測試
        config = CameraConfig()
        camera = CameraManager(config)
        logger.info(f"✓ CameraManager 實例創建成功: {camera}")
        
        detector = FaceDetector()
        logger.info(f"✓ FaceDetector 實例創建成功: {detector}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 模組導入失敗: {e}")
        return False


def test_camera_basic():
    """測試攝像頭基本功能"""
    logger.info("=== 測試攝像頭基本功能 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        
        # 創建配置
        config = CameraConfig(device_id=0, width=320, height=240, fps=15)
        camera = CameraManager(config)
        
        # 測試初始化
        if camera.initialize_camera():
            logger.info("✓ 攝像頭初始化成功")
            
            # 測試讀取
            success, frame = camera.read_frame()
            if success and frame is not None:
                logger.info(f"✓ 攝像頭讀取成功，幀尺寸: {frame.shape}")
                
                # 測試攝像頭信息
                info = camera.get_camera_info()
                logger.info(f"✓ 攝像頭信息: {info}")
                
                camera.release()
                return True
            else:
                logger.error("✗ 攝像頭讀取失敗")
        else:
            logger.error("✗ 攝像頭初始化失敗")
        
        camera.release()
        return False
        
    except Exception as e:
        logger.error(f"✗ 攝像頭測試失敗: {e}")
        return False


def test_face_detection_basic():
    """測試人臉檢測基本功能"""
    logger.info("=== 測試人臉檢測基本功能 ===")
    
    try:
        import cv2
        import numpy as np
        from src.ai_engine.modules.face_detector import FaceDetector
        
        # 創建檢測器
        detector = FaceDetector()
        
        # 創建測試圖像
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 128
        logger.info(f"✓ 測試圖像創建成功: {test_image.shape}")
        
        # 嘗試檢測（即使沒有真實人臉）
        faces = detector.detect_faces(test_image)
        logger.info(f"✓ 人臉檢測完成，檢測到 {len(faces)} 張人臉")
        
        # 測試性能統計
        stats = detector.get_performance_stats()
        logger.info(f"✓ 檢測器統計: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 人臉檢測測試失敗: {e}")
        return False


def test_real_time_capture():
    """測試即時捕獲功能"""
    logger.info("=== 測試即時捕獲功能 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        
        config = CameraConfig(device_id=0, width=320, height=240, fps=10)
        camera = CameraManager(config)
        
        if not camera.initialize_camera():
            logger.error("✗ 攝像頭初始化失敗")
            return False
        
        # 測試即時捕獲
        frame_count = 0
        max_frames = 5
        
        def frame_callback(frame):
            nonlocal frame_count
            frame_count += 1
            logger.info(f"  - 接收到第 {frame_count} 幀，尺寸: {frame.shape}")
            if frame_count >= max_frames:
                return "stop"
        
        if camera.start_real_time_capture(frame_callback):
            logger.info("✓ 即時捕獲啟動成功")
            
            # 等待接收幀
            start_time = time.time()
            while frame_count < max_frames and time.time() - start_time < 5:
                time.sleep(0.1)
            
            camera.stop_real_time_capture()
            logger.info(f"✓ 即時捕獲停止，共接收 {frame_count} 幀")
            
            # 檢查性能
            stats = camera.get_performance_stats()
            logger.info(f"✓ 性能統計: FPS={stats.fps:.1f}, 總幀數={stats.frame_count}")
            
            camera.release()
            return frame_count > 0
        else:
            logger.error("✗ 無法啟動即時捕獲")
            camera.release()
            return False
            
    except Exception as e:
        logger.error(f"✗ 即時捕獲測試失敗: {e}")
        return False


def test_integration_simple():
    """測試簡單整合"""
    logger.info("=== 測試簡單整合 ===")
    
    try:
        from src.ai_engine.modules.camera_manager import CameraManager, CameraConfig
        from src.ai_engine.modules.face_detector import FaceDetector
        
        # 初始化組件
        camera = CameraManager(CameraConfig(width=320, height=240, fps=10))
        detector = FaceDetector()
        
        if not camera.initialize_camera():
            logger.error("✗ 攝像頭初始化失敗")
            return False
        
        # 測試端到端處理
        processed_frames = 0
        total_faces = 0
        
        def process_frame(frame):
            nonlocal processed_frames, total_faces
            try:
                # 檢測人臉
                faces = detector.detect_faces(frame)
                processed_frames += 1
                total_faces += len(faces)
                
                logger.info(f"  - 處理第 {processed_frames} 幀: {len(faces)} 張人臉")
                
                if processed_frames >= 3:
                    return "stop"
                    
            except Exception as e:
                logger.error(f"  - 幀處理錯誤: {e}")
        
        # 啟動處理
        if camera.start_real_time_capture(process_frame):
            logger.info("✓ 整合處理啟動成功")
            
            start_time = time.time()
            while processed_frames < 3 and time.time() - start_time < 10:
                time.sleep(0.2)
            
            camera.stop_real_time_capture()
            camera.release()
            
            logger.info(f"✓ 整合測試完成:")
            logger.info(f"  - 處理幀數: {processed_frames}")
            logger.info(f"  - 檢測人臉: {total_faces}")
            logger.info(f"  - 平均檢測: {total_faces/max(1, processed_frames):.2f} 人臉/幀")
            
            return processed_frames > 0
            
        else:
            logger.error("✗ 無法啟動整合處理")
            camera.release()
            return False
            
    except Exception as e:
        logger.error(f"✗ 整合測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    logger.info("LivePilotAI Day 4 簡化測試開始")
    logger.info("=" * 50)
    
    tests = [
        ("基本模組導入", test_basic_imports),
        ("攝像頭基本功能", test_camera_basic),
        ("人臉檢測基本功能", test_face_detection_basic),
        ("即時捕獲功能", test_real_time_capture),
        ("簡單整合測試", test_integration_simple),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n開始測試: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✓ 通過" if result else "✗ 失敗"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: ✗ 異常 - {e}")
            results[test_name] = False
    
    # 生成總結
    logger.info("\n" + "=" * 50)
    logger.info("測試結果總結:")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓" if result else "✗"
        logger.info(f"  {status} {test_name}")
    
    success_rate = (passed / total) * 100
    logger.info(f"\n總體結果: {passed}/{total} 通過 ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 Day 4 基本功能驗證: 優秀!")
    elif success_rate >= 60:
        logger.info("😊 Day 4 基本功能驗證: 良好!")
    else:
        logger.info("⚠️  Day 4 基本功能需要改進")
    
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
