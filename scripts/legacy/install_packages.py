#!/usr/bin/env python3
"""
LivePilotAI 套件安裝與驗證腳本
自動安裝和驗證所有必需的依賴套件
"""

import subprocess
import sys
import importlib
from typing import List, Dict, Tuple

class PackageInstaller:
    def __init__(self):
        self.critical_packages = {
            # 核心 AI/ML 框架
            'tensorflow': 'tensorflow>=2.13.0',
            'opencv-python': 'opencv-python>=4.8.0', 
            'numpy': 'numpy>=1.24.0',
            'pandas': 'pandas>=2.0.0',
            'scikit-learn': 'scikit-learn>=1.3.0',
            
            # 電腦視覺與人臉識別
            'mediapipe': 'mediapipe>=0.10.0',
            'face-recognition': 'face-recognition>=1.3.0',
            'pillow': 'pillow>=10.0.0',
            
            # 系統監控與工具
            'psutil': 'psutil>=5.9.0',
            'pynput': 'pynput>=1.7.6',
            
            # 網路通訊
            'websocket-client': 'websocket-client>=1.6.0',
            'requests': 'requests>=2.31.0',
            
            # OBS 整合
            'obs-websocket-py': 'obs-websocket-py>=1.0.0',
            
            # 音訊處理
            'pyaudio': 'pyaudio>=0.2.11',
            'sounddevice': 'sounddevice>=0.4.6',
            
            # 配置管理
            'PyYAML': 'PyYAML>=6.0',
            'colorlog': 'colorlog>=6.7.0',
            
            # Web 框架
            'fastapi': 'fastapi>=0.100.0',
            'uvicorn': 'uvicorn>=0.23.0',
            
            # 資料處理
            'matplotlib': 'matplotlib>=3.7.0',
            'seaborn': 'seaborn>=0.12.0',
        }
        
        self.import_map = {
            'opencv-python': 'cv2',
            'websocket-client': 'websocket',
            'pillow': 'PIL',
            'PyYAML': 'yaml',
            'scikit-learn': 'sklearn',
        }
    
    def check_package(self, package_name: str) -> bool:
        """檢查套件是否已安裝並可匯入"""
        import_name = self.import_map.get(package_name, package_name)
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package_spec: str) -> bool:
        """安裝指定套件"""
        try:
            print(f"📦 正在安裝: {package_spec}")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_spec],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 安裝失敗: {package_spec}")
            print(f"   錯誤: {e.stderr}")
            return False
    
    def upgrade_pip(self):
        """升級 pip 到最新版本"""
        try:
            print("🔄 升級 pip...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ pip 升級完成")
        except subprocess.CalledProcessError:
            print("⚠️  pip 升級失敗，繼續安裝...")
    
    def run_installation(self) -> Dict[str, bool]:
        """執行完整的套件安裝流程"""
        print("🚀 LivePilotAI 套件安裝開始...")
        print("=" * 60)
        
        # 升級 pip
        self.upgrade_pip()
        
        # 檢查和安裝套件
        results = {}
        missing_packages = []
        
        print("\n🔍 檢查套件狀態...")
        for package_name, package_spec in self.critical_packages.items():
            if self.check_package(package_name):
                print(f"✅ {package_name}: 已安裝")
                results[package_name] = True
            else:
                print(f"❌ {package_name}: 缺失")
                missing_packages.append((package_name, package_spec))
                results[package_name] = False
        
        if not missing_packages:
            print("\n🎉 所有必需套件都已安裝！")
            return results
        
        print(f"\n📦 需要安裝 {len(missing_packages)} 個套件...")
        
        # 安裝缺失的套件
        for package_name, package_spec in missing_packages:
            success = self.install_package(package_spec)
            if success:
                # 重新檢查
                if self.check_package(package_name):
                    print(f"✅ {package_name}: 安裝成功")
                    results[package_name] = True
                else:
                    print(f"⚠️  {package_name}: 安裝完成但無法匯入")
                    results[package_name] = False
            else:
                results[package_name] = False
        
        return results
    
    def generate_report(self, results: Dict[str, bool]):
        """生成安裝報告"""
        print("\n" + "=" * 60)
        print("📊 LivePilotAI 套件安裝報告")
        print("=" * 60)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"📈 安裝成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count == total_count:
            print("🎉 所有套件安裝成功！LivePilotAI 準備就緒！")
        else:
            print("\n❌ 安裝失敗的套件:")
            for package, success in results.items():
                if not success:
                    print(f"   • {package}")
            
            print("\n🛠️  建議解決方案:")
            print("   1. 確認網路連接正常")
            print("   2. 檢查 Python 版本 (建議 3.8+)")
            print("   3. 嘗試手動安裝失敗的套件")
            print("   4. 檢查虛擬環境設定")
        
        print("\n🚀 下一步:")
        print("   python main.py  # 啟動 LivePilotAI")
        print("   python tests/integration_test.py  # 執行測試")

def main():
    """主函數"""
    installer = PackageInstaller()
    results = installer.run_installation()
    installer.generate_report(results)
    
    # 驗證 LivePilotAI 核心模組
    print("\n🔍 驗證 LivePilotAI 核心模組...")
    try:
        import main
        print("✅ main.py 可正常匯入")
    except Exception as e:
        print(f"❌ main.py 匯入失敗: {e}")
    
    try:
        from src.ai_engine.emotion_detector import EmotionDetector
        print("✅ AI 引擎模組正常")
    except Exception as e:
        print(f"❌ AI 引擎模組問題: {e}")

if __name__ == "__main__":
    main()
