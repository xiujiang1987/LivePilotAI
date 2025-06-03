# filepath: d:\AI_Park\Workspace\dev_projects\ai\LivePilotAI\src\ai_engine\emotion_detector_engine_fixed.py
"""
LivePilotAI - 情感檢測引擎 (修復版)
基於 AIEngineBase 架構的即時情感檢測實作，包含啟動時依賴檢查
"""

import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import asyncio
import time
from dataclasses import dataclass

# 設置基本日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyCheckError(Exception):
    """依賴檢查失敗異常"""
    pass


class DependencyManager:
    """依賴管理器 - 負責檢查和安裝必要的依賴包"""
    
    REQUIRED_PACKAGES = {
        'cv2': 'opencv-python',
        'numpy': 'numpy', 
        'tensorflow': 'tensorflow',
        'PIL': 'Pillow'
    }
    
    @staticmethod
    def check_dependencies() -> Tuple[List[str], List[str]]:
        """
        檢查所有必要的依賴項
        
        Returns:
            Tuple[List[str], List[str]]: (已安裝的包, 缺失的包)
        """
        installed = []
        missing = []
        
        for import_name, package_name in DependencyManager.REQUIRED_PACKAGES.items():
            try:
                importlib.import_module(import_name)
                installed.append(package_name)
                logger.info(f"✓ {package_name} 已安裝")
            except ImportError:
                missing.append(package_name)
                logger.warning(f"✗ {package_name} 缺失")
        
        return installed, missing
    
    @staticmethod
    def install_package(package_name: str) -> bool:
        """
        安裝指定的包
        
        Args:
            package_name: 要安裝的包名
            
        Returns:
            bool: 安裝是否成功
        """
        try:
            logger.info(f"正在安裝 {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✓ {package_name} 安裝成功")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ {package_name} 安裝失敗: {e}")
            logger.error(f"錯誤輸出: {e.stderr}")
            return False
    
    @staticmethod
    def install_missing_dependencies(missing_packages: List[str]) -> bool:
        """
        批量安裝缺失的依賴
        
        Args:
            missing_packages: 缺失的包列表
            
        Returns:
            bool: 所有包是否都安裝成功
        """
        success_count = 0
        for package in missing_packages:
            if DependencyManager.install_package(package):
                success_count += 1
        
        return success_count == len(missing_packages)
    
    @staticmethod
    def verify_installation() -> bool:
        """
        驗證所有依賴是否正確安裝
        
        Returns:
            bool: 所有依賴是否可用
        """
        installed, missing = DependencyManager.check_dependencies()
        
        if missing:
            logger.error(f"仍有缺失的依賴: {', '.join(missing)}")
            return False
        
        logger.info("所有依賴檢查通過！")
        return True


def startup_dependency_check(auto_install: bool = True) -> bool:
    """
    啟動時執行依賴檢查
    
    Args:
        auto_install: 是否自動安裝缺失的依賴
        
    Returns:
        bool: 依賴檢查是否通過
    """
    logger.info("開始啟動依賴檢查...")
    
    # 檢查依賴
    installed, missing = DependencyManager.check_dependencies()
    
    if not missing:
        logger.info("所有依賴已安裝，檢查通過！")
        return True
    
    if not auto_install:
        logger.error(f"缺失依賴: {', '.join(missing)}")
        raise DependencyCheckError(f"缺失必要依賴: {', '.join(missing)}")
    
    # 自動安裝缺失的依賴
    logger.info(f"發現缺失依賴: {', '.join(missing)}")
    logger.info("正在自動安裝...")
    
    if DependencyManager.install_missing_dependencies(missing):
        logger.info("依賴安裝完成，正在驗證...")
        if DependencyManager.verify_installation():
            logger.info("依賴檢查完全通過！")
            return True
        else:
            raise DependencyCheckError("依賴安裝後驗證失敗")
    else:
        raise DependencyCheckError("依賴自動安裝失敗")


# 執行啟動依賴檢查
try:
    startup_dependency_check(auto_install=True)
    logger.info("依賴檢查通過，開始載入模組...")
except DependencyCheckError as e:
    logger.error(f"依賴檢查錯誤: {e}")
    logger.info("請執行以下命令手動安裝依賴:")
    logger.info("pip install opencv-python numpy tensorflow Pillow")
    sys.exit(1)

# 依賴檢查通過後，才導入相關模組
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

# 處理 TensorFlow/Keras 版本兼容性
try:
    from tensorflow import keras
except ImportError:
    import tensorflow.keras as keras

# 導入基礎引擎類別
try:
    from .base_engine import AIEngineBase, ProcessingResult, EngineState
    logger.info("成功導入基礎引擎類別")
except ImportError as e:
    logger.warning(f"無法導入基礎引擎，使用本地定義: {e}")
    # 創建本地基礎類別定義
    from enum import Enum
    from abc import ABC, abstractmethod
    
    class EngineState(Enum):
        IDLE = "idle"
        INITIALIZING = "initializing"
        PROCESSING = "processing"
        ERROR = "error"
        STOPPED = "stopped"
    
    @dataclass
    class ProcessingResult:
        success: bool
        data: Any
        timestamp: float
        processing_time: float
        error_message: Optional[str] = None
    
    class AIEngineBase:
        def __init__(self, engine_id: str, config: Dict[str, Any]):
            self.engine_id = engine_id
            self.config = config
            self.state = EngineState.IDLE
            self.logger = logging.getLogger(f"{__name__}.{engine_id}")
            self._last_result: Optional[ProcessingResult] = None
        
        async def initialize(self) -> bool:
            """初始化引擎，載入模型和資源"""
            return True
        
        async def process(self, input_data: Any) -> ProcessingResult:
            """處理輸入數據"""
            return ProcessingResult(True, {}, time.time(), 0.0)
        
        async def cleanup(self) -> bool:
            """清理資源"""
            return True


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
    情感檢測引擎 (修復版)
    
    支援7種情感分類：
    - Happy (快樂)
    - Sad (悲傷) 
    - Angry (憤怒)
    - Surprise (驚訝)
    - Fear (恐懼)
    - Disgust (厭惡)
    - Neutral (中性)
    
    特色功能:
    - 啟動時自動依賴檢查
    - 自動依賴安裝
    - 即時人臉檢測
    - 批量情感分析
    - 情感歷史追蹤
    - 系統狀態監控
    """
    
    def __init__(self, engine_id: str = "emotion_detector", config: Optional[Dict[str, Any]] = None):
        # 使用預設配置
        default_config = {
            "model_path": None,
            "cascade_file": "haarcascade_frontalface_default.xml",
            "input_shape": (48, 48, 1),
            "num_classes": 7,
            "batch_size": 32,
            "confidence_threshold": 0.5,
            "history_length": 10
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(engine_id, default_config)
        
        # 情感類別對應
        self.emotion_labels = [
            "Angry", "Disgust", "Fear", "Happy", 
            "Sad", "Surprise", "Neutral"
        ]
        
        # 初始化模型和檢測器
        self.model: Optional[keras.Model] = None
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        
        # 情感歷史記錄
        self.emotion_history: List[Dict[str, float]] = []
        
        self.logger.info("情感檢測引擎初始化完成")
    
    async def initialize(self) -> bool:
        """
        初始化引擎，載入模型和人臉檢測器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.state = EngineState.INITIALIZING
            self.logger.info("開始初始化情感檢測引擎...")
            
            # 執行運行時依賴驗證
            if not DependencyManager.verify_installation():
                self.logger.error("運行時依賴驗證失敗")
                self.state = EngineState.ERROR
                return False
            
            # 載入情感檢測模型
            model_path = self.config.get("model_path")
            if model_path and isinstance(model_path, str):
                try:
                    self.model = keras.models.load_model(model_path)
                    self.logger.info(f"成功載入情感檢測模型: {model_path}")
                except Exception as e:
                    self.logger.warning(f"無法載入模型 {model_path}: {e}")
                    self.logger.info("使用預設模型架構")
                    self.model = self._create_default_model()
            else:
                self.logger.info("使用預設模型架構")
                self.model = self._create_default_model()
            
            # 載入人臉檢測器
            cascade_file = self.config.get("cascade_file", "haarcascade_frontalface_default.xml")
            try:
                # 嘗試使用 OpenCV 預設路徑
                cascade_path = cv2.data.haarcascades + cascade_file
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                
                if self.face_cascade.empty():
                    raise Exception("無法載入級聯檔案")
                    
                self.logger.info(f"成功載入人臉檢測器: {cascade_file}")
            except Exception as e:
                self.logger.error(f"無法載入人臉檢測器: {e}")
                self.state = EngineState.ERROR
                return False
            
            self.state = EngineState.IDLE
            self.logger.info("情感檢測引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            self.state = EngineState.ERROR
            return False
    
    def _create_default_model(self) -> keras.Model:
        """建立預設的CNN模型架構"""
        input_shape = self.config.get("input_shape", (48, 48, 1))
        num_classes = self.config.get("num_classes", 7)
        
        model = keras.Sequential([
            # 第一層卷積塊
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            keras.layers.BatchNormalization(),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D(2, 2),
            keras.layers.Dropout(0.25),
            
            # 第二層卷積塊
            keras.layers.Conv2D(128, (3, 3), activation='relu'),
            keras.layers.BatchNormalization(),
            keras.layers.Conv2D(128, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D(2, 2),
            keras.layers.Dropout(0.25),
            
            # 全連接層
            keras.layers.Flatten(),
            keras.layers.Dense(512, activation='relu'),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        檢測圖像中的人臉
        
        Args:
            image: 輸入圖像 (numpy array)
            
        Returns:
            List[Tuple[int, int, int, int]]: 人臉邊界框列表 [(x, y, w, h), ...]
        """
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 轉換為 tuple 列表格式
        return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
    
    def predict_emotion(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        預測單個人臉的情感
        
        Args:
            face_image: 人臉圖像 (numpy array)
            
        Returns:
            Dict[str, float]: 各情感的置信度
        """
        if self.model is None:
            return {label: 0.0 for label in self.emotion_labels}
        
        try:
            # 預處理圖像
            input_shape = self.config.get("input_shape", (48, 48, 1))
            processed_image = cv2.resize(face_image, input_shape[:2])
            
            if len(input_shape) == 3 and input_shape[2] == 1:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
                processed_image = processed_image.reshape(input_shape)
            
            processed_image = processed_image.astype('float32') / 255.0
            processed_image = np.expand_dims(processed_image, axis=0)
            
            # 預測
            predictions = self.model.predict(processed_image, verbose=0)
            
            # 建立情感字典
            emotions = {}
            for i, label in enumerate(self.emotion_labels):
                emotions[label] = float(predictions[0][i])
            
            return emotions
            
        except Exception as e:
            self.logger.error(f"情感預測失敗: {e}")
            return {label: 0.0 for label in self.emotion_labels}
    
    async def process(self, input_data: Any) -> ProcessingResult:
        """
        處理輸入數據並檢測情感
        
        Args:
            input_data: 輸入圖像 (numpy array 或 PIL Image)
            
        Returns:
            ProcessingResult: 處理結果
        """
        start_time = time.time()
        self.state = EngineState.PROCESSING
        
        try:
            # 輸入驗證和轉換
            if isinstance(input_data, Image.Image):
                image = np.array(input_data)
            elif isinstance(input_data, np.ndarray):
                image = input_data
            else:
                raise ValueError(f"不支援的輸入類型: {type(input_data)}")
            
            # 檢測人臉
            faces = self.detect_faces(image)
            
            if not faces:
                # 無人臉檢測到
                result_data = {
                    "faces_detected": 0,
                    "emotions": [],
                    "system_status": {
                        "engine_state": self.state.value,
                        "model_loaded": self.model is not None,
                        "face_detector_loaded": self.face_cascade is not None,
                        "dependencies_ok": DependencyManager.verify_installation()
                    }
                }
                
                processing_time = time.time() - start_time
                result = ProcessingResult(
                    success=True,
                    data=result_data,
                    timestamp=time.time(),
                    processing_time=processing_time
                )
                
                self.state = EngineState.IDLE
                self._last_result = result
                return result
            
            # 分析每個檢測到的人臉
            emotion_results = []
            for i, (x, y, w, h) in enumerate(faces):
                # 提取人臉區域
                face_roi = image[y:y+h, x:x+w]
                
                # 預測情感
                emotions = self.predict_emotion(face_roi)
                
                # 找出主要情感
                if emotions:
                    dominant_emotion = max(emotions.keys(), key=lambda k: emotions[k])
                    confidence = emotions[dominant_emotion]
                else:
                    dominant_emotion = "Neutral"
                    confidence = 0.0
                
                # 建立結果
                emotion_result = EmotionResult(
                    bbox=(x, y, w, h),
                    emotions=emotions,
                    dominant_emotion=dominant_emotion,
                    confidence=confidence,
                    face_id=i
                )
                emotion_results.append(emotion_result)
                
                # 更新情感歷史
                self._update_emotion_history(emotions)
            
            # 構建完整結果
            result_data = {
                "faces_detected": len(faces),
                "emotions": [
                    {
                        "face_id": result.face_id,
                        "bbox": result.bbox,
                        "emotions": result.emotions,
                        "dominant_emotion": result.dominant_emotion,
                        "confidence": result.confidence
                    }
                    for result in emotion_results
                ],
                "system_status": {
                    "engine_state": self.state.value,
                    "model_loaded": self.model is not None,
                    "face_detector_loaded": self.face_cascade is not None,
                    "dependencies_ok": DependencyManager.verify_installation(),
                    "emotion_history_length": len(self.emotion_history)
                }
            }
            
            processing_time = time.time() - start_time
            result = ProcessingResult(
                success=True,
                data=result_data,
                timestamp=time.time(),
                processing_time=processing_time
            )
            
            self.state = EngineState.IDLE
            self._last_result = result
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"處理失敗: {str(e)}"
            self.logger.error(error_message)
            
            result = ProcessingResult(
                success=False,
                data={},
                timestamp=time.time(),
                processing_time=processing_time,
                error_message=error_message
            )
            
            self.state = EngineState.ERROR
            self._last_result = result
            return result
    
    def _update_emotion_history(self, emotions: Dict[str, float]):
        """更新情感歷史記錄"""
        self.emotion_history.append(emotions.copy())
        
        # 保持歷史長度限制
        max_history = self.config.get("history_length", 10)
        if len(self.emotion_history) > max_history:
            self.emotion_history.pop(0)
    
    def get_emotion_statistics(self) -> Dict[str, Any]:
        """獲取情感統計資訊"""
        if not self.emotion_history:
            return {}
        
        # 計算平均情感分佈
        avg_emotions = {}
        for label in self.emotion_labels:
            avg_emotions[label] = np.mean([
                emotions.get(label, 0.0) for emotions in self.emotion_history
            ])
        
        # 找出最常見的主要情感
        dominant_emotions = [
            max(emotions.keys(), key=lambda k: emotions[k])
            for emotions in self.emotion_history
        ]
        
        from collections import Counter
        emotion_counts = Counter(dominant_emotions)
        most_common = emotion_counts.most_common(1)[0] if emotion_counts else ("Neutral", 0)
        
        return {
            "average_emotions": avg_emotions,
            "most_common_emotion": most_common[0],
            "emotion_frequency": dict(emotion_counts),
            "history_length": len(self.emotion_history)
        }
    
    async def cleanup(self) -> bool:
        """清理資源"""
        try:
            self.model = None
            self.face_cascade = None
            self.emotion_history.clear()
            self.state = EngineState.STOPPED
            self.logger.info("情感檢測引擎清理完成")
            return True
        except Exception as e:
            self.logger.error(f"清理失敗: {e}")
            return False


# 測試和使用範例
if __name__ == "__main__":
    async def test_emotion_engine():
        """測試情感檢測引擎"""
        logger.info("開始測試情感檢測引擎...")
        
        # 創建引擎實例
        engine = EmotionDetectorEngine()
        
        # 初始化
        if await engine.initialize():
            logger.info("引擎初始化成功!")
            
            # 創建測試圖像（隨機圖像）
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # 處理圖像
            result = await engine.process(test_image)
            
            if result.success:
                logger.info("處理成功!")
                logger.info(f"檢測到 {result.data['faces_detected']} 個人臉")
                logger.info(f"處理時間: {result.processing_time:.3f}秒")
                
                # 顯示系統狀態
                status = result.data['system_status']
                logger.info(f"系統狀態: {status}")
            else:
                logger.error(f"處理失敗: {result.error_message}")
            
            # 清理
            await engine.cleanup()
        else:
            logger.error("引擎初始化失敗!")
    
    # 運行測試
    asyncio.run(test_emotion_engine())
