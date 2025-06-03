"""
LivePilotAI 測試用簡化狀態機
用於測試模組化架構的核心功能
"""

import logging
import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from .states import EmotionDetectorState, StateTransitionError, EmotionDetectorError
from .modules.dependency_manager import DependencyManager
from .modules.emotion_detector import EmotionDetector, DetectionConfig


logger = logging.getLogger(__name__)


@dataclass
class SimpleEmotionDetectorConfig:
    """簡化的情感檢測器配置"""
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    max_consecutive_failures: int = 5
    auto_retry: bool = True
    retry_delay: float = 1.0


class SimpleEmotionDetectorStateMachine:
    """簡化的情感檢測狀態機（用於測試）"""
    
    def __init__(self, config: SimpleEmotionDetectorConfig = None):
        self.config = config or SimpleEmotionDetectorConfig()
        self.state = EmotionDetectorState.INIT
        self.consecutive_failures = 0
        
        # 模組實例
        self.emotion_detector: Optional[EmotionDetector] = None
        
        # 運行狀態
        self.is_running = False
        self.should_stop = False
        
        # 統計信息
        self.stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'start_time': None,
            'last_operation_time': None
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
            logger.info("開始運行簡化情感檢測狀態機")
            
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
        """處理當前狀態"""
        try:
            if self.state == EmotionDetectorState.INIT:
                return await self._init_state()
            elif self.state == EmotionDetectorState.DEPENDENCY_CHECK:
                return await self._dependency_check_state()
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
        logger.info("初始化簡化情感檢測引擎...")
        self.state = EmotionDetectorState.DEPENDENCY_CHECK
        return True
    
    async def _dependency_check_state(self) -> bool:
        """依賴檢查狀態"""
        logger.info("檢查系統依賴...")
        
        try:
            # 檢查依賴（不自動安裝，避免安裝時間過長）
            installed, missing = DependencyManager.check_dependencies()
            
            if missing:
                logger.warning(f"發現缺失依賴: {', '.join(missing)}，但將繼續測試")
            
            logger.info("依賴檢查完成")
            self.state = EmotionDetectorState.MODEL_LOADING
            return True
                
        except Exception as e:
            logger.error(f"依賴檢查過程中發生錯誤: {e}")
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
        """情感檢測運行狀態（模擬模式）"""
        try:
            self.stats['total_operations'] += 1
            
            # 模擬檢測過程
            logger.debug("執行模擬情感檢測...")
            
            # 創建模擬圖像數據
            import numpy as np
            mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 執行情感檢測
            results = self.emotion_detector.detect_emotions(mock_frame)
            
            if results:
                self.stats['successful_operations'] += 1
                self.stats['last_operation_time'] = time.time()
                
                # 記錄檢測結果
                for result in results:
                    logger.info(f"檢測到情感: {result.emotion} (信心度: {result.confidence:.2f})")
            else:
                logger.debug("未檢測到情感")
            
            # 模擬檢測幾次後停止
            if self.stats['total_operations'] >= 5:
                logger.info("測試完成，準備停止")
                self.state = EmotionDetectorState.CLEANUP
            
            return True
            
        except Exception as e:
            logger.error(f"情感檢測錯誤: {e}")
            self.stats['failed_operations'] += 1
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
        """獲取狀態機狀態信息"""
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
                    self.stats['successful_operations'] / max(self.stats['total_operations'], 1)
                    if self.stats['total_operations'] > 0 else 0
                )
            },
            'model_info': (
                self.emotion_detector.get_model_info() 
                if self.emotion_detector else {"is_loaded": False}
            )
        }


# 便利函數
async def create_and_run_simple_emotion_detector(config: SimpleEmotionDetectorConfig = None) -> bool:
    """
    創建並運行簡化的情感檢測器
    
    Args:
        config: 檢測器配置
        
    Returns:
        bool: 運行是否成功
    """
    detector = SimpleEmotionDetectorStateMachine(config)
    return await detector.run()
