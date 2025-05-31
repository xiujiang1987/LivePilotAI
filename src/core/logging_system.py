"""
LivePilotAI - 日誌系統與錯誤處理
提供統一的日誌記錄、錯誤處理和監控功能
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from datetime import datetime
import traceback
import functools
from enum import Enum
import json


class LogLevel(Enum):
    """日誌級別枚舉"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class CustomFormatter(logging.Formatter):
    """自定義日誌格式化器"""
    
    def __init__(self):
        super().__init__()
        
        # 不同日誌級別的顏色
        self.COLORS = {
            'DEBUG': '\033[36m',    # 青色
            'INFO': '\033[32m',     # 綠色
            'WARNING': '\033[33m',  # 黃色
            'ERROR': '\033[31m',    # 紅色
            'CRITICAL': '\033[35m', # 紫色
            'RESET': '\033[0m'      # 重置
        }
        
        # 日誌格式
        self.format_string = (
            "{color}[{levelname:8}]{reset} "
            "{asctime} | {name:20} | {message}"
        )
        
    def format(self, record):
        # 獲取顏色
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # 格式化消息
        formatted = self.format_string.format(
            color=color,
            reset=reset,
            levelname=record.levelname,
            asctime=self.formatTime(record, '%Y-%m-%d %H:%M:%S'),
            name=record.name,
            message=record.getMessage()
        )
        
        # 添加異常信息
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
            
        return formatted


class LoggerManager:
    """日誌管理器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_root_logger()
        
    def _setup_root_logger(self):
        """設置根日誌記錄器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除現有處理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
    def get_logger(self, name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
        """獲取指定名稱的日誌記錄器"""
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(name)
        logger.setLevel(level.value)
        
        # 防止重複添加處理器
        if not logger.handlers:
            self._setup_logger_handlers(logger, name)
            
        self.loggers[name] = logger
        return logger
        
    def _setup_logger_handlers(self, logger: logging.Logger, name: str):
        """為日誌記錄器設置處理器"""
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)
        
        # 文件處理器 - 一般日誌
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 錯誤日誌處理器
        error_file = self.log_dir / f"{name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
    def set_log_level(self, logger_name: str, level: LogLevel):
        """設置指定日誌記錄器的級別"""
        if logger_name in self.loggers:
            self.loggers[logger_name].setLevel(level.value)


class ErrorHandler:
    """錯誤處理器"""
    
    def __init__(self, logger_manager: LoggerManager):
        self.logger_manager = logger_manager
        self.error_logger = logger_manager.get_logger("ErrorHandler")
        self.error_callbacks: Dict[str, Callable] = {}
        
    def register_error_callback(self, error_type: str, callback: Callable):
        """註冊錯誤回調函數"""
        self.error_callbacks[error_type] = callback
        self.error_logger.info(f"註冊錯誤回調: {error_type}")
        
    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """處理錯誤"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 記錄錯誤
        self.error_logger.error(
            f"錯誤類型: {error_type}, 消息: {error_message}",
            exc_info=True,
            extra={"context": context}
        )
        
        # 執行錯誤回調
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error, context)
            except Exception as callback_error:
                self.error_logger.error(f"錯誤回調執行失敗: {callback_error}")
                
    def log_performance(self, function_name: str, execution_time: float, context: Dict[str, Any] = None):
        """記錄性能數據"""
        perf_logger = self.logger_manager.get_logger("Performance")
        perf_data = {
            "function": function_name,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        if execution_time > 1.0:  # 超過1秒的操作記錄為警告
            perf_logger.warning(f"慢速操作: {json.dumps(perf_data, ensure_ascii=False)}")
        else:
            perf_logger.info(f"性能數據: {json.dumps(perf_data, ensure_ascii=False)}")


def log_errors(logger_name: str = "default"):
    """錯誤記錄裝飾器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logger_manager.get_logger(logger_name)
            try:
                start_time = datetime.now()
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # 記錄性能
                error_handler.log_performance(
                    func.__name__, 
                    execution_time,
                    {"args_count": len(args), "kwargs_count": len(kwargs)}
                )
                
                return result
                
            except Exception as e:
                error_handler.handle_error(e, {
                    "function": func.__name__,
                    "args": str(args)[:200] if args else "",
                    "kwargs": str(kwargs)[:200] if kwargs else ""
                })
                raise
                
        return wrapper
    return decorator


def log_async_errors(logger_name: str = "default"):
    """異步函數錯誤記錄裝飾器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logger_manager.get_logger(logger_name)
            try:
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # 記錄性能
                error_handler.log_performance(
                    func.__name__, 
                    execution_time,
                    {"args_count": len(args), "kwargs_count": len(kwargs)}
                )
                
                return result
                
            except Exception as e:
                error_handler.handle_error(e, {
                    "function": func.__name__,
                    "args": str(args)[:200] if args else "",
                    "kwargs": str(kwargs)[:200] if kwargs else ""
                })
                raise
                
        return wrapper
    return decorator


# 全局實例
logger_manager = LoggerManager()
error_handler = ErrorHandler(logger_manager)

# 便利函數
def get_logger(name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
    """獲取日誌記錄器"""
    return logger_manager.get_logger(name, level)

def handle_error(error: Exception, context: Dict[str, Any] = None):
    """處理錯誤"""
    error_handler.handle_error(error, context)

def log_performance(function_name: str, execution_time: float, context: Dict[str, Any] = None):
    """記錄性能數據"""
    error_handler.log_performance(function_name, execution_time, context)
