#!/usr/bin/env python3
"""
OBS Integration Test
測試 LivePilotAI 與 OBS Studio 的整合功能
"""

import sys
import asyncio
import json
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

class OBSIntegrationTest:
    def __init__(self):
        self.test_results = []
          def log_test(self, test_name, result, message=""):
        """記錄測試結果"""
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            'test': test_name,
            'passed': result,
            'message': message
        })
    
    def test_imports(self):
        """測試模組導入"""
        print("🔧 測試模組導入...")
        
        try:
            from obs_integration import OBSManager, SceneController, EmotionMapper, OBSWebSocketClient
            self.log_test("OBS 整合模組導入", True)
        except ImportError as e:
            self.log_test("OBS 整合模組導入", False, str(e))
            return False
            
        try:
            import websockets
            self.log_test("WebSocket 模組", True)
        except ImportError:
            self.log_test("WebSocket 模組", False, "請安裝: pip install websockets")
            
        try:
            import obs_websocket_py
            self.log_test("OBS WebSocket Python 模組", True)
        except ImportError:
            self.log_test("OBS WebSocket Python 模組", False, "請安裝: pip install obs-websocket-py")
            
        return True
    
    def test_obs_websocket_client(self):
        """測試 OBS WebSocket 客戶端"""
        print("\n📡 測試 OBS WebSocket 客戶端...")
        
        try:
            from obs_integration.websocket_client import OBSWebSocketClient
            
            # 創建客戶端實例
            client = OBSWebSocketClient()
            self.log_test("WebSocket 客戶端創建", True)
            
            # 測試配置
            test_config = {
                'host': 'localhost',
                'port': 4455,
                'password': 'test_password'
            }
            
            client.configure(test_config)
            self.log_test("WebSocket 客戶端配置", True)
            
            return True
            
        except Exception as e:
            self.log_test("WebSocket 客戶端測試", False, str(e))
            return False
    
    def test_scene_controller(self):
        """測試場景控制器"""
        print("\n🎬 測試場景控制器...")
        
        try:
            from obs_integration.scene_controller import SceneController
            
            controller = SceneController()
            self.log_test("場景控制器創建", True)
            
            # 測試場景配置
            test_scenes = {
                'main': 'Main Scene',
                'closeup': 'Close-up Scene',
                'wide': 'Wide Scene'
            }
            
            controller.configure_scenes(test_scenes)
            self.log_test("場景配置", True)
            
            return True
            
        except Exception as e:
            self.log_test("場景控制器測試", False, str(e))
            return False
    
    def test_emotion_mapper(self):
        """測試情緒映射器"""
        print("\n😊 測試情緒映射器...")
        
        try:
            from obs_integration.emotion_mapper import EmotionMapper
            
            mapper = EmotionMapper()
            self.log_test("情緒映射器創建", True)
            
            # 測試情緒映射
            test_emotions = ['happy', 'sad', 'surprised', 'neutral']
            
            for emotion in test_emotions:
                scene = mapper.map_emotion_to_scene(emotion)
                if scene:
                    self.log_test(f"情緒映射 ({emotion})", True, f"映射到場景: {scene}")
                else:
                    self.log_test(f"情緒映射 ({emotion})", False, "未找到對應場景")
            
            return True
            
        except Exception as e:
            self.log_test("情緒映射器測試", False, str(e))
            return False
    
    def test_obs_manager(self):
        """測試 OBS 管理器"""
        print("\n🎛️ 測試 OBS 管理器...")
        
        try:
            from obs_integration.obs_manager import OBSManager
            
            manager = OBSManager()
            self.log_test("OBS 管理器創建", True)
            
            # 測試初始化
            manager.initialize()
            self.log_test("OBS 管理器初始化", True)
            
            return True
            
        except Exception as e:
            self.log_test("OBS 管理器測試", False, str(e))
            return False
    
    async def test_websocket_connection(self):
        """測試 WebSocket 連接 (需要 OBS Studio 運行)"""
        print("\n🌐 測試 WebSocket 連接...")
        
        try:
            import websockets
            
            # 嘗試連接到 OBS WebSocket
            try:
                async with websockets.connect(
                    "ws://localhost:4455", 
                    timeout=5
                ) as websocket:
                    self.log_test("WebSocket 連接", True, "成功連接到 OBS Studio")
                    return True
            except Exception as e:
                self.log_test("WebSocket 連接", False, 
                            "無法連接到 OBS Studio (請確保 OBS 正在運行且 WebSocket 插件已啟用)")
                return False
                
        except Exception as e:
            self.log_test("WebSocket 連接測試", False, str(e))
            return False
    
    def test_configuration_files(self):
        """測試配置文件"""
        print("\n📄 測試配置文件...")
        
        config_files = [
            "config/obs_config.json",
            "config/scenes.json",
            "config/emotion_mapping.json"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    self.log_test(f"配置文件 {config_file}", True, f"包含 {len(config_data)} 個項目")
                except json.JSONDecodeError:
                    self.log_test(f"配置文件 {config_file}", False, "JSON 格式錯誤")
                except Exception as e:
                    self.log_test(f"配置文件 {config_file}", False, str(e))
            else:
                self.log_test(f"配置文件 {config_file}", False, "文件不存在")
    
    def print_summary(self):
        """打印測試摘要"""
        print("\n" + "="*60)
        print("📊 OBS 整合測試摘要")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"總測試數: {total_tests}")
        print(f"通過: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n💡 建議:")
        if failed_tests == 0:
            print("  🎉 所有測試都通過了！OBS 整合系統已準備就緒。")
        else:
            print("  🔧 請修復失敗的測試後再次運行。")
            print("  📚 查看 OBS_INTEGRATION_GUIDE.md 獲取詳細說明。")
      async def run_all_tests(self):
        """運行所有測試"""
        print("開始 OBS 整合測試...")
        print("="*60)
        
        # 基礎測試
        self.test_imports()
        self.test_obs_websocket_client()
        self.test_scene_controller()
        self.test_emotion_mapper()
        self.test_obs_manager()
        self.test_configuration_files()
        
        # WebSocket 連接測試
        await self.test_websocket_connection()
        
        # 打印摘要
        self.print_summary()

def main():
    """主函數"""
    test_runner = OBSIntegrationTest()
    
    # 運行異步測試
    asyncio.run(test_runner.run_all_tests())

if __name__ == "__main__":
    main()
