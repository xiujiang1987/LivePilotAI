"""
LivePilotAI - 標註渲染器
在影像上繪製情緒檢測結果（邊界框、標籤等）
"""

import cv2
import numpy as np
from typing import Dict, List


class AnnotationRenderer:
    """
    情緒標註渲染器

    負責在影像上繪製人臉偵測邊界框與情緒標籤，
    將偵測結果視覺化呈現給使用者。
    """

    # 情緒對應的顯示顏色 (BGR)
    EMOTION_COLORS: Dict[str, tuple] = {
        'happy': (0, 255, 0),       # 綠色
        'sad': (255, 150, 0),       # 淺藍
        'angry': (0, 0, 255),       # 紅色
        'surprise': (0, 255, 255),  # 黃色
        'fear': (200, 100, 255),    # 紫色
        'disgust': (0, 128, 128),   # 橄欖綠
        'neutral': (200, 200, 200), # 灰色
        'focused': (255, 200, 0),   # 天藍
        'excited': (0, 200, 255),   # 橙色
        'relaxed': (200, 255, 200), # 淺綠
    }

    DEFAULT_COLOR = (0, 255, 0)
    LOW_CONFIDENCE_COLOR = (0, 255, 255)

    def draw_results(
        self,
        frame: np.ndarray,
        results: List[Dict],
        confidence_threshold: float = 0.6
    ) -> np.ndarray:
        """
        在影像上繪製情緒檢測結果

        Args:
            frame: 原始影像 (BGR)
            results: 檢測結果列表，每個元素包含 bbox, dominant_emotion, confidence
            confidence_threshold: 置信度閾值，高於此值使用情緒對應顏色

        Returns:
            標註後的影像副本
        """
        annotated_frame = frame.copy()

        for result in results:
            x, y, w, h = result['bbox']
            emotion = result['dominant_emotion']
            confidence = result['confidence']

            # 根據置信度與情緒選擇顏色
            if confidence > confidence_threshold:
                color = self.EMOTION_COLORS.get(emotion, self.DEFAULT_COLOR)
            else:
                color = self.LOW_CONFIDENCE_COLOR

            # 繪製人臉邊界框
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)

            # 繪製情緒標籤
            label = f"{emotion}: {confidence:.2f}"
            cv2.putText(
                annotated_frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

        return annotated_frame
