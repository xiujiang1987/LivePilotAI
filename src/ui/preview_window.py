"""
preview_window.py - Real-time Preview Window

This module provides a dedicated preview window for full-screen emotion detection 
monitoring with enhanced visualization features.

Author: LivePilotAI Development Team
Date: 2024-12-19
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import time
import threading
import logging
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from ..utils.i18n import i18n


@dataclass
class PreviewConfig:
    """Configuration for preview window"""
    window_title: str = "LivePilotAI - Live Preview"
    window_size: tuple = (800, 600)
    fullscreen_mode: bool = False
    show_emotion_overlay: bool = True
    show_face_boxes: bool = True
    show_confidence_bars: bool = True
    show_fps_counter: bool = True
    show_timestamp: bool = True
    overlay_opacity: float = 0.8
    face_box_color: tuple = (0, 255, 0)  # Green
    emotion_colors: Dict[str, tuple] = None
    font_size: int = 16
    update_interval: int = 16  # ~60 FPS


class PreviewWindow:
    """
    Dedicated preview window for real-time emotion detection monitoring
    """
    
    def __init__(self, main_panel, config: Optional[PreviewConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.main_panel = main_panel
        self.config = config or PreviewConfig()
        
        # Initialize emotion colors if not provided
        if self.config.emotion_colors is None:
            self.config.emotion_colors = {
                'happy': (0, 255, 0),      # Green
                'sad': (255, 0, 0),        # Red
                'surprise': (255, 255, 0), # Yellow
                'neutral': (128, 128, 128),# Gray
                'angry': (255, 0, 255),    # Magenta
                'fear': (255, 165, 0),     # Orange
                'disgust': (128, 0, 128)   # Purple
            }
        
        # UI components
        self.root: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.control_frame: Optional[ttk.Frame] = None
        
        # Data tracking
        self.current_frame: Optional[np.ndarray] = None
        self.current_emotions: List[Dict[str, Any]] = []
        self.fps_history: List[float] = []
        self.last_update_time: float = time.time()
        
        # Threading
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Font
        self.font = None
        self._init_font()
        
        # Setup window
        self._setup_window()
        
        # State variables (initialized after window creation to bind to correct master)
        self.is_fullscreen = tk.BooleanVar(master=self.root, value=self.config.fullscreen_mode)
        self.show_overlays = tk.BooleanVar(master=self.root, value=self.config.show_emotion_overlay)
        self.show_faces = tk.BooleanVar(master=self.root, value=self.config.show_face_boxes)
        self.show_confidence = tk.BooleanVar(master=self.root, value=self.config.show_confidence_bars)
        self.show_fps = tk.BooleanVar(master=self.root, value=self.config.show_fps_counter)
        self.show_time = tk.BooleanVar(master=self.root, value=self.config.show_timestamp)
        
        self._setup_ui()
        self._start_update_loop()
        
        self.logger.info("PreviewWindow initialized")
    
    def _init_font(self) -> None:
        """Initialize font for text drawing"""
        try:
            font_path = "arial.ttf"
            if os.name == 'nt':
                # Use absolute path for Windows font to ensure it's found
                font_path = "C:/Windows/Fonts/msjh.ttc" # Microsoft JhengHei
            
            self.font = ImageFont.truetype(font_path, 20)
        except Exception as e:
            self.logger.warning(f"Failed to load custom font: {e}, using default")
            self.font = ImageFont.load_default()

    def _setup_window(self) -> None:
        """Setup the preview window"""
        self.root = tk.Toplevel(self.main_panel.root)
        
        # Localize title if it matches default
        title = self.config.window_title
        if title == "LivePilotAI - Live Preview":
            title = i18n.get("preview_title")
        self.root.title(title)
        
        self.root.geometry(f"{self.config.window_size[0]}x{self.config.window_size[1]}")
        
        # Window configuration
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Bind events
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<Button-1>', self._on_click)
        self.root.bind('<Configure>', self._on_resize)
        
        # Focus window
        self.root.focus_set()
    
    def _setup_ui(self) -> None:
        """Setup the user interface"""
        # Main canvas for video display
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel (initially hidden)
        self.control_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self._setup_controls()
        
        # Initially hide controls
        self._hide_controls()
        
        # Bind canvas events
        self.canvas.bind('<Motion>', self._on_mouse_motion)
        self.canvas.bind('<Leave>', self._on_mouse_leave)
    
    def _setup_controls(self) -> None:
        """Setup control panel"""
        # Display options
        display_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("display_options"))
        display_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(
            display_frame, text=i18n.get("show_overlays"),
            variable=self.show_overlays
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            display_frame, text=i18n.get("show_faces"),
            variable=self.show_faces
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            display_frame, text=i18n.get("show_confidence_bars"),
            variable=self.show_confidence
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            display_frame, text=i18n.get("show_fps_counter"),
            variable=self.show_fps
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            display_frame, text=i18n.get("show_timestamp"),
            variable=self.show_time
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Window options
        window_frame = ttk.LabelFrame(self.control_frame, text=i18n.get("window_options"))
        window_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            window_frame, text=i18n.get("toggle_fullscreen"),
            command=self.toggle_fullscreen
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            window_frame, text=i18n.get("take_screenshot"),
            command=self.take_screenshot
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            window_frame, text=i18n.get("reset_view"),
            command=self.reset_view
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Close button
        ttk.Button(
            self.control_frame, text=i18n.get("close_preview"),
            command=self.close
        ).pack(side=tk.RIGHT, padx=5, pady=5)
    
    def _start_update_loop(self) -> None:
        """Start the update loop"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self) -> None:
        """Main update loop for preview window"""
        while self.running:
            try:
                # Get current frame and emotions from main panel
                if (self.main_panel.camera_running.get() and 
                    hasattr(self.main_panel, 'camera_manager') and
                    self.main_panel.camera_manager):
                    
                    frame = self.main_panel.camera_manager.get_frame()
                    if frame is not None:
                        # Get emotion detection results
                        emotions = []
                        
                        # Use shared results from MainPanel to avoid double inference
                        if hasattr(self.main_panel, 'latest_results'):
                            emotions = self.main_panel.latest_results
                        elif (hasattr(self.main_panel, 'emotion_detector') and
                            self.main_panel.emotion_detector):
                            
                            detection_results = self.main_panel.emotion_detector.detect_emotions(frame)
                            if detection_results:
                                emotions = detection_results
                        
                        # Update display
                        self.root.after(0, lambda: self._update_display(frame, emotions))
                
                time.sleep(self.config.update_interval / 1000.0)
                
            except Exception as e:
                self.logger.error(f"Error in preview update loop: {e}")
                time.sleep(0.1)
    
    def _update_display(self, frame: np.ndarray, emotions: List[Dict[str, Any]]) -> None:
        """Update the display with current frame and emotions"""
        try:
            if not self.root or not self.root.winfo_exists():
                return
            
            self.current_frame = frame.copy()
            self.current_emotions = emotions.copy()
            
            # Calculate FPS
            current_time = time.time()
            fps = 1.0 / (current_time - self.last_update_time + 0.001)
            self.fps_history.append(fps)
            if len(self.fps_history) > 30:  # Keep last 30 frames
                self.fps_history = self.fps_history[-30:]
            self.last_update_time = current_time
            
            # Create enhanced frame with overlays
            display_frame = self._create_enhanced_frame(frame, emotions, fps)
            
            # Convert to PhotoImage and display
            self._display_frame(display_frame)
            
        except Exception as e:
            self.logger.error(f"Error updating display: {e}")
    
    def _create_enhanced_frame(self, frame: np.ndarray, emotions: List[Dict[str, Any]], fps: float) -> np.ndarray:
        """Create enhanced frame with overlays and annotations"""
        enhanced_frame = frame.copy()
        
        # Draw face boxes and emotion overlays
        if emotions and self.show_faces.get():
            for emotion_data in emotions:
                if 'face_location' in emotion_data:
                    self._draw_face_box(enhanced_frame, emotion_data)
                
                if self.show_overlays.get():
                    self._draw_emotion_overlay(enhanced_frame, emotion_data)
        
        # Draw confidence bars
        if emotions and self.show_confidence.get():
            self._draw_confidence_bars(enhanced_frame, emotions)
        
        # Draw FPS counter
        if self.show_fps.get():
            avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
            self._draw_text(enhanced_frame, f"FPS: {avg_fps:.1f}", (10, 30), (0, 255, 0))
        
        # Draw timestamp
        if self.show_time.get():
            timestamp = time.strftime("%H:%M:%S")
            text_size = cv2.getTextSize(timestamp, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            self._draw_text(
                enhanced_frame, 
                timestamp, 
                (enhanced_frame.shape[1] - text_size[0] - 10, 30),
                (255, 255, 255)
            )
        
        return enhanced_frame
    
    def _draw_face_box(self, frame: np.ndarray, emotion_data: Dict[str, Any]) -> None:
        """Draw face bounding box"""
        if 'face_location' not in emotion_data:
            return
        
        location = emotion_data['face_location']
        emotion = emotion_data.get('emotion', 'unknown')
        confidence = emotion_data.get('confidence', 0.0)
        
        # Get color for this emotion
        color = self.config.emotion_colors.get(emotion, (255, 255, 255))
        
        # Draw rectangle
        cv2.rectangle(frame, (location[0], location[1]), (location[2], location[3]), color, 2)
        
        # Draw label
        emotion_text = i18n.get(emotion, emotion).title()
        label = f"{emotion_text}: {confidence:.2f}"
        
        # Use PIL to draw text (supports Chinese)
        try:
            # Convert to PIL Image
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            
            # Use pre-loaded font
            font = self.font
            if font is None:
                self._init_font()
                font = self.font
            
            # Get text size
            left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
            text_width = right - left
            text_height = bottom - top
            
            # Draw label background
            cv2.rectangle(
                frame,
                (location[0], location[1] - text_height - 10),
                (location[0] + text_width + 10, location[1]),
                color,
                -1
            )
            
            # Draw text on PIL image
            draw.text((location[0] + 5, location[1] - text_height - 5), label, font=font, fill=(0, 0, 0))
            
            # Convert back to OpenCV image
            frame[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            self.logger.error(f"Error drawing text with PIL: {e}")
            # Fallback to OpenCV putText
            cv2.putText(
                frame,
                label,
                (location[0], location[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
    
    def _draw_emotion_overlay(self, frame: np.ndarray, emotion_data: Dict[str, Any]) -> None:
        """Draw emotion overlay graphics"""
        emotion = emotion_data.get('emotion', 'unknown')
        confidence = emotion_data.get('confidence', 0.0)
        
        # Get face center if available
        center = (frame.shape[1] // 2, frame.shape[0] // 2)
        if 'face_location' in emotion_data:
            location = emotion_data['face_location']
            center = ((location[0] + location[2]) // 2, (location[1] + location[3]) // 2)
        
        # Draw emotion-specific overlay
        color = self.config.emotion_colors.get(emotion, (255, 255, 255))
        
        if emotion == 'happy':
            self._draw_smiley(frame, center, color, confidence)
        elif emotion == 'sad':
            self._draw_sad_face(frame, center, color, confidence)
        elif emotion == 'surprise':
            self._draw_surprise_face(frame, center, color, confidence)
        else:
            # Default: draw emotion name
            self._draw_text(frame, i18n.get(emotion, emotion).title(), center, color)
    
    def _draw_confidence_bars(self, frame: np.ndarray, emotions: List[Dict[str, Any]]) -> None:
        """Draw confidence bars for all detected emotions"""
        if not emotions:
            return
        
        bar_width = 20
        bar_height = 200
        start_x = frame.shape[1] - bar_width - 20
        start_y = 50
        
        # Get dominant emotion
        dominant_emotion = max(emotions, key=lambda x: x.get('confidence', 0))
        
        # Get all unique emotions with their confidences
        emotion_confidences = {}
        for emotion_data in emotions:
            emotion = emotion_data.get('emotion', 'unknown')
            confidence = emotion_data.get('confidence', 0.0)
            if emotion not in emotion_confidences or confidence > emotion_confidences[emotion]:
                emotion_confidences[emotion] = confidence
        
        # Draw bars for each emotion
        for i, (emotion, confidence) in enumerate(emotion_confidences.items()):
            bar_x = start_x - i * (bar_width + 10)
            bar_fill_height = int(bar_height * confidence)
            
            # Draw background bar
            cv2.rectangle(
                frame,
                (bar_x, start_y),
                (bar_x + bar_width, start_y + bar_height),
                (50, 50, 50),
                -1
            )
            
            # Draw confidence bar
            color = self.config.emotion_colors.get(emotion, (255, 255, 255))
            cv2.rectangle(
                frame,
                (bar_x, start_y + bar_height - bar_fill_height),
                (bar_x + bar_width, start_y + bar_height),
                color,
                -1
            )
            
            # Draw emotion label
            label = emotion[:3].upper()  # First 3 letters
            # Try to get translated short name if possible, otherwise use English
            emotion_text = i18n.get(emotion, emotion)
            if i18n.current_language == "zh_TW":
                label = emotion_text  # Use full Chinese name (usually 2 chars)
            
            # Use PIL for text drawing to support Chinese
            try:
                img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(img_pil)
                
                # Use pre-loaded font
                font = self.font
                if font is None:
                    self._init_font()
                    font = self.font
                
                # Calculate text position
                left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
                text_width = right - left
                text_x = bar_x + (bar_width - text_width) // 2
                
                # Draw text
                draw.text((text_x, start_y + bar_height + 5), label, font=font, fill=(255, 255, 255))
                
                # Draw confidence value
                conf_text = f"{confidence:.2f}"
                left, top, right, bottom = draw.textbbox((0, 0), conf_text, font=font)
                conf_width = right - left
                conf_x = bar_x + (bar_width - conf_width) // 2
                
                # Use a smaller font for confidence if possible, or same font
                draw.text((conf_x, start_y - 25), conf_text, font=font, fill=color)
                
                # Convert back
                frame[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                
            except Exception as e:
                # Fallback to OpenCV
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                text_x = bar_x + (bar_width - text_size[0]) // 2
                cv2.putText(
                    frame,
                    label,
                    (text_x, start_y + bar_height + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
                
                # Draw confidence value
                conf_text = f"{confidence:.2f}"
                conf_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 1)[0]
                conf_x = bar_x + (bar_width - conf_size[0]) // 2
                cv2.putText(
                    frame,
                    conf_text,
                    (conf_x, start_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    color,
                    1
                )
    
    def _draw_smiley(self, frame: np.ndarray, center: Tuple[int, int], color: Tuple[int, int, int], confidence: float) -> None:
        """Draw a smiley face overlay"""
        radius = int(50 * confidence)
        if radius < 10:
            return
        
        # Draw face circle
        cv2.circle(frame, center, radius, color, 3)
        
        # Draw eyes
        eye_offset = radius // 3
        cv2.circle(frame, (center[0] - eye_offset, center[1] - eye_offset), 5, color, -1)
        cv2.circle(frame, (center[0] + eye_offset, center[1] - eye_offset), 5, color, -1)
        
        # Draw smile
        smile_points = []
        for i in range(-30, 31, 5):
            angle = np.radians(i)
            x = int(center[0] + (radius // 2) * np.sin(angle))
            y = int(center[1] + (radius // 3) + (radius // 4) * np.cos(angle))
            smile_points.append((x, y))
        
        if len(smile_points) > 1:
            points = np.array(smile_points, np.int32)
            cv2.polylines(frame, [points], False, color, 3)
    
    def _draw_sad_face(self, frame: np.ndarray, center: Tuple[int, int], color: Tuple[int, int, int], confidence: float) -> None:
        """Draw a sad face overlay"""
        radius = int(50 * confidence)
        if radius < 10:
            return
        
        # Draw face circle
        cv2.circle(frame, center, radius, color, 3)
        
        # Draw eyes
        eye_offset = radius // 3
        cv2.circle(frame, (center[0] - eye_offset, center[1] - eye_offset), 5, color, -1)
        cv2.circle(frame, (center[0] + eye_offset, center[1] - eye_offset), 5, color, -1)
        
        # Draw frown
        frown_points = []
        for i in range(-30, 31, 5):
            angle = np.radians(i)
            x = int(center[0] + (radius // 2) * np.sin(angle))
            y = int(center[1] + (radius // 2) - (radius // 4) * np.cos(angle))
            frown_points.append((x, y))
        
        if len(frown_points) > 1:
            points = np.array(frown_points, np.int32)
            cv2.polylines(frame, [points], False, color, 3)
    
    def _draw_surprise_face(self, frame: np.ndarray, center: Tuple[int, int], color: Tuple[int, int, int], confidence: float) -> None:
        """Draw a surprised face overlay"""
        radius = int(50 * confidence)
        if radius < 10:
            return
        
        # Draw face circle
        cv2.circle(frame, center, radius, color, 3)
        
        # Draw wide eyes
        eye_offset = radius // 3
        cv2.circle(frame, (center[0] - eye_offset, center[1] - eye_offset), 8, color, 3)
        cv2.circle(frame, (center[0] + eye_offset, center[1] - eye_offset), 8, color, 3)
        
        # Draw open mouth (oval)
        cv2.ellipse(frame, (center[0], center[1] + radius//3), (radius//4, radius//6), 0, 0, 360, color, 3)
    
    def _draw_text(self, frame: np.ndarray, text: str, position: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Draw text with background"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        # Get text size
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (position[0] - 5, position[1] - text_size[1] - 5),
            (position[0] + text_size[0] + 5, position[1] + 5),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
    
    def _display_frame(self, frame: np.ndarray) -> None:
        """Display frame on canvas"""
        try:
            # Get canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Resize frame to fit canvas while maintaining aspect ratio
            frame_height, frame_width = frame.shape[:2]
            scale = min(canvas_width / frame_width, canvas_height / frame_height)
            
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Create PIL image and PhotoImage
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=photo
            )
            
            # Keep reference to prevent garbage collection
            self.canvas.image = photo
            
        except Exception as e:
            self.logger.error(f"Error displaying frame: {e}")
    
    def _show_controls(self) -> None:
        """Show control panel"""
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    def _hide_controls(self) -> None:
        """Hide control panel"""
        self.control_frame.grid_remove()
    
    # Event handlers
    def _on_key_press(self, event) -> None:
        """Handle key press events"""
        key = event.keysym.lower()
        
        if key == 'f' or key == 'f11':
            self.toggle_fullscreen()
        elif key == 'escape':
            if self.is_fullscreen.get():
                self.toggle_fullscreen()
            else:
                self.close()
        elif key == 'space':
            self.take_screenshot()
        elif key == 'h':
            # Toggle controls visibility
            if self.control_frame.winfo_viewable():
                self._hide_controls()
            else:
                self._show_controls()
        elif key in ['1', '2', '3', '4', '5']:
            # Toggle overlay options
            option_map = {
                '1': self.show_overlays,
                '2': self.show_faces,
                '3': self.show_confidence,
                '4': self.show_fps,
                '5': self.show_time
            }
            if key in option_map:
                var = option_map[key]
                var.set(not var.get())
    
    def _on_click(self, event) -> None:
        """Handle mouse click events"""
        # Check if click is within control frame or its children
        try:
            widget = event.widget
            # If widget is the control frame or any of its children, do not toggle visibility
            if str(widget).startswith(str(self.control_frame)):
                return
        except Exception:
            pass

        # Toggle controls on click
        if self.control_frame.winfo_viewable():
            self._hide_controls()
        else:
            self._show_controls()
    
    def _on_mouse_motion(self, event) -> None:
        """Handle mouse motion events"""
        # Show controls when mouse moves
        if not self.control_frame.winfo_viewable():
            self._show_controls()
    
    def _on_mouse_leave(self, event) -> None:
        """Handle mouse leave events"""
        # Hide controls after delay
        self.root.after(3000, lambda: self._hide_controls() if not self.is_fullscreen.get() else None)
    
    def _on_resize(self, event) -> None:
        """Handle window resize events"""
        if event.widget == self.root:
            # Update display when window is resized
            if self.current_frame is not None:
                self.root.after_idle(lambda: self._display_frame(self.current_frame))
    
    # Public methods
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode"""
        try:
            current_fullscreen = self.is_fullscreen.get()
            self.is_fullscreen.set(not current_fullscreen)
            
            self.root.attributes('-fullscreen', self.is_fullscreen.get())
            
            if self.is_fullscreen.get():
                self._hide_controls()
            else:
                self._show_controls()
            
            self.logger.info(f"Fullscreen mode: {'ON' if self.is_fullscreen.get() else 'OFF'}")
            
        except Exception as e:
            self.logger.error(f"Error toggling fullscreen: {e}")
    
    def take_screenshot(self) -> None:
        """Take a screenshot of current preview"""
        try:
            if self.current_frame is not None:
                # Create enhanced frame with all overlays
                enhanced_frame = self._create_enhanced_frame(
                    self.current_frame, 
                    self.current_emotions,
                    sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
                )
                
                # Save screenshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"livepilot_preview_{timestamp}.jpg"
                
                success = cv2.imwrite(filename, enhanced_frame)
                if success:
                    self.logger.info(f"Screenshot saved: {filename}")
                    # Could show a brief notification on canvas
                else:
                    self.logger.error("Failed to save screenshot")
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
    
    def reset_view(self) -> None:
        """Reset view to default settings"""
        try:
            self.show_overlays.set(True)
            self.show_faces.set(True)
            self.show_confidence.set(True)
            self.show_fps.set(True)
            self.show_time.set(True)
            
            if self.is_fullscreen.get():
                self.toggle_fullscreen()
            
            self.logger.info("View reset to defaults")
            
        except Exception as e:
            self.logger.error(f"Error resetting view: {e}")
    
    def close(self) -> None:
        """Close the preview window"""
        try:
            self.running = False
            
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=1)
            
            if self.root and self.root.winfo_exists():
                self.root.destroy()
            
            self.logger.info("Preview window closed")
            
        except Exception as e:
            self.logger.error(f"Error closing preview window: {e}")
    
    def show(self) -> None:
        """Show the preview window"""
        try:
            if self.root:
                self.root.deiconify()  # Show window if it was minimized
                self.root.lift()       # Bring to front
                self.logger.info("Preview window shown")
        except Exception as e:
            self.logger.error(f"Error showing preview window: {e}")
    
    def hide(self) -> None:
        """Hide the preview window"""
        try:
            if self.root:
                self.root.withdraw()   # Hide window
                self.logger.info("Preview window hidden")
        except Exception as e:
            self.logger.error(f"Error hiding preview window: {e}")
    
    def focus(self) -> None:
        """Focus the preview window"""
        try:
            if self.root:
                self.root.focus_force()  # Force focus
                self.root.lift()         # Bring to front
                self.logger.info("Preview window focused")
        except Exception as e:
            self.logger.error(f"Error focusing preview window: {e}")
    
    def is_visible(self) -> bool:
        """Check if the preview window is visible"""
        try:
            if self.root and self.root.winfo_exists():
                # Window is visible if it's not withdrawn
                return self.root.state() != 'withdrawn'
            return False
        except Exception as e:
            self.logger.error(f"Error checking window visibility: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    import tkinter as tk
    
    # Mock main panel for testing
    class MockMainPanel:
        def __init__(self):
            self.root = tk.Tk()
            self.camera_running = tk.BooleanVar(value=True)
            
            class MockCameraManager:
                def get_frame(self):
                    # Return a test frame
                    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            class MockEmotionDetector:
                def detect_emotions(self, frame):
                    return [
                        {
                            'emotion': 'happy',
                            'confidence': 0.85,
                            'face_location': [100, 100, 200, 200]
                        }
                    ]
            
            self.camera_manager = MockCameraManager()
            self.emotion_detector = MockEmotionDetector()
    
    # Test preview window
    mock_panel = MockMainPanel()
    preview = PreviewWindow(mock_panel)
    
    # Run test
    mock_panel.root.mainloop()
