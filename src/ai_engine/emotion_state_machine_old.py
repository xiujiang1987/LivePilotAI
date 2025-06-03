"""
LivePilotAI 情感檢測狀態機
基於狀態機模式的模組化情感檢測引擎
"""

import logging
import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from .states import EmotionDetectorState, StateTransitionError, EmotionDetectorError
from .modules import (
    DependencyManager, 
    EmotionDetector,
    DetectionConfig
)
from .modules.camera_manager import CameraManager, CameraConfig


logger = logging.getLogger(__name__)


@dataclass
class EmotionDetectorConfig:
    """情感檢測器配置"""
    camera_config: CameraConfig = field(default_factory=CameraConfig)
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    max_consecutive_failures: int = 5
    auto_retry: bool = True
    retry_delay: float = 1.0


class EmotionDetectorStateMachine:
    """情感檢測狀態機"""
    
    def __init__(self, config: Optional[EmotionDetectorConfig] = None):
        self.config = config or EmotionDetectorConfig()
        self.state = EmotionDetectorState.INIT
        self.consecutive_failures = 0
        
        # 模組實例
        self.camera_manager: Optional[CameraManager] = None
        self.emotion_detector: Optional[EmotionDetector] = None
        
        # 運行狀態
        self.is_running = False
        self.should_stop = False
        
        # 統計信息
        self.stats = {
            'total_frames': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'start_time': None,
            'last_detection_time': None
        }
    
    async def run(self) -> bool:
        """
        運行狀態機
        
        Returns:
            bool: 運行是否成功完成
        """
        try:
            self.is_running = True
            self.stats['start_time'] = time.time()
            logger.info("開始運行情感檢測狀態機")
            
            while self.is_running and not self.should_stop:
                success = await self._process_current_state()
                
                if not success:
                    self.consecutive_failures += 1
                    
                    if self.consecutive_failures >= self.config.max_consecutive_failures:
                        logger.error(f"連續失敗 {self.consecutive_failures} 次，停止狀態機")
                        self.state = EmotionDetectorState.ERROR_HANDLING
                        break
                    
                    if self.config.auto_retry:
                        logger.warning(f"失敗 {self.consecutive_failures} 次，等待重試...")
                        await asyncio.sleep(self.config.retry_delay)
                else:
                    self.consecutive_failures = 0
                
                # 檢查是否應該停止
                if self.state == EmotionDetectorState.STOPPED:
                    break
                
                # 避免 CPU 過載
                await asyncio.sleep(0.01)
            
            # 執行清理
            await self._cleanup_state()
            return self.state != EmotionDetectorState.ERROR_HANDLING
            
        except Exception as e:
            logger.error(f"狀態機運行錯誤: {e}")
            await self._cleanup_state()
            return False
        finally:
            self.is_running = False
    
    async def _process_current_state(self) -> bool:
        """
        處理當前狀態
        
        Returns:
            bool: 狀態處理是否成功
        """
        try:
            if self.state == EmotionDetectorState.INIT:
                return await self._init_state()
            elif self.state == EmotionDetectorState.DEPENDENCY_CHECK:
                return await self._dependency_check_state()
            elif self.state == EmotionDetectorState.CAMERA_SETUP:
                return await self._camera_setup_state()
            elif self.state == EmotionDetectorState.MODEL_LOADING:
                return await self._model_loading_state()
            elif self.state == EmotionDetectorState.DETECTION_READY:
                return await self._detection_ready_state()
            elif self.state == EmotionDetectorState.EMOTION_DETECTION:
                return await self._emotion_detection_state()
            elif self.state == EmotionDetectorState.ERROR_HANDLING:
                return await self._error_handling_state()
            else:
                logger.error(f"未知狀態: {self.state}")
                return False
                
        except Exception as e:
            logger.error(f"狀態處理錯誤 {self.state}: {e}")
            return False
    
    async def _init_state(self) -> bool:
        """初始化狀態"""
        logger.info("初始化情感檢測引擎...")
        self.state = EmotionDetectorState.DEPENDENCY_CHECK
        return True
    
    async def _dependency_check_state(self) -> bool:
        """依賴檢查狀態"""
        logger.info("檢查系統依賴...")
        
        try:
            # 使用 DependencyManager 檢查依賴
            success = DependencyManager.auto_install_dependencies()
            
            if success:
                logger.info("依賴檢查通過")
                self.state = EmotionDetectorState.CAMERA_SETUP
                return True
            else:
                logger.error("依賴檢查失敗")
                return False
                
        except Exception as e:
            logger.error(f"依賴檢查過程中發生錯誤: {e}")
            return False
    
    async def _camera_setup_state(self) -> bool:
        """攝像頭設置狀態"""
        logger.info("設置攝像頭...")
        
        try:
            self.camera_manager = CameraManager(self.config.camera_config)
            
            if self.camera_manager.initialize_camera():
                if self.camera_manager.test_camera():
                    logger.info("攝像頭設置成功")
                    self.state = EmotionDetectorState.MODEL_LOADING
                    return True
                else:
                    logger.error("攝像頭測試失敗")
                    return False
            else:
                logger.error("攝像頭初始化失敗")
                return False
                
        except Exception as e:
            logger.error(f"攝像頭設置錯誤: {e}")
            return False
    
    async def _model_loading_state(self) -> bool:
        """模型載入狀態"""
        logger.info("載入情感檢測模型...")
          try:
            self.emotion_detector = EmotionDetector(self.config.detection_config)
            
            if self.emotion_detector.load_models():
                logger.info("模型載入成功")
                self.state = EmotionDetectorState.DETECTION_READY
                return True
            else:
                logger.error("模型載入失敗")
                return False
                
        except Exception as e:
            logger.error(f"模型載入錯誤: {e}")
            return False
    
    async def _detection_ready_state(self) -> bool:
        """檢測準備就緒狀態"""
        logger.info("情感檢測準備就緒")
        self.state = EmotionDetectorState.EMOTION_DETECTION
        return True
    
    async def _emotion_detection_state(self) -> bool:
        """情感檢測運行狀態"""
        try:
            # 確認攝像頭管理器存在
            if not self.camera_manager:
                logger.error("攝像頭管理器未初始化")
                return False
                
            # 讀取攝像頭數據
            success, frame = self.camera_manager.read_frame()
            
            if not success or frame is None:
                self.stats['failed_detections'] += 1
                return False
            
            self.stats['total_frames'] += 1
            
            # 確認情感檢測器存在
            if not self.emotion_detector:
                logger.error("情感檢測器未初始化")
                return False
            
            # 執行情感檢測
            results = self.emotion_detector.detect_emotions(frame)
            
            if results:
                self.stats['successful_detections'] += 1
                self.stats['last_detection_time'] = time.time()
                
                # 記錄檢測結果
                for result in results:
                    logger.debug(f"檢測到情感: {result.emotion} (信心度: {result.confidence:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"情感檢測錯誤: {e}")
            self.stats['failed_detections'] += 1
            return False
    
    async def _error_handling_state(self) -> bool:
        """錯誤處理狀態"""
        logger.error("進入錯誤處理狀態")
        self.state = EmotionDetectorState.CLEANUP
        return False
    
    async def _cleanup_state(self) -> bool:
        """清理狀態"""
        logger.info("清理系統資源...")
        
        try:
            if self.camera_manager:
                self.camera_manager.cleanup()
            
            if self.emotion_detector:
                self.emotion_detector.cleanup()
            
            self.state = EmotionDetectorState.STOPPED
            logger.info("清理完成")
            return True
            
        except Exception as e:
            logger.error(f"清理過程中發生錯誤: {e}")
            return False
    
    def stop(self):
        """停止狀態機"""
        logger.info("請求停止狀態機")
        self.should_stop = True
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取狀態機狀態信息
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        runtime = None
        if self.stats['start_time']:
            runtime = time.time() - self.stats['start_time']
        
        return {
            'current_state': self.state.name,
            'is_running': self.is_running,
            'consecutive_failures': self.consecutive_failures,
            'stats': {
                **self.stats,
                'runtime': runtime,
                'success_rate': (
                    self.stats['successful_detections'] / max(self.stats['total_frames'], 1)
                    if self.stats['total_frames'] > 0 else 0
                )
            },
            'camera_info': (
                self.camera_manager.get_camera_info() 
                if self.camera_manager else {"status": "未初始化"}
            ),
            'model_info': (
                self.emotion_detector.get_model_info() 
                if self.emotion_detector else {"is_loaded": False}
            )
        }


# 便利函數
async def create_and_run_emotion_detector(config: Optional[EmotionDetectorConfig] = None) -> bool:
    """
    創建並運行情感檢測器
    
    Args:
        config: 檢測器配置
        
    Returns:
        bool: 運行是否成功
    """
    detector = EmotionDetectorStateMachine(config)
    return await detector.run()
