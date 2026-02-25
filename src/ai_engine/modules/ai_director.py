# -*- coding: utf-8 -*-
"""
LivePilotAI AI 智慧導播引擎 (AI Director)
整合視覺(情緒、手勢)與聽覺(語音)訊號，自動決策導播行為
"""

import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# 嘗試匯入模組，如果失敗則提供 mock 或報錯
try:
    from .emotion_detector import EmotionDetector
    from .gesture_detector import GestureDetector
    # AudioController 通常運行在獨立執行緒，這裡主要接收其狀態
except ImportError:
    pass

logger = logging.getLogger("AIDirector")

class AIDirector:
    """
    AI 導播核心
    
    職責：
    1. 接收多模態輸入 (影像 Frame, 音訊 Event, OBS 狀態)
    2. 維護導播狀態機 (State Machine)
    3. 輸出導播指令 (Switch Scene, Set Source Visibility, etc.)
    """
    
    def __init__(self, 
                 real_time_detector: Optional[Any] = None,
                 scene_controller: Optional[Any] = None,
                 emotion_mapper: Optional[Any] = None,
                 config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = True
        
        # 依賴注入
        self.real_time_detector = real_time_detector
        self.scene_controller = scene_controller
        self.emotion_mapper = emotion_mapper
        
        # 初始化子系統 (若未提供依賴，則回退到內部創建 - Backward Compatibility)
        if not self.real_time_detector:
             self.emotion_detector = EmotionDetector()
             self.gesture_detector = GestureDetector()
        else:
             self.emotion_detector = self.real_time_detector.emotion_detector
             self.gesture_detector = getattr(self.real_time_detector, 'gesture_detector', None) or GestureDetector()
        
        # 導播狀態
        self.current_scene = "Unknown"
        self.last_switch_time = time.time()
        self.min_switch_interval = self.config.get('min_switch_interval', 5.0) # 最小切換間隔(秒)
        self.face_lost_time = None
        
        # 規則庫 (簡單版)
        self.rules = self._load_default_rules()
        
        logger.info("AI Director initialized")

    def _load_default_rules(self) -> List[Dict]:
        """載入預設導播規則"""
        return [
            {
                "trigger": "gesture",
                "condition": "Thumbs_Up",
                "action": "trigger_effect",
                "param": "like_animation",
                "priority": 10
            },
            {
                "trigger": "gesture",
                "condition": "Open_Palm",
                "action": "switch_scene",
                "param": "BRB_Scene", # Be Right Back
                "priority": 10
            },
            {
                "trigger": "emotion",
                "condition": "happy",
                "action": "filter",
                "param": "warm_color",
                "priority": 5
            },
            {
                "trigger": "no_face",
                "duration": 10.0,
                "action": "switch_scene",
                "param": "Wide_Camera",
                "priority": 1
            }
        ]

    def process_frame(self, frame) -> Tuple[Optional[Dict[str, Any]], Dict]:
        """
        處理單一影像影格並做出導播決策
        
        Returns:
            decision (dict): 導播指令 (如果有的話)
            metadata (dict): 分析結果 (情緒, 手勢等)
        """
        if not self.enabled:
            return None, {}
            
        metadata = {}
        
        # 1. 視覺分析
        # 有時候我們只需要每 N 幀分析一次以節省效能，這裡假設每幀都分析
        detected_faces = self.emotion_detector.detect_emotions(frame)
        emotions = {'faces': detected_faces}
        
        # GestureDetector 處理 (已經在外面處理了異常，這裡直接 call)
        gesture = self.gesture_detector.detect(frame)   # 假設 GestureDetector 接口
        
        metadata['emotions'] = emotions
        metadata['gesture'] = gesture
        
        # 更新狀態：人臉追蹤
        if not emotions or not emotions.get('faces'):
            if self.face_lost_time is None:
                self.face_lost_time = time.time()
        else:
            self.face_lost_time = None
            
        # 2. 決策邏輯
        decision = self._evaluate_rules(metadata)
        
        return decision, metadata

    def _evaluate_rules(self, metadata: Dict) -> Optional[Dict]:
        """評估所有規則並返回最高優先級的行動"""
        now = time.time()
        
        # 冷卻時間檢查 (若是切換場景類)
        if now - self.last_switch_time < self.min_switch_interval:
            return None

        # 檢查手勢規則
        gesture = metadata.get('gesture')
        if gesture:
            for rule in self.rules:
                if rule['trigger'] == 'gesture' and rule['condition'] == gesture:
                    return self._create_action(rule)

        # 檢查無人臉規則
        if self.face_lost_time:
            lost_duration = now - self.face_lost_time
            for rule in self.rules:
                if rule['trigger'] == 'no_face' and lost_duration > rule['duration']:
                    # Reset timer to avoid spamming
                    self.face_lost_time = now 
                    return self._create_action(rule)
                    
        return None

    def _create_action(self, rule: Dict) -> Dict:
        """建立行動指令"""
        self.last_switch_time = time.time()
        return {
            "type": rule['action'],
            "target": rule['param'],
            "source_rule": rule
        }

    def update_audio_state(self, audio_event):
        """接收來自 AudioController 的事件"""
        # TODO: 實作語音觸發切換
        pass
