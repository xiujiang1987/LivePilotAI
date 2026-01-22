# -*- coding: utf-8 -*-
"""
LivePilotAI 高級功能示範 (Day 5)
展示核心新功能：
1. 多人臉穩定追蹤 (ID保持)
2. 情感強度即時分析 (Intensity Bar)
3. 進階視覺化 (Visualizer)
"""

import sys
import os
from pathlib import Path
import cv2
import time

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from ai_engine.modules.real_time_detector import RealTimeEmotionDetector, RealTimeConfig
from ai_engine.modules.camera_manager import CameraConfig

def main():
    print("🚀 啟動 LivePilotAI 高級示範 (Day 5)")
    print("=======================================")
    print("功能亮點:")
    print("  • 👥 多人臉 ID 追蹤")
    print("  • 📊 情感強度動態分析")
    print("  • 🎨 專業級視覺化標註")
    print("---------------------------------------")
    print("按 'q' 退出示範")
    
    # 配置
    camera_config = CameraConfig(device_id=0, width=1280, height=720, fps=30)
    config = RealTimeConfig(
        camera_config=camera_config,
        window_name="LivePilotAI - Day 5 Advanced Demo"
    )
    
    detector = RealTimeEmotionDetector(config)
    
    # 啟動
    if detector.start():
        try:
            while detector.is_running:
                # 這裡不需要做什麼，顯示是在後台線程處理的
                # 或者如果沒有後台線程顯示，我們需要在這裡手動顯示
                # 檢查 RealTimeDetector 實現，它有 _start_display_thread 但默認可能只是更新變量
                
                # 檢查實現細節... show_video=True (默認) 會啟動顯示線程嗎？
                # 代碼中: if self.config.show_video: self._start_display_thread()
                # 所以應該會自動顯示
                
                # 為了避免主線程退出
                time.sleep(0.1)
                
                # 檢查是否需要退出 (opencv 窗口的按鍵在線程中處理了嗎？)
                # 通常 cv2.waitKey 需要在主線程或者專門的 GUI 線程
                # 讓我們看看 RealTimeDetector 的實現
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            detector.stop()
            print("\n👋 示範結束")
    else:
        print("❌ 啟動失敗")

if __name__ == "__main__":
    main()
