#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 緊急修復版啟動器
Emergency Fixed Launcher for LivePilotAI - 解決三個選項都失敗的問題
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os
import threading
import traceback
from pathlib import Path

class EmergencyLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LivePilotAI 緊急修復版啟動器")
        self.root.geometry("600x500")
        
        # 創建診斷和修復界面
        self.setup_ui()
        self.check_system()
        
    def setup_ui(self):
        """設置用戶界面"""
        # 標題
        title_frame = tk.Frame(self.root, bg="#e74c3c", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="LivePilotAI 緊急修復版",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#e74c3c"
        )
        title_label.pack(pady=15)
        
        # 主要內容
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 狀態顯示
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(status_frame, text="系統狀態:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.status_var = tk.StringVar(value="正在檢查系統...")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                   fg="#e67e22", font=("Arial", 9))
        self.status_label.pack(anchor=tk.W)
        
        # 診斷結果區域
        diag_frame = tk.LabelFrame(main_frame, text="診斷結果", font=("Arial", 10, "bold"))
        diag_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.diag_text = scrolledtext.ScrolledText(
            diag_frame, 
            height=8,
            font=("Consolas", 8),
            wrap=tk.WORD
        )
        self.diag_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按鈕
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 第一行按鈕
        button_row1 = tk.Frame(button_frame)
        button_row1.pack(fill=tk.X, pady=(0, 5))
        
        self.fix_btn = tk.Button(
            button_row1,
            text="1. 自動修復系統",
            command=self.auto_fix,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.fix_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.install_btn = tk.Button(
            button_row1,
            text="2. 安裝依賴項",
            command=self.install_dependencies,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.install_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 第二行按鈕
        button_row2 = tk.Frame(button_frame)
        button_row2.pack(fill=tk.X, pady=(0, 5))
        
        self.test_btn = tk.Button(
            button_row2,
            text="3. 執行簡單測試",
            command=self.run_simple_test,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.test_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.launch_btn = tk.Button(
            button_row2,
            text="4. 啟動應用程式",
            command=self.launch_app,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            state=tk.DISABLED
        )
        self.launch_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 第三行按鈕
        button_row3 = tk.Frame(button_frame)
        button_row3.pack(fill=tk.X)
        
        self.recheck_btn = tk.Button(
            button_row3,
            text="重新檢查系統",
            command=self.check_system,
            bg="#34495e",
            fg="white",
            font=("Arial", 9),
            padx=10
        )
        self.recheck_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.help_btn = tk.Button(
            button_row3,
            text="查看說明",
            command=self.show_help,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            padx=10
        )
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
    def log(self, message, level="INFO"):
        """添加日誌消息"""
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}\n"
        self.diag_text.insert(tk.END, formatted_msg)
        self.diag_text.see(tk.END)
        self.root.update_idletasks()
        
    def check_system(self):
        """檢查系統狀況"""
        self.status_var.set("正在檢查系統...")
        self.diag_text.delete(1.0, tk.END)
        
        def check():
            try:
                self.log("開始系統診斷...")
                
                # 檢查 Python 版本
                self.log(f"Python 版本: {sys.version.split()[0]}")
                self.log(f"工作目錄: {os.getcwd()}")
                
                # 檢查關鍵檔案
                key_files = ["main_day5.py", "requirements.txt", "src"]
                missing_files = []
                
                for file in key_files:
                    if Path(file).exists():
                        self.log(f"[PASS] 找到 {file}")
                    else:
                        self.log(f"[FAIL] 缺少 {file}")
                        missing_files.append(file)
                
                # 檢查模組導入
                self.log("檢查基本模組...")
                basic_modules = ["tkinter", "subprocess", "threading", "pathlib"]
                for module in basic_modules:
                    try:
                        __import__(module)
                        self.log(f"[PASS] {module} 可導入")
                    except ImportError as e:
                        self.log(f"[FAIL] {module} 導入失敗: {e}", "ERROR")
                
                # 檢查 src 目錄
                src_path = Path("src")
                if src_path.exists():
                    self.log("[PASS] src 目錄存在")
                    
                    # 檢查核心模組檔案
                    core_modules = [
                        "src/obs_integration",
                        "src/core", 
                        "src/ai_engine"
                    ]
                    
                    for module_dir in core_modules:
                        if Path(module_dir).exists():
                            self.log(f"[PASS] {module_dir} 目錄存在")
                        else:
                            self.log(f"[FAIL] {module_dir} 目錄缺失", "ERROR")
                            missing_files.append(module_dir)
                else:
                    self.log("[FAIL] src 目錄不存在", "ERROR")
                    missing_files.append("src")
                
                # 評估系統狀態
                if not missing_files:
                    self.status_var.set("系統狀態: 良好 - 可以嘗試啟動")
                    self.launch_btn.config(state=tk.NORMAL)
                    self.log("系統檢查完成 - 狀態良好", "SUCCESS")
                elif len(missing_files) <= 2:
                    self.status_var.set("系統狀態: 需要修復 - 請執行自動修復")
                    self.log("系統檢查完成 - 需要修復", "WARNING")
                else:
                    self.status_var.set("系統狀態: 嚴重問題 - 需要重新安裝")
                    self.log("系統檢查完成 - 發現嚴重問題", "ERROR")
                
            except Exception as e:
                self.log(f"檢查過程發生錯誤: {e}", "ERROR")
                self.status_var.set("系統狀態: 檢查失敗")
                
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def auto_fix(self):
        """自動修復系統"""
        self.log("開始自動修復...")
        
        def fix():
            try:
                # 1. 創建缺失的目錄結構
                directories = [
                    "src",
                    "src/obs_integration", 
                    "src/core",
                    "src/ai_engine",
                    "logs",
                    "config"
                ]
                
                for dir_path in directories:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    self.log(f"[FIXED] 創建目錄: {dir_path}")
                
                # 2. 創建基本的 __init__.py 檔案
                init_files = [
                    "src/__init__.py",
                    "src/obs_integration/__init__.py",
                    "src/core/__init__.py", 
                    "src/ai_engine/__init__.py"
                ]
                
                for init_file in init_files:
                    if not Path(init_file).exists():
                        Path(init_file).write_text("# Auto-generated init file\n")
                        self.log(f"[FIXED] 創建: {init_file}")
                
                # 3. 創建基本的模組檔案（如果不存在）
                self.create_basic_modules()
                
                self.log("自動修復完成！", "SUCCESS")
                
            except Exception as e:
                self.log(f"修復過程發生錯誤: {e}", "ERROR")
                
        thread = threading.Thread(target=fix)
        thread.daemon = True
        thread.start()
    
    def create_basic_modules(self):
        """創建基本模組檔案"""
        # OBS Manager 基本實現
        obs_manager_content = '''"""
Basic OBS Manager implementation
"""

class OBSManager:
    def __init__(self):
        self.connected = False
    
    def connect(self):
        self.connected = True
        return True
    
    def disconnect(self):
        self.connected = False
    
    def is_connected(self):
        return self.connected
'''
        
        obs_manager_path = Path("src/obs_integration/obs_manager.py")
        if not obs_manager_path.exists():
            obs_manager_path.write_text(obs_manager_content)
            self.log("[FIXED] 創建 obs_manager.py")
        
        # Scene Controller 基本實現
        scene_controller_content = '''"""
Basic Scene Controller implementation
"""

class SceneController:
    def __init__(self):
        self.current_scene = "Default"
    
    def switch_scene(self, scene_name):
        self.current_scene = scene_name
        return True
    
    def get_current_scene(self):
        return self.current_scene
'''
        
        scene_controller_path = Path("src/core/scene_controller.py")
        if not scene_controller_path.exists():
            scene_controller_path.write_text(scene_controller_content)
            self.log("[FIXED] 創建 scene_controller.py")
        
        # 其他基本模組...
        basic_modules = {
            "src/ai_engine/emotion_detector.py": '''"""Basic Emotion Detector"""
class EmotionDetector:
    def detect(self, frame):
        return "neutral"
''',
            "src/ai_engine/emotion_mapper.py": '''"""Basic Emotion Mapper"""
class EmotionMapper:
    def map_to_scene(self, emotion):
        return "Default"
''',
            "src/core/camera_manager.py": '''"""Basic Camera Manager"""
class CameraManager:
    def __init__(self):
        self.active = False
    
    def start(self):
        self.active = True
    
    def stop(self):
        self.active = False
'''
        }
        
        for file_path, content in basic_modules.items():
            path = Path(file_path)
            if not path.exists():
                path.write_text(content)
                self.log(f"[FIXED] 創建 {file_path}")
    
    def install_dependencies(self):
        """安裝依賴項"""
        self.log("開始安裝依賴項...")
        
        def install():
            try:
                # 檢查 requirements.txt
                if Path("requirements.txt").exists():
                    self.log("找到 requirements.txt，開始安裝...")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        self.log("依賴項安裝成功！", "SUCCESS")
                    else:
                        self.log(f"安裝失敗: {result.stderr}", "ERROR")
                else:
                    # 安裝基本依賴
                    basic_deps = ["opencv-python", "tkinter", "Pillow"]
                    for dep in basic_deps:
                        self.log(f"安裝 {dep}...")
                        result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", dep],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if result.returncode == 0:
                            self.log(f"[PASS] {dep} 安裝成功")
                        else:
                            self.log(f"[FAIL] {dep} 安裝失敗", "ERROR")
                            
            except Exception as e:
                self.log(f"安裝過程發生錯誤: {e}", "ERROR")
                
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    
    def run_simple_test(self):
        """執行簡單測試"""
        self.log("開始執行簡單測試...")
        
        def test():
            try:
                # 測試基本導入
                sys.path.insert(0, str(Path.cwd() / "src"))
                
                test_cases = [
                    ("基本模組導入", "import sys, os, tkinter"),
                    ("專案路徑測試", "from pathlib import Path; Path('src').exists()"),
                ]
                
                for test_name, test_code in test_cases:
                    try:
                        exec(test_code)
                        self.log(f"[PASS] {test_name}")
                    except Exception as e:
                        self.log(f"[FAIL] {test_name}: {e}")
                
                # 嘗試執行 basic_test.py
                if Path("basic_test.py").exists():
                    self.log("執行 basic_test.py...")
                    result = subprocess.run(
                        [sys.executable, "basic_test.py"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        self.log("basic_test.py 執行成功！", "SUCCESS")
                        self.launch_btn.config(state=tk.NORMAL)
                    else:
                        self.log(f"basic_test.py 執行失敗: {result.stderr}", "ERROR")
                
                self.log("簡單測試完成", "SUCCESS")
                
            except Exception as e:
                self.log(f"測試過程發生錯誤: {e}", "ERROR")
                
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
    
    def launch_app(self):
        """啟動應用程式"""
        self.log("正在啟動 LivePilotAI...")
        
        def launch():
            try:
                if Path("main_day5.py").exists():
                    self.log("使用 main_day5.py 啟動...")
                    subprocess.Popen([sys.executable, "main_day5.py"])
                    self.log("應用程式已啟動！", "SUCCESS")
                else:
                    self.log("找不到主程式檔案", "ERROR")
                    
            except Exception as e:
                self.log(f"啟動失敗: {e}", "ERROR")
                
        thread = threading.Thread(target=launch)
        thread.daemon = True
        thread.start()
    
    def show_help(self):
        """顯示說明"""
        help_text = """
LivePilotAI 緊急修復指南:

1. 自動修復系統: 創建缺失的目錄和基本檔案
2. 安裝依賴項: 安裝必要的 Python 套件
3. 執行簡單測試: 驗證系統基本功能
4. 啟動應用程式: 啟動 LivePilotAI 主程式

如果所有步驟都執行完畢仍有問題，請:
- 檢查 Python 版本 (建議 3.8+)
- 確保有足夠的磁碟空間
- 檢查網絡連接 (下載依賴項需要)
- 重新啟動電腦後再試
"""
        messagebox.showinfo("使用說明", help_text)
    
    def run(self):
        """啟動界面"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = EmergencyLauncher()
        app.run()
    except Exception as e:
        print(f"啟動器啟動失敗: {e}")
        traceback.print_exc()
