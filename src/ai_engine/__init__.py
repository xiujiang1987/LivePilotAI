"""
LivePilotAI - AI Engine Module
AI引擎模組 - 提供情緒檢測、影像處理等AI功能
"""

from .base_engine import (
    AIEngineBase,
    AIEngineManager,
    EngineState,
    ProcessingResult,
    ai_manager
)

__all__ = [
    'AIEngineBase',
    'AIEngineManager', 
    'EngineState',
    'ProcessingResult',
    'ai_manager'
]

__version__ = '0.1.0'
