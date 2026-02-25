"""
LivePilotAI - 特效控制器
根據情緒檢測結果生成對應的視覺特效參數
"""

from typing import Dict, List


class EffectController:
    """
    基於情緒的特效控制器

    根據檢測到的情緒調整視覺特效參數，
    輸出可供 OBS 場景渲染使用的特效配置。
    """

    def __init__(self) -> None:
        """初始化特效控制器"""
        self.emotion_effects: Dict[str, Dict] = {
            'Happy': {
                'particles': 'sparkles',
                'color_shift': (1.2, 1.1, 0.9),
                'brightness': 1.15,
                'saturation': 1.2
            },
            'Sad': {
                'particles': 'rain',
                'color_shift': (0.8, 0.9, 1.2),
                'brightness': 0.85,
                'saturation': 0.7
            },
            'Angry': {
                'particles': 'fire',
                'color_shift': (1.3, 0.8, 0.7),
                'brightness': 1.1,
                'saturation': 1.4
            },
            'Surprise': {
                'particles': 'stars',
                'color_shift': (1.1, 1.1, 1.3),
                'brightness': 1.3,
                'saturation': 1.1
            },
            'Neutral': {
                'particles': None,
                'color_shift': (1.0, 1.0, 1.0),
                'brightness': 1.0,
                'saturation': 1.0
            }
        }

    def get_effect_params(self, emotion_results: List[Dict]) -> Dict:
        """
        根據情緒檢測結果生成特效參數

        Args:
            emotion_results: 情緒檢測結果列表

        Returns:
            特效參數字典，包含 particles, color_shift, brightness, saturation, intensity
        """
        if not emotion_results:
            return self.emotion_effects['Neutral']

        best_result = max(emotion_results, key=lambda x: x['confidence'])
        dominant_emotion = best_result['dominant_emotion']

        effect_params = self.emotion_effects.get(
            dominant_emotion,
            self.emotion_effects['Neutral']
        ).copy()

        effect_params['intensity'] = best_result['confidence']

        return effect_params
