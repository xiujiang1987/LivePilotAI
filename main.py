"""
LivePilotAI Day 5 - Main Application Entry Point
Advanced OBS integration and intelligent streaming director system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
import time
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from src.api.server import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('livepilotai_day5.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add src directory to path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Global modules will be imported lazily
MainPanel = None
PreviewWindow = None
OBSManager = None
EmotionDetector = None
ConfigManager = None

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        
        # Center the window
        width = 400
        height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Style
        self.root.configure(bg='#1e1e1e')
        
        # Title
        tk.Label(self.root, text="LivePilotAI", font=("Arial", 24, "bold"), 
                 bg='#1e1e1e', fg="#ffffff").pack(pady=(80, 20))
        
        # Subtitle
        tk.Label(self.root, text="Day 5 Build", font=("Arial", 12), 
                 bg='#1e1e1e', fg="#aaaaaa").pack(pady=(0, 40))
        
        # Loading Status
        self.status_label = tk.Label(self.root, text="Initializing...", 
                                   font=("Arial", 10), bg='#1e1e1e', fg="#888888")
        self.status_label.pack(side=tk.BOTTOM, pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=300, mode='indeterminate')
        self.progress.pack(side=tk.BOTTOM, pady=(0, 20))
        self.progress.start(10)

    def update_status(self, text):
        self.status_label.configure(text=text)
        self.root.update()

    def destroy(self):
        self.root.destroy()

def load_modules(splash):
    global MainPanel, PreviewWindow, OBSManager, EmotionDetector, ConfigManager
    global SystemStatusManager, create_obs_status_panel, create_ai_status_panel
    global create_system_status_panel, StatusLevel, show_settings_dialog
    global SceneController, EmotionMapper, OBSWebSocketClient
    global RealTimeEmotionDetector, CameraManager, FaceDetector, AIDirector
    
    try:
        splash.update_status("Loading Core Configuration...")
        import src.core as core
        ConfigManager = core.ConfigManager
        
        splash.update_status("Loading AI Engine (TensorFlow/MediaPipe)...")
        # Pre-import heavy modules
        import src.ai_engine.emotion_detector as ed
        EmotionDetector = ed.EmotionDetector
        
        import src.ai_engine.modules.real_time_detector as rtd
        RealTimeEmotionDetector = rtd.RealTimeEmotionDetector
        
        import src.ai_engine.modules.camera_manager as cam
        CameraManager = cam.CameraManager
        
        import src.ai_engine.modules.face_detector as fd
        FaceDetector = fd.FaceDetector
        
        import src.ai_engine.modules.ai_director as aid
        AIDirector = aid.AIDirector
        
        # Load Voice Commander
        import src.ai_engine.modules.voice_commander as vc
        global VoiceCommander
        VoiceCommander = vc.VoiceCommander

        splash.update_status("Loading UI Components...")
        import src.ui as ui
        MainPanel = ui.main_panel.MainPanel
        PreviewWindow = ui.PreviewWindow
        show_settings_dialog = ui.show_settings_dialog
        SystemStatusManager = ui.SystemStatusManager
        create_obs_status_panel = ui.create_obs_status_panel
        create_ai_status_panel = ui.create_ai_status_panel
        create_system_status_panel = ui.create_system_status_panel
        StatusLevel = ui.StatusLevel
        
        splash.update_status("Loading OBS Integration...")
        import src.obs_integration.obs_manager as om
        OBSManager = om.OBSManager
        import src.obs_integration.scene_controller as sc
        SceneController = sc.SceneController
        import src.obs_integration.emotion_mapper as em
        EmotionMapper = em.EmotionMapper
        import src.obs_integration.websocket_client as owc
        OBSWebSocketClient = owc.OBSWebSocketClient

        time.sleep(0.5) # Slight delay to let user see "Done"
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        messagebox.showerror("Initialization Error", f"Failed to load modules:\n{e}")
        sys.exit(1)

class LivePilotAIApp:
    """
    Main application class for LivePilotAI Day 5
    """
    
    def __init__(self):
        self.root = None
        self.main_panel = None
        self.preview_window = None
        self.status_manager = None
        
        # Core components
        self.obs_manager = None
        self.scene_controller = None
        self.emotion_mapper = None
        self.emotion_detector = None
        self.camera_manager = None
        self.real_time_detector = None
        self.ai_director = None
        self.voice_commander = None
        
        # Configuration
        self.config_file = "livepilotai_config.json"
        self.settings = self._load_default_settings()
        
        # Runtime state
        self.is_running = False
        self.preview_thread = None
        self.emotion_thread = None
        self.api_server = None
        self.api_thread = None
        self.logger = logging.getLogger("LivePilotAI")

    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            "window_title": "LivePilotAI - Intelligent Streaming Director",
            "window_size": "1200x800",
            "theme": "modern",
            "auto_connect_obs": False
        }
        
    def initialize(self, root: tk.Tk):
        """Initialize the application components"""
        self.root = root
        self.root.title(self.settings["window_title"])
        self.root.geometry(self.settings["window_size"])
        
        # Configure grid weight
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Setup clean exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        try:
            self._init_components()
            self._setup_ui()
            self._start_api_server()
            
            self.logger = logging.getLogger("LivePilotAI")
            self.logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.exception("Initialization failed")
            messagebox.showerror("Error", f"Application initialization failed:\n{str(e)}")
            sys.exit(1)
            
    def _init_components(self):
        """Initialize backend components"""
        # 1. Config
        self.config_manager = ConfigManager()
        self.app_config = self.config_manager.load_config()
        
        # 2. OBS Integration
        self.obs_manager = OBSManager()
        self.scene_controller = SceneController(self.obs_manager)
        # Fix: EmotionMapper expects config_path string, not config_manager object
        # Since config_loader handles paths internally or we can pass None for defaults
        self.emotion_mapper = EmotionMapper() 
        
        # 3. AI Engine
        # 使用異步初始化包裝
        self.emotion_detector = EmotionDetector(
            model_path=self.app_config.ai_models.emotion_model_path
        )
        self.camera_manager = CameraManager()
        self.real_time_detector = RealTimeEmotionDetector(
            config=None,
            emotion_detector=self.emotion_detector,
            camera_manager=self.camera_manager
        )
        self.ai_director = AIDirector(
            self.real_time_detector,
            self.scene_controller,
            self.emotion_mapper
        )
        self.voice_commander = VoiceCommander(self._handle_voice_command)

    def _handle_voice_command(self, text: str):
        """Handle voice commands from global context"""
        # Pass to main panel if it exists
        if self.main_panel:
            self.main_panel.handle_voice_command(text)
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Create Main Panel
        self.main_panel = MainPanel()
        
        # Inject dependencies into MainPanel
        self.main_panel.set_components(
            emotion_detector=self.emotion_detector,
            camera_manager=self.camera_manager,
            obs_manager=self.obs_manager,
            emotion_mapper=self.emotion_mapper,
            voice_commander=self.voice_commander
        )
        
        # Initialize (since we deferred it)
        self.main_panel._initialize_components()
        
        # Create Widgets (using setup_ui)
        self.main_panel.setup_ui(main_container)
        
        # Setup status indicators if needed
        # self.status_manager = SystemStatusManager(self.root)
        
    def _start_api_server(self):
        """Start the FastAPI server in a background thread"""
        try:
            self.logger.info("Starting API server on port 8000...")
            
            # Use dynamic import to get the latest app instance
            from src.api.server import app as fastapi_app
            # Attach main app instance to FastAPI state
            fastapi_app.state.main_app = self
            
            def run_server():
                uvicorn.run(
                    fastapi_app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="error"
                )
                
            self.api_thread = threading.Thread(target=run_server, daemon=True)
            self.api_thread.start()
            self.logger.info("API server is running in background.")
        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
        
    def run(self):
        """Start the application main loop"""
        self.is_running = True
        self.root.mainloop()
        
    def on_close(self):
        """Handle application shutdown"""
        if messagebox.askokcancel("Quit", "Do you want to quit LivePilotAI?"):
            logger.info("Shutting down application...")
            self.is_running = False
            
            # Stop AI components
            if self.camera_manager:
                self.camera_manager.stop()

            if self.voice_commander:
                self.voice_commander.stop()
                
            # Stop monitoring threads
            # (Add thread cleanup code here)
            
            # Disconnect OBS
            if self.obs_manager:
                self.obs_manager.disconnect()
                
            # API server runs as daemon, it will exit automatically when main thread dies
            self.root.destroy()
            sys.exit(0)


def main():
    """Application entry point"""
    # 1. Show Splash Screen
    splash = SplashScreen()
    
    # 2. Load Modules in separate thread/process simulation
    # In a real app we might use threading, but for imports we just run them
    # while updating the UI. Tkinter is single threaded so we use root.update()
    load_modules(splash)
    
    # 3. Destroy Splash and Launch Main App
    splash.destroy()
    
    root = tk.Tk()
    app = LivePilotAIApp()
    app.initialize(root)
    app.run()

if __name__ == "__main__":
    main()