"""
LivePilotAI 情感檢測引擎快速啟動腳本
用於測試依賴檢查和引擎初始化功能
"""

import asyncio
import sys
import os

# 將項目根目錄添加到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_engine.emotion_detector_engine import (
    EmotionDetectorEngine, 
    create_emotion_detector_engine,
    test_emotion_detector,
    DependencyManager,
    startup_dependency_check
)


async def main():
    """主函數 - 演示完整的啟動流程"""
    print("🚀 LivePilotAI 情感檢測引擎啟動測試")
    print("="*60)
    
    try:
        # 1. 手動執行依賴檢查
        print("\n📋 步驟 1: 執行依賴檢查...")
        startup_dependency_check(auto_install=True)
        
        # 2. 創建引擎實例
        print("\n⚙️ 步驟 2: 創建引擎實例...")
        config = {
            "dependency_check": {
                "auto_install": True,
                "verify_on_init": True
            },
            "performance": {
                "max_faces": 3,
                "target_fps": 24
            }
        }
        
        engine = create_emotion_detector_engine(config=config)
        print(f"✓ 引擎創建成功: {engine.engine_id}")
        
        # 3. 初始化引擎
        print("\n🔧 步驟 3: 初始化引擎...")
        if await engine.initialize():
            print("✓ 引擎初始化成功")
            
            # 4. 顯示引擎狀態
            print("\n📊 步驟 4: 引擎狀態...")
            status = engine.get_engine_status()
            print(f"  - 引擎ID: {status['engine_id']}")
            print(f"  - 狀態: {status['state']}")
            print(f"  - 依賴驗證: {status['dependencies_verified']}")
            print(f"  - 模型已載入: {status['model_loaded']}")
            print(f"  - 人臉檢測器就緒: {status['face_detector_ready']}")
            
            # 5. 執行完整測試
            print("\n🧪 步驟 5: 執行完整測試...")
            await test_emotion_detector()
            
            # 6. 清理資源
            print("\n🧹 步驟 6: 清理資源...")
            await engine.cleanup()
            
        else:
            print("❌ 引擎初始化失敗")
            return False
        
        print("\n🎉 所有測試完成！情感檢測引擎已準備就緒。")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_system_readiness():
    """檢查系統就緒性"""
    print("\n🔍 系統就緒性檢查...")
    
    # 檢查 Python 版本
    python_version = sys.version_info
    print(f"  - Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("  ⚠️ 建議使用 Python 3.7 或更新版本")
    else:
        print("  ✓ Python 版本符合要求")
    
    # 檢查已安裝的依賴
    print("\n  依賴檢查:")
    installed, missing = DependencyManager.check_dependencies()
    
    for package in installed:
        print(f"    ✓ {package}")
    
    for package in missing:
        print(f"    ❌ {package} (將自動安裝)")
    
    return len(missing) == 0


if __name__ == "__main__":
    print("LivePilotAI 情感檢測引擎 - 啟動測試工具")
    print("="*60)
    
    # 檢查系統就緒性
    system_ready = check_system_readiness()
    
    if not system_ready:
        print("\n⚠️ 系統未完全就緒，但將嘗試自動安裝依賴...")
    
    # 執行主測試流程
    result = asyncio.run(main())
    
    if result:
        print("\n✅ 啟動測試成功！情感檢測引擎可以正常使用。")
        sys.exit(0)
    else:
        print("\n❌ 啟動測試失敗，請檢查錯誤訊息。")
        sys.exit(1)
