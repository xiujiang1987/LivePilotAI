# -*- coding: utf-8 -*-
"""
LivePilotAI 人臉檢測模組
負責即時人臉檢測和視覺化
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class FaceDetection:
    """人臉檢測結果"""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    landmarks: Optional[List[Tuple[int, int]]] = None


@dataclass
class DetectionConfig:
    """檢測配置"""
    # Haar Cascade 配置
    scale_factor: float = 1.1
    min_neighbors: int = 5
    min_size: Tuple[int, int] = (30, 30)
    max_size: Tuple[int, int] = (300, 300)
    
    # DNN 配置
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    
    # 性能配置
    enable_dnn: bool = True
    enable_tracking: bool = True
    max_faces: int = 10


class FaceDetector:
    """
    人臉檢測器 - 支援多種檢測方法
    
    功能：
    1. Haar Cascade 檢測（快速但準確度較低）
    2. DNN 檢測（準確度高但較慢）
    3. 混合模式（根據情況自動選擇）
    4. 人臉追蹤（提升連續檢測性能）
    """
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        self.config = config or DetectionConfig()
        
        # 初始化 Haar Cascade
        self._init_haar_cascade()
        
        # 初始化 DNN 模型
        if self.config.enable_dnn:
            self._init_dnn_model()
        
        # 追蹤相關
        self.trackers = []
        self.tracking_enabled = self.config.enable_tracking
        
        # 性能統計
        self.detection_times = []
        self.last_detection_method = "none"
    
    def _init_haar_cascade(self):
        """初始化 Haar Cascade 檢測器"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                raise Exception("無法載入 Haar Cascade 分類器")
            logger.info("Haar Cascade 人臉檢測器初始化成功")
        except Exception as e:
            logger.error(f"Haar Cascade 初始化失敗: {e}")
            self.face_cascade = None
    
    def _init_dnn_model(self):
        """初始化 DNN 人臉檢測模型"""
        try:
            # 使用 OpenCV 預訓練的 DNN 模型
            model_path = "models/opencv_face_detector_uint8.pb"
            config_path = "models/opencv_face_detector.pbtxt"
            
            # 如果模型文件不存在，使用內建的 Haar Cascade
            try:
                self.dnn_net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
                logger.info("DNN 人臉檢測模型載入成功")
            except:
                logger.warning("DNN 模型文件不存在，僅使用 Haar Cascade")
                self.dnn_net = None
                self.config.enable_dnn = False
                
        except Exception as e:
            logger.error(f"DNN 模型初始化失敗: {e}")
            self.dnn_net = None
            self.config.enable_dnn = False
    
    def detect_faces(self, frame: np.ndarray, method: str = "auto") -> List[FaceDetection]:
        """
        檢測人臉
        
        Args:
            frame: 輸入影像
            method: 檢測方法 ("haar", "dnn", "auto")
        
        Returns:
            檢測到的人臉列表
        """
        start_time = time.time()
        
        try:
            if method == "auto":
                method = self._choose_detection_method(frame)
            
            if method == "dnn" and self.dnn_net is not None:
                faces = self._detect_faces_dnn(frame)
            else:
                faces = self._detect_faces_haar(frame)
            
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            if len(self.detection_times) > 100:
                self.detection_times.pop(0)
            
            self.last_detection_method = method
            
            logger.debug(f"檢測到 {len(faces)} 張人臉，耗時 {detection_time:.3f}s，方法: {method}")
            return faces[:self.config.max_faces]  # 限制最大檢測數量
            
        except Exception as e:
            logger.error(f"人臉檢測失敗: {e}")
            return []
    
    def _detect_faces_haar(self, frame: np.ndarray) -> List[FaceDetection]:
        """使用 Haar Cascade 檢測人臉"""
        if self.face_cascade is None:
            return []
        
        # 轉換為灰度圖
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 直方圖均衡化
        gray = cv2.equalizeHist(gray)
        
        # 檢測人臉
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.config.scale_factor,
            minNeighbors=self.config.min_neighbors,
            minSize=self.config.min_size,
            maxSize=self.config.max_size
        )
        
        # 轉換為 FaceDetection 對象
        detections = []
        for (x, y, w, h) in faces:
            detection = FaceDetection(
                x=int(x), y=int(y), 
                width=int(w), height=int(h),
                confidence=1.0  # Haar Cascade 不提供置信度
            )
            detections.append(detection)
        
        return detections
    
    def _detect_faces_dnn(self, frame: np.ndarray) -> List[FaceDetection]:
        """使用 DNN 檢測人臉"""
        if self.dnn_net is None:
            return self._detect_faces_haar(frame)
        
        h, w = frame.shape[:2]
        
        # 創建 blob
        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (300, 300), [104, 117, 123]
        )
        
        # 設置輸入
        self.dnn_net.setInput(blob)
        
        # 前向傳播
        detections = self.dnn_net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.config.confidence_threshold:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)
                
                # 確保座標在圖像範圍內
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                
                if x2 > x1 and y2 > y1:
                    detection = FaceDetection(
                        x=x1, y=y1,
                        width=x2-x1, height=y2-y1,
                        confidence=float(confidence)
                    )
                    faces.append(detection)
        
        return faces
    
    def _choose_detection_method(self, frame: np.ndarray) -> str:
        """自動選擇檢測方法"""
        # 簡單的策略：根據圖像大小和性能選擇
        h, w = frame.shape[:2]
        pixel_count = h * w
        
        # 如果圖像較大或需要高精度，使用 DNN
        if pixel_count > 640 * 480 and self.config.enable_dnn:
            return "dnn"
        else:
            return "haar"
    
    def draw_faces(self, frame: np.ndarray, faces: List[FaceDetection], 
                  show_confidence: bool = True) -> np.ndarray:
        """
        在圖像上繪製人臉框
        
        Args:
            frame: 輸入圖像
            faces: 檢測到的人臉
            show_confidence: 是否顯示置信度
        
        Returns:
            繪製後的圖像
        """
        result_frame = frame.copy()
        
        for i, face in enumerate(faces):
            # 繪製人臉框
            color = (0, 255, 0)  # 綠色
            thickness = 2
            
            cv2.rectangle(
                result_frame,
                (face.x, face.y),
                (face.x + face.width, face.y + face.height),
                color, thickness
            )
            
            # 繪製標籤
            label = f"Face {i+1}"
            if show_confidence and face.confidence < 1.0:
                label += f" ({face.confidence:.2f})"
            
            # 計算文字位置
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            label_y = face.y - 10 if face.y - 10 > label_size[1] else face.y + face.height + 20
            
            # 繪製背景框
            cv2.rectangle(
                result_frame,
                (face.x, label_y - label_size[1] - 5),
                (face.x + label_size[0] + 5, label_y + 5),
                color, -1
            )
            
            # 繪製文字
            cv2.putText(
                result_frame, label,
                (face.x + 2, label_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1
            )
        
        return result_frame
    
    def get_face_roi(self, frame: np.ndarray, face: FaceDetection, 
                    padding: float = 0.1) -> Optional[np.ndarray]:
        """
        提取人臉區域
        
        Args:
            frame: 原始圖像
            face: 人臉檢測結果
            padding: 邊界擴展比例
        
        Returns:
            人臉區域圖像
        """
        try:
            h, w = frame.shape[:2]
            
            # 計算擴展後的邊界
            pad_w = int(face.width * padding)
            pad_h = int(face.height * padding)
            
            x1 = max(0, face.x - pad_w)
            y1 = max(0, face.y - pad_h)
            x2 = min(w, face.x + face.width + pad_w)
            y2 = min(h, face.y + face.height + pad_h)
            
            return frame[y1:y2, x1:x2]
            
        except Exception as e:
            logger.error(f"提取人臉區域失敗: {e}")
            return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計"""
        if not self.detection_times:
            return {
                "average_detection_time": 0.0,
                "detection_fps": 0.0,
                "last_method": self.last_detection_method,
                "total_detections": 0
            }
        
        avg_time = sum(self.detection_times) / len(self.detection_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            "average_detection_time": avg_time,
            "detection_fps": fps,
            "last_method": self.last_detection_method,
            "total_detections": len(self.detection_times),
            "method_available": {
                "haar": self.face_cascade is not None,
                "dnn": self.dnn_net is not None
            }
        }


class FaceDetectionPipeline:
    """人臉檢測流水線 - 整合攝像頭和檢測功能"""
    
    def __init__(self, camera_manager, face_detector: Optional[FaceDetector] = None):
        self.camera_manager = camera_manager
        self.face_detector = face_detector or FaceDetector()
        self.is_running = False
        self.detection_callback = None
        
        # 統計信息
        self.total_frames = 0
        self.total_faces = 0
        self.start_time = None
    
    def start_detection(self, callback=None):
        """開始檢測流程"""
        self.detection_callback = callback
        self.start_time = time.time()
        self.is_running = True
        
        # 設置攝像頭回調
        return self.camera_manager.start_real_time_capture(self._process_frame)
    
    def stop_detection(self):
        """停止檢測流程"""
        self.is_running = False
        self.camera_manager.stop_real_time_capture()
    
    def _process_frame(self, frame):
        """處理每一幀"""
        if not self.is_running:
            return
        
        try:
            # 檢測人臉
            faces = self.face_detector.detect_faces(frame)
            
            # 更新統計
            self.total_frames += 1
            self.total_faces += len(faces)
            
            # 調用外部回調
            if self.detection_callback:
                self.detection_callback(frame, faces)
                
        except Exception as e:
            logger.error(f"幀處理失敗: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        runtime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "runtime_seconds": runtime,
            "total_frames": self.total_frames,
            "total_faces": self.total_faces,
            "avg_faces_per_frame": self.total_faces / max(1, self.total_frames),
            "processing_fps": self.total_frames / max(1, runtime),
            "camera_stats": self.camera_manager.get_performance_stats(),
            "detector_stats": self.face_detector.get_performance_stats()
        }
