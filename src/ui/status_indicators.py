"""
Status Indicators for LivePilotAI
Provides visual status displays for system components and real-time monitoring.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
import time
import threading
from enum import Enum
from dataclasses import dataclass
import logging
from ..utils.i18n import i18n

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StatusLevel(Enum):
    """Status levels with corresponding colors and priorities"""
    UNKNOWN = ("gray", "❓", 0)
    OFFLINE = ("#FF4444", "⭕", 1)
    ERROR = ("#FF0000", "❌", 2)
    WARNING = ("#FFA500", "⚠️", 3)
    CONNECTING = ("#FFFF00", "🔄", 4)
    ONLINE = ("#00FF00", "✅", 5)
    ACTIVE = ("#00FF88", "🟢", 6)
    
    def __init__(self, color: str, icon: str, priority: int):
        self.color = color
        self.icon = icon
        self.priority = priority


@dataclass
class StatusInfo:
    """Information about a system component status"""
    name: str
    level: StatusLevel
    message: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None


class StatusIndicator(ttk.Frame):
    """
    Individual status indicator widget
    
    Features:
    - Color-coded status display
    - Icon and text representation
    - Tooltip with detailed information
    - Click callback for actions
    - Blinking animation for alerts
    """
    
    def __init__(self, parent, name: str, callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.name = name
        self.callback = callback
        self.status_info = StatusInfo(name, StatusLevel.UNKNOWN, i18n.get("initializing"), time.time())
        self.is_blinking = False
        self.blink_job = None
        
        self._create_widgets()
        self._create_tooltip()
        
    def _create_widgets(self):
        """Create the indicator widgets"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Status icon label
        self.icon_label = tk.Label(self, font=("Arial", 12), width=3, relief="sunken", bd=1)
        self.icon_label.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status text label
        self.text_label = tk.Label(self, font=("Arial", 9), anchor="w", relief="sunken", bd=1)
        self.text_label.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind click events
        if self.callback:
            self.icon_label.bind("<Button-1>", lambda e: self.callback(self.name, self.status_info))
            self.text_label.bind("<Button-1>", lambda e: self.callback(self.name, self.status_info))
            self.icon_label.bind("<Enter>", lambda e: self.icon_label.config(cursor="hand2"))
            self.text_label.bind("<Enter>", lambda e: self.text_label.config(cursor="hand2"))
            self.icon_label.bind("<Leave>", lambda e: self.icon_label.config(cursor=""))
            self.text_label.bind("<Leave>", lambda e: self.text_label.config(cursor=""))
        
        # Initial update
        self._update_display()
    
    def _create_tooltip(self):
        """Create tooltip for detailed status information"""
        self.tooltip_window = None
        
        def show_tooltip(event):
            if self.tooltip_window:
                return
                
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            self.tooltip_window = tooltip
            
            # Tooltip content
            content = f"{i18n.get('component')}: {self.status_info.name}\n"
            content += f"{i18n.get('status')}: {self.status_info.level.name}\n"
            content += f"{i18n.get('message')}: {self.status_info.message}\n"
            content += f"{i18n.get('updated')}: {time.strftime('%H:%M:%S', time.localtime(self.status_info.timestamp))}"
            
            if self.status_info.details:
                content += f"\n\n{i18n.get('details')}:\n"
                for key, value in self.status_info.details.items():
                    content += f"  {key}: {value}\n"
            
            label = tk.Label(tooltip, text=content, justify=tk.LEFT, background="#FFFFDD", 
                           relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            
        def hide_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        
        self.icon_label.bind("<Enter>", show_tooltip)
        self.text_label.bind("<Enter>", show_tooltip)
        self.icon_label.bind("<Leave>", hide_tooltip)
        self.text_label.bind("<Leave>", hide_tooltip)
    
    def update_status(self, level: StatusLevel, message: str, details: Optional[Dict[str, Any]] = None):
        """Update the status of this indicator"""
        self.status_info = StatusInfo(self.name, level, message, time.time(), details)
        self._update_display()
        
        # Start blinking for errors and warnings
        if level in [StatusLevel.ERROR, StatusLevel.WARNING] and not self.is_blinking:
            self._start_blinking()
        elif level not in [StatusLevel.ERROR, StatusLevel.WARNING] and self.is_blinking:
            self._stop_blinking()
    
    def _update_display(self):
        """Update the visual display"""
        level = self.status_info.level
        
        # Update icon
        self.icon_label.config(text=level.icon, bg=level.color, fg="white" if level.color.startswith("#") else "black")
        
        # Update text with truncation
        display_text = f"{self.name}: {self.status_info.message}"
        if len(display_text) > 40:
            display_text = display_text[:37] + "..."
        
        self.text_label.config(text=display_text, bg=level.color, fg="white" if level.color.startswith("#") else "black")
    
    def _start_blinking(self):
        """Start blinking animation"""
        if self.is_blinking:
            return
            
        self.is_blinking = True
        self._blink()
    
    def _stop_blinking(self):
        """Stop blinking animation"""
        self.is_blinking = False
        if self.blink_job:
            self.after_cancel(self.blink_job)
            self.blink_job = None
        self._update_display()  # Restore normal display
    
    def _blink(self):
        """Blink animation implementation"""
        if not self.is_blinking:
            return
        
        # Toggle between normal and dimmed colors
        current_bg = self.icon_label.cget("bg")
        if current_bg == self.status_info.level.color:
            # Dim the color
            dim_color = "#666666"
            self.icon_label.config(bg=dim_color)
            self.text_label.config(bg=dim_color)
        else:
            # Restore normal color
            self._update_display()
        
        # Schedule next blink
        self.blink_job = self.after(500, self._blink)


class StatusPanel(ttk.Frame):
    """
    Panel containing multiple status indicators
    
    Features:
    - Organized layout of status indicators
    - Automatic status updates
    - Priority-based sorting
    - Collapse/expand functionality
    - Status history logging
    """
    
    def __init__(self, parent, title: str = "System Status", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title if title != "System Status" else i18n.get("system_status")
        self.indicators: Dict[str, StatusIndicator] = {}
        self.is_collapsed = False
        self.status_history: Dict[str, list] = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))
        header_frame.columnconfigure(1, weight=1)
        
        # Collapse/expand button
        self.collapse_button = ttk.Button(header_frame, text="▼", width=3,
                                         command=self._toggle_collapse)
        self.collapse_button.grid(row=0, column=0, padx=(0, 5))
        
        # Title label
        self.title_label = ttk.Label(header_frame, text=self.title, font=("Arial", 10, "bold"))
        self.title_label.grid(row=0, column=1, sticky=tk.W)
        
        # Status count label
        self.count_label = ttk.Label(header_frame, text="(0 components)", font=("Arial", 8))
        self.count_label.grid(row=0, column=2, sticky=tk.E)
        
        # Indicators frame
        self.indicators_frame = ttk.Frame(self)
        self.indicators_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.indicators_frame.columnconfigure(0, weight=1)
    
    def add_indicator(self, name: str, callback: Optional[Callable] = None) -> StatusIndicator:
        """Add a new status indicator"""
        if name in self.indicators:
            return self.indicators[name]
        
        indicator = StatusIndicator(self.indicators_frame, name, callback)
        self.indicators[name] = indicator
        self.status_history[name] = []
        
        self._layout_indicators()
        self._update_count()
        
        return indicator
    
    def remove_indicator(self, name: str):
        """Remove a status indicator"""
        if name in self.indicators:
            self.indicators[name].destroy()
            del self.indicators[name]
            if name in self.status_history:
                del self.status_history[name]
            
            self._layout_indicators()
            self._update_count()
    
    def update_status(self, name: str, level: StatusLevel, message: str, details: Optional[Dict[str, Any]] = None):
        """Update status for a specific indicator"""
        if name not in self.indicators:
            self.add_indicator(name)
        
        indicator = self.indicators[name]
        indicator.update_status(level, message, details)
        
        # Log to history
        self.status_history[name].append({
            'timestamp': time.time(),
            'level': level.name,
            'message': message,
            'details': details
        })
        
        # Keep only last 100 entries per indicator
        if len(self.status_history[name]) > 100:
            self.status_history[name] = self.status_history[name][-100:]
    
    def get_status(self, name: str) -> Optional[StatusInfo]:
        """Get current status for an indicator"""
        if name in self.indicators:
            return self.indicators[name].status_info
        return None
    
    def get_all_statuses(self) -> Dict[str, StatusInfo]:
        """Get all current statuses"""
        return {name: indicator.status_info for name, indicator in self.indicators.items()}
    
    def get_status_history(self, name: str) -> list:
        """Get status history for an indicator"""
        return self.status_history.get(name, [])
    
    def _layout_indicators(self):
        """Layout indicators in priority order"""
        # Sort indicators by status priority (highest first)
        sorted_indicators = sorted(self.indicators.items(), 
                                 key=lambda x: x[1].status_info.level.priority, 
                                 reverse=True)
        
        # Re-grid all indicators
        for i, (name, indicator) in enumerate(sorted_indicators):
            indicator.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=1)
            self.indicators_frame.rowconfigure(i, weight=0)
    
    def _update_count(self):
        """Update the component count display"""
        total = len(self.indicators)
        online = sum(1 for indicator in self.indicators.values() 
                    if indicator.status_info.level in [StatusLevel.ONLINE, StatusLevel.ACTIVE])
        error = sum(1 for indicator in self.indicators.values() 
                   if indicator.status_info.level == StatusLevel.ERROR)
        
        if error > 0:
            count_text = i18n.get("components_error").format(total=total, error=error)
            self.count_label.config(foreground="red")
        elif online == total and total > 0:
            count_text = i18n.get("components_all_online").format(total=total)
            self.count_label.config(foreground="green")
        else:
            count_text = i18n.get("components_count").format(total=total, online=online)
            self.count_label.config(foreground="black")
        
        self.count_label.config(text=count_text)
    
    def _toggle_collapse(self):
        """Toggle collapse/expand state"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.indicators_frame.grid_remove()
            self.collapse_button.config(text="▶")
        else:
            self.indicators_frame.grid()
            self.collapse_button.config(text="▼")


class SystemStatusManager:
    """
    Manager for all system status indicators
    
    Features:
    - Centralized status management
    - Automatic status updates
    - Component health monitoring
    - Performance tracking
    - Status notifications
    """
    
    def __init__(self, update_callback: Optional[Callable] = None):
        self.panels: Dict[str, StatusPanel] = {}
        self.update_callback = update_callback
        self.monitoring_thread = None
        self.is_monitoring = False
        self.monitor_interval = 1.0  # seconds
        
        # Component status cache
        self.component_stats: Dict[str, Dict[str, Any]] = {}
        
    def create_panel(self, parent, panel_name: str, title: str = None) -> StatusPanel:
        """Create a new status panel"""
        if title is None:
            title = panel_name.replace('_', ' ').title()
        
        panel = StatusPanel(parent, title)
        self.panels[panel_name] = panel
        return panel
    
    def get_panel(self, panel_name: str) -> Optional[StatusPanel]:
        """Get a status panel by name"""
        return self.panels.get(panel_name)
    
    def update_component_status(self, panel_name: str, component_name: str, 
                              level: StatusLevel, message: str, details: Optional[Dict[str, Any]] = None):
        """Update status for a component in a specific panel"""
        if panel_name in self.panels:
            self.panels[panel_name].update_status(component_name, level, message, details)
            
            # Cache component stats
            if panel_name not in self.component_stats:
                self.component_stats[panel_name] = {}
            
            self.component_stats[panel_name][component_name] = {
                'level': level,
                'message': message,
                'timestamp': time.time(),
                'details': details
            }
            
            # Notify callback
            if self.update_callback:
                self.update_callback(panel_name, component_name, level, message, details)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        total_components = 0
        status_counts = {level.name: 0 for level in StatusLevel}
        error_components = []
        warning_components = []
        
        for panel_name, panel in self.panels.items():
            statuses = panel.get_all_statuses()
            total_components += len(statuses)
            
            for component_name, status_info in statuses.items():
                status_counts[status_info.level.name] += 1
                
                if status_info.level == StatusLevel.ERROR:
                    error_components.append(f"{panel_name}.{component_name}")
                elif status_info.level == StatusLevel.WARNING:
                    warning_components.append(f"{panel_name}.{component_name}")
        
        # Calculate health score (0-100)
        if total_components == 0:
            health_score = 100
        else:
            online_count = status_counts.get('ONLINE', 0) + status_counts.get('ACTIVE', 0)
            health_score = int((online_count / total_components) * 100)
        
        return {
            'total_components': total_components,
            'health_score': health_score,
            'status_counts': status_counts,
            'error_components': error_components,
            'warning_components': warning_components,
            'timestamp': time.time()
        }
    
    def start_monitoring(self, monitor_functions: Dict[str, Callable] = None):
        """Start automatic status monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_functions = monitor_functions or {}
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    # Run custom monitor functions
                    for name, func in self.monitor_functions.items():
                        try:
                            result = func()
                            if isinstance(result, dict) and 'panel' in result and 'component' in result:
                                self.update_component_status(
                                    result['panel'],
                                    result['component'], 
                                    result.get('level', StatusLevel.UNKNOWN),
                                    result.get('message', 'Monitored'),
                                    result.get('details')
                                )
                        except Exception as e:
                            logger.error(f"Monitor function {name} failed: {e}")
                    
                    time.sleep(self.monitor_interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    time.sleep(self.monitor_interval)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("System status monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic status monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        logger.info("System status monitoring stopped")
    
    def export_status_report(self) -> Dict[str, Any]:
        """Export comprehensive status report"""
        report = {
            'timestamp': time.time(),
            'system_health': self.get_system_health(),
            'panels': {}
        }
        
        for panel_name, panel in self.panels.items():
            panel_data = {
                'title': panel.title,
                'component_count': len(panel.indicators),
                'components': {}
            }
            
            for component_name, indicator in panel.indicators.items():
                status_info = indicator.status_info
                panel_data['components'][component_name] = {
                    'status': status_info.level.name,
                    'message': status_info.message,
                    'timestamp': status_info.timestamp,
                    'details': status_info.details,
                    'history': panel.get_status_history(component_name)[-10:]  # Last 10 entries
                }
            
            report['panels'][panel_name] = panel_data
        
        return report


# Convenience functions for common status updates
def create_obs_status_panel(parent, status_manager: SystemStatusManager) -> StatusPanel:
    """Create a pre-configured OBS status panel"""
    panel = status_manager.create_panel(parent, 'obs', i18n.get('status_obs_studio'))
    
    # Add common OBS indicators
    panel.add_indicator('connection')
    panel.add_indicator('websocket')
    panel.add_indicator('scenes')
    panel.add_indicator('sources')
    
    return panel


def create_ai_status_panel(parent, status_manager: SystemStatusManager) -> StatusPanel:
    """Create a pre-configured AI Engine status panel"""
    panel = status_manager.create_panel(parent, 'ai_engine', i18n.get('status_ai_engine'))
    
    # Add common AI indicators
    panel.add_indicator('emotion_detector')
    panel.add_indicator('face_detector')
    panel.add_indicator('camera')
    panel.add_indicator('processing')
    
    return panel


def create_system_status_panel(parent, status_manager: SystemStatusManager) -> StatusPanel:
    """Create a pre-configured System status panel"""
    panel = status_manager.create_panel(parent, 'system', i18n.get('status_system_resources'))
    
    # Add common system indicators
    panel.add_indicator('cpu')
    panel.add_indicator('memory')
    panel.add_indicator('gpu')
    panel.add_indicator('disk')
    
    return panel


if __name__ == "__main__":
    # Test the status indicators
    import tkinter as tk
    import random
    
    def test_callback(component_name, status_info):
        print(f"Clicked on {component_name}: {status_info.message}")
    
    def update_callback(panel_name, component_name, level, message, details):
        print(f"Status update: {panel_name}.{component_name} = {level.name}: {message}")
    
    def simulate_status_updates(status_manager):
        """Simulate random status updates for testing"""
        def update_loop():
            components = [
                ('obs', 'connection'),
                ('obs', 'websocket'),
                ('ai_engine', 'emotion_detector'),
                ('ai_engine', 'camera'),
                ('system', 'cpu'),
                ('system', 'memory')
            ]
            
            levels = list(StatusLevel)
            messages = [
                "Operating normally",
                "High load detected",
                "Connection timeout", 
                "Processing frame",
                "Waiting for input",
                "Error occurred"
            ]
            
            while True:
                panel_name, component_name = random.choice(components)
                level = random.choice(levels)
                message = random.choice(messages)
                details = {'value': random.randint(0, 100), 'unit': '%'}
                
                status_manager.update_component_status(panel_name, component_name, level, message, details)
                time.sleep(2)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    # Create test window
    root = tk.Tk()
    root.title("Status Indicators Test")
    root.geometry("600x800")
    
    # Create status manager
    status_manager = SystemStatusManager(update_callback)
    
    # Create test panels
    obs_panel = create_obs_status_panel(root, status_manager)
    obs_panel.pack(fill=tk.X, padx=10, pady=5)
    
    ai_panel = create_ai_status_panel(root, status_manager)
    ai_panel.pack(fill=tk.X, padx=10, pady=5)
    
    system_panel = create_system_status_panel(root, status_manager)
    system_panel.pack(fill=tk.X, padx=10, pady=5)
    
    # Start simulated updates
    simulate_status_updates(status_manager)
    
    # Health summary
    def show_health():
        health = status_manager.get_system_health()
        print("System Health:", health)
    
    ttk.Button(root, text="Show Health Summary", command=show_health).pack(pady=10)
    
    root.mainloop()
