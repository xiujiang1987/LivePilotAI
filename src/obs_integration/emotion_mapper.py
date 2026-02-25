"""
emotion_mapper.py - Emotion to Scene Mapping Engine

This module provides intelligent mapping between detected emotions and OBS scenes,
with configurable rules, priorities, and adaptive learning capabilities.

Author: LivePilotAI Development Team
Date: 2024-12-19
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class MappingStrategy(Enum):
    """Scene mapping strategies"""
    DIRECT = "direct"           # Direct emotion-to-scene mapping
    WEIGHTED = "weighted"       # Weighted based on confidence scores
    ADAPTIVE = "adaptive"       # Learning-based adaptive mapping
    CONTEXT_AWARE = "context"   # Context-sensitive mapping


class TriggerCondition(Enum):
    """Conditions for triggering scene switches"""
    IMMEDIATE = "immediate"     # Switch immediately on detection
    SUSTAINED = "sustained"     # Require sustained emotion for duration
    CONFIDENCE = "confidence"   # Switch only above confidence threshold
    COMBINED = "combined"       # Multiple conditions must be met


@dataclass
class EmotionMapping:
    """Configuration for emotion to scene mapping"""
    emotion: str
    scene_name: str
    priority: int = 5                    # Higher number = higher priority (1-10)
    confidence_threshold: float = 0.7    # Minimum confidence to trigger
    sustained_duration: float = 2.0      # Seconds to sustain emotion
    cooldown_period: float = 5.0         # Seconds before next switch
    trigger_condition: TriggerCondition = TriggerCondition.CONFIDENCE
    strategy: MappingStrategy = MappingStrategy.DIRECT
    weight: float = 1.0                  # Weight for weighted strategies
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmotionContext:
    """Context information for emotion detection"""
    emotion: str
    confidence: float
    timestamp: float
    face_count: int = 1
    face_area: float = 0.0
    lighting_quality: float = 1.0
    motion_detected: bool = False
    previous_emotion: Optional[str] = None
    duration: float = 0.0


@dataclass
class MappingResult:
    """Result of emotion mapping evaluation"""
    recommended_scene: Optional[str]
    confidence: float
    reasoning: str
    should_switch: bool
    priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmotionMapper:
    """
    Intelligent emotion to scene mapping engine with adaptive capabilities
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "emotion_mappings.json"
        
        # Core mappings storage
        self.mappings: Dict[str, EmotionMapping] = {}
        self.default_mappings: Dict[str, EmotionMapping] = {}
        
        # State tracking
        self.current_scene: Optional[str] = None
        self.last_global_switch_time: float = 0.0
        self.last_emotion_switch_times: Dict[str, float] = {}
        self.emotion_history: List[EmotionContext] = []
        self.switch_history: List[Tuple[str, str, float]] = []  # (from, to, timestamp)
        
        # Adaptive learning
        self.scene_performance: Dict[str, Dict[str, float]] = {}  # scene -> {metric: value}
        self.user_preferences: Dict[str, float] = {}  # emotion -> preference_score
        
        # Configuration
        self.max_history_size: int = 100
        self.learning_rate: float = 0.1
        self.context_window: float = 10.0  # seconds
        self.global_cooldown: float = 1.0   # minimum time between any switches
        
        # Callbacks
        self.mapping_callbacks: List[Callable[[MappingResult], None]] = []
        
        # Initialize
        self._setup_default_mappings()
        self._load_configuration()
        
        self.logger.info("EmotionMapper initialized successfully")
    
    def _setup_default_mappings(self) -> None:
        """Setup default emotion to scene mappings"""
        default_configs = [
            EmotionMapping(
                emotion="happy",
                scene_name="Happy Scene",
                priority=8,
                confidence_threshold=0.75,
                sustained_duration=1.5,
                cooldown_period=3.0,
                trigger_condition=TriggerCondition.CONFIDENCE
            ),
            EmotionMapping(
                emotion="sad",
                scene_name="Calm Scene", 
                priority=7,
                confidence_threshold=0.7,
                sustained_duration=2.0,
                cooldown_period=4.0,
                trigger_condition=TriggerCondition.SUSTAINED
            ),
            EmotionMapping(
                emotion="surprise",
                scene_name="Dynamic Scene",
                priority=9,
                confidence_threshold=0.8,
                sustained_duration=1.0,
                cooldown_period=2.0,
                trigger_condition=TriggerCondition.IMMEDIATE
            ),
            EmotionMapping(
                emotion="neutral",
                scene_name="Default Scene",
                priority=5,
                confidence_threshold=0.6,
                sustained_duration=3.0,
                cooldown_period=5.0,
                trigger_condition=TriggerCondition.SUSTAINED
            ),
            EmotionMapping(
                emotion="angry",
                scene_name="Intense Scene",
                priority=6,
                confidence_threshold=0.75,
                sustained_duration=1.5,
                cooldown_period=4.0,
                trigger_condition=TriggerCondition.COMBINED
            ),
            EmotionMapping(
                emotion="fear",
                scene_name="Dramatic Scene",
                priority=7,
                confidence_threshold=0.7,
                sustained_duration=2.0,
                cooldown_period=3.0,
                trigger_condition=TriggerCondition.CONFIDENCE
            ),
            EmotionMapping(
                emotion="disgust",
                scene_name="Neutral Scene",
                priority=4,
                confidence_threshold=0.65,
                sustained_duration=2.5,
                cooldown_period=6.0,
                trigger_condition=TriggerCondition.SUSTAINED
            )
        ]
        
        for mapping in default_configs:
            self.default_mappings[mapping.emotion] = mapping
            self.mappings[mapping.emotion] = mapping
        
        self.logger.info(f"Setup {len(default_configs)} default emotion mappings")
    
    def _load_configuration(self) -> None:
        """Load mappings from configuration file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load custom mappings
                if 'mappings' in data:
                    for emotion, config in data['mappings'].items():
                        mapping = EmotionMapping(
                            emotion=emotion,
                            scene_name=config.get('scene_name', f"{emotion.title()} Scene"),
                            priority=config.get('priority', 5),
                            confidence_threshold=config.get('confidence_threshold', 0.7),
                            sustained_duration=config.get('sustained_duration', 2.0),
                            cooldown_period=config.get('cooldown_period', 5.0),
                            trigger_condition=TriggerCondition(config.get('trigger_condition', 'confidence')),
                            strategy=MappingStrategy(config.get('strategy', 'direct')),
                            weight=config.get('weight', 1.0),
                            enabled=config.get('enabled', True),
                            metadata=config.get('metadata', {})
                        )
                        self.mappings[emotion] = mapping
                
                # Load preferences and performance data
                self.user_preferences = data.get('user_preferences', {})
                self.scene_performance = data.get('scene_performance', {})
                
                self.logger.info(f"Loaded configuration from {self.config_path}")
            else:
                self.logger.info("No configuration file found, using defaults")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.logger.info("Falling back to default mappings")
    
    def save_configuration(self) -> bool:
        """Save current mappings and learned data to configuration file"""
        try:
            data = {
                'mappings': {},
                'user_preferences': self.user_preferences,
                'scene_performance': self.scene_performance,
                'metadata': {
                    'last_updated': time.time(),
                    'total_switches': len(self.switch_history),
                    'version': "1.0"
                }
            }
            
            # Convert mappings to serializable format
            for emotion, mapping in self.mappings.items():
                data['mappings'][emotion] = {
                    'scene_name': mapping.scene_name,
                    'priority': mapping.priority,
                    'confidence_threshold': mapping.confidence_threshold,
                    'sustained_duration': mapping.sustained_duration,
                    'cooldown_period': mapping.cooldown_period,
                    'trigger_condition': mapping.trigger_condition.value,
                    'strategy': mapping.strategy.value,
                    'weight': mapping.weight,
                    'enabled': mapping.enabled,
                    'metadata': mapping.metadata
                }
            
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def add_mapping(self, mapping: EmotionMapping) -> bool:
        """Add or update an emotion mapping"""
        try:
            self.mappings[mapping.emotion] = mapping
            self.logger.info(f"Added mapping: {mapping.emotion} -> {mapping.scene_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding mapping: {e}")
            return False
    
    def remove_mapping(self, emotion: str) -> bool:
        """Remove an emotion mapping"""
        try:
            if emotion in self.mappings:
                del self.mappings[emotion]
                self.logger.info(f"Removed mapping for emotion: {emotion}")
                return True
            else:
                self.logger.warning(f"Mapping for emotion '{emotion}' not found")
                return False
        except Exception as e:
            self.logger.error(f"Error removing mapping: {e}")
            return False
    
    def update_emotion_context(self, context: EmotionContext) -> None:
        """Update emotion context and history"""
        # Add context to history
        self.emotion_history.append(context)
        
        # Maintain history size limit
        if len(self.emotion_history) > self.max_history_size:
            self.emotion_history = self.emotion_history[-self.max_history_size:]
        
        # Update duration for sustained emotions
        if len(self.emotion_history) >= 2:
            prev_context = self.emotion_history[-2]
            if prev_context.emotion == context.emotion:
                context.duration = context.timestamp - prev_context.timestamp
    
    def evaluate_mapping(self, context: EmotionContext) -> MappingResult:
        """
        Evaluate emotion context and determine recommended scene mapping
        """
        try:
            # Check if mapping exists for this emotion
            if context.emotion not in self.mappings:
                return MappingResult(
                    recommended_scene=None,
                    confidence=0.0,
                    reasoning=f"No mapping configured for emotion: {context.emotion}",
                    should_switch=False,
                    priority=0
                )
            
            mapping = self.mappings[context.emotion]
            
            # Check if mapping is enabled
            if not mapping.enabled:
                return MappingResult(
                    recommended_scene=None,
                    confidence=0.0,
                    reasoning=f"Mapping for {context.emotion} is disabled",
                    should_switch=False,
                    priority=0
                )
            
            # Check global cooldown
            current_time = time.time()
            if current_time - self.last_global_switch_time < self.global_cooldown:
                return MappingResult(
                    recommended_scene=mapping.scene_name,
                    confidence=context.confidence,
                    reasoning="Global cooldown period active",
                    should_switch=False,
                    priority=mapping.priority
                )
            
            # Check emotion-specific cooldown
            last_emotion_switch_time = self.last_emotion_switch_times.get(context.emotion, 0.0)
            if current_time - last_emotion_switch_time < mapping.cooldown_period:
                return MappingResult(
                    recommended_scene=mapping.scene_name,
                    confidence=context.confidence,
                    reasoning=f"Cooldown period active for {context.emotion}",
                    should_switch=False,
                    priority=mapping.priority
                )
            
            # Evaluate trigger conditions
            should_switch = self._evaluate_trigger_conditions(mapping, context)
            
            # Calculate final confidence based on strategy
            final_confidence = self._calculate_strategy_confidence(mapping, context)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(mapping, context, should_switch)
            
            return MappingResult(
                recommended_scene=mapping.scene_name,
                confidence=final_confidence,
                reasoning=reasoning,
                should_switch=should_switch,
                priority=mapping.priority,
                metadata={
                    'emotion': context.emotion,
                    'mapping_strategy': mapping.strategy.value,
                    'trigger_condition': mapping.trigger_condition.value,
                    'context_timestamp': context.timestamp
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating mapping: {e}")
            return MappingResult(
                recommended_scene=None,
                confidence=0.0,
                reasoning=f"Error in mapping evaluation: {str(e)}",
                should_switch=False,
                priority=0
            )
    
    def _evaluate_trigger_conditions(self, mapping: EmotionMapping, context: EmotionContext) -> bool:
        """Evaluate if trigger conditions are met for scene switching"""
        
        if mapping.trigger_condition == TriggerCondition.IMMEDIATE:
            return context.confidence >= mapping.confidence_threshold
        
        elif mapping.trigger_condition == TriggerCondition.CONFIDENCE:
            return context.confidence >= mapping.confidence_threshold
        
        elif mapping.trigger_condition == TriggerCondition.SUSTAINED:
            if context.confidence < mapping.confidence_threshold:
                return False
            
            # Check if emotion has been sustained for required duration
            sustained_duration = self._get_sustained_duration(context.emotion)
            return sustained_duration >= mapping.sustained_duration
        
        elif mapping.trigger_condition == TriggerCondition.COMBINED:
            # All conditions must be met
            confidence_ok = context.confidence >= mapping.confidence_threshold
            sustained_duration = self._get_sustained_duration(context.emotion)
            duration_ok = sustained_duration >= mapping.sustained_duration
            
            return confidence_ok and duration_ok
        
        return False
    
    def _get_sustained_duration(self, emotion: str) -> float:
        """Calculate how long an emotion has been sustained"""
        if not self.emotion_history:
            return 0.0
        
        current_time = time.time()
        sustained_start = current_time
        
        # Look backwards through history to find when this emotion started
        for context in reversed(self.emotion_history):
            if context.emotion == emotion:
                sustained_start = context.timestamp
            else:
                break
        
        return current_time - sustained_start
    
    def _calculate_strategy_confidence(self, mapping: EmotionMapping, context: EmotionContext) -> float:
        """Calculate confidence based on mapping strategy"""
        base_confidence = context.confidence
        
        if mapping.strategy == MappingStrategy.DIRECT:
            return base_confidence
        
        elif mapping.strategy == MappingStrategy.WEIGHTED:
            # Apply weight and consider context factors
            weight_factor = mapping.weight
            context_factor = self._calculate_context_factor(context)
            return min(1.0, base_confidence * weight_factor * context_factor)
        
        elif mapping.strategy == MappingStrategy.ADAPTIVE:
            # Use learned preferences and performance
            preference_factor = self.user_preferences.get(context.emotion, 1.0)
            performance_factor = self._get_scene_performance_factor(mapping.scene_name)
            return min(1.0, base_confidence * preference_factor * performance_factor)
        
        elif mapping.strategy == MappingStrategy.CONTEXT_AWARE:
            # Consider context and history
            context_factor = self._calculate_context_factor(context)
            history_factor = self._calculate_history_factor(context.emotion)
            return min(1.0, base_confidence * context_factor * history_factor)
        
        return base_confidence
    
    def _calculate_context_factor(self, context: EmotionContext) -> float:
        """Calculate context-based confidence factor"""
        factor = 1.0
        
        # Face area factor (larger faces = higher confidence)
        if context.face_area > 0:
            area_factor = min(1.0, context.face_area / 0.1)  # Normalize to 0.1 as reference
            factor *= (0.8 + 0.2 * area_factor)
        
        # Lighting quality factor
        factor *= (0.7 + 0.3 * context.lighting_quality)
        
        # Multiple faces reduce confidence
        if context.face_count > 1:
            factor *= (1.0 / context.face_count) * 0.8
        
        return factor
    
    def _get_scene_performance_factor(self, scene_name: str) -> float:
        """Get performance factor for a scene"""
        if scene_name not in self.scene_performance:
            return 1.0
        
        performance = self.scene_performance[scene_name]
        # Use user satisfaction or switch success rate
        return performance.get('user_satisfaction', 1.0)
    
    def _calculate_history_factor(self, emotion: str) -> float:
        """Calculate factor based on recent emotion history"""
        if len(self.emotion_history) < 2:
            return 1.0
        
        # Recent similar emotions increase confidence
        recent_contexts = [ctx for ctx in self.emotion_history[-5:] 
                          if ctx.emotion == emotion]
        
        if len(recent_contexts) >= 2:
            return 1.2  # Boost confidence for consistent emotions
        
        return 1.0
    
    def _generate_reasoning(self, mapping: EmotionMapping, context: EmotionContext, should_switch: bool) -> str:
        """Generate human-readable reasoning for the mapping decision"""
        base_reason = f"Emotion '{context.emotion}' detected with {context.confidence:.2f} confidence"

        if not should_switch:
            if context.confidence < mapping.confidence_threshold:
                return f"{base_reason}, below threshold {mapping.confidence_threshold:.2f}"

            sustained_duration = self._get_sustained_duration(context.emotion)
            if sustained_duration < mapping.sustained_duration:
                return f"{base_reason}, need {mapping.sustained_duration:.1f}s sustained (current: {sustained_duration:.1f}s)"

            # MODIFICATION: Provide more accurate reasoning
            current_time = time.time()
            if current_time - self.last_global_switch_time < self.global_cooldown:
                return f"{base_reason}, but global cooldown is active"

            last_emotion_switch_time = self.last_emotion_switch_times.get(context.emotion, 0.0)
            if current_time - last_emotion_switch_time < mapping.cooldown_period:
                return f"{base_reason}, but cooldown for '{context.emotion}' is active"

            return f"{base_reason}, but other conditions not met"

        return f"{base_reason}, recommending '{mapping.scene_name}' (priority {mapping.priority})"

    # MODIFICATION: Update signature to accept emotion
    def record_scene_switch(self, from_scene: Optional[str], to_scene: str, emotion: Optional[str] = None) -> None:
        """Record a scene switch for learning and statistics"""
        current_time = time.time()

        # Update switch history
        self.switch_history.append((from_scene or "unknown", to_scene, current_time))

        # Maintain history size
        if len(self.switch_history) > self.max_history_size:
            self.switch_history = self.switch_history[-self.max_history_size:]

        # Update internal state
        self.current_scene = to_scene
        self.last_global_switch_time = current_time # Update global timer
        if emotion:
            self.last_emotion_switch_times[emotion] = current_time # Update per-emotion timer

        self.logger.info(f"Recorded scene switch: {from_scene} -> {to_scene} (triggered by {emotion or 'N/A'})")
    
    def learn_from_feedback(self, emotion: str, scene: str, satisfaction: float) -> None:
        """Learn from user feedback to improve future mappings"""
        try:
            # Update user preferences
            if emotion not in self.user_preferences:
                self.user_preferences[emotion] = satisfaction
            else:
                # Use learning rate to update preference
                current = self.user_preferences[emotion]
                self.user_preferences[emotion] = current + self.learning_rate * (satisfaction - current)
            
            # Update scene performance
            if scene not in self.scene_performance:
                self.scene_performance[scene] = {'user_satisfaction': satisfaction, 'feedback_count': 1}
            else:
                perf = self.scene_performance[scene]
                count = perf.get('feedback_count', 1)
                current_satisfaction = perf.get('user_satisfaction', 0.5)
                
                # Update with weighted average
                new_satisfaction = (current_satisfaction * count + satisfaction) / (count + 1)
                self.scene_performance[scene]['user_satisfaction'] = new_satisfaction
                self.scene_performance[scene]['feedback_count'] = count + 1
            
            self.logger.info(f"Learned from feedback: {emotion} -> {scene} (satisfaction: {satisfaction:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error learning from feedback: {e}")
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about mappings and performance"""
        return {
            'total_mappings': len(self.mappings),
            'enabled_mappings': sum(1 for m in self.mappings.values() if m.enabled),
            'total_switches': len(self.switch_history),
            'emotion_history_size': len(self.emotion_history),
            'current_scene': self.current_scene,
            'last_global_switch_time': self.last_global_switch_time, # MODIFICATION
            'last_emotion_switch_times': self.last_emotion_switch_times, # NEW
            'user_preferences': dict(self.user_preferences),
            'scene_performance': dict(self.scene_performance),
            'mapping_details': {
                emotion: {
                    'scene_name': mapping.scene_name,
                    'priority': mapping.priority,
                    'enabled': mapping.enabled,
                    'strategy': mapping.strategy.value,
                    'trigger_condition': mapping.trigger_condition.value
                }
                for emotion, mapping in self.mappings.items()
            }
        }

    def reset_learning_data(self) -> None:
        """Reset all learned data and preferences"""
        self.user_preferences.clear()
        self.scene_performance.clear()
        self.emotion_history.clear()
        self.switch_history.clear()
        self.last_global_switch_time = 0.0 # MODIFICATION
        self.last_emotion_switch_times.clear() # NEW
        self.current_scene = None

        self.logger.info("Reset all learning data and preferences")
    
    def add_mapping_callback(self, callback: Callable[[MappingResult], None]) -> None:
        """Add callback function to be called when mapping is evaluated"""
        self.mapping_callbacks.append(callback)
    
    def remove_mapping_callback(self, callback: Callable[[MappingResult], None]) -> None:
        """Remove mapping callback"""
        if callback in self.mapping_callbacks:
            self.mapping_callbacks.remove(callback)
    
    def _notify_callbacks(self, result: MappingResult) -> None:
        """Notify all registered callbacks about mapping result"""
        for callback in self.mapping_callbacks:
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in mapping callback: {e}")


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_emotion_mapper():
        """Test the emotion mapper functionality"""
        print("Testing EmotionMapper...")
        
        # Create mapper
        mapper = EmotionMapper()
        
        # Test emotion contexts
        test_contexts = [
            EmotionContext("happy", 0.85, time.time()),
            EmotionContext("sad", 0.75, time.time() + 1),
            EmotionContext("surprise", 0.9, time.time() + 2),
            EmotionContext("neutral", 0.65, time.time() + 3),
        ]
        
        # Evaluate mappings
        for context in test_contexts:
            mapper.update_emotion_context(context)
            result = mapper.evaluate_mapping(context)
            
            print(f"\nEmotion: {context.emotion}")
            print(f"Confidence: {context.confidence:.2f}")
            print(f"Recommended Scene: {result.recommended_scene}")
            print(f"Should Switch: {result.should_switch}")
            print(f"Reasoning: {result.reasoning}")
            
            if result.should_switch:
                mapper.record_scene_switch(mapper.current_scene, result.recommended_scene)
        
        # Test learning
        mapper.learn_from_feedback("happy", "Happy Scene", 0.9)
        mapper.learn_from_feedback("sad", "Calm Scene", 0.7)
        
        # Show statistics
        stats = mapper.get_mapping_statistics()
        print(f"\nStatistics:")
        print(f"Total Mappings: {stats['total_mappings']}")
        print(f"Total Switches: {stats['total_switches']}")
        print(f"Current Scene: {stats['current_scene']}")
        
        # Save configuration
        success = mapper.save_configuration()
        print(f"Configuration saved: {success}")
    
    # Run test
    asyncio.run(test_emotion_mapper())
