#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI - 修復版啟動器
Fixed version without Unicode issues
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def setup_environment():
    """Setup the runtime environment"""
    # Add src directory to Python path
    src_path = Path(__file__).parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

def run_main_application():
    """Run the main LivePilotAI application"""
    print("Starting LivePilotAI main application...")
    
    try:
        # 檢查主程式檔案
        main_file = "main_day5.py"
        if not Path(main_file).exists():
            print(f"Error: {main_file} not found!")
            return False
            
        # 嘗試直接導入並執行
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_day5", main_file)
        if spec and spec.loader:
            main_day5 = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_day5)
            print("LivePilotAI main application started successfully")
            return True
        else:
            print("Failed to load main application module")
            return False
            
    except Exception as e:
        print(f"Failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run system tests"""
    print("Running system tests...")
    
    test_files = [
        "day5_simple_test.py",
        "day5_validation_test.py", 
        "basic_test.py",
        "simple_test.py"
    ]
    
    passed = 0
    total = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            total += 1
            print(f"  Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"  [PASS] {test_file}")
                    passed += 1
                else:
                    print(f"  [FAIL] {test_file}")
                    if result.stderr:
                        print(f"    Error: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                print(f"  [TIMEOUT] {test_file}")
            except Exception as e:
                print(f"  [ERROR] {test_file}: {e}")
    
    print(f"\nTest Summary: {passed}/{total} tests passed")
    return passed > 0

def run_obs_test():
    """Run OBS integration test"""
    print("Testing OBS integration...")
    
    # 檢查可用的測試檔案
    obs_test_files = [
        "obs_test_simple.py",
        "obs_integration_test.py"
    ]
    
    for test_file in obs_test_files:
        if Path(test_file).exists():
            print(f"  Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True, timeout=20)
                if result.returncode == 0:
                    print("  [PASS] OBS integration test")
                    return True
                else:
                    print("  [FAIL] OBS integration test")
                    if result.stderr:
                        print(f"    Error: {result.stderr.strip()}")
                    return False
            except subprocess.TimeoutExpired:
                print("  [TIMEOUT] OBS test timed out")
                return False
            except Exception as e:
                print(f"  [ERROR] OBS test failed: {e}")
                return False
    
    print("  [WARNING] No OBS test files found")
    return False

def show_help():
    """Show help information"""
    print("""
LivePilotAI - AI-Powered Live Streaming Director

Usage:
  python main_fixed.py [options]

Options:
  --app, -a          Start main application (default)
  --test, -t         Run system tests
  --obs-test, -o     Test OBS integration
  --help, -h         Show this help

Examples:
  python main_fixed.py                    # Start main application
  python main_fixed.py --test             # Run tests
  python main_fixed.py --obs-test         # Test OBS
  python main_fixed.py --help             # Show help
""")

def main():
    """Main entry point"""
    setup_environment()
    
    parser = argparse.ArgumentParser(description='LivePilotAI - AI-Powered Live Streaming Director')
    parser.add_argument('--app', '-a', action='store_true', 
                       help='Start main application (default)')
    parser.add_argument('--test', '-t', action='store_true', 
                       help='Run system tests')
    parser.add_argument('--obs-test', '-o', action='store_true', 
                       help='Test OBS integration')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LivePilotAI - AI-Powered Live Streaming Director")
    print("=" * 60)
    
    success = False
    
    if args.test:
        success = run_tests()
    elif args.obs_test:
        success = run_obs_test()
    elif args.app or len(sys.argv) == 1:  # Default action
        success = run_main_application()
    else:
        show_help()
        success = True
    
    if success:
        print("\nOperation completed successfully!")
    else:
        print("\nOperation failed. Check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
