"""
LivePilotAI - 測試配置文件
pytest 配置和共用測試工具
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any
import logging

# 測試期間禁用日誌輸出
logging.disable(logging.CRITICAL)


@pytest.fixture(scope="session")
def event_loop():
    """為所有異步測試提供事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """創建臨時目錄用於測試"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_config_data():
    """範例配置數據"""
    return {
        "environment": "testing",
        "debug": True,
        "secret_key": "test-secret-key",
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        },
        "ai_models": {
            "emotion_model_path": "models/test_emotion.h5",
            "confidence_threshold": 0.8
        },
        "obs": {
            "websocket_host": "localhost",
            "websocket_port": 4455,
            "auto_connect": False
        },
        "api": {
            "host": "127.0.0.1",
            "port": 8001,
            "debug": True
        },
        "logging": {
            "level": "DEBUG",
            "console_output": False
        }
    }


@pytest.fixture
def mock_ai_input_data():
    """模擬AI輸入數據"""
    import numpy as np
    return {
        "image": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        "timestamp": 1234567890.0,
        "frame_id": 1
    }


class MockAIEngine:
    """模擬AI引擎用於測試"""
    
    def __init__(self, engine_id: str, success: bool = True):
        self.engine_id = engine_id
        self.success = success
        self.state = "idle"
        self.config = {"test": True}
        
    async def initialize(self) -> bool:
        self.state = "running"
        return self.success
        
    async def process(self, input_data):
        from src.ai_engine.base_engine import ProcessingResult
        import time
        
        if self.success:
            return ProcessingResult(
                success=True,
                data={"result": "mock_result", "confidence": 0.95},
                timestamp=time.time(),
                processing_time=0.1
            )
        else:
            return ProcessingResult(
                success=False,
                data={},
                timestamp=time.time(),
                processing_time=0.1,
                error_message="Mock error"
            )
            
    async def cleanup(self):
        self.state = "stopped"
        
    def get_state(self):
        return self.state
        
    def get_last_result(self):
        return None


@pytest.fixture
def mock_engine():
    """提供模擬AI引擎"""
    return MockAIEngine("test_engine", success=True)


@pytest.fixture
def failing_mock_engine():
    """提供失敗的模擬AI引擎"""
    return MockAIEngine("failing_engine", success=False)
