#!/usr/bin/env python3
"""
快速套件驗證測試
檢查關鍵套件是否可以正常匯入
"""

import sys
import importlib

def test_import(package_name, import_name=None):
    """測試套件匯入"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        print(f"✅ {package_name}: 匯入成功")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: 匯入失敗 - {e}")
        return False

def main():
    print("🔍 LivePilotAI 套件驗證測試")
    print("=" * 50)
    
    # 核心套件測試
    packages = [
        ('tensorflow', 'tensorflow'),
        ('opencv-python', 'cv2'),
        ('mediapipe', 'mediapipe'),
        ('psutil', 'psutil'),
        ('websocket-client', 'websocket'),
        ('numpy', 'numpy'),
        ('pillow', 'PIL'),
        ('tkinter', 'tkinter'),
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package_name, import_name in packages:
        if test_import(package_name, import_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 結果: {success_count}/{total_count} 套件可用")
    
    if success_count == total_count:
        print("🎉 所有套件都正常！")
        
        # 測試 tensorflow.keras
        try:
            import tensorflow as tf
            model = tf.keras.Sequential()
            print("✅ tensorflow.keras: 正常運作")
        except Exception as e:
            print(f"❌ tensorflow.keras: 問題 - {e}")
            
        # 測試 cv2.data
        try:
            import cv2
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            print("✅ cv2.data: 正常運作")
        except Exception as e:
            print(f"❌ cv2.data: 問題 - {e}")
    
    else:
        print("⚠️  部分套件缺失，需要安裝")
        
    # 測試 LivePilotAI 核心模組
    print("\n🔍 測試 LivePilotAI 核心模組...")
    try:
        sys.path.insert(0, 'src')
        from ai_engine.emotion_detector import EmotionDetector
        print("✅ EmotionDetector: 可以匯入")
    except Exception as e:
        print(f"❌ EmotionDetector: 匯入失敗 - {e}")

if __name__ == "__main__":
    main()
