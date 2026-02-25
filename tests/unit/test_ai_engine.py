"""
測試AI引擎基礎架構
"""

import pytest
import asyncio
from src.ai_engine.base_engine import (
    AIEngineManager,
    EngineState,
    ProcessingResult
)


class TestAIEngineManager:
    """AI引擎管理器測試"""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """測試管理器初始化"""
        manager = AIEngineManager()
        
        assert len(manager.engines) == 0
        assert not manager.is_running()
        assert manager.get_available_engines() == []
        
    @pytest.mark.asyncio
    async def test_register_engine(self, mock_engine):
        """測試註冊引擎"""
        manager = AIEngineManager()
        
        # 註冊引擎
        success = await manager.register_engine(mock_engine)
        assert success
        
        # 檢查引擎是否已註冊
        assert mock_engine.engine_id in manager.engines
        assert mock_engine.engine_id in manager.get_available_engines()
        
    @pytest.mark.asyncio
    async def test_register_failing_engine(self, failing_mock_engine):
        """測試註冊失敗的引擎"""
        # 讓引擎初始化失敗
        failing_mock_engine.success = False
        
        manager = AIEngineManager()
        success = await manager.register_engine(failing_mock_engine)
        
        assert not success
        assert failing_mock_engine.engine_id not in manager.engines
        
    @pytest.mark.asyncio
    async def test_unregister_engine(self, mock_engine):
        """測試註銷引擎"""
        manager = AIEngineManager()
        
        # 先註冊引擎
        await manager.register_engine(mock_engine)
        assert mock_engine.engine_id in manager.engines
        
        # 註銷引擎
        success = await manager.unregister_engine(mock_engine.engine_id)
        assert success
        assert mock_engine.engine_id not in manager.engines
        
    @pytest.mark.asyncio
    async def test_unregister_nonexistent_engine(self):
        """測試註銷不存在的引擎"""
        manager = AIEngineManager()
        
        success = await manager.unregister_engine("nonexistent")
        assert not success
        
    @pytest.mark.asyncio
    async def test_process_with_engine(self, mock_engine, mock_ai_input_data):
        """測試使用引擎處理數據"""
        manager = AIEngineManager()
        
        # 註冊引擎
        await manager.register_engine(mock_engine)
        
        # 處理數據
        result = await manager.process_with_engine(
            mock_engine.engine_id, 
            mock_ai_input_data
        )
        
        assert isinstance(result, ProcessingResult)
        assert result.success
        assert "result" in result.data
        assert result.data["result"] == "mock_result"
        
    @pytest.mark.asyncio
    async def test_process_with_nonexistent_engine(self, mock_ai_input_data):
        """測試使用不存在的引擎處理數據"""
        manager = AIEngineManager()
        
        result = await manager.process_with_engine(
            "nonexistent", 
            mock_ai_input_data
        )
        
        assert isinstance(result, ProcessingResult)
        assert not result.success
        assert "引擎不存在" in result.error_message
        
    @pytest.mark.asyncio
    async def test_get_engine_status(self, mock_engine):
        """測試獲取引擎狀態"""
        manager = AIEngineManager()
        
        # 註冊引擎
        await manager.register_engine(mock_engine)
        
        # 獲取狀態
        status = manager.get_engine_status()
        
        assert mock_engine.engine_id in status
        engine_status = status[mock_engine.engine_id]
        assert "state" in engine_status
        assert "config" in engine_status
        assert engine_status["config"]["test"] is True
        
    @pytest.mark.asyncio
    async def test_start_and_stop_all_engines(self, mock_engine):
        """測試啟動和停止所有引擎"""
        manager = AIEngineManager()
        
        # 註冊引擎
        await manager.register_engine(mock_engine)
        
        # 啟動所有引擎
        await manager.start_all_engines()
        assert manager.is_running()
        
        # 停止所有引擎
        await manager.stop_all_engines()
        assert not manager.is_running()


class TestProcessingResult:
    """處理結果測試"""
    
    def test_processing_result_creation(self):
        """測試處理結果創建"""
        result = ProcessingResult(
            success=True,
            data={"test": "value"},
            timestamp=1234567890.0,
            processing_time=0.5
        )
        
        assert result.success
        assert result.data["test"] == "value"
        assert result.timestamp == 1234567890.0
        assert result.processing_time == 0.5
        assert result.error_message is None
        
    def test_processing_result_with_error(self):
        """測試帶錯誤的處理結果"""
        result = ProcessingResult(
            success=False,
            data={},
            timestamp=1234567890.0,
            processing_time=0.1,
            error_message="Test error"
        )
        
        assert not result.success
        assert result.data == {}
        assert result.error_message == "Test error"
