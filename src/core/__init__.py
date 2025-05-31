"""
LivePilotAI - Core Module
核心模組 - 提供配置管理、日誌系統、錯誤處理等基礎功能
"""

from .config_manager import (
    ConfigManager,
    AppConfig,
    DatabaseConfig,
    AIModelConfig,
    OBSConfig,
    APIConfig,
    LoggingConfig,
    Environment,
    config_manager,
    get_config,
    load_config,
    save_config
)

from .logging_system import (
    LoggerManager,
    ErrorHandler,
    LogLevel,
    CustomFormatter,
    logger_manager,
    error_handler,
    get_logger,
    handle_error,
    log_performance,
    log_errors,
    log_async_errors
)

__all__ = [
    # 配置管理
    'ConfigManager',
    'AppConfig',
    'DatabaseConfig', 
    'AIModelConfig',
    'OBSConfig',
    'APIConfig',
    'LoggingConfig',
    'Environment',
    'config_manager',
    'get_config',
    'load_config',
    'save_config',
    
    # 日誌系統
    'LoggerManager',
    'ErrorHandler',
    'LogLevel',
    'CustomFormatter',
    'logger_manager',
    'error_handler',
    'get_logger',
    'handle_error',
    'log_performance',
    'log_errors',
    'log_async_errors'
]

__version__ = '0.1.0'
