# -*- coding: utf-8 -*-
"""
LivePilotAI 進階視覺化引擎
負責所有視覺特效、標註和資訊顯示的渲染
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import time

class Visualizer:
    """
    視覺化渲染引擎
    提供專業級的視覺標註功能
    """
    
    # 顏色定義 (BGR)
    COLORS = {
        'happy': (0, 255, 255),    # 黃色
        'sad': (255, 0, 0),        # 藍色
        'angry': (0, 0, 255),      # 紅色
        'surprise': (255, 0, 255), # 紫色
        'fear': (128, 0, 128),     # 深紫
        'neutral': (200, 200, 200),# 灰色
        'focused': (0, 255, 0),    # 綠色
        'excited': (0, 165, 255),  # 橘色
        'relaxed': (255, 191, 0),  # 深天藍
        'disgust': (0, 128, 0)     # 深綠
    }
    
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        繪製完整的檢測結果
        
        Args:
            frame: 原始影像
            detections: 檢測結果列表，每個元素包含 emotion, bbox, confidence, intensity 等
            
        Returns:
            標註後的影像
        """
        output = frame.copy()
        
        for det in detections:
            bbox = det.get('bbox')
            if not bbox:
                continue
                
            x, y, w, h = bbox
            emotion = det.get('emotion', 'unknown')
            confidence = det.get('confidence', 0.0)
            face_id = det.get('face_id')
            intensity = det.get('intensity', 0.0)
            
            color = self.COLORS.get(emotion, (255, 255, 255))
            
            # 1. 繪製邊框 (帶圓角效果)
            self._draw_rounded_rect(output, (x, y, w, h), color, 2, 10)
            
            # 2. 繪製標籤背景
            label = f"{emotion} {confidence:.1f}"
            if face_id is not None:
                label = f"ID:{face_id} {label}"
                
            (label_w, label_h), baseline = cv2.getTextSize(label, self.font, 0.6, 1)
            cv2.rectangle(output, (x, y - label_h - 10), (x + label_w + 10, y), color, -1)
            
            # 3. 繪製文字
            cv2.putText(output, label, (x + 5, y - 5), 
                        self.font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
            
            # 4. 繪製強度條
            if intensity > 0:
                self._draw_intensity_bar(output, x + w + 5, y, h, intensity, color)
                
            # 5. 繪製關鍵點 (如果有的話)
            landmarks = det.get('landmarks')
            if landmarks:
                for lx, ly in landmarks:
                    cv2.circle(output, (lx, ly), 2, (0, 255, 255), -1)
                    
        return output
        
    def draw_gestures(self, frame: np.ndarray, gestures: List[Dict]) -> np.ndarray:
        """
        繪製手勢檢測結果
        """
        output = frame.copy()
        for ges in gestures:
            gesture = ges['gesture']
            confidence = ges['confidence']
            landmarks = ges['landmarks']
            
            # 轉換歸一化座標到像素座標
            h, w = frame.shape[:2]
            pix_landmarks = [(int(x*w), int(y*h)) for x, y in landmarks]
            
            # 手勢外框中心
            xs = [x for x, y in pix_landmarks]
            ys = [y for x, y in pix_landmarks]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            # 繪製手部骨架 (部分)
            for i, (x, y) in enumerate(pix_landmarks):
                cv2.circle(output, (x, y), 3, (0, 255, 0), -1)
                
            # 顯示手勢名稱
            label = f"{gesture} ({confidence:.2f})"
            cv2.putText(output, label, (min_x, min_y - 10), 
                        self.font, 0.8, (0, 255, 255), 2)
            
            # 繪製邊框
            cv2.rectangle(output, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            
        return output

    def _draw_rounded_rect(self, img, rect, color, thickness, r):
        """繪製圓角矩形"""
        x, y, w, h = rect
        # 簡單實現：繪製普通矩形
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
        
        # 進階實現（如果需要圓角，可以使用多個線段和圓弧，這裡簡化處理）
        # cv2.line(img, (x+r, y), (x+w-r, y), color, thickness)
        # ...

    def _draw_intensity_bar(self, img, x, y, h, intensity, color):
        """繪製垂直強度條"""
        bar_width = 10
        total_height = h
        filled_height = int(total_height * intensity)
        
        # 背景
        cv2.rectangle(img, (x, y), (x + bar_width, y + total_height), (50, 50, 50), -1)
        
        # 前景 (強度)
        start_y = y + total_height - filled_height
        cv2.rectangle(img, (x, y + total_height - filled_height), (x + bar_width, y + total_height), color, -1)
        
        # 外框
        cv2.rectangle(img, (x, y), (x + bar_width, y + total_height), (200, 200, 200), 1)

