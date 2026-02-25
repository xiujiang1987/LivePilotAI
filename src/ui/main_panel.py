"""
main_panel.py - Main Control Panel GUI

This module provides the main control panel interface for LivePilotAI,
integrating emotion detection display, OBS controls, and system monitoring.

Author: LivePilotAI Development Team  
Date: 2024-12-19
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, List
import cv2
from PIL import Image, ImageTk
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import json

# Import our custom modules
from ..ai_engine.emotion_detector import EmotionDetector
from ..ai_engine.modules.camera_manager import CameraManager
from ..ai_engine.modules.face_tracker import FaceTracker
from ..ai_engine.modules.visualizer import Visualizer
from ..ai_engine.modules.emotion_intensity import EmotionIntensityAnalyzer
from ..ai_engine.modules.gesture_detector import GestureDetector
from ..ai_engine.modules.style_transfer import StyleTransfer
from ..obs_integration.obs_manager import OBSManager
from ..obs_integration.emotion_mapper import EmotionMapper, EmotionContext
from .preview_window import PreviewWindow
from .settings_dialog import SettingsDialog
from .status_indicators import StatusIndicator, StatusPanel, SystemStatusManager
from ..utils.i18n import i18n
from ..core.config_manager import config_manager, save_config, OBSConfig as CoreOBSConfig


@dataclass
class PanelConfig:
    """Configuration for main panel"""
    window_title: str = "LivePilotAI - Intelligent Streaming Director"
    window_size: tuple = (1200, 800)
    theme: str = "modern"
    language: str = "zh_TW"
    auto_start_camera: bool = True
    auto_connect_obs: bool = False
    preview_size: tuple = (320, 240)
    update_interval: int = 30  # milliseconds
    save_layout: bool = True


class MainPanel:
    """
    Main control panel for LivePilotAI with emotion detection and OBS integration
    """
    
    def __init__(self, config: Optional[PanelConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or PanelConfig()
        
        # Set language from config
        i18n.set_language(self.config.language)
        
        # Core components
        self.emotion_detector: Optional[EmotionDetector] = None
        self.camera_manager: Optional[CameraManager] = None
        self.obs_manager: Optional[OBSManager] = None
        self.emotion_mapper: Optional[EmotionMapper] = None
        
        # New components for Visual Upgrade
        self.face_tracker: Optional[FaceTracker] = None
        self.visualizer: Optional[Visualizer] = None
        self.analyzers: Dict[int, EmotionIntensityAnalyzer] = {}

        # UI components
        self.root: Optional[tk.Tk] = None
        self.preview_window: Optional[PreviewWindow] = None
        self.settings_dialog: Optional[SettingsDialog] = None
        self.status_indicators: Optional[SystemStatusManager] = None
        
        # UI elements
        self.main_frame: Optional[ttk.Frame] = None
        self.control_frame: Optional[ttk.Frame] = None
        self.preview_frame: Optional[ttk.Frame] = None
        self.status_frame: Optional[ttk.Frame] = None
        self.info_frame: Optional[ttk.Frame] = None
        
        # Control variables
        self.camera_running = tk.BooleanVar(value=False)
        self.obs_connected = tk.BooleanVar(value=False)
        self.auto_switching = tk.BooleanVar(value=False)
        self.current_emotion = tk.StringVar(value="Unknown")
        self.emotion_confidence = tk.DoubleVar(value=0.0)
        self.current_scene = tk.StringVar(value="No Scene")
        self.fps_counter = tk.StringVar(value="0 FPS")
        
        # Data tracking
        self.emotion_history: List[Dict[str, Any]] = []
        self.scene_switches: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
        self.last_logged_emotion: Optional[str] = None
        
        # Threading
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Asyncio Loop (Persistent)
        self.obs_loop = None
        self.obs_thread = None
        self._start_async_loop()
        
        # Components map for injection
        self.injected_components = {}

    def _start_async_loop(self):
        """Start global async loop in a separate thread"""
        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
            
        self.obs_loop = asyncio.new_event_loop()
        self.obs_thread = threading.Thread(target=run_loop, args=(self.obs_loop,), daemon=True)
        self.obs_thread.start()

    def set_components(self, **kwargs):
        """Inject external components"""
        for k, v in kwargs.items():
            self.injected_components[k] = v
        # Update attributes if they exist
        if 'emotion_detector' in kwargs: self.emotion_detector = kwargs['emotion_detector']
        if 'camera_manager' in kwargs: self.camera_manager = kwargs['camera_manager']
        if 'obs_manager' in kwargs: self.obs_manager = kwargs['obs_manager']
        if 'emotion_mapper' in kwargs: self.emotion_mapper = kwargs['emotion_mapper']
        if 'voice_commander' in kwargs: self.voice_commander = kwargs['voice_commander']

    def _initialize_components(self) -> None:
        """Initialize all core components"""
        try:
            # Initialize AI components if not injected
            if not getattr(self, 'emotion_detector', None):
                 self.emotion_detector = self.injected_components.get('emotion_detector') or EmotionDetector()
            
            if not getattr(self, 'camera_manager', None):
                 self.camera_manager = self.injected_components.get('camera_manager') or CameraManager()

            if not getattr(self, 'emotion_mapper', None):
                 self.emotion_mapper = self.injected_components.get('emotion_mapper') or EmotionMapper()

            self.voice_commander = self.injected_components.get('voice_commander')

            # Initialize new visual components
            self.face_tracker = FaceTracker()
            self.visualizer = Visualizer()
            self.gesture_detector = GestureDetector()
            self.style_transfer = StyleTransfer()
            self.analyzers = {}
            
            # Shared data for preview window
            self.latest_results = []
            
            # Initialize OBS manager with config
            app_config = config_manager.get_config()
            
            # Create OBS config from app config
            # Note: We need to map between CoreOBSConfig and the one expected by OBSManager if they differ
            # But since OBSManager expects an object with host, port, password, we can pass a compatible object
            # or update OBSManager to accept CoreOBSConfig.
            # For now, let's assume OBSManager's config is compatible or we pass the values.
            
            from ..obs_integration.obs_manager import OBSConfig as IntegrationOBSConfig
            obs_config = IntegrationOBSConfig(
                host=app_config.obs.websocket_host,
                port=app_config.obs.websocket_port,
                password=app_config.obs.websocket_password,
                auto_reconnect=app_config.obs.auto_connect,
                connection_timeout=app_config.obs.timeout
            )
            
            self.obs_manager = OBSManager(config=obs_config)
            
            self.logger.info("Core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components: {e}")
    
    def setup_ui(self, parent=None) -> None:
        """Setup the main user interface"""
        try:
            # Create main window
            if parent:
                self.root = parent
                # If parent is provided, we assume it's already configured
            else:
                self.root = tk.Tk()
                self.root.title(self.config.window_title)
                self.root.geometry(f"{self.config.window_size[0]}x{self.config.window_size[1]}")
                self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Apply theme
            self._apply_theme()
            
            # Create main layout
            self._create_main_layout()
            self._create_menu_bar()
            self._create_control_panel()
            self._create_preview_area()
            self._create_status_area()
            self._create_info_panel()
            
            # Initialize status indicators
            self.status_indicators = SystemStatusManager()
            
            # Check First Run
            self.check_first_run()
            
            # Bind events
            self._bind_events()
            
            # Auto-start if configured
            if self.config.auto_start_camera:
                self.root.after(1000, self.start_camera)
            
            if self.config.auto_connect_obs:
                self.root.after(2000, self.connect_obs)
            
            self.logger.info("UI setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up UI: {e}")
            messagebox.showerror("UI Error", f"Failed to setup UI: {e}")
    
    def _apply_theme(self) -> None:
        """Apply modern theme to the interface"""
        try:
            style = ttk.Style()
            
            if self.config.theme == "modern":
                # Configure modern theme colors
                style.theme_use('clam')
                
                # Define color scheme
                colors = {
                    'bg': '#2b2b2b',
                    'fg': '#ffffff',
                    'select_bg': '#404040',
                    'select_fg': '#ffffff',
                    'accent': '#0078d4',
                    'success': '#00b294',
                    'warning': '#ffb900',
                    'error': '#d83b01'
                }
                
                # Configure styles
                style.configure('TFrame', background=colors['bg'])
                style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
                style.configure('TButton', background=colors['accent'], foreground=colors['fg'])
                style.map('TButton', background=[('active', colors['select_bg'])])
                
                # Configure root window
                self.root.configure(bg=colors['bg'])
                
        except Exception as e:
            self.logger.warning(f"Could not apply theme: {e}")
    
    def _create_main_layout(self) -> None:
        """Create the main layout structure"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create main sections
        self.control_frame = ttk.LabelFrame(self.main_frame, text=i18n.get("camera_control"), padding="10")
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.preview_frame = ttk.LabelFrame(self.main_frame, text=i18n.get("preview"), padding="10")
        self.preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.info_frame = ttk.LabelFrame(self.main_frame, text=i18n.get("info"), padding="10")
        self.info_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_frame = ttk.LabelFrame(self.main_frame, text=i18n.get("obs_status"), padding="5")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_menu_bar(self) -> None:
        """Create the menu bar"""
        # Check if root is a Tk instance or Toplevel, otherwise we can't set menu directly easily
        # if it's a Frame. But let's try to find the top level window.
        top_level = self.root.winfo_toplevel()
        
        menubar = tk.Menu(top_level)
        top_level.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label=i18n.get("save"), command=self.save_configuration)
        file_menu.add_command(label=i18n.get("load"), command=self.load_configuration)
        file_menu.add_separator()
        file_menu.add_command(label=i18n.get("export"), command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label=i18n.get("close"), command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label=i18n.get("preview"), command=self.open_preview_window)
        view_menu.add_command(label=i18n.get("history"), command=self.show_emotion_history)
        view_menu.add_command(label=i18n.get("performance"), command=self.show_performance_metrics)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label=i18n.get("settings"), command=self.open_settings)
        tools_menu.add_command(label=i18n.get("obs_scene_manager"), command=self.open_scene_manager)
        tools_menu.add_command(label=i18n.get("emotion_mapper"), command=self.open_emotion_config)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=i18n.get("help"), menu=help_menu)
        help_menu.add_command(label=i18n.get("obs_guide"), command=self.show_obs_help)
        help_menu.add_command(label=i18n.get("about"), command=self.show_about)

    def show_obs_help(self) -> None:
        """Show OBS connection help"""
        messagebox.showinfo(i18n.get("obs_guide"), i18n.get("obs_guide_content"))
        # Removed incorrect access to help_menu
        
    def check_first_run(self):
        """Check if this is the first run and show wizard"""
        # Simple check: if obs password is empty or user manually requested
        app_config = config_manager.get_config()
        if not app_config.obs.websocket_password:
             self.logger.info("First run detected (or missing password). Launching Wizard.")
             self.root.after(1000, self.show_wizard)

    def show_wizard(self):
        """Show the First Run Wizard"""
        self.logger.info("Configuration Wizard Displayed")
        wizard = tk.Toplevel(self.root)
        wizard.title("歡迎使用 LivePilotAI (First Run Wizard)")
        wizard.geometry("500x400")
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Center contents
        frame = ttk.Frame(wizard, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="歡迎使用 / Welcome", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(frame, text="檢測到您尚未設定 OBS 密碼，或這是您第一次執行。", wraplength=450).pack(pady=5)
        
        step_frame = ttk.LabelFrame(frame, text="快速設定 / Quick Setup", padding=10)
        step_frame.pack(fill=tk.X, pady=10)
        
        # OBS Password Input
        ttk.Label(step_frame, text="OBS WebSocket Password:").grid(row=0, column=0, sticky=tk.W)
        pwd_var = tk.StringVar()
        entry = ttk.Entry(step_frame, textvariable=pwd_var, show="*")
        entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        step_frame.columnconfigure(1, weight=1)
        
        def save_and_close():
            pwd = pwd_var.get()
            if pwd:
                # Update config
                app_config = config_manager.get_config()
                app_config.obs.websocket_password = pwd
                save_config(app_config)
                
                # Update runtime obs_manager config if exists
                if self.obs_manager:
                     self.obs_manager.config.password = pwd
                
                messagebox.showinfo("Success", "設定已儲存！請嘗試點擊 '連接 OBS'。\nSettings saved! Please try connecting OBS.")
            wizard.destroy()
            
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=20)
        ttk.Button(btn_frame, text="跳過 / Skip", command=wizard.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="儲存 / Save", command=save_and_close).pack(side=tk.RIGHT)

    def _create_control_panel(self) -> None:
        """Create the main control panel"""
        # Camera controls
        camera_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("camera_control"), padding="5")
        camera_frame.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.camera_button = ttk.Button(
            camera_frame, text=i18n.get("start_camera"), 
            command=self.toggle_camera
        )
        self.camera_button.grid(row=0, column=0, pady=2)
        
        self.camera_status = ttk.Label(camera_frame, text="●", foreground="red")
        self.camera_status.grid(row=0, column=1, padx=(10, 0))
        
        # Camera selection
        ttk.Label(camera_frame, text=i18n.get("device")).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.camera_combo = ttk.Combobox(camera_frame, width=15, state="readonly")
        self.camera_combo.grid(row=1, column=1, pady=(5, 0))
        self.refresh_cameras()
        
        # OBS controls  
        obs_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("obs_control"), padding="5")
        obs_frame.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.obs_button = ttk.Button(
            obs_frame, text=i18n.get("connect_obs"),
            command=self.toggle_obs_connection
        )
        self.obs_button.grid(row=0, column=0, pady=2)
        
        self.obs_status = ttk.Label(obs_frame, text="●", foreground="red")
        self.obs_status.grid(row=0, column=1, padx=(10, 0))
        
        # Scene controls
        ttk.Label(obs_frame, text=i18n.get("current_scene")).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Change from Label to Combobox for interaction
        self.scene_combo = ttk.Combobox(obs_frame, textvariable=self.current_scene, state="readonly", width=15)
        self.scene_combo.bind("<<ComboboxSelected>>", self.on_scene_changed)
        self.scene_combo.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Auto-switching controls
        auto_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("auto_switch"), padding="5")
        auto_frame.grid(row=0, column=2, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.auto_switch_button = ttk.Button(
            auto_frame, text=i18n.get("enable_auto"),
            command=self.toggle_auto_switching
        )
        self.auto_switch_button.grid(row=0, column=0, pady=2)
        
        # Voice Command controls
        voice_frame = ttk.LabelFrame(self.control_frame, text="Voice Control", padding="5")
        voice_frame.grid(row=0, column=3, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.voice_button = ttk.Button(
            voice_frame, text="Start Voice",
            command=self.toggle_voice_control
        )
        self.voice_button.grid(row=0, column=0, pady=2)
        
        self.voice_status_indicator = ttk.Label(voice_frame, text="●", foreground="red")
        self.voice_status_indicator.grid(row=0, column=1, padx=(5, 0))
        
        self.auto_status = ttk.Label(auto_frame, text="●", foreground="red")
        self.auto_status.grid(row=0, column=1, padx=(10, 0))

        # Filter Control (New)
        filter_frame = ttk.LabelFrame(self.control_frame, text="Art Filter", padding="5")
        filter_frame.grid(row=0, column=3, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.filter_var = tk.StringVar(value="none")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=10, state="readonly")
        self.filter_combo['values'] = self.style_transfer.get_available_styles()
        self.filter_combo.grid(row=0, column=0, pady=2)
        
        # Voice Control (New)
        voice_frame = ttk.LabelFrame(self.control_frame, text="Voice Control", padding="5")
        voice_frame.grid(row=0, column=4, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.voice_button = ttk.Button(
            voice_frame, text="Start Listen",
            command=self.toggle_voice_control
        )
        self.voice_button.grid(row=0, column=0, pady=2)
        
        self.voice_status = ttk.Label(voice_frame, text="●", foreground="red")
        self.voice_status.grid(row=0, column=1, padx=(10, 0))

        self.last_cmd_label = ttk.Label(voice_frame, text="-", font=("", 8))
        self.last_cmd_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        # Emotion display
        emotion_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("current_emotion"), padding="5")
        emotion_frame.grid(row=0, column=4, sticky=(tk.W, tk.E, tk.N)) # Shifted column index
        
        emotion_display = ttk.Label(
            emotion_frame, textvariable=self.current_emotion,
            font=("", 12, "bold")
        )
        emotion_display.grid(row=0, column=0, pady=2)
        
        # Confidence bar
        self.confidence_progress = ttk.Progressbar(
            emotion_frame, variable=self.emotion_confidence,
            maximum=1.0, length=100
        )
        self.confidence_progress.grid(row=1, column=0, pady=(5, 0))
        
        confidence_label = ttk.Label(emotion_frame, text=i18n.get("confidence"))
        confidence_label.grid(row=2, column=0)
    
    def _create_preview_area(self) -> None:
        """Create the live preview area"""
        # Preview canvas
        self.preview_canvas = tk.Canvas(
            self.preview_frame,
            width=self.config.preview_size[0],
            height=self.config.preview_size[1],
            bg='black'
        )
        self.preview_canvas.pack(pady=10)
        
        # Preview controls
        preview_controls = ttk.Frame(self.preview_frame)
        preview_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            preview_controls, text=i18n.get("full_window"),
            command=self.open_preview_window
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            preview_controls, text=i18n.get("snapshot"),
            command=self.take_snapshot
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # FPS display
        fps_label = ttk.Label(preview_controls, textvariable=self.fps_counter)
        fps_label.pack(side=tk.RIGHT)
        
        # Placeholder text
        self.preview_canvas.create_text(
            self.config.preview_size[0]//2, 
            self.config.preview_size[1]//2,
            text=i18n.get("no_video_feed"), fill="white", font=("", 12)
        )
    
    def _create_status_area(self) -> None:
        """Create the status area"""
        # This will be handled by StatusIndicators class
        pass
    
    def _create_info_panel(self) -> None:
        """Create the system information panel"""
        # Create notebook for tabbed info
        info_notebook = ttk.Notebook(self.info_frame)
        info_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Emotion History tab
        emotion_tab = ttk.Frame(info_notebook)
        info_notebook.add(emotion_tab, text=i18n.get("emotions"))
        
        self.emotion_listbox = tk.Listbox(emotion_tab, height=8)
        self.emotion_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        emotion_scrollbar = ttk.Scrollbar(emotion_tab, orient=tk.VERTICAL)
        emotion_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.emotion_listbox.config(yscrollcommand=emotion_scrollbar.set)
        emotion_scrollbar.config(command=self.emotion_listbox.yview)
        
        # Scene History tab
        scene_tab = ttk.Frame(info_notebook)
        info_notebook.add(scene_tab, text=i18n.get("history"))
        
        self.scene_listbox = tk.Listbox(scene_tab, height=8)
        self.scene_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scene_scrollbar = ttk.Scrollbar(scene_tab, orient=tk.VERTICAL)
        scene_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scene_listbox.config(yscrollcommand=scene_scrollbar.set)
        scene_scrollbar.config(command=self.scene_listbox.yview)
        
        # Performance tab
        perf_tab = ttk.Frame(info_notebook)
        info_notebook.add(perf_tab, text=i18n.get("performance"))
        
        self.perf_text = tk.Text(perf_tab, height=8, width=30)
        self.perf_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        perf_scrollbar = ttk.Scrollbar(perf_tab, orient=tk.VERTICAL)
        perf_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.perf_text.config(yscrollcommand=perf_scrollbar.set)
        perf_scrollbar.config(command=self.perf_text.yview)
    
    def _bind_events(self) -> None:
        """Bind UI events"""
        # Start update loop
        self.root.after(self.config.update_interval, self.update_ui)
        
        # Bind keyboard shortcuts
        self.root.bind('<F1>', lambda e: self.show_about())
        self.root.bind('<F5>', lambda e: self.refresh_cameras())
        self.root.bind('<Control-s>', lambda e: self.save_configuration())
        self.root.bind('<Control-o>', lambda e: self.load_configuration())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
    
    def start_camera(self) -> None:
        """Start the camera and emotion detection"""
        try:
            if not self.camera_running.get():
                camera_index = self.camera_combo.current()
                if camera_index >= 0:
                    # Start camera
                    success = self.camera_manager.start_camera(camera_index)
                    if success:
                        # Start emotion detection
                        self.emotion_detector.start()
                        
                        self.camera_running.set(True)
                        self.camera_button.config(text=i18n.get("stop_camera"))
                        self.camera_status.config(foreground="green")
                        
                        # Start processing thread
                        self.running = True
                        self.update_thread = threading.Thread(target=self.processing_loop, daemon=True)
                        self.update_thread.start()
                        
                        self.logger.info("Camera and emotion detection started")
                    else:
                        messagebox.showerror(i18n.get("camera_error"), i18n.get("start_camera_error"))
                else:
                    messagebox.showwarning(i18n.get("camera_warning"), i18n.get("select_camera_msg"))
                    
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            messagebox.showerror(i18n.get("camera_error"), f"{i18n.get('start_camera_error')}: {e}")
    
    def stop_camera(self) -> None:
        """Stop the camera and emotion detection"""
        try:
            if self.camera_running.get():
                # Stop processing
                self.running = False
                if self.update_thread:
                    self.update_thread.join(timeout=2)
                
                # Stop components
                if self.emotion_detector:
                    self.emotion_detector.stop()
                if self.camera_manager:
                    self.camera_manager.stop()
                
                self.camera_running.set(False)
                self.camera_button.config(text=i18n.get("start_camera"))
                self.camera_status.config(foreground="red")
                
                # Clear preview
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(
                    self.config.preview_size[0]//2,
                    self.config.preview_size[1]//2,
                    text=i18n.get("no_video_feed"), fill="white", font=("", 12)
                )
                
                self.logger.info("Camera and emotion detection stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping camera: {e}")
    
    def toggle_camera(self) -> None:
        """Toggle camera on/off"""
        if self.camera_running.get():
            self.stop_camera()
        else:
            self.start_camera()
    
    def connect_obs(self) -> None:
        """Connect to OBS Studio"""
        try:
            if not self.obs_connected.get():
                if not self.obs_manager:
                     self._initialize_components()

                self.logger.info("Connecting to OBS...")
                
                # Callback for persistent loop
                def on_connect_complete(future):
                    try:
                        success = future.result()
                        self.root.after(0, lambda: self._handle_connect_result(success))
                    except Exception as e:
                        self.logger.error(f"OBS connection future exception: {e}")
                        self.root.after(0, lambda: self._handle_connect_result(False, str(e)))

                # Dispatch to persistent loop
                if self.obs_loop and self.obs_loop.is_running():
                     future = asyncio.run_coroutine_threadsafe(self.obs_manager.connect(), self.obs_loop)
                     future.add_done_callback(on_connect_complete)
                else:
                     self.logger.error("OBS Async Loop is not running!")
                
        except Exception as e:
            self.logger.error(f"Error connecting to OBS: {e}")
            messagebox.showerror(i18n.get("obs_error"), f"{i18n.get('obs_connect_error_msg')}: {e}")

    def _handle_connect_result(self, success, error_msg=None):
        self._update_obs_status(success)
        if not success:
            msg = error_msg or self.obs_manager.stats.get('last_error', 'Unknown error')
            messagebox.showerror(
                i18n.get("obs_error"), 
                f"{i18n.get('obs_connect_error_msg')}\n{msg}"
            )
    
    def disconnect_obs(self) -> None:
        """Disconnect from OBS Studio"""
        try:
            if self.obs_connected.get():
                def on_disconnect_complete(future):
                     self.root.after(0, lambda: self._update_obs_status(False))

                if self.obs_loop and self.obs_loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(self.obs_manager.disconnect(), self.obs_loop)
                    future.add_done_callback(on_disconnect_complete)
                else:
                    self.logger.error("OBS loop not running, cannot disconnect cleanly")
                    self._update_obs_status(False)
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from OBS: {e}")
    
    def _update_obs_status(self, connected: bool) -> None:
        """Update OBS connection status in UI"""
        self.obs_connected.set(connected)
        if connected:
            self.obs_button.config(text=i18n.get("disconnect_obs"))
            self.obs_status.config(foreground="green")
            self.logger.info("OBS connected successfully")
            # Update scenes
            self.update_scenes_from_obs()
        else:
            self.obs_button.config(text=i18n.get("connect_obs"))
            self.obs_status.config(foreground="red")
            self.current_scene.set(i18n.get("no_scene"))
            if hasattr(self, 'scene_combo'):
                self.scene_combo['values'] = []

    def update_scenes_from_obs(self):
        """Fetch scene list from OBS and update combo"""
        
        def on_fetch_complete(future):
            try:
                scenes = future.result()
                self.logger.info(f"OBS Scenes Fetched: {scenes}")
                self.root.after(0, lambda: self._update_scene_combo(scenes))
            except Exception as e:
                self.logger.error(f"Failed to fetch scenes: {e}")

        if self.obs_loop and self.obs_loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.obs_manager.get_scene_list(), self.obs_loop)
            future.add_done_callback(on_fetch_complete)
        else:
             self.logger.error("OBS loop not running for fetch_scenes")

    def _update_scene_combo(self, scenes):
        self.available_scenes = scenes  # Store for voice commands
        if hasattr(self, 'scene_combo'):
            self.scene_combo['values'] = scenes
            if scenes:
                 # Default to first if none selected
                 if not self.current_scene.get() or self.current_scene.get() == "No Scene":
                      self.current_scene.set(scenes[0])

    def on_scene_changed(self, event):
        """Handle scene selection from combo"""
        scene_name = self.current_scene.get()
        if not self.obs_connected.get() or not scene_name:
            return
            
        if self.obs_loop and self.obs_loop.is_running():
            asyncio.run_coroutine_threadsafe(self.obs_manager.set_current_program_scene(scene_name), self.obs_loop)
        else:
            self.logger.error("OBS loop not running for scene switch")
    
    def toggle_obs_connection(self) -> None:
        """Toggle OBS connection"""
        if self.obs_connected.get():
            self.disconnect_obs()
        else:
            self.connect_obs()
    
    def toggle_auto_switching(self) -> None:
        """Toggle automatic scene switching"""
        if self.auto_switching.get():
            self.auto_switching.set(False)
            self.auto_switch_button.config(text=i18n.get("enable_auto"))
            self.auto_status.config(foreground="red")
        else:
            if self.obs_connected.get():
                self.auto_switching.set(True)
                self.auto_switch_button.config(text=i18n.get("disable_auto"))
                self.auto_status.config(foreground="green")
            else:
                messagebox.showwarning(i18n.get("auto_switch_warning_title"), i18n.get("auto_switch_warning_msg"))
    
    def toggle_voice_control(self) -> None:
        """Toggle voice control system"""
        if not self.voice_commander:
            messagebox.showwarning("Warning", "Voice Commander not initialized")
            return
            
        if self.voice_commander.is_running:
            self.voice_commander.stop()
            self.voice_button.config(text="Start Voice")
            self.voice_status_indicator.config(foreground="red")
            self.logger.info("Voice control stopped")
        else:
            success = self.voice_commander.start()
            if success:
                self.voice_button.config(text="Stop Voice")
                self.voice_status_indicator.config(foreground="green")
                self.logger.info("Voice control started")
            else:
                messagebox.showerror("Error", "Failed to start microphone (SpeechRecognition may be missing)")

    def handle_voice_command(self, cmd: str) -> None:
        """Handle incoming voice commands (Public API)"""
        if not cmd:
            return
        # Execute logic in UI thread to be safe
        self.root.after(0, lambda: self._process_voice_command(cmd))
    
    def _process_voice_command(self, cmd: str) -> None:
        """Internal voice command processing"""
        self.logger.info(f"Processing Voice Command: {cmd}")
        
        cmd_lower = cmd.lower()
        
        # 1. System Commands
        if "start" in cmd_lower or "啟用" in cmd_lower:
             if not self.auto_switching.get():
                 self.toggle_auto_switching()
                 self.logger.info("Voice: Auto Switch Enabled")
        elif "stop" in cmd_lower or "停用" in cmd_lower:
             if self.auto_switching.get():
                 self.toggle_auto_switching()
                 self.logger.info("Voice: Auto Switch Disabled")
        elif "snapshot" in cmd_lower or "拍照" in cmd_lower or "截圖" in cmd_lower:
             self.take_snapshot()
             self.logger.info("Voice: Snapshot taken")
        
        # 2. Scene Switching Commands
        elif ("switch" in cmd_lower or "切換" in cmd_lower) and hasattr(self, 'available_scenes'):
            target_scene = None
            # Sort scenes by length descending to match longest name first (e.g. "Game 2" vs "Game")
            sorted_scenes = sorted(self.available_scenes, key=len, reverse=True)
            
            for scene in sorted_scenes:
                if scene.lower() in cmd_lower:
                    target_scene = scene
                    break
            
            if target_scene:
                self.logger.info(f"Voice: Switching to scene '{target_scene}'")
                self.current_scene.set(target_scene)
                
                if self.obs_connected.get() and self.obs_loop and self.obs_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.obs_manager.set_current_program_scene(target_scene), 
                        self.obs_loop
                    )
                else:
                    self.logger.warning("OBS not connected, cannot switch scene via voice")

    def processing_loop(self) -> None:
        """Main processing loop for camera and emotion detection"""
        fps_counter = 0
        fps_timer = time.time()
        
        while self.running:
            try:
                # Capture frame
                frame = self.camera_manager.get_frame()
                if frame is not None:
                    # Detect emotions
                    results = self.emotion_detector.detect_emotions(frame)
                    
                    # --- Advanced Processing Logic (Face Tracking & Intensity) ---
                    annotated_frame = frame.copy()
                    
                    if results:
                        # 1. Update tracker with current detections
                        rects = [res['bbox'] for res in results if 'bbox' in res]
                        tracked_objects = self.face_tracker.update(rects)
                        
                        # 2. Enrich results with ID and Intensity
                        for res in results:
                            bbox = res.get('bbox')
                            if not bbox: continue
                                
                            # Find matching ID (Distance based)
                            cx, cy = bbox[0] + bbox[2]//2, bbox[1] + bbox[3]//2
                            best_id = None
                            min_dist = float('inf')
                            
                            for fid, tracked_obj in tracked_objects.items():
                                t_cx, t_cy = tracked_obj.centroid
                                dist_val = ((cx-t_cx)**2 + (cy-t_cy)**2)**0.5
                                if dist_val < 50: # Threshold
                                    if dist_val < min_dist:
                                        min_dist = dist_val
                                        best_id = fid
                            
                            if best_id is not None:
                                res['face_id'] = best_id
                                
                                # Intensity Analysis
                                if best_id not in self.analyzers:
                                    self.analyzers[best_id] = EmotionIntensityAnalyzer()
                                
                                emotions_dist = res.get('emotions', {})
                                if not emotions_dist and 'emotion' in res:
                                    emotions_dist = {res['emotion']: res['confidence']}
                                    
                                dynamics = self.analyzers[best_id].analyze(emotions_dist)
                                res['intensity'] = dynamics.intensity
                        
                        # 3. Visualization
                        annotated_frame = self.visualizer.draw_detections(frame, results)
                        
                        # Update self.latest_results for other components
                        self.latest_results = results

                        # Get dominant emotion for UI stats (using first face)
                        dominant = results[0]
                        emotion = dominant.get('dominant_emotion') or dominant.get('emotion')
                        confidence = dominant.get('confidence', 0.0)
                        
                        # Update UI variables
                        self.root.after(0, lambda: self._update_emotion_display(emotion, confidence))
                        
                        # Handle auto switching
                        if self.auto_switching.get() and self.obs_connected.get():
                            self._handle_auto_switching(emotion, confidence, frame)
                    
                    # --- Gesture Detection ---
                    gestures = self.gesture_detector.detect(frame)
                    if gestures:
                         annotated_frame = self.visualizer.draw_gestures(annotated_frame, gestures)
                         
                         # Handle Gesture Actions
                         for ges in gestures:
                             g_name = ges['gesture']
                             if g_name == "Thumbs_Up":
                                 # Action: Log for now
                                 self.logger.info("Gesture Detected: Thumbs Up")
                             elif g_name == "Open_Palm":
                                 self.logger.info("Gesture Detected: Open Palm")
                             elif g_name == "OK":
                                 self.logger.info("Gesture Detected: OK")

                    # --- Style Transfer ---
                    current_style = self.filter_var.get()
                    if current_style != "none":
                        annotated_frame = self.style_transfer.apply_style(annotated_frame, current_style)

                    # Update preview with VISUALIZED frame
                    self.root.after(0, lambda: self._update_preview(annotated_frame))
                    
                    # Calculate FPS
                    fps_counter += 1
                    if time.time() - fps_timer >= 1.0:
                        fps = fps_counter / (time.time() - fps_timer)
                        self.root.after(0, lambda: self.fps_counter.set(f"{fps:.1f} FPS"))
                        fps_counter = 0
                        fps_timer = time.time()
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
    
    def _update_emotion_display(self, emotion: str, confidence: float) -> None:
        """Update emotion display in UI"""
        # Translate emotion
        translated_emotion = i18n.get(emotion, emotion.title())
        self.current_emotion.set(translated_emotion)
        self.emotion_confidence.set(confidence)
        
        # Only add to history if emotion changed
        if emotion != self.last_logged_emotion:
            # Add to history
            timestamp = time.strftime("%H:%M:%S")
            entry = f"{timestamp} - {translated_emotion} ({confidence:.2f})"
            
            self.emotion_listbox.insert(0, entry)
            if self.emotion_listbox.size() > 50:  # Limit history size
                self.emotion_listbox.delete(50)
            
            # Store in data
            self.emotion_history.append({
                'timestamp': time.time(),
                'emotion': emotion,
                'confidence': confidence
            })
            
            self.last_logged_emotion = emotion
    
    def _update_preview(self, frame) -> None:
        """Update preview canvas with current frame"""
        try:
            # Resize frame to preview size
            height, width = frame.shape[:2]
            preview_width, preview_height = self.config.preview_size
            
            scale = min(preview_width / width, preview_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB and create PIL image
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                preview_width // 2, preview_height // 2,
                image=photo
            )
            
            # Keep reference to prevent garbage collection
            self.preview_canvas.image = photo
            
        except Exception as e:
            self.logger.error(f"Error updating preview: {e}")
    
    def _handle_auto_switching(self, emotion: str, confidence: float, frame) -> None:
        """Handle automatic scene switching based on emotion"""
        try:
            # Create emotion context
            context = EmotionContext(
                emotion=emotion,
                confidence=confidence,
                timestamp=time.time(),
                face_count=1,  # Simplified for now
                face_area=0.1   # Simplified for now
            )
            
            # Update emotion mapper
            self.emotion_mapper.update_emotion_context(context)
            
            # Evaluate mapping
            result = self.emotion_mapper.evaluate_mapping(context)
            
            if result.should_switch and result.recommended_scene:
                # Switch scene in OBS
                def on_switch_complete(future):
                    try:
                        success = future.result()
                        if success:
                             self.root.after(0, lambda: self._update_scene_display(result.recommended_scene))
                             # MODIFICATION: Pass the triggering emotion
                             self.emotion_mapper.record_scene_switch(
                                 self.current_scene.get(),
                                 result.recommended_scene,
                                 emotion=context.emotion
                             )
                    except Exception as e:
                        self.logger.error(f"Auto switch scene failed: {e}")

                if self.obs_loop and self.obs_loop.is_running():
                     # Use set_current_program_scene instead of non-existent switch_scene
                     future = asyncio.run_coroutine_threadsafe(
                         self.obs_manager.set_current_program_scene(result.recommended_scene), 
                         self.obs_loop
                     )
                     future.add_done_callback(on_switch_complete)
                
        except Exception as e:
            self.logger.error(f"Error in auto switching: {e}")
    
    def _update_scene_display(self, scene_name: str) -> None:
        """Update scene display in UI"""
        self.current_scene.set(scene_name)
        
        # Add to history
        timestamp = time.strftime("%H:%M:%S")
        entry = f"{timestamp} - Switched to: {scene_name}"
        
        self.scene_listbox.insert(0, entry)
        if self.scene_listbox.size() > 50:
            self.scene_listbox.delete(50)
        
        # Store in data
        self.scene_switches.append({
            'timestamp': time.time(),
            'scene': scene_name
        })
    
    def refresh_cameras(self) -> None:
        """Refresh available camera devices"""
        try:
            devices = self.camera_manager.get_available_cameras()
            camera_names = [f"{i18n.get('camera')} {i}: {name}" for i, name in enumerate(devices)]
            
            self.camera_combo['values'] = camera_names
            if camera_names:
                self.camera_combo.current(0)
                
        except Exception as e:
            self.logger.error(f"Error refreshing cameras: {e}")
    
    def update_ui(self) -> None:
        """Update UI elements periodically"""
        try:
            # Update performance metrics
            self._update_performance_display()
            
            # Schedule next update
            self.root.after(self.config.update_interval, self.update_ui)
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
    
    def _update_performance_display(self) -> None:
        """Update performance metrics display"""
        try:
            metrics = {
                'Camera FPS': self.fps_counter.get(),
                'Emotions Detected': len(self.emotion_history),
                'Scene Switches': len(self.scene_switches),
                'OBS Connected': 'Yes' if self.obs_connected.get() else 'No',
                'Auto Switching': 'Enabled' if self.auto_switching.get() else 'Disabled'
            }
            
            self.perf_text.delete(1.0, tk.END)
            for key, value in metrics.items():
                self.perf_text.insert(tk.END, f"{key}: {value}\n")
                
        except Exception as e:
            self.logger.error(f"Error updating performance: {e}")
    
    # Menu functions
    def open_preview_window(self) -> None:
        """Open full preview window"""
        if not self.preview_window or not self.preview_window.root.winfo_exists():
            self.preview_window = PreviewWindow(self)
    
    def open_settings(self) -> None:
        """Open settings dialog"""
        app_config = config_manager.get_config()
        
        # Create settings dictionary from current config
        current_settings = {
            'obs': {
                'host': app_config.obs.websocket_host,
                'port': app_config.obs.websocket_port,
                'password': app_config.obs.websocket_password,
                'auto_connect': app_config.obs.auto_connect,
                'reconnect_interval': 5,
                'timeout': app_config.obs.timeout
            },
            'emotion': {
                'confidence_threshold': app_config.ai_models.confidence_threshold,
                'update_interval': self.config.update_interval,
                'smoothing_factor': 0.3,
                'min_face_size': 30,
                'max_faces': 5
            },
            'scene_switching': {
                'enable_auto_switch': self.auto_switching.get(),
                'switch_cooldown': 2.0,
                'transition_duration': 1000,
                'confidence_required': 0.8,
                'sustained_duration': 1.0
            },
            'ui': {
                'theme': self.config.theme,
                'language': i18n.current_language,
                'update_fps': 30,
                'show_confidence': True,
                'show_fps': True,
                'emotion_colors': {}
            },
            'performance': {
                'max_cpu_usage': 80,
                'memory_limit_mb': 512,
                'gpu_acceleration': True,
                'threading_enabled': True,
                'cache_size': 100
            }
        }
        
        def on_save(new_settings):
            # Update AppConfig
            app_config.obs.websocket_host = new_settings['obs']['host']
            app_config.obs.websocket_port = new_settings['obs']['port']
            app_config.obs.websocket_password = new_settings['obs']['password']
            app_config.obs.auto_connect = new_settings['obs']['auto_connect']
            app_config.obs.timeout = new_settings['obs']['timeout']
            
            app_config.ai_models.confidence_threshold = new_settings['emotion']['confidence_threshold']
            
            # Save to file
            if save_config(app_config):
                self.logger.info("Configuration saved to file")
            else:
                self.logger.error("Failed to save configuration to file")
            
            # Update runtime components
            if self.obs_manager:
                self.obs_manager.config.host = new_settings['obs']['host']
                self.obs_manager.config.port = new_settings['obs']['port']
                self.obs_manager.config.password = new_settings['obs']['password']
            
            # Apply new settings
            self.config.theme = new_settings['ui']['theme']
            self._apply_theme()
            
            # Apply language
            if 'language' in new_settings['ui']:
                if i18n.set_language(new_settings['ui']['language']):
                    # Update config language
                    self.config.language = new_settings['ui']['language']
                    messagebox.showinfo(i18n.get("language_changed"), i18n.get("restart_required"))
            
            self.logger.info("Settings updated")
        
        self.settings_dialog = SettingsDialog(self.root, current_settings, on_save)
        self.settings_dialog.show()
    
    def take_snapshot(self) -> None:
        """Take a snapshot of current frame"""
        try:
            if self.camera_running.get():
                frame = self.camera_manager.get_frame()
                if frame is not None:
                    filename = f"snapshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                    filepath = filedialog.asksaveasfilename(
                        defaultextension=".jpg",
                        filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
                        initialvalue=filename
                    )
                    
                    if filepath:
                        cv2.imwrite(filepath, frame)
                        messagebox.showinfo("Snapshot", f"Snapshot saved to {filepath}")
            else:
                messagebox.showwarning("Snapshot", "Camera is not running")
                
        except Exception as e:
            self.logger.error(f"Error taking snapshot: {e}")
            messagebox.showerror("Snapshot Error", f"Failed to save snapshot: {e}")
    
    def save_configuration(self) -> None:
        """Save current configuration"""
        try:
            config = {
                'camera_settings': {
                    'auto_start': self.config.auto_start_camera,
                    'selected_device': self.camera_combo.current()
                },
                'obs_settings': {
                    'auto_connect': self.config.auto_connect_obs,
                    'host': 'localhost',  # Can be made configurable
                    'port': 4455
                },
                'ui_settings': {
                    'window_size': self.config.window_size,
                    'theme': self.config.theme,
                    'preview_size': self.config.preview_size,
                    'language': i18n.current_language
                },
                'auto_switching': {
                    'enabled': self.auto_switching.get()
                }
            }
            
            # Save emotion mappings
            if self.emotion_mapper:
                self.emotion_mapper.save_configuration()
            
            # Save main config
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialvalue="livepilot_config.json"
            )
            
            if filepath:
                with open(filepath, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messagebox.showinfo("Configuration", i18n.get("save_success"))
                
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
    
    def load_configuration(self) -> None:
        """Load configuration from file"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                
                # Apply configuration
                if 'ui_settings' in config and 'language' in config['ui_settings']:
                    i18n.set_language(config['ui_settings']['language'])
                    # Note: Full UI refresh might be needed for language change to take effect immediately
                
                messagebox.showinfo("Configuration", f"Configuration loaded from {filepath}")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            messagebox.showerror("Load Error", f"Failed to load configuration: {e}")
    
    def export_data(self) -> None:
        """Export collected data"""
        try:
            data = {
                'emotion_history': self.emotion_history,
                'scene_switches': self.scene_switches,
                'performance_metrics': self.performance_metrics,
                'export_timestamp': time.time()
            }
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialvalue=f"livepilot_data_{time.strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filepath:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                messagebox.showinfo("Export", f"Data exported to {filepath}")
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def show_about(self) -> None:
        """Show about dialog"""
        about_text = """
LivePilotAI - Intelligent Streaming Director

Version: 2.0.0
Author: LivePilotAI Development Team
Date: 2024-12-19

An AI-powered streaming assistant that automatically switches OBS scenes 
based on real-time emotion detection from your camera feed.

Features:
• Real-time emotion detection
• Automatic OBS scene switching  
• Customizable emotion mappings
• Live preview and monitoring
• Performance analytics

© 2024 LivePilotAI Team. All rights reserved.
        """
        
        messagebox.showinfo("About LivePilotAI", about_text)
    
    def show_documentation(self) -> None:
        """Show documentation"""
        messagebox.showinfo("Documentation", "Documentation will be available online soon!")
    
    def show_emotion_history(self) -> None:
        """Show detailed emotion history"""
        # This could open a separate window with detailed charts
        pass
    
    def show_performance_metrics(self) -> None:
        """Show detailed performance metrics"""
        # This could open a separate window with performance graphs
        pass
    
    def open_scene_manager(self) -> None:
        """Open OBS scene manager"""
        # This could open a separate window for managing OBS scenes
        pass
    
    def open_emotion_config(self) -> None:
        """Open emotion mapper configuration"""
        # This could open a separate window for configuring emotion mappings
        pass
    
    def on_closing(self) -> None:
        """Handle application closing"""
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit LivePilotAI?"):
                # Stop all operations
                self.running = False
                
                # Stop Audio
                if hasattr(self, 'audio_controller'):
                    try:
                        self.audio_controller.stop_listening()
                    except: pass


                if self.camera_running.get():
                    try:
                        self.stop_camera()
                    except: pass
                
                # Close Camera Manager
                if hasattr(self, 'camera_manager') and self.camera_manager:
                    try:
                         self.camera_manager.stop()
                    except Exception as e:
                        self.logger.error(f"Error stopping camera manager: {e}")
                
                if self.obs_connected.get():
                    try:
                        self.disconnect_obs()
                    except: pass
                
                # Save configuration if enabled
                try:
                    if self.config.save_layout:
                        if self.emotion_mapper:
                            self.emotion_mapper.save_configuration()
                except: pass
                
                # Close windows
                try:
                    if self.preview_window:
                        self.preview_window.close()
                except: pass
                
                try:
                    if self.settings_dialog:
                        self.settings_dialog.close()
                except: pass
                
                self.root.destroy()
                import sys
                sys.exit(0)
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
            import sys
            sys.exit(0)
    
    def run(self) -> None:
        """Run the main application"""
        try:
            self.setup_ui()
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            messagebox.showerror("Application Error", f"Failed to run application: {e}")


# Main entry point
if __name__ == "__main__":
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create and run main panel
        config = PanelConfig(
            window_title="LivePilotAI - Day 5 Development",
            auto_start_camera=False,
            auto_connect_obs=False
        )
        
        app = MainPanel(config)
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
