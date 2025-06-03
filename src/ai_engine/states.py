"""
LivePilotAI 狀態機狀態定義
定義情感檢測引擎的各個狀態
"""

from enum import Enum


class EmotionDetectorState(Enum):
    """情感檢測引擎狀態枚舉"""
    INIT = 1                    # 初始化狀態
    DEPENDENCY_CHECK = 2        # 依賴檢查狀態
    CAMERA_SETUP = 3           # 攝像頭設置狀態
    MODEL_LOADING = 4          # 模型載入狀態
    DETECTION_READY = 5        # 檢測準備就緒
    EMOTION_DETECTION = 6      # 情感檢測運行中
    ERROR_HANDLING = 7         # 錯誤處理狀態
    CLEANUP = 8                # 清理狀態
    STOPPED = 9                # 停止狀態


class StateTransitionError(Exception):
    """狀態轉換錯誤"""
    pass


class EmotionDetectorError(Exception):
    """情感檢測器錯誤"""
    pass
