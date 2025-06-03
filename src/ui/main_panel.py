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
from ..obs_integration.obs_manager import OBSManager
from ..obs_integration.emotion_mapper import EmotionMapper, EmotionContext
from .preview_window import PreviewWindow
from .settings_dialog import SettingsDialog
from .status_indicators import StatusIndicators


@dataclass
class PanelConfig:
    """Configuration for main panel"""
    window_title: str = "LivePilotAI - Intelligent Streaming Director"
    window_size: tuple = (1200, 800)
    theme: str = "modern"
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
        
        # Core components
        self.emotion_detector: Optional[EmotionDetector] = None
        self.camera_manager: Optional[CameraManager] = None
        self.obs_manager: Optional[OBSManager] = None
        self.emotion_mapper: Optional[EmotionMapper] = None
        
        # UI components
        self.root: Optional[tk.Tk] = None
        self.preview_window: Optional[PreviewWindow] = None
        self.settings_dialog: Optional[SettingsDialog] = None
        self.status_indicators: Optional[StatusIndicators] = None
        
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
        
        # Threading
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Initialize components
        self._setup_logging()
        self._initialize_components()
        
        self.logger.info("MainPanel initialized")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('livepilot_ui.log')
            ]
        )
    
    def _initialize_components(self) -> None:
        """Initialize all core components"""
        try:
            # Initialize AI components
            self.emotion_detector = EmotionDetector()
            self.camera_manager = CameraManager()
            self.emotion_mapper = EmotionMapper()
            
            # Initialize OBS manager
            self.obs_manager = OBSManager()
            
            self.logger.info("Core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components: {e}")
    
    def setup_ui(self) -> None:
        """Setup the main user interface"""
        try:
            # Create main window
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
            self.status_indicators = StatusIndicators(self.status_frame)
            
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
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="Live Preview", padding="10")
        self.preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.info_frame = ttk.LabelFrame(self.main_frame, text="System Info", padding="10")
        self.info_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="5")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_menu_bar(self) -> None:
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self.save_configuration)
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Preview Window", command=self.open_preview_window)
        view_menu.add_command(label="Emotion History", command=self.show_emotion_history)
        view_menu.add_command(label="Performance Metrics", command=self.show_performance_metrics)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        tools_menu.add_command(label="OBS Scene Manager", command=self.open_scene_manager)
        tools_menu.add_command(label="Emotion Mapper Config", command=self.open_emotion_config)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
    
    def _create_control_panel(self) -> None:
        """Create the main control panel"""
        # Camera controls
        camera_frame = ttk.LabelFrame(self.control_frame, text="Camera", padding="5")
        camera_frame.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.camera_button = ttk.Button(
            camera_frame, text="Start Camera", 
            command=self.toggle_camera
        )
        self.camera_button.grid(row=0, column=0, pady=2)
        
        self.camera_status = ttk.Label(camera_frame, text="●", foreground="red")
        self.camera_status.grid(row=0, column=1, padx=(10, 0))
        
        # Camera selection
        ttk.Label(camera_frame, text="Device:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.camera_combo = ttk.Combobox(camera_frame, width=15, state="readonly")
        self.camera_combo.grid(row=1, column=1, pady=(5, 0))
        self.refresh_cameras()
        
        # OBS controls  
        obs_frame = ttk.LabelFrame(self.control_frame, text="OBS Studio", padding="5")
        obs_frame.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.obs_button = ttk.Button(
            obs_frame, text="Connect OBS",
            command=self.toggle_obs_connection
        )
        self.obs_button.grid(row=0, column=0, pady=2)
        
        self.obs_status = ttk.Label(obs_frame, text="●", foreground="red")
        self.obs_status.grid(row=0, column=1, padx=(10, 0))
        
        # Scene controls
        ttk.Label(obs_frame, text="Current Scene:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        scene_label = ttk.Label(obs_frame, textvariable=self.current_scene, font=("", 9, "bold"))
        scene_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Auto-switching controls
        auto_frame = ttk.LabelFrame(self.control_frame, text="Auto Switching", padding="5")
        auto_frame.grid(row=0, column=2, padx=(0, 10), sticky=(tk.W, tk.E, tk.N))
        
        self.auto_switch_button = ttk.Button(
            auto_frame, text="Enable Auto Switch",
            command=self.toggle_auto_switching
        )
        self.auto_switch_button.grid(row=0, column=0, pady=2)
        
        self.auto_status = ttk.Label(auto_frame, text="●", foreground="red")
        self.auto_status.grid(row=0, column=1, padx=(10, 0))
        
        # Emotion display
        emotion_frame = ttk.LabelFrame(self.control_frame, text="Current Emotion", padding="5")
        emotion_frame.grid(row=0, column=3, sticky=(tk.W, tk.E, tk.N))
        
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
        
        confidence_label = ttk.Label(emotion_frame, text="Confidence")
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
            preview_controls, text="Full Window",
            command=self.open_preview_window
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            preview_controls, text="Snapshot",
            command=self.take_snapshot
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # FPS display
        fps_label = ttk.Label(preview_controls, textvariable=self.fps_counter)
        fps_label.pack(side=tk.RIGHT)
        
        # Placeholder text
        self.preview_canvas.create_text(
            self.config.preview_size[0]//2, 
            self.config.preview_size[1]//2,
            text="No Video Feed", fill="white", font=("", 12)
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
        info_notebook.add(emotion_tab, text="Emotions")
        
        self.emotion_listbox = tk.Listbox(emotion_tab, height=8)
        self.emotion_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        emotion_scrollbar = ttk.Scrollbar(emotion_tab, orient=tk.VERTICAL)
        emotion_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.emotion_listbox.config(yscrollcommand=emotion_scrollbar.set)
        emotion_scrollbar.config(command=self.emotion_listbox.yview)
        
        # Scene History tab
        scene_tab = ttk.Frame(info_notebook)
        info_notebook.add(scene_tab, text="Scenes")
        
        self.scene_listbox = tk.Listbox(scene_tab, height=8)
        self.scene_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scene_scrollbar = ttk.Scrollbar(scene_tab, orient=tk.VERTICAL)
        scene_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scene_listbox.config(yscrollcommand=scene_scrollbar.set)
        scene_scrollbar.config(command=self.scene_listbox.yview)
        
        # Performance tab
        perf_tab = ttk.Frame(info_notebook)
        info_notebook.add(perf_tab, text="Performance")
        
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
                        self.camera_button.config(text="Stop Camera")
                        self.camera_status.config(foreground="green")
                        
                        # Start processing thread
                        self.running = True
                        self.update_thread = threading.Thread(target=self.processing_loop, daemon=True)
                        self.update_thread.start()
                        
                        self.logger.info("Camera and emotion detection started")
                    else:
                        messagebox.showerror("Camera Error", "Failed to start camera")
                else:
                    messagebox.showwarning("Camera Warning", "Please select a camera device")
                    
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            messagebox.showerror("Camera Error", f"Failed to start camera: {e}")
    
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
                    self.camera_manager.stop_camera()
                
                self.camera_running.set(False)
                self.camera_button.config(text="Start Camera")
                self.camera_status.config(foreground="red")
                
                # Clear preview
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(
                    self.config.preview_size[0]//2,
                    self.config.preview_size[1]//2,
                    text="No Video Feed", fill="white", font=("", 12)
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
                # Run connection in background thread
                def connect_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(self.obs_manager.connect())
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self._update_obs_status(success))
                
                threading.Thread(target=connect_async, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error connecting to OBS: {e}")
            messagebox.showerror("OBS Error", f"Failed to connect to OBS: {e}")
    
    def disconnect_obs(self) -> None:
        """Disconnect from OBS Studio"""
        try:
            if self.obs_connected.get():
                def disconnect_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    loop.run_until_complete(self.obs_manager.disconnect())
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self._update_obs_status(False))
                
                threading.Thread(target=disconnect_async, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from OBS: {e}")
    
    def _update_obs_status(self, connected: bool) -> None:
        """Update OBS connection status in UI"""
        self.obs_connected.set(connected)
        if connected:
            self.obs_button.config(text="Disconnect OBS")
            self.obs_status.config(foreground="green")
            self.logger.info("OBS connected successfully")
        else:
            self.obs_button.config(text="Connect OBS")
            self.obs_status.config(foreground="red")
            self.current_scene.set("No Scene")
    
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
            self.auto_switch_button.config(text="Enable Auto Switch")
            self.auto_status.config(foreground="red")
        else:
            if self.obs_connected.get():
                self.auto_switching.set(True)
                self.auto_switch_button.config(text="Disable Auto Switch")
                self.auto_status.config(foreground="green")
            else:
                messagebox.showwarning("Auto Switch", "Please connect to OBS first")
    
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
                    
                    if results:
                        # Get dominant emotion
                        dominant = results[0]  # Assuming first result is dominant
                        emotion = dominant['emotion']
                        confidence = dominant['confidence']
                        
                        # Update UI variables
                        self.root.after(0, lambda: self._update_emotion_display(emotion, confidence))
                        
                        # Handle auto switching
                        if self.auto_switching.get() and self.obs_connected.get():
                            self._handle_auto_switching(emotion, confidence, frame)
                    
                    # Update preview
                    self.root.after(0, lambda: self._update_preview(frame))
                    
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
        self.current_emotion.set(emotion.title())
        self.emotion_confidence.set(confidence)
        
        # Add to history
        timestamp = time.strftime("%H:%M:%S")
        entry = f"{timestamp} - {emotion.title()} ({confidence:.2f})"
        
        self.emotion_listbox.insert(0, entry)
        if self.emotion_listbox.size() > 50:  # Limit history size
            self.emotion_listbox.delete(50)
        
        # Store in data
        self.emotion_history.append({
            'timestamp': time.time(),
            'emotion': emotion,
            'confidence': confidence
        })
    
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
                def switch_scene():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        self.obs_manager.switch_scene(result.recommended_scene)
                    )
                    
                    if success:
                        # Update UI
                        self.root.after(0, lambda: self._update_scene_display(result.recommended_scene))
                        
                        # Record switch
                        self.emotion_mapper.record_scene_switch(
                            self.current_scene.get(),
                            result.recommended_scene
                        )
                
                threading.Thread(target=switch_scene, daemon=True).start()
                
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
            camera_names = [f"Camera {i}: {name}" for i, name in enumerate(devices)]
            
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
        if not self.settings_dialog or not self.settings_dialog.root.winfo_exists():
            self.settings_dialog = SettingsDialog(self)
    
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
                    'preview_size': self.config.preview_size
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
                
                messagebox.showinfo("Configuration", f"Configuration saved to {filepath}")
                
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
                # This would update UI elements and settings
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
                
                if self.camera_running.get():
                    self.stop_camera()
                
                if self.obs_connected.get():
                    self.disconnect_obs()
                
                # Save configuration if enabled
                if self.config.save_layout:
                    if self.emotion_mapper:
                        self.emotion_mapper.save_configuration()
                
                # Close windows
                if self.preview_window:
                    self.preview_window.close()
                
                if self.settings_dialog:
                    self.settings_dialog.close()
                
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
    
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
