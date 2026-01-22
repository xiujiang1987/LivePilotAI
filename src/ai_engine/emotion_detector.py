"""
LivePilotAI - 情緒識別核心引擎
即時人臉情緒分析模組，支援實時情緒檢測與分析
"""

import cv2
import numpy as np
# Lazy import tensorflow to improve startup time and allow TFLite usage
# import tensorflow as tf 
from typing import Dict, List, Tuple, Optional, Any
import logging
import asyncio
import mediapipe as mp
from dataclasses import dataclass
import time
import os
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmotionResult:
    """情緒檢測結果"""
    emotion: str
    confidence: float
    bbox: List[int]
    probabilities: Dict[str, float]
    landmarks: Optional[List[List[int]]] = None
    metrics: Optional[Dict[str, float]] = None

class EmotionDetector:
    """
    即時情緒識別類別
    
    支援10種情緒分類：
    - 快樂 (Happy) 
    - 悲傷 (Sad)
    - 憤怒 (Angry)
    - 驚訝 (Surprise) 
    - 恐懼 (Fear)
    - 厭惡 (Disgust)
    - 中性 (Neutral)
    - 專注 (Focused)
    - 興奮 (Excited)  
    - 放鬆 (Relaxed)
    """
    
    def __init__(self, model_path: str = "models/emotion_detection.h5"):
        """
        初始化情緒檢測器
        
        Args:
            model_path: 預訓練模型路徑
        """
        self.emotion_labels = [
            'angry', 'disgust', 'fear', 'happy', 
            'sad', 'surprise', 'neutral', 'focused',
            'excited', 'relaxed'
        ]
        
        # 模型相關
        self.interpreter = None # TFLite Interpreter
        self.model = None       # Keras Model (Fallback)
        self.model_path = model_path
        self.input_size = (224, 224)
        
        # 嘗試載入模型 (優先嘗試 TFLite)
        self._load_model_sync()

    def _load_model_sync(self):
        """同步載入模型，優先使用 TFLite"""
        tflite_path = str(Path(self.model_path).with_suffix('.tflite'))
        
        # 1. 嘗試載入 TFLite
        if os.path.exists(tflite_path):
            try:
                # 嘗試導入 TFLite Runtime
                try:
                    import tflite_runtime.interpreter as tflite
                except ImportError:
                    try:
                        import tensorflow.lite.python.interpreter as tflite
                    except ImportError:
                        import tensorflow as tf
                        tflite = tf.lite
                
                self.interpreter = tflite.Interpreter(model_path=tflite_path)
                self.interpreter.allocate_tensors()
                
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                
                # 更新輸入尺寸
                input_shape = self.input_details[0]['shape']
                self.input_size = (input_shape[1], input_shape[2])
                
                logger.info(f"成功載入 TFLite 模型: {tflite_path}")
                return
            except Exception as e:
                logger.warning(f"TFLite 模型載入失敗: {e}，嘗試載入 H5 模型...")

        # 2. 回退到 H5 (Keras)
        try:
            import tensorflow as tf
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"載入 Keras 模型: {self.model_path}")
            else:
                self.model = self._create_default_model(tf)
                logger.info("創建預設 Keras 模型")
        except Exception as e:
            logger.error(f"載入模型完全失敗: {e}")
            self.model = None

    def _initialize_mediapipe(self):
        """初始化 MediaPipe (Moved from inline to method)"""
        # MediaPipe人臉檢測
        try:
            if self.mp_face_detection:
                self.face_detection = self.mp_face_detection.FaceDetection(
                    min_detection_confidence=0.5
                )
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=4,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                return True
        except Exception as e:
            logger.warning(f"MediaPipe 初始化失敗: {e}")
        return False
        
        # 處理參數
        self.confidence_threshold = 0.7
        self.face_detection_confidence = 0.5
        
        # 性能統計
        self.stats = {
            "total_detections": 0,
            "successful_detections": 0,
            "processing_times": [],
            "emotion_counts": {emotion: 0 for emotion in self.emotion_labels}
        }
    
    async def initialize(self) -> bool:
        """
        異步初始化檢測器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("正在初始化情緒檢測器...")
            
            # 1. 載入情緒檢測模型
            if not await self._load_emotion_model():
                return False
            
            # 2. 初始化MediaPipe
            if not self._initialize_mediapipe():
                return False
            
            # 3. 驗證模型
            if not self._validate_model():
                return False
            
            logger.info("情緒檢測器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化情緒檢測器失敗: {e}")
            return False
    
    async def _load_emotion_model(self) -> bool:
        """載入情緒檢測模型(Compat Layer)"""
        # Already handled in __init__
        return self.interpreter is not None or self.model is not None

    # _initialize_mediapipe moved to __init__ but kept logic here for compatibility
    
    def _create_default_model(self, tf_module=None) -> Any:
        """建立預設的CNN模型架構"""
        if tf_module is None:
            import tensorflow as tf
            tf_module = tf
            
        model = tf_module.keras.Sequential([
            tf_module.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
            tf_module.keras.layers.BatchNormalization(),
            tf_module.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf_module.keras.layers.MaxPooling2D(2, 2),
            tf_module.keras.layers.Dropout(0.25),
            
            tf_module.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf_module.keras.layers.BatchNormalization(),
            tf_module.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf_module.keras.layers.MaxPooling2D(2, 2),
            tf_module.keras.layers.Dropout(0.25),
            
            tf_module.keras.layers.Flatten(),
            tf_module.keras.layers.Dense(512, activation='relu'),
            tf_module.keras.layers.BatchNormalization(),
            tf_module.keras.layers.Dropout(0.5),
            tf_module.keras.layers.Dense(7, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        檢測畫面中的人臉
        
        Args:
            frame: 輸入影像 (BGR格式)
            
        Returns:
            人臉邊界框列表 [(x, y, w, h), ...]
        """
        # 優先使用 MediaPipe
        if self.face_detection:
            try:
                # MediaPipe 需要 RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(frame_rgb)
                
                faces = []
                if results.detections:
                    h, w, _ = frame.shape
                    for detection in results.detections:
                        bboxC = detection.location_data.relative_bounding_box
                        x = int(bboxC.xmin * w)
                        y = int(bboxC.ymin * h)
                        width = int(bboxC.width * w)
                        height = int(bboxC.height * h)
                        
                        # 確保邊界在圖片範圍內
                        x = max(0, x)
                        y = max(0, y)
                        width = min(w - x, width)
                        height = min(h - y, height)
                        
                        faces.append((x, y, width, height))
                    return faces
            except Exception as e:
                logger.warning(f"MediaPipe 人臉檢測失敗: {e}，切換回 Haar Cascade")

        # Fallback to Haar Cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        if isinstance(faces, tuple):
            return []
            
        return faces.tolist()
    
    def preprocess_face(self, face_region: np.ndarray) -> np.ndarray:
        """
        預處理人臉區域用於情緒識別
        
        Args:
            face_region: 人臉影像區域
            
        Returns:
            預處理後的影像張量
        """
        # 轉換為灰階
        if len(face_region.shape) == 3:
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_region
            
        # 調整大小為48x48
        face_resized = cv2.resize(face_gray, (48, 48))
        
        # 正規化像素值
        face_normalized = face_resized / 255.0
        
        # 擴展維度以符合模型輸入
        face_tensor = np.expand_dims(face_normalized, axis=-1)
        face_tensor = np.expand_dims(face_tensor, axis=0)
        
        return face_tensor
    
    def predict_emotion(self, face_tensor: np.ndarray) -> Dict[str, float]:
        """
        Input: Tensor
        Output: Emotion dict
        """
        try:
            # A. 使用 TFLite
            if self.interpreter is not None:
                # 簡單檢查形狀是否匹配 (目前模型輸入為 48x48x1)
                # TFLite input details: self.input_details[0]['shape']
                
                # 執行推論
                self.interpreter.set_tensor(self.input_details[0]['index'], face_tensor.astype(np.float32))
                self.interpreter.invoke()
                predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
                
            # B. 使用 Keras (Fallback)
            elif self.model is not None:
                predictions = self.model.predict(face_tensor, verbose=0)
            else:
                return {e: 0.1 for e in self.emotion_labels}

            emotion_probs = predictions[0]
            
            # 建立情緒-置信度字典
            emotion_dict = {
                emotion: float(prob) 
                for emotion, prob in zip(self.emotion_labels, emotion_probs)
            }
            
            return emotion_dict
            
        except Exception as e:
            logger.error(f"情緒預測失敗: {e}")
            # 返回中性情緒作為預設值
            return {emotion: 0.0 for emotion in self.emotion_labels}

    def predict_emotion_from_image(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        直接從人臉影像預測情緒
        
        Args:
            face_image: 人臉區域影像 (BGR)
            
        Returns:
            情緒預測結果字典
        """
        try:
            tensor = self.preprocess_face(face_image)
            return self.predict_emotion(tensor)
        except Exception as e:
            logger.error(f"Image emotion prediction failed: {e}")
            return {e: 0.0 for e in self.emotion_labels}
    
    def _detect_emotion_from_landmarks(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, float]:
        """
        使用 MediaPipe Landmarks 進行簡單的情緒推斷 (Fallback)
        
        Args:
            frame: 原始影像
            bbox: 人臉區域 (x, y, w, h)
            
        Returns:
            情緒預測結果字典
        """
        if not self.face_mesh:
            return {e: 0.1 for e in self.emotion_labels} # 無法檢測，返回低置信度
            
        try:
            # 轉換為 RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)
            
            if not results.multi_face_landmarks:
                return {e: 0.1 for e in self.emotion_labels}
                
            landmarks = results.multi_face_landmarks[0].landmark
            
            # 簡單的幾何特徵提取
            # 嘴巴開合度 (上唇 13, 下唇 14)
            mouth_open = abs(landmarks[13].y - landmarks[14].y)
            
            # 嘴角高度 (左 61, 右 291) vs 嘴中心 (13, 14)
            mouth_corners_y = (landmarks[61].y + landmarks[291].y) / 2
            mouth_center_y = (landmarks[13].y + landmarks[14].y) / 2
            smile_ratio = mouth_corners_y - mouth_center_y # 負值表示嘴角上揚 (因為 y 軸向下)
            
            # 眉毛高度 (左眉 105, 右眉 334)
            eyebrow_h = (landmarks[105].y + landmarks[334].y) / 2
            
            # 簡單規則
            emotions = {e: 0.0 for e in self.emotion_labels}
            
            if smile_ratio < -0.02: # 嘴角明顯上揚
                emotions['happy'] = 0.8 + abs(smile_ratio)
                emotions['neutral'] = 0.2
            elif mouth_open > 0.05: # 嘴巴張開
                emotions['surprise'] = 0.7 + mouth_open
                emotions['neutral'] = 0.2
            elif smile_ratio > 0.01: # 嘴角下垂
                emotions['sad'] = 0.6
                emotions['neutral'] = 0.3
            else:
                emotions['neutral'] = 0.8
                emotions['focused'] = 0.4
                
            # 正規化
            total = sum(emotions.values())
            if total > 0:
                for k in emotions:
                    emotions[k] /= total
                    
            return emotions
            
        except Exception as e:
            logger.warning(f"Landmark emotion detection failed: {e}")
            return {e: 0.1 for e in self.emotion_labels}

    def smooth_emotion(self, current_emotion: Dict[str, float]) -> Dict[str, float]:
        """
        使用歷史記錄平滑情緒預測結果
        
        Args:
            current_emotion: 當前情緒預測
            
        Returns:
            平滑後的情緒預測
        """
        # 加入當前預測到歷史記錄
        self.emotion_history.append(current_emotion)
        
        # 保持歷史記錄大小
        if len(self.emotion_history) > self.history_size:
            self.emotion_history.pop(0)
        
        # 計算平均值
        if len(self.emotion_history) == 1:
            return current_emotion
        
        smoothed_emotion = {}
        for emotion in self.emotion_labels:
            avg_confidence = np.mean([
                hist.get(emotion, 0.0) for hist in self.emotion_history
            ])
            smoothed_emotion[emotion] = float(avg_confidence)
        
        return smoothed_emotion
    
    def start(self):
        """啟動檢測器 (兼容性接口)"""
        pass

    def stop(self):
        """停止檢測器 (兼容性接口)"""
        pass

    def detect_emotions(self, frame: np.ndarray) -> List[Dict]:
        """
        檢測情緒 (兼容性接口)
        
        Args:
            frame: 輸入影像
            
        Returns:
            檢測結果列表 (格式適配 MainPanel)
        """
        results = self.detect_emotion(frame)
        
        # 適配舊版接口格式
        adapted_results = []
        for res in results:
            adapted_res = res.copy()
            adapted_res['emotion'] = res['dominant_emotion']
            
            # 轉換 bbox (x, y, w, h) 為 (x1, y1, x2, y2) 供 PreviewWindow 使用
            x, y, w, h = res['bbox']
            adapted_res['face_location'] = (x, y, x + w, y + h)
            
            adapted_results.append(adapted_res)
            
        return adapted_results

    def detect_emotion(self, frame: np.ndarray, smooth: bool = True) -> List[Dict]:
        """
        檢測畫面中所有人臉的情緒
        
        Args:
            frame: 輸入影像 (BGR格式)
            smooth: 是否使用平滑處理
            
        Returns:
            檢測結果列表，每個元素包含：
            {
                'bbox': (x, y, w, h),
                'emotions': {emotion: confidence, ...},
                'dominant_emotion': 'emotion_name',
                'confidence': float
            }
        """
        results = []
        
        # 檢測人臉
        faces = self.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            # 判斷是否使用 DNN 模型 (如果模型存在且已載入)
            use_dnn = self.model is not None and os.path.exists(self.model_path)
            
            if use_dnn:
                # 擷取人臉區域
                face_region = frame[y:y+h, x:x+w]
                # 預處理
                face_tensor = self.preprocess_face(face_region)
                # 情緒預測
                emotions = self.predict_emotion(face_tensor)
            else:
                # 使用 Landmark Fallback
                emotions = self._detect_emotion_from_landmarks(frame, (x, y, w, h))
            
            # 平滑處理
            if smooth:
                emotions = self.smooth_emotion(emotions)
            
            # 找出主要情緒
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion]
            
            result = {
                'bbox': (x, y, w, h),
                'emotions': emotions,
                'dominant_emotion': dominant_emotion,
                'confidence': confidence
            }
            
            results.append(result)
        
        return results
    
    def draw_emotion_info(self, frame: np.ndarray, results: List[Dict]) -> np.ndarray:
        """
        在影像上繪製情緒檢測結果
        
        Args:
            frame: 原始影像
            results: 檢測結果列表
            
        Returns:
            標註後的影像
        """
        annotated_frame = frame.copy()
        
        for result in results:
            x, y, w, h = result['bbox']
            emotion = result['dominant_emotion']
            confidence = result['confidence']
            
            # 繪製人臉邊界框
            color = (0, 255, 0) if confidence > 0.6 else (0, 255, 255)
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
            
            # 繪製情緒標籤
            label = f"{emotion}: {confidence:.2f}"
            cv2.putText(
                annotated_frame, 
                label, 
                (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                color, 
                2
            )
        
        return annotated_frame


class EffectController:
    """
    基於情緒的特效控制器
    根據檢測到的情緒調整視覺特效參數
    """
    
    def __init__(self):
        """初始化特效控制器"""
        # 情緒到特效的映射
        self.emotion_effects = {
            'Happy': {
                'particles': 'sparkles',
                'color_shift': (1.2, 1.1, 0.9),  # 暖色調
                'brightness': 1.15,
                'saturation': 1.2
            },
            'Sad': {
                'particles': 'rain',
                'color_shift': (0.8, 0.9, 1.2),  # 冷色調  
                'brightness': 0.85,
                'saturation': 0.7
            },
            'Angry': {
                'particles': 'fire',
                'color_shift': (1.3, 0.8, 0.7),  # 紅色調
                'brightness': 1.1,
                'saturation': 1.4
            },
            'Surprise': {
                'particles': 'stars',
                'color_shift': (1.1, 1.1, 1.3),  # 亮色調
                'brightness': 1.3,
                'saturation': 1.1
            },
            'Neutral': {
                'particles': None,
                'color_shift': (1.0, 1.0, 1.0),  # 原色
                'brightness': 1.0,
                'saturation': 1.0
            }
        }
    
    def get_effect_params(self, emotion_results: List[Dict]) -> Dict:
        """
        根據情緒檢測結果生成特效參數
        
        Args:
            emotion_results: 情緒檢測結果
            
        Returns:
            特效參數字典
        """
        if not emotion_results:
            return self.emotion_effects['Neutral']
        
        # 使用置信度最高的情緒
        best_result = max(emotion_results, key=lambda x: x['confidence'])
        dominant_emotion = best_result['dominant_emotion']
        
        # 獲取對應的特效參數
        effect_params = self.emotion_effects.get(
            dominant_emotion, 
            self.emotion_effects['Neutral']
        ).copy()
        
        # 根據置信度調整強度
        confidence = best_result['confidence']
        effect_params['intensity'] = confidence
        
        return effect_params


# 使用範例
if __name__ == "__main__":
    # 初始化檢測器
    detector = EmotionDetector()
    effect_controller = EffectController()
    
    # 開啟攝影機
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 檢測情緒
        results = detector.detect_emotion(frame)
        
        # 繪製檢測結果
        annotated_frame = detector.draw_emotion_info(frame, results)
        
        # 獲取特效參數
        effect_params = effect_controller.get_effect_params(results)
        
        # 顯示結果
        cv2.imshow('LivePilotAI - Emotion Detection', annotated_frame)
        
        # 印出特效參數 (實際應用中會傳送給OBS)
        if results:
            print(f"檢測到情緒: {results[0]['dominant_emotion']} "
                  f"({results[0]['confidence']:.2f})")
            print(f"特效參數: {effect_params}")
        
        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
