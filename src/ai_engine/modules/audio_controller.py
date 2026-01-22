# -*- coding: utf-8 -*-
"""
LivePilotAI 語音指令識別模組 (Keyword Spotting)
使用 SpeechRecognition 進行語音轉文字並識別特定指令
"""

import speech_recognition as sr
import threading
import time
import logging
from typing import Callable, Optional, Dict

logger = logging.getLogger(__name__)

class AudioController:
    """
    音訊控制器
    負責監聽麥克風並觸發語音指令
    """
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.callback = callback
        
        # 指令映射表 (關鍵字 -> 動作代碼)
        self.commands = {
            "剪輯": "clip",
            "精彩": "clip", 
            "clip": "clip",
            "暫離": "brb",
            "休息": "brb",
            "brb": "brb",
            "開始": "start",
            "start": "start",
            "停止": "stop",
            "stop": "stop"
        }
        
        # 背景聽寫執行緒
        self.listen_thread = None
        self.stop_listening_event = threading.Event()

    def initialize(self) -> bool:
        """初始化麥克風"""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                # 自動調整環境噪音基準
                logger.info("正在調整環境噪音基準，請安靜...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("音訊系統初始化完成")
            return True
        except Exception as e:
            logger.error(f"音訊系統初始化失敗 (可能無麥克風): {e}")
            return False

    def start_listening(self):
        """開始背景監聽"""
        if self.is_listening or not self.microphone:
            return

        self.is_listening = True
        self.stop_listening_event.clear()
        
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("開始語音監聽...")

    def stop_listening(self):
        """停止監聽"""
        if not self.is_listening:
            return
            
        self.is_listening = False
        self.stop_listening_event.set()
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        logger.info("停止語音監聽")

    def _listen_loop(self):
        """監聽迴圈"""
        while self.is_listening and not self.stop_listening_event.is_set():
            try:
                with self.microphone as source:
                    # 設定較短的 timeout 以便能回應停止訊號
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    except sr.WaitTimeoutError:
                        continue
                    
                    try:
                        # 嘗試識別 (使用 Google Web Speech API，需聯網但最簡單)
                        # 若要離線可用 Sphinx (需安裝 pocketsphinx)
                        text = self.recognizer.recognize_google(audio, language="zh-TW")
                        logger.debug(f"聽到: {text}")
                        
                        self._process_command(text)
                        
                    except sr.UnknownValueError:
                        # 無法辨識 (噪音)
                        pass
                    except sr.RequestError as e:
                        logger.error(f"語音識別服務錯誤: {e}")
                        
            except Exception as e:
                logger.error(f"監聽迴圈錯誤: {e}")
                time.sleep(1)

    def _process_command(self, text: str):
        """處理識別出的文字"""
        text = text.lower()
        for keyword, cmd in self.commands.items():
            if keyword in text:
                logger.info(f"觸發語音指令: {cmd} (關鍵字: {keyword})")
                if self.callback:
                    self.callback(cmd)
                return

