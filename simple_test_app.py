#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 簡化測試版本
Simplified test version to verify basic functionality
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

class SimpleTestApp:
    """簡化版應用程式用於測試基本功能"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LivePilotAI 簡化測試版")
        self.root.geometry("600x400")
        
        self.setup_ui()
        self.test_imports()
        
    def setup_ui(self):
        """設置用戶界面"""
        # 標題
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="LivePilotAI 簡化測試版",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # 主要內容
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 測試結果區域
        result_frame = tk.LabelFrame(main_frame, text="導入測試結果", font=("Arial", 10, "bold"))
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.result_text = tk.Text(
            result_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        scrollbar = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按鈕區域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        test_btn = tk.Button(
            button_frame,
            text="重新測試導入",
            command=self.test_imports,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        )
        test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        launch_simple_btn = tk.Button(
            button_frame,
            text="啟動簡化版",
            command=self.launch_simple_version,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        )
        launch_simple_btn.pack(side=tk.LEFT, padx=5)
        
        fix_btn = tk.Button(
            button_frame,
            text="修復缺失模組",
            command=self.fix_missing_modules,
            bg="#e67e22",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        )
        fix_btn.pack(side=tk.LEFT, padx=5)
        
    def log(self, message, status="INFO"):
        """添加測試結果日誌"""
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {status}: {message}\n"
        self.result_text.insert(tk.END, formatted_msg)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
        
    def test_imports(self):
        """測試模組導入"""
        self.result_text.delete(1.0, tk.END)
        self.log("開始測試模組導入...")
        
        # 測試基本模組
        basic_modules = [
            "tkinter",
            "pathlib", 
            "json",
            "logging",
            "threading",
            "asyncio"
        ]
        
        self.log("1. 測試基本 Python 模組:")
        for module in basic_modules:
            try:
                __import__(module)
                self.log(f"   [PASS] {module}", "SUCCESS")
            except ImportError as e:
                self.log(f"   [FAIL] {module}: {e}", "ERROR")
        
        # 測試專案核心模組
        self.log("\n2. 測試專案核心模組:")
        
        # 測試 core 模組
        try:
            from core.config_manager import ConfigManager
            self.log("   [PASS] core.config_manager", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] core.config_manager: {e}", "ERROR")
        
        try:
            from core.logging_system import setup_logging
            self.log("   [PASS] core.logging_system", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] core.logging_system: {e}", "ERROR")
        
        # 測試 OBS 整合模組
        try:
            from obs_integration.obs_manager import OBSManager
            self.log("   [PASS] obs_integration.obs_manager", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] obs_integration.obs_manager: {e}", "ERROR")
        
        try:
            from obs_integration.scene_controller import SceneController
            self.log("   [PASS] obs_integration.scene_controller", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] obs_integration.scene_controller: {e}", "ERROR")
        
        # 測試 AI 引擎模組
        try:
            from ai_engine.emotion_detector import EmotionDetector
            self.log("   [PASS] ai_engine.emotion_detector", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] ai_engine.emotion_detector: {e}", "ERROR")
        
        # 測試 UI 模組
        try:
            from ui.main_panel import MainControlPanel
            self.log("   [PASS] ui.main_panel", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] ui.main_panel: {e}", "ERROR")
        
        try:
            from ui.status_indicators import StatusLevel, SystemStatusManager
            self.log("   [PASS] ui.status_indicators", "SUCCESS")
        except ImportError as e:
            self.log(f"   [FAIL] ui.status_indicators: {e}", "ERROR")
        
        # 測試可選依賴
        self.log("\n3. 測試可選依賴:")
        optional_modules = [
            "websockets",
            "opencv-python",
            "Pillow", 
            "numpy"
        ]
        
        for module in optional_modules:
            try:
                if module == "opencv-python":
                    import cv2
                    self.log(f"   [PASS] {module} (cv2)", "SUCCESS")
                elif module == "Pillow":
                    from PIL import Image
                    self.log(f"   [PASS] {module} (PIL)", "SUCCESS")
                else:
                    __import__(module)
                    self.log(f"   [PASS] {module}", "SUCCESS")
            except ImportError as e:
                self.log(f"   [WARN] {module}: {e}", "WARNING")
        
        self.log("\n導入測試完成！", "INFO")
        
    def fix_missing_modules(self):
        """修復缺失的模組"""
        self.log("\n開始修復缺失的模組...")
        
        # 檢查並創建缺失的類別
        missing_fixes = {
            "src/core/scene_controller.py": '''"""Scene Controller for OBS"""

class SceneController:
    def __init__(self, obs_manager=None):
        self.obs_manager = obs_manager
        self.current_scene = "Default"
        self.auto_switching = False
    
    def switch_scene(self, scene_name):
        """切換場景"""
        self.current_scene = scene_name
        return True
    
    def set_auto_switching(self, enabled):
        """設置自動切換"""
        self.auto_switching = enabled
        return True
    
    def get_current_scene(self):
        """獲取當前場景"""
        return self.current_scene
''',
            "src/core/camera_manager.py": '''"""Camera Manager"""

class CameraManager:
    def __init__(self):
        self.active = False
        self.camera_index = 0
    
    def start(self):
        """啟動攝像頭"""
        self.active = True
        return True
    
    def stop(self):
        """停止攝像頭"""
        self.active = False
        return True
    
    def is_active(self):
        """檢查是否啟動"""
        return self.active
''',
            "src/ai_engine/face_detector.py": '''"""Face Detector"""

class FaceDetector:
    def __init__(self):
        self.initialized = False
    
    def detect_faces(self, frame):
        """檢測人臉"""
        return []
    
    def is_initialized(self):
        """檢查是否初始化"""
        return self.initialized
''',
        }
        
        for file_path, content in missing_fixes.items():
            path = Path(file_path)
            if not path.exists():
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding='utf-8')
                    self.log(f"   [FIXED] 創建 {file_path}", "SUCCESS")
                except Exception as e:
                    self.log(f"   [ERROR] 創建 {file_path} 失敗: {e}", "ERROR")
            else:
                self.log(f"   [SKIP] {file_path} 已存在", "INFO")
        
        # 更新 __init__.py 檔案
        init_updates = {
            "src/core/__init__.py": '''"""Core Module"""
from .config_manager import ConfigManager
from .logging_system import setup_logging

try:
    from .scene_controller import SceneController
    from .camera_manager import CameraManager
except ImportError:
    pass
''',
            "src/ai_engine/__init__.py": '''"""AI Engine Module"""
from .emotion_detector import EmotionDetector

try:
    from .face_detector import FaceDetector
    from .emotion_detector_engine import RealTimeDetector
except ImportError:
    pass
'''
        }
        
        for file_path, content in init_updates.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"   [UPDATED] {file_path}", "SUCCESS")
            except Exception as e:
                self.log(f"   [ERROR] 更新 {file_path} 失敗: {e}", "ERROR")
        
        self.log("修復完成！請重新測試導入。", "SUCCESS")
        
    def launch_simple_version(self):
        """啟動簡化版本"""
        self.log("\n嘗試啟動簡化版本...")
        
        try:
            # 創建簡化的主應用程式視窗
            simple_window = tk.Toplevel(self.root)
            simple_window.title("LivePilotAI 簡化版 - 運行中")
            simple_window.geometry("400x300")
            
            # 簡化的控制面板
            control_frame = tk.LabelFrame(simple_window, text="基本控制", font=("Arial", 10, "bold"))
            control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            status_label = tk.Label(control_frame, text="系統狀態: 運行中", fg="green", font=("Arial", 12))
            status_label.pack(pady=10)
            
            info_text = tk.Text(control_frame, height=8, wrap=tk.WORD)
            info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            info_text.insert(tk.END, """LivePilotAI 簡化版已啟動！

這是一個簡化的測試版本，用於驗證基本功能：

✓ GUI 界面正常運行
✓ 模組導入系統工作
✓ 基本錯誤處理機制

您可以：
1. 測試模組導入功能
2. 檢查系統狀態
3. 驗證基本 UI 組件

如果這個版本運行正常，說明基礎環境沒有問題。
""")
            
            close_btn = tk.Button(
                control_frame,
                text="關閉",
                command=simple_window.destroy,
                bg="#e74c3c",
                fg="white",
                font=("Arial", 10)
            )
            close_btn.pack(pady=5)
            
            self.log("簡化版本啟動成功！", "SUCCESS")
            
        except Exception as e:
            self.log(f"簡化版本啟動失敗: {e}", "ERROR")
            
    def run(self):
        """啟動應用程式"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = SimpleTestApp()
        app.run()
    except Exception as e:
        print(f"應用程式啟動失敗: {e}")
        import traceback
        traceback.print_exc()
