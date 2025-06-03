#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 修復版圖形化啟動器 (無 Unicode 問題)
Fixed Graphical Launcher for LivePilotAI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
from pathlib import Path

class LivePilotAILauncherFixed:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LivePilotAI 啟動器")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """設置用戶界面"""
        # 標題
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="LivePilotAI",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            title_frame,
            text="智能直播導播系統",
            font=("Arial", 10),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        subtitle_label.pack()
        
        # 主要內容區域
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 狀態顯示
        self.status_var = tk.StringVar(value="準備就緒")
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            fg="#27ae60",
            bg="white"
        )
        status_label.pack(pady=(0, 20))
        
        # 按鈕區域
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X)
        
        # 主應用程式按鈕
        self.main_btn = tk.Button(
            button_frame,
            text="啟動主應用程式",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.launch_main_app
        )
        self.main_btn.pack(fill=tk.X, pady=5)
        
        # 測試按鈕
        self.test_btn = tk.Button(
            button_frame,
            text="執行系統測試",
            font=("Arial", 12),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.run_tests
        )
        self.test_btn.pack(fill=tk.X, pady=5)
        
        # OBS 測試按鈕
        self.obs_btn = tk.Button(
            button_frame,
            text="測試 OBS 整合",
            font=("Arial", 12),
            bg="#e67e22",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.test_obs
        )
        self.obs_btn.pack(fill=tk.X, pady=5)
        
        # 分隔線
        separator = ttk.Separator(button_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)
        
        # 實用工具按鈕
        utils_frame = tk.Frame(button_frame, bg="white")
        utils_frame.pack(fill=tk.X)
        
        help_btn = tk.Button(
            utils_frame,
            text="使用說明",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        exit_btn = tk.Button(
            utils_frame,
            text="退出",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.root.quit
        )
        exit_btn.pack(side=tk.RIGHT)
        
        # 日誌區域
        log_frame = tk.LabelFrame(main_frame, text="執行日誌", bg="white")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 9),
            bg="#f8f9fa",
            wrap=tk.WORD
        )
        scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 歡迎消息
        self.log("歡迎使用 LivePilotAI 智能直播導播系統！")
        self.log("請選擇要執行的操作...")
        
    def log(self, message):
        """添加日誌消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def set_status(self, status):
        """設置狀態"""
        self.status_var.set(status)
        
    def disable_buttons(self):
        """禁用所有按鈕"""
        for btn in [self.main_btn, self.test_btn, self.obs_btn]:
            btn.config(state=tk.DISABLED)
            
    def enable_buttons(self):
        """啟用所有按鈕"""
        for btn in [self.main_btn, self.test_btn, self.obs_btn]:
            btn.config(state=tk.NORMAL)
            
    def run_command_async(self, command, description):
        """異步執行命令"""
        def run():
            self.disable_buttons()
            self.set_status(f"正在{description}...")
            self.log(f"開始{description}...")
            
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=Path.cwd()
                )
                
                if result.returncode == 0:
                    self.log(f"{description}成功！")
                    if result.stdout:
                        self.log(f"輸出: {result.stdout.strip()}")
                    self.set_status("執行成功")
                else:
                    self.log(f"{description}失敗")
                    if result.stderr:
                        self.log(f"錯誤: {result.stderr.strip()}")
                    if result.stdout:
                        self.log(f"輸出: {result.stdout.strip()}")
                    self.set_status("執行失敗")
                    
            except subprocess.TimeoutExpired:
                self.log(f"{description}超時")
                self.set_status("執行超時")
            except FileNotFoundError:
                self.log(f"找不到檔案或命令")
                self.set_status("檔案未找到")
            except Exception as e:
                self.log(f"執行錯誤: {str(e)}")
                self.set_status("執行錯誤")
            finally:
                self.enable_buttons()
                
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        
    def launch_main_app(self):
        """啟動主應用程式"""
        # 嘗試使用修復版的啟動器
        if Path("main_fixed.py").exists():
            command = [sys.executable, "main_fixed.py", "--app"]
        elif Path("main_day5.py").exists():
            command = [sys.executable, "main_day5.py"]
        else:
            self.log("錯誤: 找不到主應用程式檔案")
            return
            
        self.run_command_async(command, "啟動主應用程式")
        
    def run_tests(self):
        """執行系統測試"""
        if Path("main_fixed.py").exists():
            command = [sys.executable, "main_fixed.py", "--test"]
        else:
            # 備用測試方案
            test_files = ["basic_test.py", "simple_test.py", "day5_simple_test.py"]
            for test_file in test_files:
                if Path(test_file).exists():
                    command = [sys.executable, test_file]
                    break
            else:
                self.log("錯誤: 找不到測試檔案")
                return
                
        self.run_command_async(command, "執行系統測試")
        
    def test_obs(self):
        """測試 OBS 整合"""
        if Path("main_fixed.py").exists():
            command = [sys.executable, "main_fixed.py", "--obs-test"]
        elif Path("obs_test_simple.py").exists():
            command = [sys.executable, "obs_test_simple.py"]
        else:
            self.log("錯誤: 找不到 OBS 測試檔案")
            return
            
        self.run_command_async(command, "測試 OBS 整合")
        
    def show_help(self):
        """顯示幫助信息"""
        help_text = """
LivePilotAI 智能直播導播系統

啟動主應用程式: 啟動完整的 AI 導播系統
執行系統測試: 檢查所有系統組件
測試 OBS 整合: 測試與 OBS Studio 的連接

使用前請確保:
1. 已安裝 Python 3.8+
2. 已安裝所有依賴包
3. OBS Studio 已安裝（如需要）

更多信息請查看文檔。
        """
        messagebox.showinfo("使用說明", help_text)
            
    def run(self):
        """運行啟動器"""
        self.root.mainloop()

if __name__ == "__main__":
    launcher = LivePilotAILauncherFixed()
    launcher.run()
