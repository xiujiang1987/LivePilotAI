"""
LivePilotAI - AI Engine Module
AI引擎模組 - 提供情緒檢測、影像處理等AI功能
"""

# 版本信息
__version__ = '0.1.0'

# 基本狀態定義
try:
    from .states import EmotionDetectorState, StateTransitionError, EmotionDetectorError
    _states_available = True
except ImportError as e:
    print(f"Warning: Could not import states: {e}")
    _states_available = False

# 延遲導入函數（避免循環依賴）
def get_dependency_manager():
    """獲取依賴管理器類別"""
    try:
        from .modules.dependency_manager import DependencyManager
        return DependencyManager
    except ImportError as e:
        print(f"Error: Could not import DependencyManager: {e}")
        return None

def get_camera_manager():
    """獲取攝像頭管理器類別"""
    try:
        from .modules.camera_manager import CameraManager, CameraConfig
        return CameraManager, CameraConfig
    except ImportError as e:
        print(f"Error: Could not import CameraManager: {e}")
        return None, None

def get_emotion_detector():
    """獲取情感檢測器類別"""
    try:
        from .modules.emotion_detector import EmotionDetector, EmotionResult, DetectionConfig
        return EmotionDetector, EmotionResult, DetectionConfig
    except ImportError as e:
        print(f"Error: Could not import EmotionDetector: {e}")
        return None, None, None

def get_simple_state_machine():
    """獲取簡化狀態機"""
    try:
        from .simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
        return SimpleEmotionDetectorStateMachine
    except ImportError as e:
        print(f"Error: Could not import SimpleEmotionDetectorStateMachine: {e}")
        return None

def get_full_state_machine():
    """獲取完整狀態機"""
    try:
        from .emotion_state_machine import EmotionDetectorStateMachine, EmotionDetectorConfig
        return EmotionDetectorStateMachine, EmotionDetectorConfig
    except ImportError as e:
        print(f"Error: Could not import EmotionDetectorStateMachine: {e}")
        return None, None

# 舊版引擎（向後兼容）
def get_legacy_engine():
    """獲取舊版情感檢測引擎"""
    try:
        from .emotion_detector_engine import EmotionDetectorEngine
        return EmotionDetectorEngine
    except ImportError as e:
        print(f"Error: Could not import legacy EmotionDetectorEngine: {e}")
        return None

# 導出的主要組件（只包含確實可用的）
__all__ = [
    'get_dependency_manager',
    'get_camera_manager', 
    'get_emotion_detector',
    'get_simple_state_machine',
    'get_full_state_machine',
    'get_legacy_engine'
]

# 如果狀態可用，則添加到導出列表
if _states_available:
    __all__.extend(['EmotionDetectorState', 'StateTransitionError', 'EmotionDetectorError'])
