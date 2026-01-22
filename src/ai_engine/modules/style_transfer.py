# -*- coding: utf-8 -*-
"""
LivePilotAI 風格轉換模組
提供即時影像風格濾鏡 (OpenCV 濾鏡 + TensorFlow Hub 模型)
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)

class StyleTransfer:
    """
    影像風格轉換引擎
    支援:
    1. OpenCV 快速濾鏡 (Cartoon, Sketch, Edge)
    2. TensorFlow Hub 風格轉換 (預留介面)
    """
    
    def __init__(self):
        self.current_style = "none"
        self.tf_model = None
        self.styles = {
            "none": "原始影像",
            "cartoon": "卡通風格",
            "sketch": "素描畫",
            "edge": "邊緣檢測",
            "sepia": "懷舊濾鏡",
            "autumn": "秋意濃",
        }
        
    def apply_style(self, frame: np.ndarray, style: str) -> np.ndarray:
        """
        應用風格濾鏡
        
        Args:
            frame: 輸入影像 (BGR)
            style: 風格名稱
            
        Returns:
            處理後的影像
        """
        if style not in self.styles:
            return frame
            
        if style == "none":
            return frame
            
        try:
            method_name = f"_apply_{style}"
            if hasattr(self, method_name):
                return getattr(self, method_name)(frame)
            return frame
        except Exception as e:
            logger.warning(f"Apply style '{style}' failed: {e}")
            return frame
            
    def _apply_cartoon(self, frame: np.ndarray) -> np.ndarray:
        """卡通風格濾鏡"""
        # 1. 邊緣檢測
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, 
                                    cv2.ADAPTIVE_THRESH_MEAN_C, 
                                    cv2.THRESH_BINARY, 9, 9)
        
        # 2. 顏色量化 (Bilateral Filter 減少雜訊但保留邊緣)
        color = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # 3. 合併
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon

    def _apply_sketch(self, frame: np.ndarray) -> np.ndarray:
        """素描風格"""
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted_gray_image = 255 - gray_image
        blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        inverted_blurred_image = 255 - blurred_image
        sketch_image = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
        
        # 轉回 3 channel 方便顯示
        return cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)

    def _apply_edge(self, frame: np.ndarray) -> np.ndarray:
        """邊緣檢測 (Canny)"""
        edges = cv2.Canny(frame, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
    def _apply_sepia(self, frame: np.ndarray) -> np.ndarray:
        """懷舊濾鏡"""
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        return cv2.transform(frame, kernel)

    def _apply_autumn(self, frame: np.ndarray) -> np.ndarray:
        """秋天濾鏡 (Color Map)"""
        return cv2.applyColorMap(frame, cv2.COLORMAP_AUTUMN)

    def get_available_styles(self) -> List[str]:
        return list(self.styles.keys())
