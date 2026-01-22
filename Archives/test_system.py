#!/usr/bin/env python3
"""
LivePilotAI 系統測試腳本
驗證所有核心組件是否正常工作
"""

import sys
import os
import asyncio
import time
from pathlib import Path
import traceback

# 添加源代碼路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

class LivePilotTester:
    """LivePilotAI 系統測試器"""
    
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.total_tests = 0
    
    def print_header(self):
        """打印測試標題"""
        print("=" * 80)
        print("🧪 LivePilotAI 系統測試")
        print("=" * 80)
        print()
    
    def print_test(self, test_name: str):
        """打印測試名稱"""
        print(f"🔍 測試: {test_name}")
        self.total_tests += 1
    
    def print_success(self, message: str = "通過"):
        """打印成功訊息"""
        print(f"  ✅ {message}")
        self.passed_tests += 1
        print()
    
    def print_failure(self, error: str):
        """打印失敗訊息"""
        print(f"  ❌ 失敗: {error}")
        print()
    
    def print_warning(self, message: str):
        """打印警告訊息"""
        print(f"  ⚠️  警告: {message}")
        print()
    
    def test_python_environment(self):
        """測試Python環境"""
        self.print_test("Python環境檢查")
        
        # 檢查Python版本
        if sys.version_info < (3, 8):
            self.print_failure(f"Python版本過低: {sys.version}, 需要3.8+")
            return False
        
        self.print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    
    def test_core_dependencies(self):
        """測試核心依賴包"""
        self.print_test("核心依賴包檢查")
        
        required_packages = [
            ('cv2', 'opencv-python'),
            ('numpy', 'numpy'),
            ('PIL', 'pillow'),
        ]
        
        missing_packages = []
        
        for module, package in required_packages:
            try:
                __import__(module)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} 未安裝")
        
        if missing_packages:
            self.print_failure(f"缺少依賴包: {', '.join(missing_packages)}")
            return False
        
        self.print_success("所有核心依賴包已安裝")
        return True
    
    def test_web_dependencies(self):
        """測試Web依賴包"""
        self.print_test("Web依賴包檢查")
        
        web_packages = [
            ('fastapi', 'fastapi'),
            ('uvicorn', 'uvicorn'),
            ('websockets', 'websockets'),
            ('pydantic', 'pydantic'),
        ]
        
        missing_packages = []
        
        for module, package in web_packages:
            try:
                __import__(module)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} 未安裝")
        
        if missing_packages:
            self.print_warning(f"Web功能將不可用，缺少: {', '.join(missing_packages)}")
            return False
        
        self.print_success("所有Web依賴包已安裝")
        return True
    
    def test_camera_access(self):
        """測試攝影機訪問"""
        self.print_test("攝影機訪問測試")
        
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                self.print_failure("無法開啟攝影機")
                return False
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                self.print_failure("無法讀取攝影機畫面")
                return False
            
            height, width = frame.shape[:2]
            self.print_success(f"攝影機可用 ({width}x{height})")
            return True
            
        except Exception as e:
            self.print_failure(f"攝影機測試錯誤: {e}")
            return False
    
    def test_emotion_detector(self):
        """測試情緒檢測模組"""
        self.print_test("情緒檢測模組測試")
        
        try:
            # 測試修正版情緒檢測器
            from ai.emotion_detector_fix import EmotionDetector
            
            detector = EmotionDetector()
            print(f"  ✅ 情緒檢測器初始化成功")
            print(f"  ✅ 支援情緒類別: {len(detector.emotion_categories)}種")
            
            # 創建測試圖像
            import numpy as np
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 測試檢測功能
            result = detector.detect_emotion(test_image)
            if result:
                print(f"  ✅ 情緒檢測功能正常")
                self.print_success("情緒檢測模組可用")
                return True
            else:
                self.print_warning("情緒檢測返回空結果（可能無臉部）")
                return True
                
        except Exception as e:
            self.print_failure(f"情緒檢測模組錯誤: {e}")
            return False
    
    def test_config_manager(self):
        """測試配置管理器"""
        self.print_test("配置管理器測試")
        
        try:
            from config.config_manager import ConfigManager, get_config
            
            # 測試配置管理器
            config_manager = ConfigManager()
            config = get_config()
            
            print(f"  ✅ 配置管理器初始化成功")
            print(f"  ✅ OBS配置: {config.obs.host}:{config.obs.port}")
            print(f"  ✅ 攝影機配置: {config.camera.width}x{config.camera.height}")
            print(f"  ✅ AI配置: 檢測間隔 {config.ai.emotion_detection_interval}s")
            
            # 測試配置驗證
            errors = config_manager.validate_config()
            if errors:
                self.print_warning(f"配置驗證發現問題: {errors}")
            else:
                print(f"  ✅ 配置驗證通過")
            
            self.print_success("配置管理器可用")
            return True
            
        except Exception as e:
            self.print_failure(f"配置管理器錯誤: {e}")
            return False
    
    def test_obs_integration(self):
        """測試OBS整合模組"""
        self.print_test("OBS整合模組測試")
        
        try:
            from obs_integration.scene_manager import OBSSceneManager
            from config.config_manager import get_obs_config
            
            obs_config = get_obs_config()
            scene_manager = OBSSceneManager(obs_config)
            
            print(f"  ✅ OBS場景管理器初始化成功")
            print(f"  ✅ 支援佈局類型: {len(scene_manager.layout_templates)}種")
            
            # 注意：不實際連接OBS，只測試模組載入
            self.print_warning("OBS連接測試需要OBS Studio運行")
            self.print_success("OBS整合模組可用")
            return True
            
        except Exception as e:
            self.print_failure(f"OBS整合模組錯誤: {e}")
            return False
    
    def test_ai_layout_engine(self):
        """測試AI佈局引擎"""
        self.print_test("AI佈局引擎測試")
        
        try:
            from obs_integration.ai_layout_engine import LayoutDecisionEngine, ViewerMetrics, ContextData, ContentType
            
            engine = LayoutDecisionEngine()
            print(f"  ✅ AI佈局引擎初始化成功")
            
            # 創建測試數據
            test_metrics = ViewerMetrics(
                viewer_count=100,
                chat_messages_per_minute=15.0,
                average_message_length=25.0,
                emoji_usage_rate=0.3,
                follow_rate=0.05,
                donation_frequency=0.02
            )
            
            test_context = ContextData(
                content_type=ContentType.GAMING,
                stream_duration=1800,
                current_game="測試遊戲"
            )
            
            # 測試決策功能
            decision = engine.make_layout_decision("happy", 0.8, test_metrics, test_context)
            print(f"  ✅ 佈局決策測試: {decision.recommended_layout}")
            print(f"  ✅ 決策信心度: {decision.confidence:.2f}")
            
            self.print_success("AI佈局引擎可用")
            return True
            
        except Exception as e:
            self.print_failure(f"AI佈局引擎錯誤: {e}")
            return False
    
    def test_web_control_panel(self):
        """測試Web控制台"""
        self.print_test("Web控制台測試")
        
        try:
            # 檢查是否有FastAPI依賴
            import fastapi
            import uvicorn
            
            # 測試模組導入
            from api.web_control_panel import app
            
            print(f"  ✅ FastAPI應用初始化成功")
            print(f"  ✅ Web控制台模組可用")
            
            self.print_warning("Web服務器測試需要手動啟動")
            self.print_success("Web控制台模組可用")
            return True
            
        except ImportError as e:
            self.print_failure(f"Web依賴缺失: {e}")
            return False
        except Exception as e:
            self.print_failure(f"Web控制台錯誤: {e}")
            return False
    
    async def test_bridge_integration(self):
        """測試橋接器整合"""
        self.print_test("系統橋接器測試")
        
        try:
            from obs_integration.livepilot_bridge import LivePilotAIBridge, StreamingConfig
            
            config = StreamingConfig()
            bridge = LivePilotAIBridge(config)
            
            print(f"  ✅ 系統橋接器初始化成功")
            print(f"  ✅ 配置載入完成")
            
            # 測試狀態獲取
            status = bridge.get_current_status()
            print(f"  ✅ 系統狀態: {status}")
            
            self.print_warning("完整功能測試需要OBS和攝影機")
            self.print_success("系統橋接器可用")
            return True
            
        except Exception as e:
            self.print_failure(f"系統橋接器錯誤: {e}")
            return False
    
    def test_directory_structure(self):
        """測試目錄結構"""
        self.print_test("目錄結構檢查")
        
        required_dirs = [
            "src",
            "src/ai",
            "src/obs_integration", 
            "src/api",
            "src/config"
        ]
        
        optional_dirs = [
            "logs",
            "models",
            "static",
            "temp"
        ]
        
        missing_dirs = []
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
                print(f"  ❌ {dir_path}")
            else:
                print(f"  ✅ {dir_path}")
        
        for dir_path in optional_dirs:
            if not Path(dir_path).exists():
                print(f"  ⚠️  {dir_path} (將自動創建)")
                Path(dir_path).mkdir(exist_ok=True)
            else:
                print(f"  ✅ {dir_path}")
        
        if missing_dirs:
            self.print_failure(f"缺少必要目錄: {', '.join(missing_dirs)}")
            return False
        
        self.print_success("目錄結構完整")
        return True
    
    def test_file_permissions(self):
        """測試文件權限"""
        self.print_test("文件權限檢查")
        
        # 測試寫入權限
        try:
            test_file = Path("temp/test_write.txt")
            test_file.parent.mkdir(exist_ok=True)
            
            with open(test_file, "w") as f:
                f.write("test")
            
            test_file.unlink()
            print(f"  ✅ 文件寫入權限正常")
            
        except Exception as e:
            self.print_failure(f"文件寫入權限錯誤: {e}")
            return False
        
        self.print_success("文件權限正常")
        return True
    
    async def run_all_tests(self):
        """運行所有測試"""
        self.print_header()
        
        # 基礎環境測試
        tests = [
            self.test_python_environment,
            self.test_directory_structure,
            self.test_file_permissions,
            self.test_core_dependencies,
            self.test_web_dependencies,
            self.test_camera_access,
            self.test_config_manager,
            self.test_emotion_detector,
            self.test_obs_integration,
            self.test_ai_layout_engine,
            self.test_web_control_panel,
        ]
        
        # 運行同步測試
        for test in tests:
            try:
                test()
            except Exception as e:
                self.print_failure(f"測試執行錯誤: {e}")
                traceback.print_exc()
        
        # 運行異步測試
        try:
            await self.test_bridge_integration()
        except Exception as e:
            self.print_failure(f"橋接器測試錯誤: {e}")
        
        # 打印總結
        self.print_summary()
    
    def print_summary(self):
        """打印測試總結"""
        print("=" * 80)
        print("📊 測試總結")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"✅ 通過測試: {self.passed_tests}/{self.total_tests}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 系統狀態良好！")
        elif success_rate >= 60:
            print("⚠️  系統部分功能可用，建議檢查失敗項目")
        else:
            print("❌ 系統存在嚴重問題，需要修復")
        
        print()
        print("💡 使用建議:")
        if self.passed_tests >= 8:
            print("  - 可以嘗試啟動 start.bat 或 start.ps1")
            print("  - 確保OBS Studio已安裝並設置WebSocket")
            print("  - 瀏覽器開啟 http://localhost:8000")
        else:
            print("  - 請先解決依賴問題: pip install -r requirements.txt")
            print("  - 檢查Python版本和系統權限")
            print("  - 重新運行測試確認修復")
        
        print()

async def main():
    """主函數"""
    tester = LivePilotTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
