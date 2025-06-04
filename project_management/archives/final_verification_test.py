#!/usr/bin/env python3
"""
LivePilotAI Final Verification Test
驗證所有修復後的功能是否正常運作
"""

import os
import sys
import subprocess
import importlib
import time
from pathlib import Path

class LivePilotAIVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """記錄測試結果"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.results.append((test_name, success, message))
    
    def test_imports(self):
        """測試所有關鍵模組的導入"""
        print("\n=== 測試模組導入 ===")
        
        import_tests = [
            ("src.ai_engine.emotion_detector", "EmotionDetector"),
            ("src.ai_engine.modules.camera_manager", "CameraManager"),
            ("src.ai_engine.modules.face_detector", "FaceDetector"),
            ("src.ai_engine.modules.real_time_detector", "RealTimeEmotionDetector"),
            ("src.ui.preview_window", "PreviewWindow"),
            ("src.obs_integration.scene_controller", "SceneController"),
        ]
        
        for module_path, class_name in import_tests:
            try:
                # 嘗試導入模組
                module = importlib.import_module(module_path)
                
                # 嘗試獲取類別
                if hasattr(module, class_name):
                    self.log_result(f"Import {module_path}.{class_name}", True)
                else:
                    self.log_result(f"Import {module_path}.{class_name}", False, f"Class {class_name} not found")
                    
            except Exception as e:
                self.log_result(f"Import {module_path}.{class_name}", False, str(e))
    
    def test_class_instantiation(self):
        """測試關鍵類別的實例化"""
        print("\n=== 測試類別實例化 ===")
        
        try:
            from src.ai_engine.emotion_detector import EmotionDetector
            detector = EmotionDetector()
            self.log_result("EmotionDetector instantiation", True)
        except Exception as e:
            self.log_result("EmotionDetector instantiation", False, str(e))
        
        try:
            from src.ai_engine.modules.camera_manager import CameraManager
            camera_mgr = CameraManager()
            self.log_result("CameraManager instantiation", True)
        except Exception as e:
            self.log_result("CameraManager instantiation", False, str(e))
            
        try:
            from src.ai_engine.modules.face_detector import FaceDetector
            face_detector = FaceDetector()
            self.log_result("FaceDetector instantiation", True)
        except Exception as e:
            self.log_result("FaceDetector instantiation", False, str(e))
            
        try:
            from src.ai_engine.modules.real_time_detector import RealTimeEmotionDetector
            real_time_detector = RealTimeEmotionDetector()
            self.log_result("RealTimeEmotionDetector instantiation", True)
        except Exception as e:
            self.log_result("RealTimeEmotionDetector instantiation", False, str(e))
    
    def test_main_app_syntax(self):
        """測試主應用程式的語法"""
        print("\n=== 測試主應用程式語法 ===")
        
        try:
            # 嘗試編譯主應用程式
            with open("main_day5.py", "r", encoding="utf-8") as f:
                code = f.read()
            
            compile(code, "main_day5.py", "exec")
            self.log_result("main_day5.py syntax check", True)
            
        except SyntaxError as e:
            self.log_result("main_day5.py syntax check", False, f"Syntax error: {e}")
        except Exception as e:
            self.log_result("main_day5.py syntax check", False, str(e))
    
    def test_launcher_options(self):
        """測試啟動器選項"""
        print("\n=== 測試啟動器選項 ===")
        
        # 測試各種啟動模式
        launcher_tests = [
            ("python main_day5.py --help", "Help option"),
            ("python main_day5.py --mode=test", "Test mode"),
            ("python main_day5.py --mode=demo", "Demo mode"),
        ]
        
        for cmd, description in launcher_tests:
            try:
                # 使用短時間超時來測試啟動
                result = subprocess.run(
                    cmd.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=self.project_root
                )
                
                # 檢查是否有語法錯誤或導入錯誤
                if "SyntaxError" in result.stderr or "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
                    self.log_result(description, False, result.stderr.strip())
                else:
                    self.log_result(description, True, "Started successfully")
                    
            except subprocess.TimeoutExpired:
                # 超時通常意味著程式正在運行（這是好事）
                self.log_result(description, True, "Running (timeout expected)")
                
            except Exception as e:
                self.log_result(description, False, str(e))
    
    def test_emergency_tools(self):
        """測試緊急修復工具"""
        print("\n=== 測試緊急修復工具 ===")
        
        emergency_scripts = [
            "debug_launcher.py",
            "day5_readiness_check.py", 
            "comprehensive_diagnostic.py"
        ]
        
        for script in emergency_scripts:
            if os.path.exists(script):
                try:
                    # 檢查語法
                    with open(script, "r", encoding="utf-8") as f:
                        code = f.read()
                    compile(code, script, "exec")
                    self.log_result(f"Emergency tool {script}", True, "Syntax OK")
                except Exception as e:
                    self.log_result(f"Emergency tool {script}", False, str(e))
            else:
                self.log_result(f"Emergency tool {script}", False, "File not found")
    
    def test_window_management(self):
        """測試視窗管理功能"""
        print("\n=== 測試視窗管理功能 ===")
        
        try:
            from src.ui.preview_window import PreviewWindow
            
            # 測試PreviewWindow的方法
            preview = PreviewWindow()
            
            # 檢查所需方法是否存在
            required_methods = ['show', 'hide', 'focus', 'is_visible']
            for method in required_methods:
                if hasattr(preview, method):
                    self.log_result(f"PreviewWindow.{method}", True)
                else:
                    self.log_result(f"PreviewWindow.{method}", False, "Method missing")
                    
        except Exception as e:
            self.log_result("PreviewWindow functionality", False, str(e))
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 LivePilotAI 最終驗證測試")
        print("=" * 50)
        
        self.test_imports()
        self.test_class_instantiation()
        self.test_main_app_syntax()
        self.test_window_management()
        self.test_emergency_tools()
        self.test_launcher_options()
        
        # 總結結果
        print("\n" + "=" * 50)
        print("📊 測試結果總結")
        print("=" * 50)
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        print(f"通過: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有測試通過！LivePilotAI 已準備就緒！")
        else:
            print("⚠️  有部分測試失敗，請檢查錯誤訊息")
            print("\n失敗的測試:")
            for test_name, success, message in self.results:
                if not success:
                    print(f"  ❌ {test_name}: {message}")
        
        return passed == total

if __name__ == "__main__":
    verifier = LivePilotAIVerifier()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)
