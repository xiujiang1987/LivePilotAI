"""
LivePilotAI OBS Integration Module
Provides OBS Studio integration capabilities for intelligent streaming direction.
"""

from .obs_manager import OBSManager
from .scene_controller import SceneController
from .emotion_mapper import EmotionMapper
from .websocket_client import OBSWebSocketClient

__all__ = [
    'OBSManager',
    'SceneController', 
    'EmotionMapper',
    'OBSWebSocketClient'
]

__version__ = '1.0.0'
