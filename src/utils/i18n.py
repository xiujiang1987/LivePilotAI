"""
LivePilotAI Localization Module
Provides multi-language support (Traditional Chinese and English)
"""

import json
import os
from typing import Dict, Any

class LocalizationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.current_language = "zh_TW"  # Default to Traditional Chinese
        self.translations = {
            "zh_TW": {
                # General
                "app_title": "LivePilotAI - 智能導播助手",
                "ready": "就緒",
                "error": "錯誤",
                "warning": "警告",
                "info": "資訊",
                "confirm": "確認",
                "cancel": "取消",
                "save": "儲存",
                "load": "載入",
                "export": "匯出資料",
                "close": "關閉",
                "apply": "套用",
                "reset": "重置",
                "browse": "瀏覽",
                
                # Main Panel
                "camera_control": "攝影機控制",
                "camera": "攝影機",
                "start_camera": "啟動攝影機",
                "stop_camera": "停止攝影機",
                "obs_control": "OBS 控制",
                "connect_obs": "連接 OBS",
                "disconnect_obs": "斷開 OBS",
                "obs_status": "OBS 狀態",
                "connected": "已連接",
                "disconnected": "未連接",
                "auto_switch": "自動切換場景",
                "enable_auto": "啟用自動切換",
                "disable_auto": "停用自動切換",
                "current_emotion": "當前情緒",
                "confidence": "置信度",
                "fps": "FPS",
                "preview": "預覽",
                "settings": "設定",
                "logs": "日誌",
                "history": "歷史記錄",
                "clear_history": "清除歷史",
                "performance": "效能",
                "obs_scene_manager": "OBS 場景管理器",
                "emotion_mapper": "情緒映射設定",
                "about": "關於",
                "camera_warning": "攝影機警告",
                "select_camera_msg": "請選擇攝影機裝置",
                "start_camera_error": "無法啟動攝影機",
                "no_video_feed": "無視訊訊號",
                "device": "裝置",
                "current_scene": "當前場景",
                "no_scene": "無場景",
                "full_window": "全螢幕",
                "snapshot": "快照",
                "emotions": "情緒",
                
                # Status Panels
                "status_obs_studio": "OBS Studio",
                "status_ai_engine": "AI 引擎",
                "status_system_resources": "系統資源",
                "component": "組件",
                "status": "狀態",
                "message": "訊息",
                "updated": "更新於",
                "details": "詳細資訊",
                
                # Help
                "help": "說明",
                "obs_guide": "OBS 連接指南",
                "obs_guide_content": "OBS 連接步驟：\n\n1. 開啟 OBS Studio\n2. 點選上方選單「工具」->「WebSocket 伺服器設定」\n3. 勾選「啟用 WebSocket 伺服器」\n4. 記下「伺服器連接埠」(預設 4455) 與「伺服器密碼」\n5. 回到本程式，點選「設定」->「OBS 設定」\n6. 輸入對應的連接埠與密碼\n7. 點選「儲存」並嘗試連接",
                "auto_switch_warning_title": "自動切換",
                "auto_switch_warning_msg": "請先連接 OBS",

                # Settings Dialog
                "settings_title": "系統設定",
                "general_settings": "一般設定",
                "language": "語言",
                "theme": "主題",
                "obs_settings": "OBS 設定",
                "host": "主機",
                "port": "連接埠",
                "password": "密碼",
                "auto_connect": "自動連接",
                "emotion_settings": "情緒偵測設定",
                "confidence_threshold": "置信度閾值",
                "update_interval": "更新間隔 (ms)",
                "smoothing": "平滑係數",
                "ui_settings": "介面設定",
                "show_confidence": "顯示置信度",
                "show_fps": "顯示 FPS",
                "emotion_colors": "情緒顏色",
                
                # Settings Dialog Tabs & Groups
                "tab_obs": "OBS 連接",
                "tab_emotion": "情緒偵測",
                "tab_scene": "場景切換",
                "tab_ui": "介面偏好",
                "tab_perf": "效能設定",
                "group_connection": "連接設定",
                "group_advanced": "進階設定",
                "group_detection": "偵測參數",
                "group_auto_switch": "自動切換",
                "group_appearance": "外觀設定",
                "group_resources": "資源限制",
                "group_optimization": "最佳化",
                
                # Settings Labels
                "reconnect_interval": "重連間隔 (秒)",
                "timeout": "逾時 (秒)",
                "min_face_size": "最小人臉尺寸 (px)",
                "max_faces": "最大人臉數",
                "switch_cooldown": "切換冷卻 (秒)",
                "transition_duration": "轉場時間 (ms)",
                "confidence_req": "所需置信度",
                "sustained_duration": "持續時間 (秒)",
                "memory_limit": "記憶體限制 (MB)",
                "cache_size": "快取大小",
                "max_cpu": "最大 CPU 使用率 (%)",
                "gpu_accel": "GPU 加速 (若可用)",
                "multithreading": "多執行緒",
                "load_profile": "載入設定檔",
                "save_profile": "儲存設定檔",
                "reset_defaults": "重置為預設值",
                "test_connection": "測試連接",
                "test_success": "OBS 連接成功！",
                "test_fail": "無法連接至 OBS。",
                "test_error": "連接錯誤：",
                "profile_loaded": "設定檔載入成功！",
                "profile_saved": "設定檔儲存成功！",
                "reset_confirm": "確定要將所有設定重置為預設值嗎？",
                
                # Emotions
                "happy": "快樂",
                "sad": "悲傷",
                "angry": "憤怒",
                "fear": "恐懼",
                "surprise": "驚訝",
                "disgust": "厭惡",
                "neutral": "中性",
                "focused": "專注",
                "excited": "興奮",
                "relaxed": "放鬆",
                
                # Messages
                "obs_connect_success": "OBS 連接成功",
                "obs_connect_fail": "OBS 連接失敗",
                "obs_error": "OBS 錯誤",
                "obs_connect_error_msg": "無法連接至 OBS",
                "camera_error": "攝影機錯誤",
                "save_success": "設定已儲存",
                "language_changed": "語言已變更",
                "restart_required": "部分設定需要重啟應用程式才能生效",
                
                # Preview Window
                "preview_title": "LivePilotAI - 實時預覽",
                "display_options": "顯示選項",
                "show_overlays": "顯示情緒疊加",
                "show_faces": "顯示人臉框",
                "show_confidence_bars": "顯示置信度條",
                "show_fps_counter": "顯示 FPS 計數",
                "show_timestamp": "顯示時間戳",
                "window_options": "視窗選項",
                "toggle_fullscreen": "切換全螢幕",
                "take_screenshot": "截圖",
                "reset_view": "重置視圖",
                "close_preview": "關閉預覽",
                
                # Status Indicators
                "initializing": "初始化中...",
                "system_status": "系統狀態",
                "components_count": "({total} 個組件, {online} 上線)",
                "components_error": "({total} 個組件, {error} 錯誤)",
                "components_all_online": "({total} 個組件, 全部上線)"
            },
            "en_US": {
                # General
                "app_title": "LivePilotAI - Intelligent Director Assistant",
                "ready": "Ready",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "save": "Save",
                "close": "Close",
                "apply": "Apply",
                "reset": "Reset",
                "browse": "Browse",
                
                # Main Panel
                "camera_control": "Camera Control",
                "camera": "Camera",
                "start_camera": "Start Camera",
                "stop_camera": "Stop Camera",
                "obs_control": "OBS Control",
                "connect_obs": "Connect OBS",
                "disconnect_obs": "Disconnect OBS",
                "obs_status": "OBS Status",
                "connected": "Connected",
                "disconnected": "Disconnected",
                "auto_switch": "Auto Scene Switch",
                "enable_auto": "Enable Auto Switch",
                "disable_auto": "Disable Auto Switch",
                "current_emotion": "Current Emotion",
                "confidence": "Confidence",
                "fps": "FPS",
                "preview": "Preview",
                "settings": "Settings",
                "logs": "Logs",
                "history": "History",
                "clear_history": "Clear History",
                "performance": "Performance",
                "camera_warning": "Camera Warning",
                "select_camera_msg": "Please select a camera device",
                "start_camera_error": "Failed to start camera",
                "no_video_feed": "No Video Feed",
                "device": "Device",
                "current_scene": "Current Scene",
                "no_scene": "No Scene",
                "full_window": "Full Window",
                "snapshot": "Snapshot",
                "emotions": "Emotions",
                
                # Status Panels
                "status_obs_studio": "OBS Studio",
                "status_ai_engine": "AI Engine",
                "status_system_resources": "System Resources",
                "component": "Component",
                "status": "Status",
                "message": "Message",
                "updated": "Updated",
                "details": "Details",

                # Help
                "help": "Help",
                "obs_guide": "OBS Connection Guide",
                "obs_guide_content": "OBS Connection Steps:\n\n1. Open OBS Studio\n2. Go to Tools -> WebSocket Server Settings\n3. Enable WebSocket Server\n4. Note the Server Port (default 4455) and Password\n5. In LivePilotAI, go to Settings -> OBS Settings\n6. Enter the Port and Password\n7. Click Save and try to connect",
                "auto_switch_warning_title": "Auto Switch",
                "auto_switch_warning_msg": "Please connect to OBS first",
                
                # Settings Dialog
                "settings_title": "System Settings",
                "general_settings": "General Settings",
                "language": "Language",
                "theme": "Theme",
                "obs_settings": "OBS Settings",
                "host": "Host",
                "port": "Port",
                "password": "Password",
                "auto_connect": "Auto Connect",
                "emotion_settings": "Emotion Detection",
                "confidence_threshold": "Confidence Threshold",
                "update_interval": "Update Interval (ms)",
                "smoothing": "Smoothing Factor",
                "ui_settings": "Interface Settings",
                "show_confidence": "Show Confidence",
                "show_fps": "Show FPS",
                "emotion_colors": "Emotion Colors",
                
                # Settings Dialog Tabs & Groups
                "tab_obs": "OBS Connection",
                "tab_emotion": "Emotion Detection",
                "tab_scene": "Scene Switching",
                "tab_ui": "UI Preferences",
                "tab_perf": "Performance",
                "group_connection": "Connection Settings",
                "group_advanced": "Advanced Settings",
                "group_detection": "Detection Parameters",
                "group_auto_switch": "Auto-Switching",
                "group_appearance": "Appearance",
                "group_resources": "Resource Limits",
                "group_optimization": "Optimizations",
                
                # Settings Labels
                "reconnect_interval": "Reconnect Interval (s)",
                "timeout": "Timeout (s)",
                "min_face_size": "Min Face Size (px)",
                "max_faces": "Max Faces",
                "switch_cooldown": "Switch Cooldown (s)",
                "transition_duration": "Transition Duration (ms)",
                "confidence_req": "Confidence Required",
                "sustained_duration": "Sustained Duration (s)",
                "memory_limit": "Memory Limit (MB)",
                "cache_size": "Cache Size",
                "max_cpu": "Max CPU Usage (%)",
                "gpu_accel": "GPU Acceleration (if available)",
                "multithreading": "Multi-threading",
                "load_profile": "Load Profile",
                "save_profile": "Save Profile",
                "reset_defaults": "Reset to Defaults",
                "test_connection": "Test Connection",
                "test_success": "OBS connection successful!",
                "test_fail": "Failed to connect to OBS.",
                "test_error": "Connection error: ",
                "profile_loaded": "Settings profile loaded successfully!",
                "profile_saved": "Settings profile saved successfully!",
                "reset_confirm": "Are you sure you want to reset all settings to defaults?",
                
                # Preview Window
                "preview_title": "LivePilotAI - Live Preview",
                "display_options": "Display Options",
                "show_overlays": "Show Emotion Overlays",
                "show_faces": "Show Face Boxes",
                "show_confidence_bars": "Show Confidence Bars",
                "show_fps_counter": "Show FPS Counter",
                "show_timestamp": "Show Timestamp",
                "window_options": "Window Options",
                "toggle_fullscreen": "Toggle Fullscreen",
                "take_screenshot": "Take Screenshot",
                "reset_view": "Reset View",
                "close_preview": "Close Preview",
                
                # Status Indicators
                "initializing": "Initializing...",
                "system_status": "System Status",
                "component": "Component",
                "status": "Status",
                "message": "Message",
                "updated": "Last Updated",
                "details": "Details",
                "components_count": "({total} components, {online} online)",
                "components_error": "({total} components, {error} errors)",
                "components_all_online": "({total} components, all online)",
                
                # Emotions
                "happy": "Happy",
                "sad": "Sad",
                "angry": "Angry",
                "fear": "Fear",
                "surprise": "Surprise",
                "disgust": "Disgust",
                "neutral": "Neutral",
                "focused": "Focused",
                "excited": "Excited",
                "relaxed": "Relaxed",
                
                # Messages
                "obs_connect_success": "OBS Connected Successfully",
                "obs_connect_fail": "OBS Connection Failed",
                "obs_error": "OBS Error",
                "obs_connect_error_msg": "Failed to connect to OBS",
                "camera_error": "Camera Error",
                "save_success": "Settings Saved",
                "language_changed": "Language Changed",
                "restart_required": "Some settings require restart to take effect"
            }
        }
        self._initialized = True
    
    def set_language(self, lang_code: str):
        """Set current language"""
        if lang_code in self.translations:
            if self.current_language != lang_code:
                self.current_language = lang_code
                return True
        return False
    
    def get(self, key: str, default: str = None) -> str:
        """Get translated string"""
        lang_dict = self.translations.get(self.current_language, {})
        return lang_dict.get(key, default or key)

# Global instance
i18n = LocalizationManager()
