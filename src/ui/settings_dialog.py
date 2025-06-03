"""
Settings Dialog for LivePilotAI
Provides configuration interface for system settings, OBS connection, and emotion mapping parameters.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from typing import Dict, Any, Optional, Callable
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SettingsDialog:
    """
    Advanced settings dialog for LivePilotAI configuration
    
    Features:
    - OBS connection settings
    - Emotion detection parameters
    - Scene mapping configuration
    - UI preferences
    - Performance tuning
    - Profile management
    """
    
    def __init__(self, parent, settings: Dict[str, Any], callback: Optional[Callable] = None):
        """
        Initialize settings dialog
        
        Args:
            parent: Parent window
            settings: Current settings dictionary
            callback: Callback function when settings are saved
        """
        self.parent = parent
        self.settings = settings.copy()  # Work with a copy
        self.callback = callback
        self.dialog = None
        self.widgets = {}
        
        # Default settings structure
        self.default_settings = {
            'obs': {
                'host': 'localhost',
                'port': 4455,
                'password': '',
                'auto_connect': True,
                'reconnect_interval': 5,
                'timeout': 10
            },
            'emotion': {
                'confidence_threshold': 0.7,
                'update_interval': 100,
                'smoothing_factor': 0.3,
                'min_face_size': 30,
                'max_faces': 5
            },
            'scene_switching': {
                'enable_auto_switch': True,
                'switch_cooldown': 2.0,
                'transition_duration': 1000,
                'confidence_required': 0.8,
                'sustained_duration': 1.0
            },
            'ui': {
                'theme': 'dark',
                'update_fps': 30,
                'show_confidence': True,
                'show_fps': True,
                'preview_size': (640, 480),
                'emotion_colors': {
                    'happy': '#00FF00',
                    'sad': '#0080FF',
                    'angry': '#FF4444',
                    'fear': '#800080',
                    'surprise': '#FFFF00',
                    'disgust': '#008000',
                    'neutral': '#FFFFFF'
                }
            },
            'performance': {
                'max_cpu_usage': 80,
                'memory_limit_mb': 512,
                'gpu_acceleration': True,
                'threading_enabled': True,
                'cache_size': 100
            }
        }
        
        # Merge default settings with provided settings
        self._merge_defaults()
        
    def _merge_defaults(self):
        """Merge default settings with provided settings"""
        def merge_dict(default: dict, provided: dict) -> dict:
            result = default.copy()
            for key, value in provided.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.settings = merge_dict(self.default_settings, self.settings)
    
    def show(self):
        """Display the settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("LivePilotAI Settings")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create UI
        self._create_widgets()
        
        # Load current settings
        self._load_settings()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Focus on dialog
        self.dialog.focus_set()
        
    def _center_dialog(self):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create the settings dialog widgets"""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self._create_obs_tab(notebook)
        self._create_emotion_tab(notebook)
        self._create_scene_tab(notebook)
        self._create_ui_tab(notebook)
        self._create_performance_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        # Buttons
        ttk.Button(button_frame, text="Load Profile", 
                  command=self._load_profile).grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        ttk.Button(button_frame, text="Save Profile", 
                  command=self._save_profile).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_defaults).grid(row=0, column=2, padx=5, sticky=tk.W)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).grid(row=0, column=3, padx=(5, 0), sticky=tk.E)
        ttk.Button(button_frame, text="OK", 
                  command=self._on_ok).grid(row=0, column=4, padx=(5, 0), sticky=tk.E)
    
    def _create_obs_tab(self, notebook):
        """Create OBS settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="OBS Connection")
        
        # Connection settings
        conn_group = ttk.LabelFrame(frame, text="Connection Settings", padding="10")
        conn_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        conn_group.columnconfigure(1, weight=1)
        
        ttk.Label(conn_group, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['obs_host'] = ttk.Entry(conn_group)
        self.widgets['obs_host'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(conn_group, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['obs_port'] = ttk.Spinbox(conn_group, from_=1, to=65535, width=10)
        self.widgets['obs_port'].grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(conn_group, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets['obs_password'] = ttk.Entry(conn_group, show="*")
        self.widgets['obs_password'].grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        self.widgets['obs_auto_connect'] = tk.BooleanVar()
        ttk.Checkbutton(conn_group, text="Auto-connect on startup", 
                       variable=self.widgets['obs_auto_connect']).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Advanced settings
        adv_group = ttk.LabelFrame(frame, text="Advanced Settings", padding="10")
        adv_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        adv_group.columnconfigure(1, weight=1)
        
        ttk.Label(adv_group, text="Reconnect Interval (s):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['obs_reconnect_interval'] = ttk.Spinbox(adv_group, from_=1, to=60, width=10)
        self.widgets['obs_reconnect_interval'].grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(adv_group, text="Timeout (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['obs_timeout'] = ttk.Spinbox(adv_group, from_=1, to=30, width=10)
        self.widgets['obs_timeout'].grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Test connection button
        ttk.Button(frame, text="Test Connection", 
                  command=self._test_obs_connection).grid(row=2, column=0, pady=10)
    
    def _create_emotion_tab(self, notebook):
        """Create emotion detection settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Emotion Detection")
        
        # Detection settings
        det_group = ttk.LabelFrame(frame, text="Detection Parameters", padding="10")
        det_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        det_group.columnconfigure(1, weight=1)
        
        ttk.Label(det_group, text="Confidence Threshold:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['emotion_confidence_threshold'] = ttk.Scale(det_group, from_=0.1, to=1.0, orient=tk.HORIZONTAL)
        self.widgets['emotion_confidence_threshold'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(det_group, text="Update Interval (ms):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['emotion_update_interval'] = ttk.Spinbox(det_group, from_=50, to=1000, increment=50, width=10)
        self.widgets['emotion_update_interval'].grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(det_group, text="Smoothing Factor:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets['emotion_smoothing_factor'] = ttk.Scale(det_group, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
        self.widgets['emotion_smoothing_factor'].grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(det_group, text="Min Face Size (px):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.widgets['emotion_min_face_size'] = ttk.Spinbox(det_group, from_=10, to=200, width=10)
        self.widgets['emotion_min_face_size'].grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(det_group, text="Max Faces:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.widgets['emotion_max_faces'] = ttk.Spinbox(det_group, from_=1, to=10, width=10)
        self.widgets['emotion_max_faces'].grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
    
    def _create_scene_tab(self, notebook):
        """Create scene switching settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Scene Switching")
        
        # Auto-switching settings
        auto_group = ttk.LabelFrame(frame, text="Auto-Switching", padding="10")
        auto_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        auto_group.columnconfigure(1, weight=1)
        
        self.widgets['scene_enable_auto_switch'] = tk.BooleanVar()
        ttk.Checkbutton(auto_group, text="Enable automatic scene switching", 
                       variable=self.widgets['scene_enable_auto_switch']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(auto_group, text="Switch Cooldown (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['scene_switch_cooldown'] = ttk.Scale(auto_group, from_=0.5, to=10.0, orient=tk.HORIZONTAL)
        self.widgets['scene_switch_cooldown'].grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(auto_group, text="Transition Duration (ms):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets['scene_transition_duration'] = ttk.Spinbox(auto_group, from_=100, to=5000, increment=100, width=10)
        self.widgets['scene_transition_duration'].grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(auto_group, text="Confidence Required:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.widgets['scene_confidence_required'] = ttk.Scale(auto_group, from_=0.1, to=1.0, orient=tk.HORIZONTAL)
        self.widgets['scene_confidence_required'].grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(auto_group, text="Sustained Duration (s):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.widgets['scene_sustained_duration'] = ttk.Scale(auto_group, from_=0.1, to=5.0, orient=tk.HORIZONTAL)
        self.widgets['scene_sustained_duration'].grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
    
    def _create_ui_tab(self, notebook):
        """Create UI preferences tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="UI Preferences")
        
        # Appearance settings
        app_group = ttk.LabelFrame(frame, text="Appearance", padding="10")
        app_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        app_group.columnconfigure(1, weight=1)
        
        ttk.Label(app_group, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['ui_theme'] = ttk.Combobox(app_group, values=['light', 'dark'], state='readonly', width=15)
        self.widgets['ui_theme'].grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(app_group, text="Update FPS:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['ui_update_fps'] = ttk.Spinbox(app_group, from_=10, to=60, width=10)
        self.widgets['ui_update_fps'].grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.widgets['ui_show_confidence'] = tk.BooleanVar()
        ttk.Checkbutton(app_group, text="Show confidence values", 
                       variable=self.widgets['ui_show_confidence']).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.widgets['ui_show_fps'] = tk.BooleanVar()
        ttk.Checkbutton(app_group, text="Show FPS counter", 
                       variable=self.widgets['ui_show_fps']).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Color settings
        color_group = ttk.LabelFrame(frame, text="Emotion Colors", padding="10")
        color_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        color_group.columnconfigure(1, weight=1)
        
        self.color_buttons = {}
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        for i, emotion in enumerate(emotions):
            ttk.Label(color_group, text=f"{emotion.title()}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.color_buttons[emotion] = tk.Button(color_group, width=10, height=1,
                                                   command=lambda e=emotion: self._choose_color(e))
            self.color_buttons[emotion].grid(row=i, column=1, sticky=tk.W, padx=(5, 0), pady=2)
    
    def _create_performance_tab(self, notebook):
        """Create performance settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Performance")
        
        # Resource limits
        res_group = ttk.LabelFrame(frame, text="Resource Limits", padding="10")
        res_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        res_group.columnconfigure(1, weight=1)
        
        ttk.Label(res_group, text="Max CPU Usage (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['perf_max_cpu_usage'] = ttk.Scale(res_group, from_=10, to=100, orient=tk.HORIZONTAL)
        self.widgets['perf_max_cpu_usage'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(res_group, text="Memory Limit (MB):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['perf_memory_limit_mb'] = ttk.Spinbox(res_group, from_=128, to=2048, increment=128, width=10)
        self.widgets['perf_memory_limit_mb'].grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(res_group, text="Cache Size:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets['perf_cache_size'] = ttk.Spinbox(res_group, from_=10, to=500, increment=10, width=10)
        self.widgets['perf_cache_size'].grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Optimization settings
        opt_group = ttk.LabelFrame(frame, text="Optimizations", padding="10")
        opt_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        
        self.widgets['perf_gpu_acceleration'] = tk.BooleanVar()
        ttk.Checkbutton(opt_group, text="GPU Acceleration (if available)", 
                       variable=self.widgets['perf_gpu_acceleration']).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.widgets['perf_threading_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(opt_group, text="Multi-threading", 
                       variable=self.widgets['perf_threading_enabled']).grid(row=1, column=0, sticky=tk.W, pady=2)
    
    def _choose_color(self, emotion: str):
        """Open color chooser for emotion"""
        current_color = self.settings['ui']['emotion_colors'].get(emotion, '#FFFFFF')
        color = colorchooser.askcolor(color=current_color, title=f"Choose color for {emotion}")
        if color[1]:  # User didn't cancel
            self.settings['ui']['emotion_colors'][emotion] = color[1]
            self.color_buttons[emotion].config(bg=color[1])
    
    def _load_settings(self):
        """Load current settings into widgets"""
        # OBS settings
        self.widgets['obs_host'].insert(0, self.settings['obs']['host'])
        self.widgets['obs_port'].set(self.settings['obs']['port'])
        self.widgets['obs_password'].insert(0, self.settings['obs']['password'])
        self.widgets['obs_auto_connect'].set(self.settings['obs']['auto_connect'])
        self.widgets['obs_reconnect_interval'].set(self.settings['obs']['reconnect_interval'])
        self.widgets['obs_timeout'].set(self.settings['obs']['timeout'])
        
        # Emotion settings
        self.widgets['emotion_confidence_threshold'].set(self.settings['emotion']['confidence_threshold'])
        self.widgets['emotion_update_interval'].set(self.settings['emotion']['update_interval'])
        self.widgets['emotion_smoothing_factor'].set(self.settings['emotion']['smoothing_factor'])
        self.widgets['emotion_min_face_size'].set(self.settings['emotion']['min_face_size'])
        self.widgets['emotion_max_faces'].set(self.settings['emotion']['max_faces'])
        
        # Scene settings
        self.widgets['scene_enable_auto_switch'].set(self.settings['scene_switching']['enable_auto_switch'])
        self.widgets['scene_switch_cooldown'].set(self.settings['scene_switching']['switch_cooldown'])
        self.widgets['scene_transition_duration'].set(self.settings['scene_switching']['transition_duration'])
        self.widgets['scene_confidence_required'].set(self.settings['scene_switching']['confidence_required'])
        self.widgets['scene_sustained_duration'].set(self.settings['scene_switching']['sustained_duration'])
        
        # UI settings
        self.widgets['ui_theme'].set(self.settings['ui']['theme'])
        self.widgets['ui_update_fps'].set(self.settings['ui']['update_fps'])
        self.widgets['ui_show_confidence'].set(self.settings['ui']['show_confidence'])
        self.widgets['ui_show_fps'].set(self.settings['ui']['show_fps'])
        
        # Load emotion colors
        for emotion, color in self.settings['ui']['emotion_colors'].items():
            if emotion in self.color_buttons:
                self.color_buttons[emotion].config(bg=color)
        
        # Performance settings
        self.widgets['perf_max_cpu_usage'].set(self.settings['performance']['max_cpu_usage'])
        self.widgets['perf_memory_limit_mb'].set(self.settings['performance']['memory_limit_mb'])
        self.widgets['perf_cache_size'].set(self.settings['performance']['cache_size'])
        self.widgets['perf_gpu_acceleration'].set(self.settings['performance']['gpu_acceleration'])
        self.widgets['perf_threading_enabled'].set(self.settings['performance']['threading_enabled'])
    
    def _save_settings(self):
        """Save widget values to settings"""
        # OBS settings
        self.settings['obs']['host'] = self.widgets['obs_host'].get()
        self.settings['obs']['port'] = int(self.widgets['obs_port'].get())
        self.settings['obs']['password'] = self.widgets['obs_password'].get()
        self.settings['obs']['auto_connect'] = self.widgets['obs_auto_connect'].get()
        self.settings['obs']['reconnect_interval'] = int(self.widgets['obs_reconnect_interval'].get())
        self.settings['obs']['timeout'] = int(self.widgets['obs_timeout'].get())
        
        # Emotion settings
        self.settings['emotion']['confidence_threshold'] = float(self.widgets['emotion_confidence_threshold'].get())
        self.settings['emotion']['update_interval'] = int(self.widgets['emotion_update_interval'].get())
        self.settings['emotion']['smoothing_factor'] = float(self.widgets['emotion_smoothing_factor'].get())
        self.settings['emotion']['min_face_size'] = int(self.widgets['emotion_min_face_size'].get())
        self.settings['emotion']['max_faces'] = int(self.widgets['emotion_max_faces'].get())
        
        # Scene settings
        self.settings['scene_switching']['enable_auto_switch'] = self.widgets['scene_enable_auto_switch'].get()
        self.settings['scene_switching']['switch_cooldown'] = float(self.widgets['scene_switch_cooldown'].get())
        self.settings['scene_switching']['transition_duration'] = int(self.widgets['scene_transition_duration'].get())
        self.settings['scene_switching']['confidence_required'] = float(self.widgets['scene_confidence_required'].get())
        self.settings['scene_switching']['sustained_duration'] = float(self.widgets['scene_sustained_duration'].get())
        
        # UI settings
        self.settings['ui']['theme'] = self.widgets['ui_theme'].get()
        self.settings['ui']['update_fps'] = int(self.widgets['ui_update_fps'].get())
        self.settings['ui']['show_confidence'] = self.widgets['ui_show_confidence'].get()
        self.settings['ui']['show_fps'] = self.widgets['ui_show_fps'].get()
        
        # Performance settings
        self.settings['performance']['max_cpu_usage'] = int(self.widgets['perf_max_cpu_usage'].get())
        self.settings['performance']['memory_limit_mb'] = int(self.widgets['perf_memory_limit_mb'].get())
        self.settings['performance']['cache_size'] = int(self.widgets['perf_cache_size'].get())
        self.settings['performance']['gpu_acceleration'] = self.widgets['perf_gpu_acceleration'].get()
        self.settings['performance']['threading_enabled'] = self.widgets['perf_threading_enabled'].get()
    
    def _test_obs_connection(self):
        """Test OBS connection with current settings"""
        def test_connection():
            try:
                # Import here to avoid circular imports
                from ..obs_integration.websocket_client import OBSWebSocketClient
                
                host = self.widgets['obs_host'].get()
                port = int(self.widgets['obs_port'].get())
                password = self.widgets['obs_password'].get()
                timeout = int(self.widgets['obs_timeout'].get())
                
                # Test connection
                client = OBSWebSocketClient(host, port, password)
                success = client.connect(timeout=timeout)
                
                if success:
                    client.disconnect()
                    messagebox.showinfo("Connection Test", "OBS connection successful!")
                else:
                    messagebox.showerror("Connection Test", "Failed to connect to OBS.")
                    
            except Exception as e:
                messagebox.showerror("Connection Test", f"Connection error: {str(e)}")
        
        # Run test in separate thread
        thread = threading.Thread(target=test_connection, daemon=True)
        thread.start()
    
    def _load_profile(self):
        """Load settings from file"""
        filename = filedialog.askopenfilename(
            title="Load Settings Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge loaded settings
                self.settings = loaded_settings
                self._merge_defaults()
                
                # Reload UI
                self._clear_widgets()
                self._load_settings()
                
                messagebox.showinfo("Load Profile", "Settings profile loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Load Profile", f"Failed to load profile: {str(e)}")
    
    def _save_profile(self):
        """Save current settings to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Settings Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        
        if filename:
            try:
                # Save current widget values first
                self._save_settings()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Save Profile", "Settings profile saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Save Profile", f"Failed to save profile: {str(e)}")
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings = self.default_settings.copy()
            self._clear_widgets()
            self._load_settings()
    
    def _clear_widgets(self):
        """Clear all widget values"""
        # Clear text entries
        for key, widget in self.widgets.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, (ttk.Spinbox, ttk.Combobox)):
                widget.set('')
            elif isinstance(widget, ttk.Scale):
                widget.set(0)
            elif isinstance(widget, tk.BooleanVar):
                widget.set(False)
    
    def _on_ok(self):
        """Handle OK button click"""
        try:
            self._save_settings()
            
            if self.callback:
                self.callback(self.settings)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to save settings: {str(e)}")
    
    def _on_cancel(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


def show_settings_dialog(parent, settings: Dict[str, Any], callback: Optional[Callable] = None):
    """
    Convenience function to show settings dialog
    
    Args:
        parent: Parent window
        settings: Current settings dictionary
        callback: Callback function when settings are saved
    """
    dialog = SettingsDialog(parent, settings, callback)
    dialog.show()


if __name__ == "__main__":
    # Test the settings dialog
    import tkinter as tk
    
    def on_settings_saved(settings):
        print("Settings saved:")
        print(json.dumps(settings, indent=2))
    
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("400x300")
    
    test_settings = {
        'obs': {
            'host': 'localhost',
            'port': 4455,
            'password': 'test123'
        }
    }
    
    ttk.Button(root, text="Open Settings", 
              command=lambda: show_settings_dialog(root, test_settings, on_settings_saved)).pack(pady=20)
    
    root.mainloop()
