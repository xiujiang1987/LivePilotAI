#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 系統診斷工具
檢查各種潛在問題並提供修復建議
"""

import sys
import os
import importlib
import logging
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version < (3, 9):
        print("⚠️  警告: 建議使用 Python 3.9 或更高版本")
        return False
    print("✅ Python 版本兼容")
    return True

def check_dependencies():
    """檢查重要依賴"""
    deps = {
        'tkinter': '圖形界面',
        'cv2': 'OpenCV 圖像處理',
        'numpy': '數值計算',
        'tensorflow': '機器學習',
        'websockets': 'WebSocket 通信',
        'psutil': '系統監控'
    }
    
    print("\n📦 檢查依賴套件:")
    missing = []
    for dep, desc in deps.items():
        try:
            mod = importlib.import_module(dep)
            version = getattr(mod, '__version__', '未知版本')
            print(f"✅ {dep} ({desc}): {version}")
        except ImportError:
            print(f"❌ {dep} ({desc}): 未安裝")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  缺少依賴: {', '.join(missing)}")
        print("💡 請運行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有必要依賴已安裝")
    return True

def check_file_structure():
    """檢查檔案結構"""
    print("\n📁 檢查檔案結構:")
    
    required_files = [
        'src/__init__.py',
        'src/ui/__init__.py',
        'src/ai_engine/__init__.py',
        'src/obs_integration/__init__.py',
        'src/core/__init__.py',
        'main.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少檔案: {', '.join(missing_files)}")
        return False
    
    print("✅ 檔案結構完整")
    return True

def check_imports():
    """檢查主要模組匯入"""
    print("\n🔗 檢查模組匯入:")
    
    # 添加 src 到路徑
    sys.path.insert(0, '.')
    sys.path.insert(0, 'src')
    
    modules = [
        ('src.ui', 'UI 模組'),
        ('src.ai_engine.emotion_detector', '情感檢測'),
        ('src.obs_integration.obs_manager', 'OBS 整合'),
        ('src.core.config_manager', '配置管理')
    ]
    
    failed_imports = []
    for module_name, desc in modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} ({desc})")
        except Exception as e:
            print(f"❌ {module_name} ({desc}): {str(e)}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n⚠️  匯入失敗: {', '.join(failed_imports)}")
        return False
    
    print("✅ 所有模組匯入成功")
    return True

def check_websockets_compatibility():
    """檢查 WebSocket 版本兼容性"""
    print("\n🔌 檢查 WebSocket 兼容性:")
    
    try:
        import websockets
        version = websockets.__version__
        major_version = int(version.split('.')[0])
        
        print(f"📡 WebSockets 版本: {version}")
        
        if major_version >= 12:
            print("⚠️  使用新版 WebSockets (>= 12.0)，可能存在兼容性問題")
            print("💡 建議: pip install 'websockets>=11.0.0,<12.0.0'")
            return False
        else:
            print("✅ WebSockets 版本兼容")
            return True
            
    except ImportError:
        print("❌ WebSockets 未安裝")
        return False

def check_camera_access():
    """檢查攝像頭訪問"""
    print("\n📹 檢查攝像頭訪問:")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✅ 攝像頭可用")
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"📐 攝像頭解析度: {w}x{h}")
            cap.release()
            return True
        else:
            print("❌ 無法訪問攝像頭")
            return False
            
    except Exception as e:
        print(f"❌ 攝像頭檢查失敗: {e}")
        return False

def generate_fix_suggestions(failed_checks):
    """生成修復建議"""
    print("\n🛠️  修復建議:")
    
    suggestions = {
        'python_version': '升級到 Python 3.9+',
        'dependencies': '運行: pip install -r requirements.txt',
        'file_structure': '檢查檔案完整性，重新下載專案',
        'imports': '檢查模組結構，修復匯入錯誤',
        'websockets': '降級 WebSockets: pip install "websockets>=11.0.0,<12.0.0"',
        'camera': '確保攝像頭已連接且沒有被其他應用使用'
    }
    
    for check in failed_checks:
        if check in suggestions:
            print(f"• {suggestions[check]}")

def main():
    """主診斷函數"""
    print("🔍 LivePilotAI 系統診斷工具")
    print("=" * 50)
    
    checks = {
        'python_version': check_python_version,
        'dependencies': check_dependencies,
        'file_structure': check_file_structure,
        'imports': check_imports,
        'websockets': check_websockets_compatibility,
        'camera': check_camera_access
    }
    
    failed_checks = []
    for check_name, check_func in checks.items():
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} 檢查失敗: {e}")
            failed_checks.append(check_name)
    
    print("\n" + "=" * 50)
    
    if not failed_checks:
        print("🎉 所有檢查通過！系統狀態良好")
        print("💡 提示: 可以嘗試運行 python main.py")
    else:
        print(f"⚠️  發現 {len(failed_checks)} 個問題")
        generate_fix_suggestions(failed_checks)
    
    print("\n📊 診斷完成")

if __name__ == "__main__":
    main()
