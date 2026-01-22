# -*- coding: utf-8 -*-
"""
LivePilotAI 手勢識別模組
使用 MediaPipe Hands 進行即時手勢檢測
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import Optional, Tuple, Dict, List

logger = logging.getLogger(__name__)

class GestureDetector:
    """
    即時手勢識別器
    支援識別: 加油(Thumbs Up), 停止(Open Palm), OK
    """
    
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        # 手指尖端索引
        self.tip_ids = [4, 8, 12, 16, 20]
        
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        檢測影像中的手勢
        
        Args:
            frame: 輸入影像 (BGR)
            
        Returns:
            檢測到的手勢列表，每個元素包含:
            {
                'gesture': str,      # 手勢名稱
                'hand': str,         # 'Left' or 'Right'
                'confidence': float, # 置信度
                'landmarks': list    # 關鍵點
            }
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        detections = []
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 判斷左右手
                label = "Unknown"
                score = 0.0
                if results.multi_handedness:
                    label = results.multi_handedness[hand_idx].classification[0].label
                    score = results.multi_handedness[hand_idx].classification[0].score
                
                # 識別手勢
                gesture = self._recognize_gesture(hand_landmarks)
                
                if gesture != "None":
                    detections.append({
                        'gesture': gesture,
                        'hand': label,
                        'confidence': score,
                        # 簡單轉換 landmarks 為 list 供繪圖使用
                        'landmarks': [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                    })
                    
        return detections

    def _recognize_gesture(self, landmarks) -> str:
        """
        根據關鍵點識別手勢規則
        """
        # 獲取關鍵點座標 (y軸向下增加)
        lms = landmarks.landmark
        
        # 狀態：手指是否伸直 (1:伸直, 0:彎曲)
        fingers = []
        
        # 拇指 (Thumb) - 比較 x 座標 (需要根據左右手判斷，這裡簡化判斷：指尖在指關節外側)
        # 用簡單的幾何規則：大拇指指尖(4) 與 關節(3) 的相對位置太依賴手掌方向
        # 這裡改用通用規則：計算指尖與掌心的距離 vs 關節與掌心的距離 (較魯棒)
        # 但為了簡單，我們先用 y 軸判斷是否有 "Thumbs Up" (拇指朝上)
        
        # 食指到小指 (Index to Pinky)
        # 指尖(8,12,16,20) 是否高於(y值小於) 關節(6,10,14,18)
        for id in range(1, 5):
            if lms[self.tip_ids[id]].y < lms[self.tip_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
                
        # 拇指特殊處理 for "Thumbs Up"
        # 拇指尖(4) 高於 關節(3) 且 其他手指彎曲
        is_thumb_up = lms[4].y < lms[3].y
        
        total_fingers = fingers.count(1)
        
        # --- 規則判定 ---
        
        # 1. Open Palm (停止/High Five): 5指全開
        # 拇指也要判斷是否張開 (指尖與食指掌關節距離 > 閾值) 比較準確，但簡單起見：
        # 如果4指伸直 + 拇指看起來也沒有嚴重彎曲
        if total_fingers == 4:
            # 檢查 thumb (稍微寬鬆)
             if abs(lms[4].x - lms[9].x) > 0.05: # 拇指水平遠離食指根部
                 return "Open_Palm"
        
        # 2. Thumbs Up (讚): 僅拇指朝上，其他捲曲
        if total_fingers == 0 and is_thumb_up:
            return "Thumbs_Up"
            
        # 3. OK Gesture: 拇指尖與食指尖接觸，其他3指伸直
        # 接觸: 距離小於閾值
        thumb_tip = lms[4]
        index_tip = lms[8]
        distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
        
        # 需檢查 中指、無名指、小指 伸直
        # fingers陣列對應: [食指(1), 中指(2), 無名指(3), 小指(4)]
        # index(0) 是食指
        if distance < 0.05 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1:
            # 食指應該是彎曲的(形成圓圈)，所以在 fingers[0] 可能是 0 或 1 取決於角度
            # 重點是接觸 + 其他三指伸直
            return "OK"
            
        return "None"
