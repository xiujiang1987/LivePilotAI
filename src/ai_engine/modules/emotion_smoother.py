"""
LivePilotAI - 情緒平滑處理器
使用歷史記錄平滑情緒預測結果，減少波動
"""

import numpy as np
from typing import Dict, List


class EmotionSmoother:
    """
    情緒平滑處理器

    透過滑動窗口平均法 (Moving Average) 平滑即時情緒預測結果，
    避免因單幀偵測誤差導致的畫面閃爍或場景頻繁切換。

    Args:
        emotion_labels: 支援的情緒標籤列表
        history_size: 歷史記錄窗口大小 (預設 5 幀)
    """

    def __init__(self, emotion_labels: List[str], history_size: int = 5):
        self.emotion_labels = emotion_labels
        self.history_size = history_size
        self.emotion_history: List[Dict[str, float]] = []

    def smooth(self, current_emotion: Dict[str, float]) -> Dict[str, float]:
        """
        使用歷史記錄平滑情緒預測結果

        Args:
            current_emotion: 當前情緒預測 (emotion -> confidence)

        Returns:
            平滑後的情緒預測
        """
        self.emotion_history.append(current_emotion)

        if len(self.emotion_history) > self.history_size:
            self.emotion_history.pop(0)

        if len(self.emotion_history) == 1:
            return current_emotion

        smoothed_emotion = {}
        for emotion in self.emotion_labels:
            avg_confidence = float(np.mean([
                hist.get(emotion, 0.0) for hist in self.emotion_history
            ]))
            smoothed_emotion[emotion] = avg_confidence

        return smoothed_emotion

    def reset(self) -> None:
        """清除歷史記錄"""
        self.emotion_history.clear()
