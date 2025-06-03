#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 情感檢測狀態機 (重構版)
基於狀態機模式的模組化情感檢測引擎，包含完整攝像頭支援
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
    """情感檢測狀態機 (完整版)"""
    
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
    
    async def run_detection(self, duration: Optional[float] = None) -> bool:
        """
        運行情感檢測
        
        Args:
            duration: 運行時長(秒)，None 表示無限運行
            
        Returns:
            bool: 運行是否成功
        """
        if self.is_running:
            logger.warning("情感檢測已在運行中")
            return False
        
        try:
            self.is_running = True
            self.should_stop = False
            self.stats['start_time'] = time.time()
            logger.info("開始情感檢測運行")
            
            start_time = time.time()
            
            while not self.should_stop:
                # 檢查運行時長
                if duration and (time.time() - start_time) >= duration:
                    logger.info(f"達到指定運行時長 {duration} 秒，停止檢測")
                    break
                
                # 處理當前狀態
                success = await self._process_current_state()
                
                if not success:
                    self.consecutive_failures += 1
                    logger.warning(f"狀態處理失敗 (連續失敗: {self.consecutive_failures})")
                    
                    if self.consecutive_failures >= self.config.max_consecutive_failures:
                        logger.error("達到最大連續失敗次數，停止運行")
                        self.state = EmotionDetectorState.ERROR_HANDLING
                        break
                    
                    if self.config.auto_retry:
                        await asyncio.sleep(self.config.retry_delay)
                else:
                    self.consecutive_failures = 0
                
                # 短暫延遲以避免過度佔用 CPU
                await asyncio.sleep(0.1)
            
            # 清理資源
            await self._cleanup_state()
            return True
            
        except Exception as e:
            logger.error(f"運行檢測時發生錯誤: {e}")
            await self._cleanup_state()
            return False
        finally:
            self.is_running = False
    
    async def stop_detection(self):
        """停止情感檢測"""
        logger.info("請求停止情感檢測")
        self.should_stop = True
        self.state = EmotionDetectorState.CLEANUP
    
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
                self.camera_manager.release()
                self.camera_manager = None
            
            if self.emotion_detector:
                # EmotionDetector 可能需要特殊清理邏輯
                self.emotion_detector = None
            
            self.state = EmotionDetectorState.STOPPED
            logger.info("資源清理完成")
            return True
            
        except Exception as e:
            logger.error(f"清理過程中發生錯誤: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        獲取運行統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self.stats.copy()
        if stats['start_time']:
            stats['running_time'] = time.time() - stats['start_time']
        else:
            stats['running_time'] = 0
        
        if stats['total_frames'] > 0:
            stats['success_rate'] = stats['successful_detections'] / stats['total_frames']
        else:
            stats['success_rate'] = 0
        
        stats['current_state'] = self.state.value
        stats['consecutive_failures'] = self.consecutive_failures
        
        return stats
    
    def reset_stats(self):
        """重置統計信息"""
        self.stats = {
            'total_frames': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'start_time': None,
            'last_detection_time': None
        }
        self.consecutive_failures = 0


# 便利函數
async def create_and_run_emotion_detector(config: Optional[EmotionDetectorConfig] = None) -> bool:
    """
    創建並運行情感檢測器的便利函數
    
    Args:
        config: 檢測器配置
        
    Returns:
        bool: 運行是否成功
    """
    detector = EmotionDetectorStateMachine(config)
    return await detector.run_detection()


def create_default_config() -> EmotionDetectorConfig:
    """
    創建默認配置
    
    Returns:
        EmotionDetectorConfig: 默認配置
    """
    return EmotionDetectorConfig(
        camera_config=CameraConfig(),
        detection_config=DetectionConfig(),
        max_consecutive_failures=5,
        auto_retry=True,
        retry_delay=1.0
    )
