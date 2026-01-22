# -*- coding: utf-8 -*-
"""
LivePilotAI 情感強度分析模組
負責計算情感強度、穩定性和主導情感
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque
from dataclasses import dataclass, field
import time

logger = logging.getLogger(__name__)

@dataclass
class EmotionDynamics:
    """情感動態特徵"""
    current_emotion: str
    intensity: float  # 當前強度 0.0-1.0
    stability: float  # 穩定性 0.0-1.0
    dominant_emotions: List[Tuple[str, float]] # 主要情感列表 (情感, 強度)
    transition_speed: float # 情感變化速度

@dataclass
class IntensityConfig:
    """強度分析配置"""
    smoothing_window: int = 5    # 平滑窗口大小
    stability_threshold: float = 0.2 # 穩定性閾值
    decay_rate: float = 0.1      # 衰減率
    min_intensity: float = 0.1   # 最小強度

class EmotionIntensityAnalyzer:
    """
    情感強度分析器
    使用時間序列分析情感的變化、強度和穩定性
    """
    
    def __init__(self, config: IntensityConfig = None):
        self.config = config or IntensityConfig()
        
        # 歷史數據緩衝區
        self.history: Deque[Dict[str, float]] = deque(maxlen=self.config.smoothing_window)
        
        # 上一次分析結果
        self.last_dynamics: Optional[EmotionDynamics] = None
        self.last_update_time = time.time()
        
        logger.info("情感強度分析器初始化完成")

    def analyze(self, emotion_probs: Dict[str, float]) -> EmotionDynamics:
        """
        分析情感強度和動態
        
        Args:
            emotion_probs: 情感概率字典 {'happy': 0.8, 'sad': 0.1, ...}
            
        Returns:
            EmotionDynamics 對象
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 添加到歷史記錄
        self.history.append(emotion_probs)
        
        # 1. 計算平均概率 (平滑)
        avg_probs = self._calculate_average_probs()

        if not avg_probs:
            return EmotionDynamics(
                current_emotion="neutral",
                intensity=0.0,
                stability=0.0,
                dominant_emotions=[],
                transition_speed=0.0
            )
        
        # 2. 確定當前主導情感
        current_emotion = max(avg_probs.items(), key=lambda x: x[1])[0]
        current_intensity = avg_probs[current_emotion]
        
        # 3. 計算穩定性 (標準差的倒數相關)
        stability = self._calculate_stability(current_emotion)
        
        # 4. 計算變化速度
        transition_speed = 0.0
        if self.last_dynamics:
            prev_intensity = self.last_dynamics.intensity
            transition_speed = abs(current_intensity - prev_intensity) / (dt + 1e-6)
            
        # 5. 獲取排序後的情感列表
        sorted_emotions = sorted(avg_probs.items(), key=lambda x: x[1], reverse=True)
        
        dynamics = EmotionDynamics(
            current_emotion=current_emotion,
            intensity=current_intensity,
            stability=stability,
            dominant_emotions=sorted_emotions[:3], # 取前三名
            transition_speed=transition_speed
        )
        
        self.last_dynamics = dynamics
        return dynamics

    def _calculate_average_probs(self) -> Dict[str, float]:
        """計算歷史窗口內的平均概率"""
        if not self.history:
            return {}
            
        avg_probs = {}
        emotions = self.history[0].keys()
        
        for emotion in emotions:
            values = [frame[emotion] for frame in self.history if emotion in frame]
            avg_probs[emotion] = sum(values) / len(values) if values else 0.0
            
        return avg_probs

    def _calculate_stability(self, target_emotion: str) -> float:
        """計算特定情感的穩定性"""
        if len(self.history) < 2:
            return 1.0
            
        # 計算該情感在窗口內的變化標準差
        values = [frame.get(target_emotion, 0.0) for frame in self.history]
        std_dev = np.std(values)
        
        # 標準差越小越穩定，歸一化到 0-1
        # 假設最大標準差約為 0.5 (0到1之間跳變)
        stability = max(0.0, 1.0 - (std_dev * 2))
        return stability
