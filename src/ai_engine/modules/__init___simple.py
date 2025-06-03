"""
LivePilotAI 模組包
包含所有功能模組的導入 - 簡化版本
"""

# 避免循環導入，只提供延遲導入函數

def get_dependency_manager():
    from .dependency_manager import DependencyManager, DependencyCheckError
    return DependencyManager, DependencyCheckError

def get_camera_manager():
    from .camera_manager import CameraManager, CameraConfig, CameraSetupError
    return CameraManager, CameraConfig, CameraSetupError

def get_emotion_detector():
    from .emotion_detector import EmotionDetector, EmotionResult, DetectionConfig
    return EmotionDetector, EmotionResult, DetectionConfig

__all__ = [
    'get_dependency_manager',
    'get_camera_manager',
    'get_emotion_detector'
]
