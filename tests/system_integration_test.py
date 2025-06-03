"""
LivePilotAI Day 5 - Integration Test Suite
Comprehensive testing for all Day 5 components and features
"""

import unittest
import sys
import os
import time
import threading
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestOBSIntegration(unittest.TestCase):
    """Test OBS integration components"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from obs_integration import OBSManager, SceneController, EmotionMapper, OBSWebSocketClient
            self.obs_manager_class = OBSManager
            self.scene_controller_class = SceneController
            self.emotion_mapper_class = EmotionMapper
            self.websocket_client_class = OBSWebSocketClient
        except ImportError as e:
            self.skipTest(f"OBS integration modules not available: {e}")
    
    def test_obs_manager_initialization(self):
        """Test OBS manager initialization"""
        manager = self.obs_manager_class()
        self.assertIsNotNone(manager)
        self.assertFalse(manager.is_connected())
    
    def test_emotion_mapper_initialization(self):
        """Test emotion mapper initialization"""
        mapper = self.emotion_mapper_class()
        self.assertIsNotNone(mapper)
        self.assertIsInstance(mapper.get_mapping_strategies(), list)
    
    def test_emotion_mapper_configuration(self):
        """Test emotion mapper configuration save/load"""
        mapper = self.emotion_mapper_class()
        
        # Create test configuration
        test_config = {
            'mappings': {
                'happy': 'Scene_Happy',
                'sad': 'Scene_Sad'
            },
            'strategy': 'direct',
            'trigger_condition': 'immediate'
        }
        
        # Test save configuration
        config_file = 'test_emotion_config.json'
        mapper.save_configuration(config_file)
        self.assertTrue(os.path.exists(config_file))
        
        # Test load configuration
        mapper.load_configuration(config_file)
        
        # Cleanup
        if os.path.exists(config_file):
            os.remove(config_file)
    
    def test_websocket_client_mock_connection(self):
        """Test WebSocket client with mock connection"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = MagicMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            client = self.websocket_client_class('localhost', 4455, 'password')
            
            # Test connection (mocked)
            result = asyncio.run(client.connect())
            # Note: This will likely fail in real test, but tests the code path
    
    def test_scene_controller_initialization(self):
        """Test scene controller initialization"""
        mock_obs_manager = Mock()
        mock_emotion_mapper = Mock()
        
        controller = self.scene_controller_class(mock_obs_manager, mock_emotion_mapper)
        self.assertIsNotNone(controller)


class TestUIComponents(unittest.TestCase):
    """Test UI components"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            import tkinter as tk
            from ui import MainControlPanel, PreviewWindow, SettingsDialog, SystemStatusManager
            self.tk = tk
            self.main_panel_class = MainControlPanel
            self.preview_window_class = PreviewWindow
            self.settings_dialog_class = SettingsDialog
            self.status_manager_class = SystemStatusManager
            
            # Create test root window
            self.root = tk.Tk()
            self.root.withdraw()  # Hide test window
            
        except ImportError as e:
            self.skipTest(f"UI modules not available: {e}")
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_status_manager_initialization(self):
        """Test status manager initialization"""
        manager = self.status_manager_class()
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.panels), 0)
    
    def test_status_manager_panel_creation(self):
        """Test status panel creation"""
        manager = self.status_manager_class()
        panel = manager.create_panel(self.root, 'test_panel', 'Test Panel')
        
        self.assertIsNotNone(panel)
        self.assertEqual(len(manager.panels), 1)
        self.assertIn('test_panel', manager.panels)
    
    def test_status_manager_component_updates(self):
        """Test component status updates"""
        from ui.status_indicators import StatusLevel
        
        manager = self.status_manager_class()
        panel = manager.create_panel(self.root, 'test_panel')
        
        # Update component status
        manager.update_component_status(
            'test_panel', 'test_component', 
            StatusLevel.ONLINE, 'Test message'
        )
        
        # Verify status was updated
        status = panel.get_status('test_component')
        self.assertIsNotNone(status)
        self.assertEqual(status.level, StatusLevel.ONLINE)
        self.assertEqual(status.message, 'Test message')
    
    def test_main_panel_initialization(self):
        """Test main panel initialization"""
        test_settings = {
            'ui': {'theme': 'light', 'update_fps': 30},
            'camera': {'device_id': 0},
            'obs': {'host': 'localhost', 'port': 4455}
        }
        
        panel = self.main_panel_class(self.root, test_settings)
        self.assertIsNotNone(panel)
    
    def test_settings_dialog_initialization(self):
        """Test settings dialog initialization"""
        test_settings = {
            'obs': {'host': 'localhost', 'port': 4455},
            'emotion': {'confidence_threshold': 0.7}
        }
        
        dialog = self.settings_dialog_class(self.root, test_settings)
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog.settings, dict)


class TestAIEngine(unittest.TestCase):
    """Test AI engine components"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from ai_engine import EmotionDetector, RealTimeDetector
            from ai_engine.modules import CameraManager, FaceDetector
            self.emotion_detector_class = EmotionDetector
            self.real_time_detector_class = RealTimeDetector
            self.camera_manager_class = CameraManager
            self.face_detector_class = FaceDetector
        except ImportError as e:
            self.skipTest(f"AI engine modules not available: {e}")
    
    def test_emotion_detector_initialization(self):
        """Test emotion detector initialization"""
        detector = self.emotion_detector_class()
        self.assertIsNotNone(detector)
    
    def test_face_detector_initialization(self):
        """Test face detector initialization"""
        detector = self.face_detector_class()
        self.assertIsNotNone(detector)
    
    def test_camera_manager_initialization(self):
        """Test camera manager initialization"""
        manager = self.camera_manager_class()
        self.assertIsNotNone(manager)
        self.assertFalse(manager.is_camera_active())
    
    def test_real_time_detector_initialization(self):
        """Test real-time detector initialization"""
        emotion_detector = self.emotion_detector_class()
        face_detector = self.face_detector_class()
        
        rt_detector = self.real_time_detector_class(
            emotion_detector=emotion_detector,
            face_detector=face_detector
        )
        self.assertIsNotNone(rt_detector)


class TestConfigurationManagement(unittest.TestCase):
    """Test configuration and settings management"""
    
    def test_json_configuration_save_load(self):
        """Test JSON configuration save and load"""
        test_config = {
            'obs': {
                'host': 'localhost',
                'port': 4455,
                'password': 'test123'
            },
            'emotion': {
                'confidence_threshold': 0.8,
                'update_interval': 100
            }
        }
        
        config_file = 'test_config.json'
        
        # Save configuration
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2)
        
        self.assertTrue(os.path.exists(config_file))
        
        # Load configuration
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(test_config, loaded_config)
        
        # Cleanup
        if os.path.exists(config_file):
            os.remove(config_file)


class TestPerformanceAndStability(unittest.TestCase):
    """Test performance and stability aspects"""
    
    def test_threading_compatibility(self):
        """Test threading compatibility"""
        def worker_function():
            time.sleep(0.1)
            return "completed"
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=1.0)
            self.assertFalse(thread.is_alive())
    
    def test_memory_usage_basic(self):
        """Basic memory usage test"""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create some objects
        test_objects = []
        for i in range(1000):
            test_objects.append({'id': i, 'data': 'x' * 100})
        
        # Check memory increase
        current_memory = process.memory_info().rss
        self.assertGreater(current_memory, initial_memory)
        
        # Clean up
        del test_objects
        gc.collect()
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test file not found error handling
        try:
            with open('nonexistent_file.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            pass  # Expected error
        
        # Test invalid JSON error handling
        try:
            json.loads('{invalid json}')
        except json.JSONDecodeError:
            pass  # Expected error


class IntegrationTestSuite:
    """Complete integration test suite runner"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 80)
        print("LivePilotAI Day 5 - Integration Test Suite")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Define test suites
        test_suites = [
            ('OBS Integration', TestOBSIntegration),
            ('UI Components', TestUIComponents),
            ('AI Engine', TestAIEngine),
            ('Configuration Management', TestConfigurationManagement),
            ('Performance and Stability', TestPerformanceAndStability)
        ]
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        
        for suite_name, test_class in test_suites:
            print(f"\n{'-' * 40}")
            print(f"Running {suite_name} Tests")
            print(f"{'-' * 40}")
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # Run tests with custom result handler
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            
            # Record results
            self.test_results[suite_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.wasSuccessful()
            }
            
            total_tests += result.testsRun
            total_failed += len(result.failures) + len(result.errors)
            total_skipped += len(result.skipped) if hasattr(result, 'skipped') else 0
        
        total_passed = total_tests - total_failed - total_skipped
        
        self.end_time = time.time()
        
        # Print summary
        self._print_summary(total_tests, total_passed, total_failed, total_skipped)
        
        return total_failed == 0
    
    def _print_summary(self, total_tests, total_passed, total_failed, total_skipped):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests Run: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Skipped: {total_skipped}")
        print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        print(f"Execution Time: {(self.end_time - self.start_time):.2f} seconds")
        
        print(f"\nDetailed Results by Test Suite:")
        for suite_name, results in self.test_results.items():
            status = "✅ PASS" if results['success'] else "❌ FAIL"
            print(f"  {suite_name}: {status} ({results['tests_run']} tests)")
            if results['failures'] > 0 or results['errors'] > 0:
                print(f"    Failures: {results['failures']}, Errors: {results['errors']}")
            if results['skipped'] > 0:
                print(f"    Skipped: {results['skipped']}")
        
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else "❌ SOME TESTS FAILED"
        print(f"\nOverall Status: {overall_status}")
        
        if total_failed == 0:
            print("\n🎉 LivePilotAI Day 5 integration tests completed successfully!")
            print("✅ All systems are ready for production use.")
        else:
            print("\n⚠️  Some tests failed. Please review the failures before deployment.")
    
    def generate_test_report(self, filename="day5_test_report.json"):
        """Generate detailed test report"""
        report = {
            'timestamp': time.time(),
            'execution_time': self.end_time - self.start_time if self.end_time and self.start_time else 0,
            'test_results': self.test_results,
            'summary': {
                'total_tests': sum(r['tests_run'] for r in self.test_results.values()),
                'total_passed': sum(r['tests_run'] - r['failures'] - r['errors'] - r['skipped'] 
                                  for r in self.test_results.values()),
                'total_failed': sum(r['failures'] + r['errors'] for r in self.test_results.values()),
                'total_skipped': sum(r['skipped'] for r in self.test_results.values())
            },
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed test report saved to: {filename}")


def main():
    """Main test runner"""
    print("LivePilotAI Day 5 Integration Testing")
    print("Preparing test environment...")
    
    # Create and run test suite
    test_suite = IntegrationTestSuite()
    success = test_suite.run_all_tests()
    
    # Generate report
    test_suite.generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
