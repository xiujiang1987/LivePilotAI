# -*- coding: utf-8 -*-
"""
LivePilotAI 攝像頭管理模組
負責攝像頭的初始化、配置和管理
"""

import cv2
import logging
from typing import Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    """攝像頭配置"""
    device_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    buffer_size: int = 1


class CameraSetupError(Exception):
    """攝像頭設置錯誤"""
    pass


class CameraManager:
    """攝像頭管理器"""
    
    def __init__(self, config: Optional[CameraConfig] = None):
        self.config = config or CameraConfig()
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
    
    def initialize_camera(self) -> bool:
        """初始化攝像頭"""
        try:
            logger.info(f"正在初始化攝像頭 (device_id: {self.config.device_id})...")
            
            self.cap = cv2.VideoCapture(self.config.device_id)
            
            if not self.cap.isOpened():
                raise CameraSetupError(f"無法打開攝像頭 {self.config.device_id}")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)
            
            self.is_initialized = True
            logger.info("攝像頭初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"攝像頭初始化失敗: {e}")
            self.is_initialized = False
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[Any]]:
        """讀取攝像頭幀"""
        try:
            if not self.is_initialized or self.cap is None:
                logger.error("攝像頭未初始化")
                return False, None
            
            ret, frame = self.cap.read()
            if not ret:
                logger.error("無法讀取攝像頭數據")
                return False, None
            
            return True, frame
            
        except Exception as e:
            logger.error(f"讀取攝像頭數據失敗: {e}")
            return False, None
    
    def release(self):
        """釋放攝像頭資源"""
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                logger.info("攝像頭資源已釋放")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"釋放攝像頭資源失敗: {e}")