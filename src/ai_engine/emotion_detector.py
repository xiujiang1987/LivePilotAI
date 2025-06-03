"""
LivePilotAI - 情緒識別核心引擎
即時人臉情緒分析模組
"""

import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Optional
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    即時情緒識別類別
    
    支援7種情緒分類：
    - 快樂 (Happy)
    - 悲傷 (Sad) 
    - 憤怒 (Angry)
    - 驚訝 (Surprise)
    - 恐懼 (Fear)
    - 厭惡 (Disgust)
    - 中性 (Neutral)
    """
    
    def __init__(self, model_path: str = "models/emotion_detection.h5"):
        """
        初始化情緒檢測器
        
        Args:
            model_path: 預訓練模型路徑
        """
        self.emotion_labels = [
            'Angry', 'Disgust', 'Fear', 'Happy', 
            'Sad', 'Surprise', 'Neutral'
        ]
        
        # 載入預訓練模型
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"成功載入情緒識別模型: {model_path}")
        except Exception as e:
            logger.warning(f"無法載入模型，使用預設模型: {e}")
            self.model = self._create_default_model()
        
        # 初始化人臉檢測器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # 情緒歷史記錄 (用於平滑處理)
        self.emotion_history = []
        self.history_size = 5
        
    def _create_default_model(self) -> tf.keras.Model:
        """建立預設的CNN模型架構"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(7, activation='softmax')
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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
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
        預測人臉情緒
        
        Args:
            face_tensor: 預處理後的人臉張量
            
        Returns:
            情緒預測結果字典 {emotion: confidence, ...}
        """
        try:
            predictions = self.model.predict(face_tensor, verbose=0)
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
    
    def predict_emotion_from_image(self, face_image: np.ndarray):
        """
        從人臉圖像直接預測情緒
        
        Args:
            face_image: 人臉區域圖像 (BGR格式)
            
        Returns:
            包含主要情緒、置信度和所有情緒分佈的字典
        """
        try:
            # 預處理人臉圖像
            face_tensor = self.preprocess_face(face_image)
            
            # 預測情緒
            emotion_probs = self.predict_emotion(face_tensor)
            
            # 找出主要情緒
            dominant_emotion = ""
            max_confidence = 0.0
            for emotion, confidence in emotion_probs.items():
                if confidence > max_confidence:
                    max_confidence = confidence
                    dominant_emotion = emotion
            
            # 返回完整結果
            return {
                'dominant_emotion': dominant_emotion,
                'confidence': max_confidence,
                'emotions': emotion_probs
            }
            
        except Exception as e:
            logger.error(f"情緒預測失敗: {e}")
            return {
                'dominant_emotion': 'Neutral',
                'confidence': 0.0,
                'emotions': {emotion: 0.0 for emotion in self.emotion_labels}
            }

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
                hist[emotion] for hist in self.emotion_history
            ])
            smoothed_emotion[emotion] = float(avg_confidence)
        
        return smoothed_emotion
    
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
            # 擷取人臉區域
            face_region = frame[y:y+h, x:x+w]
            
            # 預處理
            face_tensor = self.preprocess_face(face_region)
            
            # 情緒預測
            emotions = self.predict_emotion(face_tensor)
            
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
