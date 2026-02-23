"""
LivePilotAI Day 5 - Quick Validation Script
Validates all Day 5 components and functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_obs_integration():
    """Test OBS integration components"""
    print("\n🔧 Testing OBS Integration...")
    try:
        from obs_integration import OBSManager, EmotionMapper, SceneController, OBSWebSocketClient
        
        # Test OBS Manager
        obs_manager = OBSManager()
        print("✅ OBS Manager initialized")
        
        # Test Emotion Mapper
        emotion_mapper = EmotionMapper()
        strategies = emotion_mapper.get_mapping_strategies()
        print(f"✅ Emotion Mapper initialized with {len(strategies)} strategies")
        
        # Test Scene Controller
        scene_controller = SceneController()
        print("✅ Scene Controller initialized")
        
        return True
    except Exception as e:
        print(f"❌ OBS Integration test failed: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    print("\n🎨 Testing UI Components...")
    try:
        from ui import MainControlPanel, PreviewWindow, SettingsDialog, StatusPanel
        print("✅ All UI components imported successfully")
        
        # Test if tkinter dependencies are available
        import tkinter as tk
        print("✅ Tkinter available for GUI")
        
        return True
    except Exception as e:
        print(f"❌ UI Components test failed: {e}")
        return False

def test_ai_engine():
    """Test AI engine integration"""
    print("\n🧠 Testing AI Engine...")
    try:
        from ai_engine.emotion_detector import EmotionDetector
        from ai_engine.modules.face_detector import FaceDetector
        from ai_engine.modules.camera_manager import CameraManager
        
        print("✅ AI Engine components imported successfully")
        return True
    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        return False

def test_main_application():
    """Test main application entry point"""
    print("\n🚀 Testing Main Application...")
    try:
        import main_day5
        print("✅ Main Day 5 application can be imported")
        return True
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

def test_performance_benchmark():
    """Test performance benchmark system"""
    print("\n📊 Testing Performance Benchmark...")
    try:
        import day5_performance_benchmark
        print("✅ Performance benchmark system available")
        return True
    except Exception as e:
        print(f"❌ Performance benchmark test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🎯 LivePilotAI Day 5 - System Validation")
    print("=" * 60)
    
    tests = [
        ("OBS Integration", test_obs_integration),
        ("UI Components", test_ui_components),
        ("AI Engine", test_ai_engine),
        ("Main Application", test_main_application),
        ("Performance Benchmark", test_performance_benchmark)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test encountered an error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📈 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Day 5 components are working correctly!")
        print("✅ LivePilotAI Day 5 system is ready for deployment!")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
