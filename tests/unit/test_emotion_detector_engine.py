"""
EmotionDetectorEngine 測試模組
測試情感檢測引擎的核心功能
"""

import pytest
import numpy as np
import cv2
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

from src.ai_engine.emotion_detector_engine import (
    EmotionDetectorEngine,
    EmotionResult,
    create_emotion_detector_engine,
    draw_emotion_results
)
from src.ai_engine.base_engine import EngineState, ProcessingResult


class TestEmotionDetectorEngine:
    """EmotionDetectorEngine 測試類別"""
    
    @pytest.fixture
    def engine_config(self):
        """測試用引擎配置"""
        return {
            "model_path": "test_model.h5",
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
                "history_size": 3,
                "threshold": 0.6
            },
            "performance": {
                "max_faces": 3,
                "target_fps": 30
            }
        }
    
    @pytest.fixture
    def sample_frame(self):
        """生成測試用影像"""
        # 創建一個 480x640 的彩色影像
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        return frame
    
    @pytest.fixture
    def mock_model(self):
        """模擬 TensorFlow 模型"""
        mock = Mock()
        # 模擬預測結果 - 7個情感的機率分布
        mock.predict.return_value = np.array([[0.1, 0.1, 0.1, 0.6, 0.05, 0.1, 0.05]])
        return mock
    
    def test_engine_initialization(self, engine_config):
        """測試引擎初始化"""
        engine = EmotionDetectorEngine("test_emotion", engine_config)
        
        assert engine.engine_id == "test_emotion"
        assert engine.state == EngineState.IDLE
        assert engine.config == engine_config
        assert engine.model is None
        assert engine.face_cascade is None
        
    def test_factory_function(self, engine_config):
        """測試工廠函數"""
        engine = create_emotion_detector_engine(engine_config)
        
        assert isinstance(engine, EmotionDetectorEngine)
        assert engine.config == engine_config
    
    def test_default_config(self):
        """測試預設配置"""
        engine = EmotionDetectorEngine()
        
        assert "emotion_labels" in engine.config
        assert len(engine.config["emotion_labels"]) == 7
        assert "Happy" in engine.config["emotion_labels"]
        assert "input_size" in engine.config
        
    @patch('tensorflow.keras.models.load_model')
    @patch('cv2.CascadeClassifier')
    async def test_successful_initialization(self, mock_cascade, mock_load_model, 
                                           engine_config, mock_model):
        """測試成功的引擎初始化"""
        # 設置 mocks
        mock_load_model.return_value = mock_model
        mock_cascade_instance = Mock()
        mock_cascade_instance.empty.return_value = False
        mock_cascade.return_value = mock_cascade_instance
        
        engine = EmotionDetectorEngine("test", engine_config)
        
        # 測試初始化
        result = await engine.initialize()
        
        assert result is True
        assert engine.state == EngineState.IDLE
        assert engine.model is not None
        assert engine.face_cascade is not None
        
    @patch('tensorflow.keras.models.load_model')
    async def test_model_loading_failure(self, mock_load_model, engine_config):
        """測試模型載入失敗的情況"""
        # 模擬檔案不存在
        mock_load_model.side_effect = FileNotFoundError("Model file not found")
        
        engine = EmotionDetectorEngine("test", engine_config)
        
        # 初始化應該成功，因為會建立預設模型
        result = await engine.initialize()
        
        assert result is True
        assert engine.model is not None  # 預設模型
        
    def test_create_default_model(self, engine_config):
        """測試預設模型建立"""
        engine = EmotionDetectorEngine("test", engine_config)
        model = engine._create_default_model()
        
        assert model is not None
        assert len(model.layers) > 0
        
        # 檢查輸入形狀
        expected_shape = (*engine_config["input_size"], 1)
        assert model.input_shape[1:] == expected_shape
        
    @patch('cv2.CascadeClassifier')
    def test_face_detection(self, mock_cascade, engine_config, sample_frame):
        """測試人臉檢測功能"""
        # 設置模擬的人臉檢測結果
        mock_cascade_instance = Mock()
        mock_cascade_instance.detectMultiScale.return_value = np.array([
            [100, 100, 80, 80],  # 第一個人臉
            [300, 200, 90, 90]   # 第二個人臉
        ])
        mock_cascade.return_value = mock_cascade_instance
        
        engine = EmotionDetectorEngine("test", engine_config)
        engine.face_cascade = mock_cascade_instance
        
        # 執行人臉檢測
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        faces = loop.run_until_complete(engine._detect_faces(sample_frame))
        
        assert len(faces) == 2
        assert faces[0] == [100, 100, 80, 80]
        assert faces[1] == [300, 200, 90, 90]
        
    def test_preprocess_face(self, engine_config):
        """測試人臉預處理功能"""
        engine = EmotionDetectorEngine("test", engine_config)
        
        # 創建測試人臉區域
        face_region = np.random.randint(0, 255, (80, 80, 3), dtype=np.uint8)
        
        # 預處理
        processed = engine._preprocess_face(face_region)
        
        # 檢查結果形狀和值範圍
        expected_shape = (1, 48, 48, 1)  # (batch, height, width, channels)
        assert processed.shape == expected_shape
        assert processed.min() >= 0.0
        assert processed.max() <= 1.0
        
    async def test_emotion_prediction(self, engine_config, mock_model):
        """測試情感預測功能"""
        engine = EmotionDetectorEngine("test", engine_config)
        engine.model = mock_model
        
        # 創建測試輸入
        face_tensor = np.random.random((1, 48, 48, 1))
        
        # 執行預測
        emotions = await engine._predict_emotion(face_tensor)
        
        # 檢查結果
        assert isinstance(emotions, dict)
        assert len(emotions) == 7
        assert "Happy" in emotions
        assert all(0 <= prob <= 1 for prob in emotions.values())
        
        # 檢查機率總和接近1
        total_prob = sum(emotions.values())
        assert abs(total_prob - 1.0) < 0.01
        
    def test_emotion_smoothing(self, engine_config):
        """測試情感平滑處理"""
        engine = EmotionDetectorEngine("test", engine_config)
        
        # 模擬連續的情感預測
        emotions1 = {"Happy": 0.8, "Sad": 0.2, "Neutral": 0.0}
        emotions2 = {"Happy": 0.6, "Sad": 0.3, "Neutral": 0.1}
        emotions3 = {"Happy": 0.7, "Sad": 0.2, "Neutral": 0.1}
        
        # 第一次預測（無平滑）
        result1 = engine._smooth_emotions(emotions1, 0)
        assert result1 == emotions1
        
        # 第二次預測（開始平滑）
        result2 = engine._smooth_emotions(emotions2, 0)
        
        # 第三次預測
        result3 = engine._smooth_emotions(emotions3, 0)
        
        # 檢查平滑效果
        assert "Happy" in result3
        assert result3["Happy"] != emotions3["Happy"]  # 應該被平滑
        
    @patch('cv2.CascadeClassifier')
    async def test_full_processing(self, mock_cascade, engine_config, 
                                 sample_frame, mock_model):
        """測試完整的處理流程"""
        # 設置 mocks
        mock_cascade_instance = Mock()
        mock_cascade_instance.empty.return_value = False
        mock_cascade_instance.detectMultiScale.return_value = np.array([
            [100, 100, 80, 80]
        ])
        mock_cascade.return_value = mock_cascade_instance
        
        engine = EmotionDetectorEngine("test", engine_config)
        engine.model = mock_model
        engine.face_cascade = mock_cascade_instance
        
        # 執行處理
        result = await engine.process(sample_frame)
        
        # 檢查結果
        assert isinstance(result, ProcessingResult)
        assert result.success is True
        assert "emotions" in result.data
        assert "frame_info" in result.data
        assert "performance" in result.data
        
        emotions = result.data["emotions"]
        assert len(emotions) == 1  # 一個人臉
        assert "bbox" in emotions[0]
        assert "dominant_emotion" in emotions[0]
        assert "confidence" in emotions[0]
        
    async def test_processing_invalid_input(self, engine_config):
        """測試無效輸入的處理"""
        engine = EmotionDetectorEngine("test", engine_config)
        
        # 測試非numpy array輸入
        result = await engine.process("invalid_input")
        
        assert isinstance(result, ProcessingResult)
        assert result.success is False
        assert result.error_message is not None
        assert "輸入數據必須是numpy array" in result.error_message
        
    async def test_cleanup(self, engine_config, mock_model):
        """測試資源清理"""
        engine = EmotionDetectorEngine("test", engine_config)
        engine.model = mock_model
        
        # 添加一些歷史記錄
        engine.emotion_history.append([{"Happy": 0.8}])
        engine.processing_times.append(0.1)
        
        # 執行清理
        result = await engine.cleanup()
        
        assert result is True
        assert engine.state == EngineState.STOPPED
        assert engine.model is None
        assert len(engine.emotion_history) == 0
        assert len(engine.processing_times) == 0
        
    def test_get_engine_status(self, engine_config):
        """測試引擎狀態獲取"""
        engine = EmotionDetectorEngine("test", engine_config)
        engine.processing_times = [0.1, 0.2, 0.15]
        
        status = engine.get_engine_status()
        
        assert "engine_id" in status
        assert "state" in status
        assert "performance" in status
        assert status["engine_id"] == "test"
        assert status["performance"]["total_processed"] == 3


class TestEmotionResult:
    """EmotionResult 資料類別測試"""
    
    def test_emotion_result_creation(self):
        """測試 EmotionResult 建立"""
        emotions = {"Happy": 0.8, "Sad": 0.2}
        result = EmotionResult(
            bbox=(100, 100, 80, 80),
            emotions=emotions,
            dominant_emotion="Happy",
            confidence=0.8,
            face_id=0
        )
        
        assert result.bbox == (100, 100, 80, 80)
        assert result.emotions == emotions
        assert result.dominant_emotion == "Happy"
        assert result.confidence == 0.8
        assert result.face_id == 0


class TestDrawEmotionResults:
    """測試繪製功能"""
    
    def test_draw_emotion_results(self):
        """測試情感結果繪製"""
        # 創建測試影像
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 創建測試結果
        emotion_results = [
            {
                "bbox": (100, 100, 80, 80),
                "dominant_emotion": "Happy",
                "confidence": 0.85
            },
            {
                "bbox": (300, 200, 90, 90),
                "dominant_emotion": "Sad",
                "confidence": 0.65
            }
        ]
        
        # 繪製結果
        annotated_frame = draw_emotion_results(frame, emotion_results)
        
        # 檢查返回的影像
        assert annotated_frame.shape == frame.shape
        assert not np.array_equal(annotated_frame, frame)  # 應該有變化
        
    def test_draw_empty_results(self):
        """測試空結果的繪製"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 空結果列表
        annotated_frame = draw_emotion_results(frame, [])
        
        # 應該返回原始影像
        assert np.array_equal(annotated_frame, frame)


@pytest.mark.integration
class TestEmotionDetectorIntegration:
    """整合測試"""
    
    @patch('tensorflow.keras.models.load_model')
    @patch('cv2.CascadeClassifier')
    async def test_end_to_end_workflow(self, mock_cascade, mock_load_model):
        """測試端到端工作流程"""
        # 設置 mocks
        mock_model = Mock()
        mock_model.predict.return_value = np.array([[0.1, 0.1, 0.1, 0.6, 0.05, 0.1, 0.05]])
        mock_load_model.return_value = mock_model
        
        mock_cascade_instance = Mock()
        mock_cascade_instance.empty.return_value = False
        mock_cascade_instance.detectMultiScale.return_value = np.array([
            [100, 100, 80, 80]
        ])
        mock_cascade.return_value = mock_cascade_instance
        
        # 創建引擎
        engine = create_emotion_detector_engine()
        
        # 初始化
        init_result = await engine.initialize()
        assert init_result is True
        
        # 創建測試影像
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 處理影像
        result = await engine.process(test_frame)
        assert result.success is True
        
        # 獲取狀態
        status = engine.get_engine_status()
        assert status["state"] == EngineState.IDLE.value
        
        # 清理
        cleanup_result = await engine.cleanup()
        assert cleanup_result is True


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v"])
