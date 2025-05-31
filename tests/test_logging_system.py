"""
測試日誌系統和錯誤處理
"""

import pytest
import logging
import tempfile
from pathlib import Path
from src.core.logging_system import (
    LoggerManager,
    ErrorHandler,
    LogLevel,
    get_logger,
    log_errors,
    log_async_errors
)


class TestLoggerManager:
    """日誌管理器測試"""
    
    def test_logger_manager_initialization(self, temp_dir):
        """測試日誌管理器初始化"""
        logger_manager = LoggerManager(str(temp_dir))
        
        assert logger_manager.log_dir == temp_dir
        assert logger_manager.log_dir.exists()
        assert len(logger_manager.loggers) == 0
        
    def test_get_logger(self, temp_dir):
        """測試獲取日誌記錄器"""
        logger_manager = LoggerManager(str(temp_dir))
        
        logger = logger_manager.get_logger("test_logger", LogLevel.DEBUG)
        
        assert logger.name == "test_logger"
        assert logger.level == LogLevel.DEBUG.value
        assert "test_logger" in logger_manager.loggers
        
        # 重複獲取應返回同一個實例
        same_logger = logger_manager.get_logger("test_logger")
        assert same_logger is logger
        
    def test_set_log_level(self, temp_dir):
        """測試設置日誌級別"""
        logger_manager = LoggerManager(str(temp_dir))
        
        logger = logger_manager.get_logger("test_logger", LogLevel.INFO)
        assert logger.level == LogLevel.INFO.value
        
        logger_manager.set_log_level("test_logger", LogLevel.ERROR)
        assert logger.level == LogLevel.ERROR.value


class TestErrorHandler:
    """錯誤處理器測試"""
    
    def test_error_handler_initialization(self, temp_dir):
        """測試錯誤處理器初始化"""
        logger_manager = LoggerManager(str(temp_dir))
        error_handler = ErrorHandler(logger_manager)
        
        assert error_handler.logger_manager is logger_manager
        assert error_handler.error_logger is not None
        assert len(error_handler.error_callbacks) == 0
        
    def test_register_error_callback(self, temp_dir):
        """測試註冊錯誤回調"""
        logger_manager = LoggerManager(str(temp_dir))
        error_handler = ErrorHandler(logger_manager)
        
        callback_called = False
        
        def test_callback(error, context):
            nonlocal callback_called
            callback_called = True
            
        error_handler.register_error_callback("ValueError", test_callback)
        
        assert "ValueError" in error_handler.error_callbacks
        
        # 測試回調執行
        test_error = ValueError("Test error")
        error_handler.handle_error(test_error)
        
        assert callback_called
        
    def test_handle_error_without_callback(self, temp_dir):
        """測試處理沒有回調的錯誤"""
        logger_manager = LoggerManager(str(temp_dir))
        error_handler = ErrorHandler(logger_manager)
        
        test_error = RuntimeError("Test runtime error")
        
        # 不應該拋出異常
        error_handler.handle_error(test_error, {"context": "test"})
        
    def test_log_performance(self, temp_dir):
        """測試性能記錄"""
        logger_manager = LoggerManager(str(temp_dir))
        error_handler = ErrorHandler(logger_manager)
        
        # 不應該拋出異常
        error_handler.log_performance("test_function", 0.5, {"param": "value"})
        error_handler.log_performance("slow_function", 2.0, {"param": "value"})


class TestLogDecorators:
    """日誌裝飾器測試"""
    
    def test_log_errors_decorator_success(self):
        """測試錯誤記錄裝飾器 - 成功情況"""
        
        @log_errors("test")
        def test_function(x, y):
            return x + y
            
        result = test_function(1, 2)
        assert result == 3
        
    def test_log_errors_decorator_exception(self):
        """測試錯誤記錄裝飾器 - 異常情況"""
        
        @log_errors("test")
        def test_function():
            raise ValueError("Test error")
            
        with pytest.raises(ValueError):
            test_function()
            
    @pytest.mark.asyncio
    async def test_log_async_errors_decorator_success(self):
        """測試異步錯誤記錄裝飾器 - 成功情況"""
        
        @log_async_errors("test")
        async def async_test_function(x, y):
            return x + y
            
        result = await async_test_function(1, 2)
        assert result == 3
        
    @pytest.mark.asyncio
    async def test_log_async_errors_decorator_exception(self):
        """測試異步錯誤記錄裝飾器 - 異常情況"""
        
        @log_async_errors("test")
        async def async_test_function():
            raise ValueError("Async test error")
            
        with pytest.raises(ValueError):
            await async_test_function()


class TestUtilityFunctions:
    """工具函數測試"""
    
    def test_get_logger_function(self):
        """測試 get_logger 便利函數"""
        logger = get_logger("utility_test", LogLevel.WARNING)
        
        assert logger.name == "utility_test"
        assert logger.level == LogLevel.WARNING.value
