"""
LivePilotAI Day 5 - Main Application Entry Point
Advanced OBS integration and intelligent streaming director system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

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

try:
    # Import UI components
    from src.ui import (
        MainControlPanel, PreviewWindow, show_settings_dialog,
        SystemStatusManager, create_obs_status_panel, 
        create_ai_status_panel, create_system_status_panel,
        StatusLevel
    )
      # Import OBS integration
    from src.obs_integration.obs_manager import OBSManager
    from src.obs_integration.scene_controller import SceneController
    from src.obs_integration.emotion_mapper import EmotionMapper
    from src.obs_integration.websocket_client import OBSWebSocketClient
    
    # Import AI engine components
    from src.ai_engine.emotion_detector import EmotionDetector
    from src.ai_engine.modules.real_time_detector import RealTimeEmotionDetector
    from src.ai_engine.modules.camera_manager import CameraManager
    from src.ai_engine.modules.face_detector import FaceDetector
    
    # Import core components
    from src.core.config_manager import ConfigManager
    
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and modules are available.")
    sys.exit(1)


class LivePilotAIApp:
    """
    Main application class for LivePilotAI Day 5
    
    Features:
    - Complete GUI application with all components
    - OBS Studio integration and control
    - Real-time emotion detection and scene switching
    - System monitoring and status display
    - Configuration management
    - Multi-threaded operation
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
        
        # Configuration
        self.config_file = "livepilotai_config.json"
        self.settings = self._load_default_settings()
        
        # Runtime state
        self.is_running = False
        self.preview_thread = None
        self.emotion_thread = None
        
        logger.info("LivePilotAI Day 5 Application initialized")
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            'app': {
                'window_size': (1200, 800),
                'window_position': (100, 100),
                'auto_start_camera': True,
                'auto_connect_obs': False,
                'show_preview_window': True
            },
            'obs': {
                'host': 'localhost',
                'port': 4455,
                'password': '',
                'auto_connect': False,
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
    
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults
                self._merge_settings(self.settings, loaded_settings)
                logger.info(f"Settings loaded from {self.config_file}")
            else:
                logger.info("No configuration file found, using defaults")
                
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            messagebox.showerror("Settings Error", f"Failed to load settings: {e}")
    
    def save_settings(self):
        """Save current settings to configuration file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Settings Error", f"Failed to save settings: {e}")
    
    def _merge_settings(self, default: dict, loaded: dict):
        """Recursively merge loaded settings with defaults"""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_settings(default[key], value)
            else:
                default[key] = value
    
    def create_gui(self):
        """Create the main GUI application"""
        self.root = tk.Tk()
        self.root.title("LivePilotAI - Intelligent Streaming Director")
        
        # Set window size and position
        width, height = self.settings['app']['window_size']
        x, y = self.settings['app']['window_position']
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure root window
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main layout
        self._create_main_layout()
        
        # Set window icon (if available)
        try:
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Icon not critical
        
        logger.info("GUI created successfully")
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Settings...", command=self._load_settings_file)
        file_menu.add_command(label="Save Settings...", command=self._save_settings_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Preview Window", command=self._toggle_preview_window)
        view_menu.add_command(label="Show Status Panel", command=self._toggle_status_panel)
        view_menu.add_separator()
        view_menu.add_command(label="Preferences...", command=self._show_preferences)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test OBS Connection", command=self._test_obs_connection)
        tools_menu.add_command(label="Calibrate Camera", command=self._calibrate_camera)
        tools_menu.add_command(label="Export Status Report", command=self._export_status_report)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create the main application layout"""
        # Configure main grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        main_container.columnconfigure(0, weight=3)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Create main control panel
        self.main_panel = MainControlPanel(main_container, self.settings)
        self.main_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Create status panel container
        status_container = ttk.Frame(main_container)
        status_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_container.columnconfigure(0, weight=1)
        status_container.rowconfigure(0, weight=1)
        status_container.rowconfigure(1, weight=1)
        status_container.rowconfigure(2, weight=1)
        
        # Create status manager and panels
        self.status_manager = SystemStatusManager(self._on_status_update)
        
        # OBS Status Panel
        self.obs_status_panel = create_obs_status_panel(status_container, self.status_manager)
        self.obs_status_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # AI Engine Status Panel
        self.ai_status_panel = create_ai_status_panel(status_container, self.status_manager)
        self.ai_status_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # System Status Panel
        self.system_status_panel = create_system_status_panel(status_container, self.status_manager)
        self.system_status_panel.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Set up callbacks for main panel
        self.main_panel.set_callbacks({
            'start_camera': self._start_camera,
            'stop_camera': self._stop_camera,
            'connect_obs': self._connect_obs,
            'disconnect_obs': self._disconnect_obs,
            'toggle_auto_switch': self._toggle_auto_switch,
            'manual_scene_switch': self._manual_scene_switch,
            'show_preview': self._show_preview_window,
            'show_settings': self._show_preferences
        })
    
    def initialize_components(self):
        """Initialize all core components"""
        try:
            # Initialize camera manager
            self.camera_manager = CameraManager()
            self.status_manager.update_component_status(
                'ai_engine', 'camera', StatusLevel.OFFLINE, "Camera manager initialized"
            )
            
            # Initialize emotion detector
            self.emotion_detector = EmotionDetector()
            self.status_manager.update_component_status(
                'ai_engine', 'emotion_detector', StatusLevel.OFFLINE, "Emotion detector ready"
            )
              # Initialize face detector
            face_detector = FaceDetector()
            self.status_manager.update_component_status(
                'ai_engine', 'face_detector', StatusLevel.OFFLINE, "Face detector ready"
            )
            
            # Initialize real-time detector (includes its own camera manager and components)
            self.real_time_detector = RealTimeEmotionDetector()
            self.status_manager.update_component_status(
                'ai_engine', 'processing', StatusLevel.OFFLINE, "Real-time processor ready"
            )
            
            # Initialize OBS components
            self.obs_manager = OBSManager(
                host=self.settings['obs']['host'],
                port=self.settings['obs']['port'],
                password=self.settings['obs']['password']
            )
            self.status_manager.update_component_status(
                'obs', 'connection', StatusLevel.OFFLINE, "OBS manager initialized"
            )
            
            # Initialize emotion mapper
            self.emotion_mapper = EmotionMapper()
            self.status_manager.update_component_status(
                'obs', 'scenes', StatusLevel.OFFLINE, "Emotion mapper ready"
            )
            
            # Initialize scene controller
            self.scene_controller = SceneController(self.obs_manager, self.emotion_mapper)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components: {e}")
    
    def start_application(self):
        """Start the main application"""
        try:
            # Load settings
            self.load_settings()
            
            # Create GUI
            self.create_gui()
            
            # Initialize components
            self.initialize_components()
            
            # Auto-start features if configured
            if self.settings['app']['auto_start_camera']:
                self.root.after(1000, self._start_camera)
            
            if self.settings['app']['auto_connect_obs']:
                self.root.after(2000, self._connect_obs)
            
            if self.settings['app']['show_preview_window']:
                self.root.after(3000, self._show_preview_window)
            
            # Start status monitoring
            self._start_status_monitoring()
            
            self.is_running = True
            logger.info("LivePilotAI Day 5 application started successfully")
            
            # Start GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            messagebox.showerror("Startup Error", f"Failed to start application: {e}")
    
    def _start_camera(self):
        """Start camera capture"""
        try:
            if not self.camera_manager:
                raise Exception("Camera manager not initialized")
            
            success = self.camera_manager.start_camera()
            if success:
                self.status_manager.update_component_status(
                    'ai_engine', 'camera', StatusLevel.ACTIVE, "Camera active"
                )
                logger.info("Camera started successfully")
            else:
                self.status_manager.update_component_status(
                    'ai_engine', 'camera', StatusLevel.ERROR, "Failed to start camera"
                )
                
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.status_manager.update_component_status(
                'ai_engine', 'camera', StatusLevel.ERROR, f"Camera error: {str(e)}"
            )
    
    def _stop_camera(self):
        """Stop camera capture"""
        try:
            if self.camera_manager:
                self.camera_manager.stop_camera()
                self.status_manager.update_component_status(
                    'ai_engine', 'camera', StatusLevel.OFFLINE, "Camera stopped"
                )
                logger.info("Camera stopped")
                
        except Exception as e:
            logger.error(f"Failed to stop camera: {e}")
    
    def _connect_obs(self):
        """Connect to OBS Studio"""
        try:
            if not self.obs_manager:
                raise Exception("OBS manager not initialized")
            
            # Run connection in separate thread
            def connect_thread():
                try:
                    self.status_manager.update_component_status(
                        'obs', 'connection', StatusLevel.CONNECTING, "Connecting to OBS..."
                    )
                    
                    success = asyncio.run(self.obs_manager.connect())
                    if success:
                        self.status_manager.update_component_status(
                            'obs', 'connection', StatusLevel.ONLINE, "Connected to OBS"
                        )
                        self.status_manager.update_component_status(
                            'obs', 'websocket', StatusLevel.ACTIVE, "WebSocket active"
                        )
                        logger.info("Connected to OBS successfully")
                    else:
                        self.status_manager.update_component_status(
                            'obs', 'connection', StatusLevel.ERROR, "Failed to connect"
                        )
                        
                except Exception as e:
                    self.status_manager.update_component_status(
                        'obs', 'connection', StatusLevel.ERROR, f"Connection error: {str(e)}"
                    )
                    logger.error(f"OBS connection failed: {e}")
            
            thread = threading.Thread(target=connect_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to connect to OBS: {e}")
    
    def _disconnect_obs(self):
        """Disconnect from OBS Studio"""
        try:
            if self.obs_manager:
                asyncio.run(self.obs_manager.disconnect())
                self.status_manager.update_component_status(
                    'obs', 'connection', StatusLevel.OFFLINE, "Disconnected from OBS"
                )
                self.status_manager.update_component_status(
                    'obs', 'websocket', StatusLevel.OFFLINE, "WebSocket inactive"
                )
                logger.info("Disconnected from OBS")
                
        except Exception as e:
            logger.error(f"Failed to disconnect from OBS: {e}")
    
    def _toggle_auto_switch(self, enabled: bool):
        """Toggle automatic scene switching"""
        if self.scene_controller:
            self.scene_controller.set_auto_switching(enabled)
            status = "Auto-switching enabled" if enabled else "Auto-switching disabled"
            self.status_manager.update_component_status(
                'obs', 'scenes', StatusLevel.ACTIVE if enabled else StatusLevel.ONLINE, status
            )
    
    def _manual_scene_switch(self, scene_name: str):
        """Manually switch to a scene"""
        if self.scene_controller:
            asyncio.run(self.scene_controller.switch_scene(scene_name, "Manual switch"))
    
    def _show_preview_window(self):
        """Show or create preview window"""
        if not self.preview_window:
            self.preview_window = PreviewWindow(self.root, self.real_time_detector)
            self.preview_window.show()
        else:
            self.preview_window.focus()
    
    def _toggle_preview_window(self):
        """Toggle preview window visibility"""
        if self.preview_window and self.preview_window.is_visible():
            self.preview_window.hide()
        else:
            self._show_preview_window()
    
    def _toggle_status_panel(self):
        """Toggle status panel visibility"""
        # Implementation for toggling status panel
        pass
    
    def _show_preferences(self):
        """Show preferences/settings dialog"""
        def on_settings_saved(new_settings):
            self.settings = new_settings
            self.save_settings()
            logger.info("Settings updated")
        
        show_settings_dialog(self.root, self.settings, on_settings_saved)
    
    def _start_status_monitoring(self):
        """Start system status monitoring"""
        def monitor_system():
            import psutil
            return {
                'panel': 'system',
                'component': 'cpu',
                'level': StatusLevel.ONLINE if psutil.cpu_percent() < 80 else StatusLevel.WARNING,
                'message': f"CPU: {psutil.cpu_percent():.1f}%",
                'details': {'value': psutil.cpu_percent(), 'unit': '%'}
            }
        
        def monitor_memory():
            import psutil
            memory = psutil.virtual_memory()
            return {
                'panel': 'system',
                'component': 'memory',
                'level': StatusLevel.ONLINE if memory.percent < 80 else StatusLevel.WARNING,
                'message': f"Memory: {memory.percent:.1f}%",
                'details': {'value': memory.percent, 'unit': '%'}
            }
        
        monitor_functions = {
            'system_cpu': monitor_system,
            'system_memory': monitor_memory
        }
        
        self.status_manager.start_monitoring(monitor_functions)
    
    def _on_status_update(self, panel_name, component_name, level, message, details):
        """Handle status updates"""
        logger.debug(f"Status update: {panel_name}.{component_name} = {level.name}: {message}")
    
    def _test_obs_connection(self):
        """Test OBS connection"""
        self._connect_obs()
    
    def _calibrate_camera(self):
        """Run camera calibration"""
        messagebox.showinfo("Camera Calibration", "Camera calibration feature coming soon!")
    
    def _export_status_report(self):
        """Export system status report"""
        try:
            report = self.status_manager.export_status_report()
            filename = f"livepilotai_status_report_{int(time.time())}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Complete", f"Status report saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export status report: {e}")
    
    def _load_settings_file(self):
        """Load settings from file dialog"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Load Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                messagebox.showinfo("Settings Loaded", "Settings loaded successfully!")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load settings: {e}")
    
    def _save_settings_file(self):
        """Save settings to file dialog"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Save Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Settings Saved", "Settings saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save settings: {e}")
    
    def _show_user_guide(self):
        """Show user guide"""
        guide_text = """
LivePilotAI - User Guide

1. Camera Setup:
   - Click 'Start Camera' to begin video capture
   - Ensure good lighting for emotion detection
   
2. OBS Connection:
   - Start OBS Studio first
   - Enable WebSocket server in OBS Tools menu
   - Click 'Connect to OBS' in LivePilotAI
   
3. Scene Switching:
   - Create scenes in OBS for different emotions
   - Enable 'Auto Switch' for automatic scene changes
   - Monitor emotion detection in the preview window
   
4. Configuration:
   - Use View > Preferences to adjust settings
   - Save/load configuration profiles via File menu
   
5. Monitoring:
   - Check status panels for system health
   - View detailed information by clicking status indicators
        """
        
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        
        text_widget = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """LivePilotAI - Intelligent Streaming Director
Version: Day 5 Release
Date: 2025年6月4日

An AI-powered streaming assistant that automatically 
switches OBS scenes based on real-time emotion detection.

Features:
• Real-time emotion detection
• Automatic OBS scene switching  
• Advanced GUI control panel
• System monitoring and status
• Configurable emotion mapping

Developed for the 2025 AI Innovation Award"""
        
        messagebox.showinfo("About LivePilotAI", about_text)
    
    def _on_closing(self):
        """Handle application closing"""
        try:
            # Save current settings
            self.save_settings()
            
            # Stop monitoring
            if self.status_manager:
                self.status_manager.stop_monitoring()
            
            # Stop camera
            if self.camera_manager:
                self.camera_manager.stop_camera()
            
            # Disconnect OBS
            if self.obs_manager:
                asyncio.run(self.obs_manager.disconnect())
            
            # Close preview window
            if self.preview_window:
                self.preview_window.close()
            
            self.is_running = False
            logger.info("LivePilotAI application closed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        finally:
            self.root.destroy()


def main():
    """Main entry point"""
    try:
        # Create and start application
        app = LivePilotAIApp()
        app.start_application()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Application error: {e}")
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
