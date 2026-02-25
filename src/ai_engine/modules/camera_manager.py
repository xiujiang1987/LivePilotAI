# -*- coding: utf-8 -*-
"""
LivePilotAI 攝像頭管理模組
負責攝像頭的初始化、配置和管理
"""

import cv2
import logging
import time
import threading
import os
from typing import Optional, Tuple, Any, Callable
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    """攝像頭配置"""
    device_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    buffer_size: int = 1


@dataclass
class PerformanceStats:
    """性能統計"""
    fps: float = 0.0
    frame_count: int = 0
    dropped_frames: int = 0
    average_process_time: float = 0.0
    last_update_time: float = 0.0


class CameraSetupError(Exception):
    """攝像頭設置錯誤"""
    pass


class CameraManager:
    """增強的攝像頭管理器 - 支援即時捕獲和性能監控"""
    
    def __init__(self, config: Optional[CameraConfig] = None):
        self.config = config or CameraConfig()
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
        
        # 即時捕獲相關
        self.real_time_mode = False
        self.capture_thread: Optional[threading.Thread] = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        
        # 性能監控
        self.performance = PerformanceStats()
        self.frame_times = deque(maxlen=30)  # 保存最近30幀的時間
        self.process_times = deque(maxlen=30)  # 保存最近30次處理時間
        
        # 回調函數
        self.frame_callback: Optional[Callable] = None
    
    def initialize_camera(self) -> bool:
        """初始化攝像頭"""
        try:
            logger.info(f"正在初始化攝像頭 (device_id: {self.config.device_id})...")
            
            # 嘗試使用 DirectShow (Windows) 或默認後端
            if os.name == 'nt':
                self.cap = cv2.VideoCapture(self.config.device_id, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(self.config.device_id)
            
            if not self.cap.isOpened():
                # 如果 DirectShow 失敗，嘗試默認
                if os.name == 'nt':
                    logger.warning("DirectShow 初始化失敗，嘗試默認後端...")
                    self.cap = cv2.VideoCapture(self.config.device_id)
                
                if not self.cap.isOpened():
                    raise CameraSetupError(f"無法打開攝像頭 {self.config.device_id}")
            
            # 設置攝像頭參數
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)
            
            # 驗證設置
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"攝像頭設置完成: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_initialized = True
            logger.info("攝像頭初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"攝像頭初始化失敗: {e}")
            self.is_initialized = False
            return False
    
    def start_camera(self, device_id: Optional[int] = None) -> bool:
        """啟動攝像頭 - 為兼容性提供"""
        if device_id is not None:
            self.config.device_id = device_id
            # 如果已經初始化且設備ID改變，需要重新初始化
            if self.is_initialized:
                self.stop_real_time_capture()
                self.release()
                self.is_initialized = False
                
        return self.start_real_time_capture()
    
    def stop(self):
        """停止攝像頭"""
        self.stop_real_time_capture()
    
    def start_real_time_capture(self, callback: Optional[Callable] = None) -> bool:
        """
        啟動即時捕獲模式
        
        Args:
            callback: 幀處理回調函數
        """
        try:
            if not self.is_initialized:
                if not self.initialize_camera():
                    return False
            
            if self.real_time_mode:
                logger.warning("即時捕獲模式已啟動")
                return True
            
            self.frame_callback = callback
            self.running = True
            self.real_time_mode = True
            
            # 啟動捕獲線程
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            logger.info("即時捕獲模式已啟動")
            return True
            
        except Exception as e:
            logger.error(f"啟動即時捕獲失敗: {e}")
            return False
    
    def stop_real_time_capture(self):
        """停止即時捕獲模式"""
        try:
            self.running = False
            self.real_time_mode = False
            
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2.0)
            
            logger.info("即時捕獲模式已停止")
            
        except Exception as e:
            logger.error(f"停止即時捕獲失敗: {e}")
    
    def _capture_loop(self):
        """捕獲循環（在獨立線程中運行）"""
        while self.running and self.cap is not None:
            try:
                start_time = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("無法讀取攝像頭數據")
                    self.performance.dropped_frames += 1
                    continue
                
                # 更新當前幀
                with self.frame_lock:
                    self.current_frame = frame.copy()
                
                # 調用回調函數
                if self.frame_callback:
                    try:
                        process_start = time.time()
                        self.frame_callback(frame)
                        process_time = time.time() - process_start
                        self.process_times.append(process_time)
                    except Exception as e:
                        logger.error(f"幀處理回調失敗: {e}")
                
                # 更新性能統計
                frame_time = time.time() - start_time
                self.frame_times.append(frame_time)
                self._update_performance_stats()
                
                # 控制幀率
                target_delay = 1.0 / self.config.fps
                actual_delay = time.time() - start_time
                if actual_delay < target_delay:
                    time.sleep(target_delay - actual_delay)
                
            except Exception as e:
                logger.error(f"捕獲循環錯誤: {e}")
                time.sleep(0.1)
    
    def get_frame(self) -> Optional[Any]:
        """獲取當前幀 (兼容 PreviewWindow)"""
        if self.real_time_mode:
            with self.frame_lock:
                return self.current_frame.copy() if self.current_frame is not None else None
        else:
            success, frame = self.read_frame()
            return frame if success else None

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
    
    def test_camera(self) -> bool:
        """測試攝像頭是否正常工作"""
        try:
            logger.info("正在測試攝像頭...")
            
            if not self.is_initialized:
                if not self.initialize_camera():
                    return False
            
            for i in range(3):
                success, frame = self.read_frame()
                if not success:
                    logger.error(f"攝像頭測試失敗 - 第 {i+1} 次讀取失敗")
                    return False
            
            logger.info("攝像頭測試成功")
            return True
            
        except Exception as e:
            logger.error(f"攝像頭測試失敗: {e}")
            return False
    
    def get_camera_info(self) -> dict:
        """獲取攝像頭信息"""
        try:
            if not self.is_initialized or self.cap is None:
                return {"status": "未初始化"}
            
            return {
                "status": "正常",
                "device_id": self.config.device_id,
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
                "is_opened": self.cap.isOpened()
            }
            
        except Exception as e:
            logger.error(f"獲取攝像頭信息失敗: {e}")
            return {"status": "錯誤", "error": str(e)}
    
    def release(self):
        """釋放攝像頭資源"""
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                logger.info("攝像頭資源已釋放")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"釋放攝像頭資源失敗: {e}")
    
    def _update_performance_stats(self):
        """更新性能統計"""
        current_time = time.time()
        
        # 更新幀計數
        self.performance.frame_count += 1
        
        # 計算FPS（每秒更新一次）
        if current_time - self.performance.last_update_time >= 1.0:
            if len(self.frame_times) > 1:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.performance.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            # 計算平均處理時間
            if self.process_times:
                self.performance.average_process_time = sum(self.process_times) / len(self.process_times)
            
            self.performance.last_update_time = current_time
    
    def get_performance_stats(self) -> PerformanceStats:
        """獲取性能統計"""
        return self.performance

    def get_available_cameras(self) -> list:
        """獲取可用攝像頭列表"""
        available_cameras = []
        # 掃描前 5 個索引
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(f"Camera {i}")
                    cap.release()
            except:
                pass
        return available_cameras if available_cameras else ["Default Camera"]

    def __del__(self):
        """析構函數，確保資源被釋放"""
        self.release()
