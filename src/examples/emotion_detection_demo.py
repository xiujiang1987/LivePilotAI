"""
LivePilotAI 情感檢測示例應用程式
展示如何使用情感檢測引擎進行即時情感分析
"""

import asyncio
import cv2
import numpy as np
import time
import argparse
import logging
from typing import Optional

from src.ai_engine import (
    AIEngineManager,
    EmotionDetectorEngine,
    draw_emotion_results,
    ai_manager
)
from src.core.logging_system import LoggerManager


class EmotionDetectionDemo:
    """情感檢測示例應用程式"""
    
    def __init__(self, camera_id: int = 0, show_fps: bool = True):
        """
        初始化示例應用程式
        
        Args:
            camera_id: 攝影機ID
            show_fps: 是否顯示FPS
        """
        self.camera_id = camera_id
        self.show_fps = show_fps
        self.running = False
        
        # 初始化日誌
        self.logger_manager = LoggerManager()
        self.logger = self.logger_manager.get_logger("EmotionDemo")
        
        # 初始化AI引擎管理器
        self.engine_manager: Optional[AIEngineManager] = None
        self.emotion_engine: Optional[EmotionDetectorEngine] = None
        
        # FPS計算
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    async def initialize(self):
        """初始化應用程式"""
        try:
            self.logger.info("初始化情感檢測示例應用程式...")
            
            # 建立情感檢測引擎配置
            emotion_config = {
                "input_size": (48, 48),
                "emotion_labels": [
                    'Angry', 'Disgust', 'Fear', 'Happy', 
                    'Sad', 'Surprise', 'Neutral'
                ],
                "face_detection": {
                    "cascade_file": "haarcascade_frontalface_default.xml",
                    "scale_factor": 1.1,
                    "min_neighbors": 5,
                    "min_size": (30, 30)
                },
                "smoothing": {
                    "enabled": True,
                    "history_size": 5,
                    "threshold": 0.6
                },
                "performance": {
                    "max_faces": 3,
                    "target_fps": 30
                }
            }
            
            # 創建情感檢測引擎
            self.emotion_engine = EmotionDetectorEngine(
                engine_id="demo_emotion_detector",
                config=emotion_config
            )
            
            # 初始化引擎
            if not await self.emotion_engine.initialize():
                raise RuntimeError("情感檢測引擎初始化失敗")
            
            # 註冊到引擎管理器
            self.engine_manager = ai_manager
            await self.engine_manager.register_engine(self.emotion_engine)
            
            self.logger.info("應用程式初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return False
    
    async def run_camera_demo(self):
        """運行攝影機即時檢測示例"""
        try:
            self.logger.info(f"開啟攝影機 {self.camera_id}...")
            
            # 初始化攝影機
            cap = cv2.VideoCapture(self.camera_id)
            if not cap.isOpened():
                raise RuntimeError(f"無法開啟攝影機 {self.camera_id}")
            
            # 設置攝影機參數
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.running = True
            self.logger.info("開始即時情感檢測 (按 'q' 退出)")
            
            while self.running:
                # 讀取攝影機畫面
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("無法讀取攝影機畫面")
                    break
                
                # 處理畫面
                processed_frame = await self._process_frame(frame)
                
                # 顯示結果
                cv2.imshow('LivePilotAI - 情感檢測示例', processed_frame)
                
                # 更新FPS
                self._update_fps()
                
                # 檢查退出鍵
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("用戶請求退出")
                    break
                elif key == ord('s'):
                    # 保存截圖
                    timestamp = int(time.time())
                    filename = f"emotion_detection_{timestamp}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    self.logger.info(f"截圖已保存: {filename}")
                elif key == ord('r'):
                    # 重置FPS計數器
                    self.fps_counter = 0
                    self.fps_start_time = time.time()
                    self.logger.info("FPS計數器已重置")
            
            # 清理資源
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            self.logger.error(f"攝影機示例運行失敗: {e}")
        finally:
            self.running = False
    
    async def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """處理單一畫面"""
        try:
            # 使用情感檢測引擎處理畫面
            result = await self.emotion_engine.process(frame)
            
            if result.success:
                emotion_results = result.data.get("emotions", [])
                
                # 繪製檢測結果
                processed_frame = draw_emotion_results(frame, emotion_results)
                
                # 添加性能資訊
                if self.show_fps:
                    processed_frame = self._add_performance_info(
                        processed_frame, result.data.get("performance", {})
                    )
                
                # 添加引擎狀態資訊
                processed_frame = self._add_status_info(processed_frame, emotion_results)
                
                return processed_frame
            else:
                # 處理失敗時顯示錯誤訊息
                error_frame = frame.copy()
                cv2.putText(
                    error_frame,
                    f"處理失敗: {result.error_message}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
                return error_frame
                
        except Exception as e:
            self.logger.error(f"畫面處理失敗: {e}")
            error_frame = frame.copy()
            cv2.putText(
                error_frame,
                f"處理錯誤: {str(e)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
            return error_frame
    
    def _add_performance_info(self, frame: np.ndarray, performance: dict) -> np.ndarray:
        """添加性能資訊到畫面"""
        # FPS資訊
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(
            frame,
            fps_text,
            (10, frame.shape[0] - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        # 處理時間
        processing_time = performance.get("processing_time", 0)
        time_text = f"處理時間: {processing_time*1000:.1f}ms"
        cv2.putText(
            frame,
            time_text,
            (10, frame.shape[0] - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        # 引擎FPS
        engine_fps = performance.get("fps", 0)
        engine_fps_text = f"引擎 FPS: {engine_fps:.1f}"
        cv2.putText(
            frame,
            engine_fps_text,
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        return frame
    
    def _add_status_info(self, frame: np.ndarray, emotion_results: list) -> np.ndarray:
        """添加狀態資訊到畫面"""
        # 檢測到的人臉數量
        faces_count = len(emotion_results)
        status_text = f"檢測到 {faces_count} 張人臉"
        cv2.putText(
            frame,
            status_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # 顯示主要情感統計
        if emotion_results:
            emotions = [result["dominant_emotion"] for result in emotion_results]
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            y_offset = 60
            for emotion, count in emotion_counts.items():
                emotion_text = f"{emotion}: {count}"
                cv2.putText(
                    frame,
                    emotion_text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
                y_offset += 25
        
        # 添加操作提示
        help_text = "按 'q' 退出, 's' 截圖, 'r' 重置FPS"
        cv2.putText(
            frame,
            help_text,
            (frame.shape[1] - 400, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )
        
        return frame
    
    def _update_fps(self):
        """更新FPS計算"""
        self.fps_counter += 1
        
        if self.fps_counter % 30 == 0:  # 每30幀計算一次FPS
            current_time = time.time()
            elapsed_time = current_time - self.fps_start_time
            
            if elapsed_time > 0:
                self.current_fps = 30 / elapsed_time
                self.fps_start_time = current_time
    
    async def run_image_demo(self, image_path: str):
        """運行靜態圖片檢測示例"""
        try:
            self.logger.info(f"處理圖片: {image_path}")
            
            # 讀取圖片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"無法讀取圖片: {image_path}")
            
            # 處理圖片
            processed_image = await self._process_frame(image)
            
            # 顯示結果
            cv2.imshow('LivePilotAI - 圖片情感檢測', processed_image)
            
            # 保存結果
            output_path = f"processed_{image_path}"
            cv2.imwrite(output_path, processed_image)
            self.logger.info(f"處理結果已保存: {output_path}")
            
            # 等待用戶按鍵
            self.logger.info("按任意鍵關閉視窗...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            self.logger.error(f"圖片處理失敗: {e}")
    
    async def cleanup(self):
        """清理資源"""
        try:
            self.running = False
            
            if self.engine_manager and self.emotion_engine:
                await self.engine_manager.unregister_engine(self.emotion_engine.engine_id)
            
            if self.emotion_engine:
                await self.emotion_engine.cleanup()
            
            cv2.destroyAllWindows()
            self.logger.info("應用程式清理完成")
            
        except Exception as e:
            self.logger.error(f"清理過程發生錯誤: {e}")


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="LivePilotAI 情感檢測示例")
    parser.add_argument(
        "--camera", 
        type=int, 
        default=0, 
        help="攝影機ID (預設: 0)"
    )
    parser.add_argument(
        "--image", 
        type=str, 
        help="要處理的圖片路徑"
    )
    parser.add_argument(
        "--no-fps", 
        action="store_true", 
        help="不顯示FPS資訊"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日誌級別"
    )
    
    args = parser.parse_args()
    
    # 設置日誌級別
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 創建示例應用程式
    demo = EmotionDetectionDemo(
        camera_id=args.camera,
        show_fps=not args.no_fps
    )
    
    try:
        # 初始化
        if not await demo.initialize():
            print("應用程式初始化失敗")
            return
        
        # 運行對應的示例
        if args.image:
            await demo.run_image_demo(args.image)
        else:
            await demo.run_camera_demo()
            
    except KeyboardInterrupt:
        print("\n用戶中斷執行")
    except Exception as e:
        print(f"執行過程發生錯誤: {e}")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    # 運行示例應用程式
    asyncio.run(main())
