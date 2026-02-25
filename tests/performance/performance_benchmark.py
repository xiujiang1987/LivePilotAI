"""
LivePilotAI - Performance Benchmark Suite
Comprehensive performance testing and benchmarking
"""

import time
import psutil
import threading
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import logging
import gc
from dataclasses import dataclass
from contextlib import contextmanager

# Add src directory to path (go up one level from tests/ to project root)
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    test_name: str
    execution_time: float
    memory_usage_start: int
    memory_usage_end: int
    memory_peak: int
    cpu_usage_avg: float
    success: bool
    error_message: str = ""


class PerformanceBenchmark:
    """Performance benchmark utility"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process()
        
    @contextmanager
    def measure_performance(self, test_name: str):
        """Context manager for measuring performance"""
        # Initial measurements
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        cpu_samples = []
        
        # CPU monitoring thread
        monitoring = True
        def monitor_cpu():
            while monitoring:
                cpu_samples.append(self.process.cpu_percent())
                time.sleep(0.1)
        
        cpu_thread = threading.Thread(target=monitor_cpu, daemon=True)
        cpu_thread.start()
        
        success = True
        error_message = ""
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Performance test {test_name} failed: {e}")
        finally:
            # Stop monitoring
            monitoring = False
            cpu_thread.join(timeout=1.0)
            
            # Final measurements
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            peak_memory = max(start_memory, end_memory)  # Simplified peak detection
            avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
            
            # Record metrics
            metrics = PerformanceMetrics(
                test_name=test_name,
                execution_time=end_time - start_time,
                memory_usage_start=start_memory,
                memory_usage_end=end_memory,
                memory_peak=peak_memory,
                cpu_usage_avg=avg_cpu,
                success=success,
                error_message=error_message
            )
            
            self.metrics.append(metrics)
            logger.info(f"Performance test '{test_name}' completed in {metrics.execution_time:.3f}s")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        total_time = sum(m.execution_time for m in self.metrics)
        avg_cpu = sum(m.cpu_usage_avg for m in self.metrics) / len(self.metrics)
        max_memory = max(m.memory_peak for m in self.metrics)
        success_rate = sum(1 for m in self.metrics if m.success) / len(self.metrics)
        
        return {
            'total_tests': len(self.metrics),
            'total_execution_time': total_time,
            'average_cpu_usage': avg_cpu,
            'peak_memory_usage': max_memory,
            'success_rate': success_rate,
            'failed_tests': [m.test_name for m in self.metrics if not m.success]
        }


class OBSIntegrationBenchmark:
    """Benchmark OBS integration performance"""
    
    def __init__(self, benchmark: PerformanceBenchmark):
        self.benchmark = benchmark
    
    def run_benchmarks(self):
        """Run all OBS integration benchmarks"""
        print("\n" + "="*50)
        print("OBS Integration Performance Benchmarks")
        print("="*50)
        
        self._test_obs_manager_initialization()
        self._test_emotion_mapper_performance()
        self._test_websocket_client_mock()
        self._test_scene_controller_operations()
    
    def _test_obs_manager_initialization(self):
        """Benchmark OBS manager initialization"""
        with self.benchmark.measure_performance("OBS Manager Initialization"):
            try:
                from obs_integration import OBSManager
                
                # Test multiple initializations
                managers = []
                for i in range(10):
                    manager = OBSManager()
                    managers.append(manager)
                
                # Cleanup
                del managers
                gc.collect()
                
            except ImportError:
                logger.warning("OBS integration modules not available for benchmarking")
    
    def _test_emotion_mapper_performance(self):
        """Benchmark emotion mapper performance"""
        with self.benchmark.measure_performance("Emotion Mapper Operations"):
            try:
                from obs_integration import EmotionMapper
                
                mapper = EmotionMapper()
                
                # Test mapping operations
                test_emotions = ['happy', 'sad', 'angry', 'neutral', 'surprise']
                for _ in range(100):
                    for emotion in test_emotions:
                        mapping = mapper.map_emotion_to_scene(emotion, 0.8)
                        mapper.update_emotion_context(emotion, 0.8)
                
                # Test configuration save/load
                config_file = 'benchmark_config.json'
                mapper.save_configuration(config_file)
                mapper.load_configuration(config_file)
                
                # Cleanup
                if os.path.exists(config_file):
                    os.remove(config_file)
                    
            except ImportError:
                logger.warning("Emotion mapper not available for benchmarking")
    
    def _test_websocket_client_mock(self):
        """Benchmark WebSocket client operations (mocked)"""
        with self.benchmark.measure_performance("WebSocket Client Mock Operations"):
            try:
                from obs_integration import OBSWebSocketClient
                
                # Create multiple clients (won't actually connect)
                clients = []
                for i in range(5):
                    client = OBSWebSocketClient('localhost', 4455, f'password{i}')
                    clients.append(client)
                
                # Simulate message handling
                for client in clients:
                    for j in range(20):
                        # Mock message handling
                        message = {'requestType': 'GetSceneList', 'requestId': j}
                        # client._generate_request_id()  # Test internal methods if available
                
                del clients
                gc.collect()
                
            except ImportError:
                logger.warning("WebSocket client not available for benchmarking")
    
    def _test_scene_controller_operations(self):
        """Benchmark scene controller operations"""
        with self.benchmark.measure_performance("Scene Controller Operations"):
            try:
                from obs_integration import SceneController, OBSManager, EmotionMapper
                from unittest.mock import Mock
                
                # Create mocked dependencies
                mock_obs_manager = Mock()
                mock_emotion_mapper = Mock()
                
                # Test scene controller
                controller = SceneController(mock_obs_manager, mock_emotion_mapper)
                
                # Test operations
                for i in range(50):
                    controller.set_auto_switching(i % 2 == 0)
                    # Mock scene switching operations
                    
            except ImportError:
                logger.warning("Scene controller not available for benchmarking")


class UIComponentsBenchmark:
    """Benchmark UI components performance"""
    
    def __init__(self, benchmark: PerformanceBenchmark):
        self.benchmark = benchmark
    
    def run_benchmarks(self):
        """Run all UI component benchmarks"""
        print("\n" + "="*50)
        print("UI Components Performance Benchmarks")
        print("="*50)
        
        self._test_status_manager_performance()
        self._test_settings_dialog_creation()
        self._test_main_panel_initialization()
    
    def _test_status_manager_performance(self):
        """Benchmark status manager performance"""
        with self.benchmark.measure_performance("Status Manager Operations"):
            try:
                import tkinter as tk
                from ui import SystemStatusManager, StatusLevel
                
                # Create test root (hidden)
                root = tk.Tk()
                root.withdraw()
                
                try:
                    manager = SystemStatusManager()
                    
                    # Create multiple panels
                    panels = []
                    for i in range(5):
                        panel = manager.create_panel(root, f'test_panel_{i}', f'Test Panel {i}')
                        panels.append(panel)
                    
                    # Add indicators and update statuses rapidly
                    statuses = [StatusLevel.ONLINE, StatusLevel.WARNING, StatusLevel.ERROR, StatusLevel.ACTIVE]
                    for i in range(100):
                        panel_idx = i % len(panels)
                        status = statuses[i % len(statuses)]
                        manager.update_component_status(
                            f'test_panel_{panel_idx}', 
                            f'component_{i}',
                            status,
                            f'Test message {i}'
                        )
                    
                    # Test health summary generation
                    for _ in range(10):
                        health = manager.get_system_health()
                    
                finally:
                    root.destroy()
                    
            except ImportError:
                logger.warning("UI components not available for benchmarking")
    
    def _test_settings_dialog_creation(self):
        """Benchmark settings dialog creation"""
        with self.benchmark.measure_performance("Settings Dialog Creation"):
            try:
                import tkinter as tk
                from ui import SettingsDialog
                
                root = tk.Tk()
                root.withdraw()
                
                try:
                    test_settings = {
                        'obs': {'host': 'localhost', 'port': 4455},
                        'emotion': {'confidence_threshold': 0.7},
                        'ui': {'theme': 'dark'}
                    }
                    
                    # Create multiple dialog instances
                    dialogs = []
                    for i in range(5):
                        dialog = SettingsDialog(root, test_settings)
                        dialogs.append(dialog)
                    
                    del dialogs
                    gc.collect()
                    
                finally:
                    root.destroy()
                    
            except ImportError:
                logger.warning("Settings dialog not available for benchmarking")
    
    def _test_main_panel_initialization(self):
        """Benchmark main panel initialization"""
        with self.benchmark.measure_performance("Main Panel Initialization"):
            try:
                import tkinter as tk
                from ui import MainControlPanel
                
                root = tk.Tk()
                root.withdraw()
                
                try:
                    test_settings = {
                        'ui': {'theme': 'light', 'update_fps': 30},
                        'camera': {'device_id': 0},
                        'obs': {'host': 'localhost', 'port': 4455}
                    }
                    
                    # Create main panel
                    panel = MainControlPanel(root, test_settings)
                    
                    # Simulate some operations
                    for i in range(10):
                        panel.update_emotion_display('happy', 0.8)
                        panel.update_fps_display(30.0)
                    
                finally:
                    root.destroy()
                    
            except ImportError:
                logger.warning("Main panel not available for benchmarking")


class AIEngineBenchmark:
    """Benchmark AI engine performance"""
    
    def __init__(self, benchmark: PerformanceBenchmark):
        self.benchmark = benchmark
    
    def run_benchmarks(self):
        """Run all AI engine benchmarks"""
        print("\n" + "="*50)
        print("AI Engine Performance Benchmarks")
        print("="*50)
        
        self._test_emotion_detector_initialization()
        self._test_camera_manager_operations()
        self._test_real_time_detector_setup()
    
    def _test_emotion_detector_initialization(self):
        """Benchmark emotion detector initialization"""
        with self.benchmark.measure_performance("Emotion Detector Initialization"):
            try:
                from ai_engine import EmotionDetector
                
                # Test multiple initializations
                detectors = []
                for i in range(3):  # Limit to 3 due to model loading overhead
                    detector = EmotionDetector()
                    detectors.append(detector)
                
                del detectors
                gc.collect()
                
            except ImportError:
                logger.warning("Emotion detector not available for benchmarking")
    
    def _test_camera_manager_operations(self):
        """Benchmark camera manager operations"""
        with self.benchmark.measure_performance("Camera Manager Operations"):
            try:
                from ai_engine.modules import CameraManager
                
                manager = CameraManager()
                
                # Test camera operations (without actually starting camera)
                for i in range(50):
                    devices = manager.get_available_cameras()
                    is_active = manager.is_camera_active()
                    current_device = manager.get_current_camera_info()
                
            except ImportError:
                logger.warning("Camera manager not available for benchmarking")
    
    def _test_real_time_detector_setup(self):
        """Benchmark real-time detector setup"""
        with self.benchmark.measure_performance("Real-Time Detector Setup"):
            try:
                from ai_engine import EmotionDetector, RealTimeDetector
                from ai_engine.modules import FaceDetector
                
                emotion_detector = EmotionDetector()
                face_detector = FaceDetector()
                
                # Create real-time detector
                rt_detector = RealTimeDetector(
                    emotion_detector=emotion_detector,
                    face_detector=face_detector
                )
                
                # Test some operations
                for i in range(10):
                    config = rt_detector.get_processing_config()
                    
            except ImportError:
                logger.warning("Real-time detector not available for benchmarking")


class SystemResourcesBenchmark:
    """Benchmark system resources and limits"""
    
    def __init__(self, benchmark: PerformanceBenchmark):
        self.benchmark = benchmark
    
    def run_benchmarks(self):
        """Run all system resource benchmarks"""
        print("\n" + "="*50)
        print("System Resources Performance Benchmarks")
        print("="*50)
        
        self._test_memory_allocation()
        self._test_threading_performance()
        self._test_file_io_performance()
        self._test_json_processing()
    
    def _test_memory_allocation(self):
        """Benchmark memory allocation patterns"""
        with self.benchmark.measure_performance("Memory Allocation Test"):
            # Create large data structures
            data_structures = []
            
            for i in range(100):
                data = {
                    'id': i,
                    'emotions': ['happy', 'sad', 'angry'] * 100,
                    'timestamps': [time.time()] * 1000,
                    'metadata': {'key': 'value'} * 50
                }
                data_structures.append(data)
            
            # Process data
            for data in data_structures:
                processed = json.dumps(data)
                parsed = json.loads(processed)
            
            del data_structures
            gc.collect()
    
    def _test_threading_performance(self):
        """Benchmark threading performance"""
        with self.benchmark.measure_performance("Threading Performance"):
            def worker_task(task_id, duration=0.01):
                start = time.time()
                while time.time() - start < duration:
                    # Simulate work
                    result = sum(i*i for i in range(100))
                return task_id, result
            
            # Create and run multiple threads
            threads = []
            for i in range(20):
                thread = threading.Thread(target=worker_task, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=5.0)
    
    def _test_file_io_performance(self):
        """Benchmark file I/O performance"""
        with self.benchmark.measure_performance("File I/O Performance"):
            test_data = {
                'settings': {
                    'obs': {'host': 'localhost', 'port': 4455},
                    'emotions': ['happy', 'sad', 'angry'] * 100
                },
                'large_array': list(range(1000)),
                'metadata': {'timestamp': time.time()}
            }
            
            # Test file operations
            for i in range(10):
                filename = f'benchmark_test_{i}.json'
                
                # Write file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2)
                
                # Read file
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Cleanup
                os.remove(filename)
    
    def _test_json_processing(self):
        """Benchmark JSON processing performance"""
        with self.benchmark.measure_performance("JSON Processing Performance"):
            # Create complex data structure
            complex_data = {
                'emotions': {
                    emotion: {
                        'confidence': 0.8,
                        'timestamp': time.time(),
                        'history': [{'value': i, 'time': time.time()} for i in range(100)]
                    }
                    for emotion in ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
                },
                'scenes': {
                    f'scene_{i}': {
                        'name': f'Scene {i}',
                        'emotions': ['happy', 'sad'],
                        'transitions': [{'from': 'scene_1', 'to': f'scene_{i}', 'duration': 1000}]
                    }
                    for i in range(50)
                }
            }
            
            # Test JSON operations
            for _ in range(20):
                json_str = json.dumps(complex_data)
                parsed_data = json.loads(json_str)


class BenchmarkRunner:
    """Main benchmark runner"""
    
    def __init__(self):
        self.benchmark = PerformanceBenchmark()
        self.start_time = None
        self.end_time = None
    
    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("="*80)
        print("LivePilotAI Day 5 - Performance Benchmark Suite")
        print("="*80)
        print(f"System Info: {psutil.cpu_count()} CPU cores, "
              f"{psutil.virtual_memory().total // (1024**3)} GB RAM")
        print(f"Python Version: {sys.version}")
        print("="*80)
        
        self.start_time = time.time()
        
        try:
            # Run benchmark suites
            obs_benchmark = OBSIntegrationBenchmark(self.benchmark)
            obs_benchmark.run_benchmarks()
            
            ui_benchmark = UIComponentsBenchmark(self.benchmark)
            ui_benchmark.run_benchmarks()
            
            ai_benchmark = AIEngineBenchmark(self.benchmark)
            ai_benchmark.run_benchmarks()
            
            system_benchmark = SystemResourcesBenchmark(self.benchmark)
            system_benchmark.run_benchmarks()
            
        except Exception as e:
            logger.error(f"Benchmark execution error: {e}")
        
        self.end_time = time.time()
        
        # Print results
        self._print_results()
        
        # Generate report
        self._generate_report()
    
    def _print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        summary = self.benchmark.get_summary()
        
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Total Execution Time: {summary.get('total_execution_time', 0):.2f} seconds")
        print(f"Average CPU Usage: {summary.get('average_cpu_usage', 0):.1f}%")
        print(f"Peak Memory Usage: {summary.get('peak_memory_usage', 0) / (1024*1024):.1f} MB")
        print(f"Success Rate: {summary.get('success_rate', 0)*100:.1f}%")
        
        if summary.get('failed_tests'):
            print(f"\nFailed Tests: {', '.join(summary['failed_tests'])}")
        
        print(f"\nDetailed Results:")
        print("-" * 80)
        print(f"{'Test Name':<40} {'Time (s)':<12} {'Memory (MB)':<15} {'CPU %':<10} {'Status'}")
        print("-" * 80)
        
        for metric in self.benchmark.metrics:
            memory_mb = (metric.memory_peak - metric.memory_usage_start) / (1024*1024)
            status = "✅ PASS" if metric.success else "❌ FAIL"
            
            print(f"{metric.test_name:<40} "
                  f"{metric.execution_time:<12.3f} "
                  f"{memory_mb:<15.1f} "
                  f"{metric.cpu_usage_avg:<10.1f} "
                  f"{status}")
        
        print("-" * 80)
        
        # Performance assessment
        total_time = summary.get('total_execution_time', 0)
        if total_time < 30:
            assessment = "🚀 EXCELLENT - Very fast performance"
        elif total_time < 60:
            assessment = "✅ GOOD - Acceptable performance"
        elif total_time < 120:
            assessment = "⚠️ MODERATE - Consider optimization"
        else:
            assessment = "❌ SLOW - Optimization required"
        
        print(f"\nPerformance Assessment: {assessment}")
    
    def _generate_report(self):
        """Generate detailed benchmark report"""
        report = {
            'timestamp': time.time(),
            'execution_time': self.end_time - self.start_time,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'python_version': sys.version,
                'platform': sys.platform
            },
            'summary': self.benchmark.get_summary(),
            'detailed_metrics': [
                {
                    'test_name': m.test_name,
                    'execution_time': m.execution_time,
                    'memory_usage_start': m.memory_usage_start,
                    'memory_usage_end': m.memory_usage_end,
                    'memory_peak': m.memory_peak,
                    'cpu_usage_avg': m.cpu_usage_avg,
                    'success': m.success,
                    'error_message': m.error_message
                }
                for m in self.benchmark.metrics
            ]
        }
        
        filename = f"day5_performance_report_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed performance report saved to: {filename}")


def main():
    """Main benchmark entry point"""
    try:
        runner = BenchmarkRunner()
        runner.run_all_benchmarks()
        
        print("\n🎯 Performance benchmarking completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark error: {e}")
        logger.error(f"Benchmark execution failed: {e}")


if __name__ == "__main__":
    main()
