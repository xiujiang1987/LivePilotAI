"""
voice_commander.py - Voice Command Recognition Module

This module handles real-time voice recognition and command processing
for the LivePilotAI system.

Author: LivePilotAI Development Team
"""

import logging
import threading
import time
from typing import Callable, Optional, Dict

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False

class VoiceCommander:
    def __init__(self, command_callback: Callable[[str], None]):
        self.logger = logging.getLogger(__name__)
        self.callback = command_callback
        self.recognizer = None
        self.microphone = None
        self.stop_listening_func = None
        self.is_running = False
        
        # Command configurations
        self.enabled = False
        self.language = "zh-TW"  # Default to Traditional Chinese
        
        if HAS_SPEECH_RECOGNITION:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.logger.info("VoiceCommander initialized with SpeechRecognition")
            except Exception as e:
                self.logger.error(f"Failed to initialize microphone: {e}")
                self.microphone = None
        else:
            self.logger.warning("SpeechRecognition not installed. Voice features disabled.")

    def start(self) -> bool:
        """Start listening for voice commands in background"""
        if not HAS_SPEECH_RECOGNITION or not self.microphone:
            return False
            
        if self.is_running:
            return True

        try:
            self.logger.info("Calibrating microphone for ambient noise...")
            # Brief calibration
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("Starting background listening...")
            # listen_in_background creates a daemon thread
            self.stop_listening_func = self.recognizer.listen_in_background(
                self.microphone, 
                self._on_audio_input,
                phrase_time_limit=5
            )
            self.is_running = True
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting voice listener: {e}")
            return False

    def stop(self):
        """Stop listening"""
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None
        self.is_running = False
        self.logger.info("Voice listener stopped")

    def _on_audio_input(self, recognizer, audio):
        """Callback when audio is captured"""
        try:
            # Use Google Speech Recognition (free tier, good enough for POC)
            # For production, we might want faster offline models like Vosk or Whisper
            text = recognizer.recognize_google(audio, language=self.language)
            self.logger.info(f"Voice Detected: '{text}'")
            
            # Simple keyword matching logic could go here or in the callback
            # We pass the raw text to the callback (Director) to decide
            if self.callback:
                self.callback(text)
                
        except sr.UnknownValueError:
            # Audio was not understood
            pass
        except sr.RequestError as e:
            self.logger.error(f"Speech service error: {e}")
        except Exception as e:
            self.logger.error(f"Voice processing error: {e}")
