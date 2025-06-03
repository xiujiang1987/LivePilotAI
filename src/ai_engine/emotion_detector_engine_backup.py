"""
LivePilotAI - 情感檢測引擎
基於 AIEngineBase 架構的即時情感檢測實作
"""

import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import time
from dataclasses import dataclass
import logging

from .base_engine import AIEngineBase, ProcessingResult, EngineState


@dataclass
class EmotionResult:
    """情感檢測結果數據類"""
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    emotions: Dict[str, float]       # 各情感的置信度
    dominant_emotion: str            # 主要情感
    confidence: float               # 主要情感的置信度
    face_id: Optional[int] = None   # 人臉追蹤ID


class EmotionDetectorEngine(AIEngineBase):
    """
    情感檢測引擎
    
    支援7種情感分類：
    - Happy (快樂)
    - Sad (悲傷) 
    - Angry (憤怒)
    - Surprise (驚訝)
    - Fear (恐懼)
    - Disgust (厭惡)
    - Neutral (中性)
    """
    
    def __init__(self, engine_id: str = "emotion_detector", config: Optional[Dict[str, Any]] = None):
        """
        初始化情感檢測引擎
        
        Args:
            engine_id: 引擎唯一識別碼
            config: 配置參數
        """
        default_config = {
            "model_path": "assets/models/emotion_detection.h5",
            "input_size": (48, 48),
            "emotion_labels": [
                'Angry', 'Disgust', 'Fear', 'Happy', 
                'Sad', 'Surprise', 'Neutral'
            ],
            "face_detection": {
                "cascade_file": "haarcascade_frontalface_default.xml",
                "scale_factor": 1.1,
                "min_neighbors": 5,
                "min_size": (30, 30)
            },
            "smoothing": {
                "enabled": True,
                "history_size": 5,
                "threshold": 0.6
            },
            "performance": {
                "max_faces": 5,
                "target_fps": 30
            }
        }
        
        # 合併預設配置和用戶配置
        if config:
            default_config.update(config)
            
        super().__init__(engine_id, default_config)
        
        # 初始化模型和檢測器變數
        self.model: Optional[tf.keras.Model] = None
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
          # 情感歷史記錄 (用於平滑處理)
        self.emotion_history: List[List[Dict[str, float]]] = []
        self.last_faces: List[EmotionResult] = []
        
        # 效能監控
        self.processing_times: List[float] = []
        
    async def initialize(self) -> bool:
        """初始化情感檢測引擎"""
        try:
            self.state = EngineState.INITIALIZING
            self.logger.info(f"初始化情感檢測引擎: {self.engine_id}")
            
            # 載入TensorFlow模型
            await self._load_model()
            
            # 初始化OpenCV人臉檢測器
            await self._init_face_detector()
            
            self.state = EngineState.IDLE
            self.logger.info("情感檢測引擎初始化完成")
            return True
            
        except Exception as e:
            self.state = EngineState.ERROR
            self.logger.error(f"引擎初始化失敗: {e}")
            return False
    
    async def _load_model(self):
        """載入情感檢測模型"""
        model_path = self.config["model_path"]
        
        try:
            # 嘗試載入預訓練模型
            self.model = tf.keras.models.load_model(model_path)
            self.logger.info(f"成功載入情感檢測模型: {model_path}")
            
        except (FileNotFoundError, OSError) as e:
            self.logger.warning(f"無法載入模型檔案 {model_path}: {e}")
            self.logger.info("建立預設CNN模型...")
            
            # 建立預設模型架構
            self.model = self._create_default_model()
            
        except Exception as e:
            self.logger.error(f"模型載入失敗: {e}")
            raise
    
    def _create_default_model(self) -> tf.keras.Model:
        """建立預設的CNN模型架構"""
        input_shape = (*self.config["input_size"], 1)
        num_classes = len(self.config["emotion_labels"])
        
        model = tf.keras.Sequential([
            # 第一層卷積塊
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Dropout(0.25),
            
            # 第二層卷積塊
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Dropout(0.25),
            
            # 全連接層
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.logger.info("預設CNN模型建立完成")
        return model
      async def _init_face_detector(self):
        """初始化OpenCV人臉檢測器"""
        cascade_file = self.config["face_detection"]["cascade_file"]
        
        try:
            # 使用OpenCV預設的人臉檢測器
            cascade_path = cv2.data.haarcascades + cascade_file
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade is None or self.face_cascade.empty():
                raise ValueError("無法載入人臉檢測器")
                
            self.logger.info("人臉檢測器初始化完成")
              except Exception as e:
            self.logger.error(f"人臉檢測器初始化失敗: {e}")
            raise
    
    async def process(self, input_data: Any) -> ProcessingResult:
        """
        處理輸入數據進行情感檢測
        
        Args:
            input_data: 輸入影像 (numpy array, BGR格式)
            
        Returns:
            ProcessingResult: 處理結果
        """
        start_time = time.time()
        
        try:
            self.state = EngineState.PROCESSING
            
            # 驗證輸入數據
            if not isinstance(input_data, np.ndarray):
                raise ValueError("輸入數據必須是numpy array")
            
            # 檢測人臉和情感
            emotion_results = await self._detect_emotions(input_data)
            
            # 計算處理時間
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # 保持處理時間歷史記錄在合理範圍內
            if len(self.processing_times) > 100:
                self.processing_times = self.processing_times[-50:]
            
            result_data = {
                "emotions": emotion_results,
                "frame_info": {
                    "shape": input_data.shape,
                    "faces_detected": len(emotion_results)
                },
                "performance": {
                    "processing_time": processing_time,
                    "fps": 1.0 / processing_time if processing_time > 0 else 0,
                    "avg_processing_time": np.mean(self.processing_times)
                }
            }
            
            self.state = EngineState.IDLE
            
            result = ProcessingResult(
                success=True,
                data=result_data,
                timestamp=time.time(),
                processing_time=processing_time
            )
            
            self._last_result = result
            return result
            
        except Exception as e:
            self.state = EngineState.ERROR
            error_msg = f"情感檢測處理失敗: {e}"
            self.logger.error(error_msg)
            
            return ProcessingResult(
                success=False,
                data={},
                timestamp=time.time(),
                processing_time=time.time() - start_time,
                error_message=error_msg
            )
    
    async def _detect_emotions(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """檢測畫面中所有人臉的情感"""
        # 檢測人臉
        faces = await self._detect_faces(frame)
        
        if not faces:
            return []
        
        emotion_results = []
        max_faces = self.config["performance"]["max_faces"]
        
        # 限制處理的人臉數量以提升效能
        for i, (x, y, w, h) in enumerate(faces[:max_faces]):
            # 擷取人臉區域
            face_region = frame[y:y+h, x:x+w]
            
            # 預處理人臉
            face_tensor = self._preprocess_face(face_region)
            
            # 情感預測
            emotions = await self._predict_emotion(face_tensor)
            
            # 平滑處理
            if self.config["smoothing"]["enabled"]:
                emotions = self._smooth_emotions(emotions, i)
              # 找出主要情感
            dominant_emotion = max(emotions.keys(), key=lambda k: emotions[k])
            confidence = emotions[dominant_emotion]
            
            emotion_result = EmotionResult(
                bbox=(x, y, w, h),
                emotions=emotions,
                dominant_emotion=dominant_emotion,
                confidence=confidence,
                face_id=i
            )
            
            emotion_results.append(emotion_result.__dict__)
        
        return emotion_results
    
    async def _detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """檢測畫面中的人臉"""
        # 轉換為灰階
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
          # 人臉檢測
        face_config = self.config["face_detection"]
        if self.face_cascade is not None:
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=face_config["scale_factor"],
                minNeighbors=face_config["min_neighbors"],
                minSize=face_config["min_size"]
            )
        else:
            faces = []
        
        return list(faces) if len(faces) > 0 else []
    
    def _preprocess_face(self, face_region: np.ndarray) -> np.ndarray:
        """預處理人臉區域用於情感識別"""
        input_size = self.config["input_size"]
        
        # 轉換為灰階
        if len(face_region.shape) == 3:
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_region
        
        # 調整大小
        face_resized = cv2.resize(face_gray, input_size)
        
        # 正規化像素值
        face_normalized = face_resized / 255.0
        
        # 擴展維度以符合模型輸入
        face_tensor = np.expand_dims(face_normalized, axis=-1)
        face_tensor = np.expand_dims(face_tensor, axis=0)
          return face_tensor
    
    async def _predict_emotion(self, face_tensor: np.ndarray) -> Dict[str, float]:
        """預測人臉情感"""
        try:
            # 使用模型進行預測
            if self.model is not None:
                predictions = self.model.predict(face_tensor, verbose=0)
                emotion_probs = predictions[0]
                
                # 建立情感-置信度字典
                emotion_labels = self.config["emotion_labels"]
                emotion_dict = {
                    emotion: float(prob) 
                    for emotion, prob in zip(emotion_labels, emotion_probs)
                }
                
                return emotion_dict
            else:
                # 返回中性情感作為預設值
                emotion_labels = self.config["emotion_labels"]
                return {emotion: 0.0 for emotion in emotion_labels}
            
        except Exception as e:
            self.logger.error(f"情感預測失敗: {e}")
            # 返回中性情感作為預設值
            emotion_labels = self.config["emotion_labels"]
            return {emotion: 0.0 for emotion in emotion_labels}
    
    def _smooth_emotions(self, current_emotions: Dict[str, float], face_id: int) -> Dict[str, float]:
        """使用歷史記錄平滑情感預測結果"""
        # 確保歷史記錄列表足夠大
        while len(self.emotion_history) <= face_id:
            self.emotion_history.append([])
        
        face_history = self.emotion_history[face_id]
        history_size = self.config["smoothing"]["history_size"]
        
        # 加入當前預測到歷史記錄
        face_history.append(current_emotions)
        
        # 保持歷史記錄大小
        if len(face_history) > history_size:
            face_history.pop(0)
        
        # 計算平均值
        if len(face_history) == 1:
            return current_emotions
        
        smoothed_emotions = {}
        emotion_labels = self.config["emotion_labels"]
        
        for emotion in emotion_labels:
            avg_confidence = np.mean([
                hist[emotion] for hist in face_history
            ])
            smoothed_emotions[emotion] = float(avg_confidence)
        
        return smoothed_emotions
    
    async def cleanup(self) -> bool:
        """清理資源"""
        try:
            self.state = EngineState.STOPPED
            
            # 清理模型資源
            if self.model:
                del self.model
                self.model = None
            
            # 清理歷史記錄
            self.emotion_history.clear()
            self.processing_times.clear()
            
            self.logger.info("情感檢測引擎資源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"資源清理失敗: {e}")
            return False
    
    def get_engine_status(self) -> Dict[str, Any]:
        """獲取引擎狀態資訊"""
        avg_processing_time = (
            np.mean(self.processing_times) 
            if self.processing_times else 0
        )
        
        return {
            "engine_id": self.engine_id,
            "state": self.state.value,
            "model_loaded": self.model is not None,
            "face_detector_ready": self.face_cascade is not None,
            "performance": {
                "avg_processing_time": avg_processing_time,
                "estimated_fps": 1.0 / avg_processing_time if avg_processing_time > 0 else 0,
                "total_processed": len(self.processing_times)
            },
            "last_result": {
                "timestamp": self._last_result.timestamp if self._last_result else None,
                "success": self._last_result.success if self._last_result else None
            }
        }


# 輔助函數
def create_emotion_detector_engine(config: Optional[Dict[str, Any]] = None) -> EmotionDetectorEngine:
    """
    建立情感檢測引擎實例的工廠函數
    
    Args:
        config: 可選的配置參數
        
    Returns:
        EmotionDetectorEngine: 情感檢測引擎實例
    """
    return EmotionDetectorEngine(config=config)


def draw_emotion_results(frame: np.ndarray, emotion_results: List[Dict[str, Any]]) -> np.ndarray:
    """
    在影像上繪製情感檢測結果
    
    Args:
        frame: 原始影像
        emotion_results: 情感檢測結果列表
        
    Returns:
        標註後的影像
    """
    annotated_frame = frame.copy()
    
    for result in emotion_results:
        x, y, w, h = result['bbox']
        emotion = result['dominant_emotion']
        confidence = result['confidence']
        
        # 根據置信度選擇顏色
        if confidence > 0.8:
            color = (0, 255, 0)  # 綠色 - 高置信度
        elif confidence > 0.6:
            color = (0, 255, 255)  # 黃色 - 中等置信度
        else:
            color = (0, 0, 255)  # 紅色 - 低置信度
        
        # 繪製人臉邊界框
        cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
        
        # 準備顯示文字
        label = f"{emotion}: {confidence:.2f}"
        
        # 計算文字大小和位置
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        # 繪製文字背景
        cv2.rectangle(
            annotated_frame,
            (x, y - text_height - 10),
            (x + text_width, y),
            color,
            -1
        )
        
        # 繪製文字
        cv2.putText(
            annotated_frame,
            label,
            (x, y - 5),
            font,
            font_scale,
            (255, 255, 255),  # 白色文字
            thickness
        )
    
    return annotated_frame
