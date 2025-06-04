"""
LivePilotAI 模組化情感檢測引擎測試
測試新的狀態機架構
"""

import asyncio
import logging
import time
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入新的狀態機模組
from ai_engine.emotion_state_machine import (
    EmotionDetectorStateMachine,
    EmotionDetectorConfig,
    create_and_run_emotion_detector
)
from ai_engine.modules import CameraConfig, DetectionConfig


async def test_emotion_detector_state_machine():
    """測試情感檢測狀態機"""
    logger.info("開始測試模組化情感檢測引擎")
    
    try:
        # 創建配置
        camera_config = CameraConfig(
            device_id=0,
            width=640,
            height=480,
            fps=30
        )
        
        detection_config = DetectionConfig(
            confidence_threshold=0.6
        )
        
        config = EmotionDetectorConfig(
            camera_config=camera_config,
            detection_config=detection_config,
            max_consecutive_failures=3,
            auto_retry=True,
            retry_delay=0.5
        )
        
        # 創建狀態機實例
        detector = EmotionDetectorStateMachine(config)
        
        # 創建運行任務
        detection_task = asyncio.create_task(detector.run())
        
        # 運行一段時間後停止
        await asyncio.sleep(10)  # 運行 10 秒
        
        # 獲取狀態信息
        status = detector.get_status()
        logger.info(f"檢測器狀態: {status}")
        
        # 停止檢測器
        detector.stop()
        
        # 等待任務完成
        result = await detection_task
        
        logger.info(f"測試完成，結果: {result}")
        return result
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        return False


async def test_individual_modules():
    """測試個別模組"""
    logger.info("開始測試個別模組")
    
    # 測試依賴管理器
    from ai_engine.modules import DependencyManager
    
    logger.info("測試依賴管理器...")
    installed, missing = DependencyManager.check_dependencies()
    logger.info(f"已安裝: {installed}")
    logger.info(f"缺失: {missing}")
    
    # 測試攝像頭管理器
    from ai_engine.modules import CameraManager, CameraConfig
    
    logger.info("測試攝像頭管理器...")
    camera_config = CameraConfig(device_id=0)
    camera_manager = CameraManager(camera_config)
    
    if camera_manager.initialize_camera():
        logger.info("攝像頭初始化成功")
        
        if camera_manager.test_camera():
            logger.info("攝像頭測試通過")
        else:
            logger.warning("攝像頭測試失敗")
        
        camera_manager.cleanup()
    else:
        logger.warning("攝像頭初始化失敗")
    
    # 測試情感檢測器
    from ai_engine.modules import EmotionDetector, DetectionConfig
    
    logger.info("測試情感檢測器...")
    detection_config = DetectionConfig()
    emotion_detector = EmotionDetector(detection_config)
    
    if emotion_detector.load_models():
        logger.info("模型載入成功")
        model_info = emotion_detector.get_model_info()
        logger.info(f"模型信息: {model_info}")
        emotion_detector.cleanup()
    else:
        logger.warning("模型載入失敗")


async def test_quick_detection():
    """快速檢測測試"""
    logger.info("開始快速檢測測試")
    
    try:
        # 使用便利函數
        config = EmotionDetectorConfig(
            max_consecutive_failures=2,
            auto_retry=False
        )
        
        # 設置超時運行
        result = await asyncio.wait_for(
            create_and_run_emotion_detector(config),
            timeout=5.0
        )
        
        logger.info(f"快速檢測結果: {result}")
        return result
        
    except asyncio.TimeoutError:
        logger.info("快速檢測超時（正常，用於測試）")
        return True
    except Exception as e:
        logger.error(f"快速檢測錯誤: {e}")
        return False


async def main():
    """主測試函數"""
    logger.info("=" * 50)
    logger.info("LivePilotAI 模組化架構測試開始")
    logger.info("=" * 50)
    
    # 測試個別模組
    await test_individual_modules()
    
    logger.info("\n" + "=" * 50)
    
    # 測試完整狀態機
    await test_emotion_detector_state_machine()
    
    logger.info("\n" + "=" * 50)
    
    # 快速檢測測試
    await test_quick_detection()
    
    logger.info("=" * 50)
    logger.info("所有測試完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    # 確保在正確的目錄中運行
    import sys
    from pathlib import Path
    
    # 添加源碼路徑
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    # 運行測試
    asyncio.run(main())
