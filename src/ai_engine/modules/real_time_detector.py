# -*- coding: utf-8 -*-
"""
LivePilotAI 即時情感檢測系統
整合人臉檢測、情感識別和攝像頭管理
"""

import cv2
import numpy as np
import logging
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path

from .camera_manager import CameraManager, CameraConfig
from .face_detector import FaceDetector, FaceDetection, DetectionConfig
from ..emotion_detector import EmotionDetector
from .face_tracker import FaceTracker
from .emotion_intensity import EmotionIntensityAnalyzer, EmotionDynamics
from .visualizer import Visualizer

logger = logging.getLogger(__name__)


@dataclass
class EmotionResult:
    """情感檢測結果"""
    face_id: int
    emotion: str
    confidence: float
    emotions_distribution: Dict[str, float]
    face_detection: FaceDetection


@dataclass
class RealTimeConfig:
    """即時檢測配置"""
    # 攝像頭配置
    camera_config: CameraConfig = field(default_factory=CameraConfig)
    
    # 檢測配置
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    
    # 情感檢測配置
    emotion_model_path: str = "models/emotion_detection.h5"
    
    # 性能配置
    target_fps: int = 24
    max_detection_delay: float = 0.1  # 最大檢測延遲 100ms
    
    # 顯示配置
    show_video: bool = True
    show_emotions: bool = True
    show_confidence: bool = True
    window_name: str = "LivePilotAI - 即時情感檢測"


class RealTimeEmotionDetector:
    """
    即時情感檢測系統
    
    功能：
    1. 即時攝像頭捕獲
    2. 人臉檢測
    3. 情感識別
    4. 視覺化顯示
    5. 性能監控
    """
    
    def __init__(self, config: Optional[RealTimeConfig] = None, 
                 emotion_detector: Optional[EmotionDetector] = None,
                 camera_manager: Optional[CameraManager] = None):
        self.config = config or RealTimeConfig()
        
        # 初始化組件 - 支援依賴注入
        self.camera_manager = camera_manager or CameraManager(self.config.camera_config)
        self.face_detector = FaceDetector(self.config.detection_config)
        self.emotion_detector = emotion_detector or EmotionDetector(self.config.emotion_model_path)
        
        # Day 5 新增組件
        self.face_tracker = FaceTracker()
        self.visualizer = Visualizer()
        self.analyzers: Dict[int, EmotionIntensityAnalyzer] = {} # face_id -> analyzer
        
        # 運行狀態
        self.is_running = False
        self.is_paused = False
        
        # 結果存儲
        self.latest_results: List[EmotionResult] = []
        self.results_lock = threading.Lock()
        
        # 性能統計
        self.performance_stats = {
            "total_frames": 0,
            "total_faces": 0,
            "total_emotions": 0,
            "avg_processing_time": 0.0,
            "current_fps": 0.0,
            "start_time": None
        }
        
        # 回調函數
        self.result_callback: Optional[Callable] = None
        
        # 視覺化
        self.display_frame = None
    
    def start(self, result_callback: Optional[Callable] = None) -> bool:
        """
        啟動即時檢測系統
        
        Args:
            result_callback: 結果回調函數，接收 (frame, results) 參數
        
        Returns:
            是否成功啟動
        """
        try:
            logger.info("正在啟動即時情感檢測系統...")
            
            # 設置回調函數
            self.result_callback = result_callback
            
            # 初始化攝像頭
            if not self.camera_manager.initialize_camera():
                logger.error("攝像頭初始化失敗")
                return False
            
            # 重置統計
            self.performance_stats["start_time"] = time.time()
            self.performance_stats["total_frames"] = 0
            self.performance_stats["total_faces"] = 0
            self.performance_stats["total_emotions"] = 0
            
            # 啟動即時捕獲
            success = self.camera_manager.start_real_time_capture(self._process_frame)
            if success:
                self.is_running = True
                logger.info("即時情感檢測系統啟動成功")
                
                # 如果需要顯示視頻，啟動顯示線程
                if self.config.show_video:
                    self._start_display_thread()
            
            return success
            
        except Exception as e:
            logger.error(f"啟動即時檢測系統失敗: {e}")
            return False
    
    def stop(self):
        """停止即時檢測系統"""
        try:
            logger.info("正在停止即時情感檢測系統...")
            
            self.is_running = False
            
            # 停止攝像頭捕獲
            self.camera_manager.stop_real_time_capture()
            
            # 關閉顯示窗口
            if self.config.show_video:
                cv2.destroyAllWindows()
            
            logger.info("即時情感檢測系統已停止")
            
        except Exception as e:
            logger.error(f"停止即時檢測系統失敗: {e}")
    
    def pause(self):
        """暫停檢測（保持攝像頭運行）"""
        self.is_paused = True
        logger.info("檢測已暫停")
    
    def resume(self):
        """恢復檢測"""
        self.is_paused = False
        logger.info("檢測已恢復")
    
    def _process_frame(self, frame: np.ndarray):
        """處理每一幀"""
        if not self.is_running or self.is_paused:
            return
        
        try:
            start_time = time.time()
            
            # 檢測人臉
            faces = self.face_detector.detect_faces(frame)
            
            # 轉換為矩形列表供追蹤器使用
            rects = [(f.x, f.y, f.width, f.height) for f in faces]
            
            # 更新追蹤器
            tracked_faces = self.face_tracker.update(rects)
            
            # 情感識別
            emotion_results = []
            
            # 處理每個被追蹤的人臉
            for face_id, tracked_face in tracked_faces.items():
                # 如果消失太久，跳過處理
                if tracked_face.disappeared_frames > 0:
                    continue
                    
                x, y, w, h = tracked_face.bbox
                
                # 邊界檢查與修正
                h_img, w_img = frame.shape[:2]
                x = max(0, x); y = max(0, y)
                w = min(w, w_img - x); h = min(h, h_img - y)
                
                if w < 20 or h < 20: continue

                # 提取 ROI
                face_roi = frame[y:y+h, x:x+w]
                
                # 情感檢測
                emotion_data = self.emotion_detector.predict_emotion_from_image(face_roi)
                
                if emotion_data:
                    # 獲取或創建分析器
                    if face_id not in self.analyzers:
                        self.analyzers[face_id] = EmotionIntensityAnalyzer()
                    
                    analyzer = self.analyzers[face_id]
                    
                    # 分析強度與動態
                    dynamics = analyzer.analyze(emotion_data.get('emotions', {}))
                    
                    # 構造結果
                    face_detection_obj = FaceDetection(x=x, y=y, width=w, height=h)
                    
                    emotion_result = EmotionResult(
                        face_id=face_id,
                        emotion=dynamics.current_emotion,
                        confidence=dynamics.intensity, 
                        emotions_distribution=emotion_data.get('emotions', {}),
                        face_detection=face_detection_obj
                    )
                    # 附加動態屬性供視覺化使用
                    emotion_result.intensity = dynamics.intensity
                    emotion_result.metrics = {
                        "stability": dynamics.stability,
                        "transition_speed": dynamics.transition_speed
                    }
                    
                    emotion_results.append(emotion_result)
            
            # 清理過期的分析器
            for fid in list(self.analyzers.keys()):
                if fid not in tracked_faces:
                    del self.analyzers[fid]
            
            # 更新結果
            with self.results_lock:
                self.latest_results = emotion_results
            
            # 生成視覺化幀
            display_frame = self._create_display_frame(frame, emotion_results)
            self.display_frame = display_frame
            
            # 更新性能統計
            processing_time = time.time() - start_time
            self._update_performance_stats(len(faces), len(emotion_results), processing_time)
            
            # 調用外部回調
            if self.result_callback:
                self.result_callback(frame, emotion_results)
            
            # 檢查性能
            if processing_time > self.config.max_detection_delay:
                # logger.warning(f"檢測延遲過高: {processing_time:.3f}s")
                pass
                
        except Exception as e:
            logger.error(f"幀處理失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_display_frame(self, frame: np.ndarray, results: List[EmotionResult]) -> np.ndarray:
        """創建顯示幀"""
        # 轉換數據供 Visualizer 使用
        detections_data = []
        for result in results:
            face = result.face_detection
            data = {
                "bbox": (face.x, face.y, face.width, face.height),
                "emotion": result.emotion,
                "confidence": result.confidence,
                "face_id": result.face_id,
                "intensity": getattr(result, "intensity", 0.0),
                "landmarks": getattr(face, "landmarks", None)
            }
            detections_data.append(data)
            
        # 使用 Visualizer 強大的繪圖功能
        display_frame = self.visualizer.draw_detections(frame, detections_data)
        
        # 繪製系統信息 (FPS, 狀態等)
        self._draw_system_info(display_frame)
        
        return display_frame
    
    def _draw_system_info(self, frame: np.ndarray):
        """繪製系統信息"""
        # 系統狀態
        status_text = "RUNNING" if not self.is_paused else "PAUSED"
        status_color = (0, 255, 0) if not self.is_paused else (0, 255, 255)
        
        cv2.putText(frame, f"Status: {status_text}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # FPS 信息
        fps_text = f"FPS: {self.performance_stats['current_fps']:.1f}"
        cv2.putText(frame, fps_text, (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 檢測統計
        faces_count = len(self.latest_results)
        stats_text = f"Faces: {faces_count}"
        cv2.putText(frame, stats_text, (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 操作提示
        help_text = "Press 'p' to pause, 'q' to quit, 's' to save"
        cv2.putText(frame, help_text, (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def _start_display_thread(self):
        """啟動顯示線程"""
        def display_loop():
            while self.is_running:
                if self.display_frame is not None:
                    cv2.imshow(self.config.window_name, self.display_frame)
                    
                    # 處理按鍵
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.stop()
                        break
                    elif key == ord('p'):
                        if self.is_paused:
                            self.resume()
                        else:
                            self.pause()
                    elif key == ord('s'):
                        self._save_screenshot()
                
                time.sleep(0.01)  # 控制顯示頻率
        
        display_thread = threading.Thread(target=display_loop)
        display_thread.daemon = True
        display_thread.start()
    
    def _save_screenshot(self):
        """保存截圖"""
        if self.display_frame is not None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"livepilot_screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.display_frame)
            logger.info(f"截圖已保存: {filename}")
    
    def _update_performance_stats(self, faces_count: int, emotions_count: int, processing_time: float):
        """更新性能統計"""
        self.performance_stats["total_frames"] += 1
        self.performance_stats["total_faces"] += faces_count
        self.performance_stats["total_emotions"] += emotions_count
        
        # 計算當前 FPS
        if self.performance_stats["start_time"]:
            runtime = time.time() - self.performance_stats["start_time"]
            self.performance_stats["current_fps"] = self.performance_stats["total_frames"] / runtime
        
        # 更新平均處理時間
        total_frames = self.performance_stats["total_frames"]
        current_avg = self.performance_stats["avg_processing_time"]
        self.performance_stats["avg_processing_time"] = (
            (current_avg * (total_frames - 1) + processing_time) / total_frames
        )
    
    def get_latest_results(self) -> List[EmotionResult]:
        """獲取最新檢測結果"""
        with self.results_lock:
            return self.latest_results.copy()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計"""
        stats = self.performance_stats.copy()
        
        # 添加組件統計
        stats["camera_stats"] = self.camera_manager.get_performance_stats()
        stats["detector_stats"] = self.face_detector.get_performance_stats()
        
        return stats
    
    def save_performance_report(self, filepath: str):
        """保存性能報告"""
        try:
            stats = self.get_performance_stats()
            
            report = f"""
LivePilotAI 即時情感檢測性能報告
===================================

系統配置:
- 目標 FPS: {self.config.target_fps}
- 最大延遲: {self.config.max_detection_delay}s
- 攝像頭解析度: {self.config.camera_config.width}x{self.config.camera_config.height}

檢測統計:
- 總處理幀數: {stats['total_frames']}
- 總檢測人臉: {stats['total_faces']}
- 總情感檢測: {stats['total_emotions']}
- 當前 FPS: {stats['current_fps']:.2f}
- 平均處理時間: {stats['avg_processing_time']:.3f}s

攝像頭性能:
- 攝像頭 FPS: {stats['camera_stats'].fps:.2f}
- 丟失幀數: {stats['camera_stats'].dropped_frames}

檢測器性能:
- 檢測 FPS: {stats['detector_stats']['detection_fps']:.2f}
- 平均檢測時間: {stats['detector_stats']['average_detection_time']:.3f}s
- 使用方法: {stats['detector_stats']['last_method']}

生成時間: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"性能報告已保存: {filepath}")
            
        except Exception as e:
            logger.error(f"保存性能報告失敗: {e}")


def create_real_time_detector(
    camera_device: int = 0,
    target_fps: int = 24,
    show_video: bool = True
) -> RealTimeEmotionDetector:
    """
    創建即時檢測器的便捷函數
    
    Args:
        camera_device: 攝像頭設備ID
        target_fps: 目標FPS
        show_video: 是否顯示視頻
    
    Returns:
        配置好的即時檢測器
    """
    config = RealTimeConfig()
    config.camera_config.device_id = camera_device
    config.target_fps = target_fps
    config.show_video = show_video
    
    return RealTimeEmotionDetector(config)
