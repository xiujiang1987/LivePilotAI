import sys
import os
from pathlib import Path

# 設置路徑
project_root = Path.cwd()
sys.path.insert(0, str(project_root / 'src'))

print('🎬 LivePilotAI 實例測試開始')
print('=' * 50)

# 測試 1: 基本庫
try:
    import cv2
    import numpy as np
    print(f'✅ OpenCV: {cv2.__version__}')
    print(f'✅ NumPy: {np.__version__}')
except Exception as e:
    print(f'❌ 基本庫失敗: {e}')
    sys.exit(1)

# 測試 2: 專案模組
try:
    from ai_engine.modules.camera_manager import CameraManager, CameraConfig
    from ai_engine.modules.face_detector import FaceDetector, DetectionConfig
    from ai_engine.emotion_detector import EmotionDetector
    print('✅ 所有專案模組導入成功')
except Exception as e:
    print(f'❌ 專案模組失敗: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 測試 3: 實例化
try:
    config = CameraConfig(device_id=0, width=640, height=480, fps=30)
    camera = CameraManager(config)
    
    detection_config = DetectionConfig(detection_method='haar', min_face_size=(30, 30))
    face_detector = FaceDetector(detection_config)
    
    emotion_detector = EmotionDetector()
    
    print('✅ 所有模組實例化成功')
except Exception as e:
    print(f'❌ 實例化失敗: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 測試 4: 攝像頭
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f'✅ 攝像頭工作正常，幀大小: {frame.shape}')
            camera_ready = True
        else:
            print('⚠️ 攝像頭無法讀取幀')
            camera_ready = False
        cap.release()
    else:
        print('⚠️ 攝像頭不可用')
        camera_ready = False
except Exception as e:
    print(f'⚠️ 攝像頭測試失敗: {e}')
    camera_ready = False

print('\n🎉 基礎測試完成！')
print('📋 測試結果:')
print('  • 基本庫: ✅ 正常')
print('  • 專案模組: ✅ 正常')
print('  • 模組實例化: ✅ 正常')
print(f'  • 攝像頭: {"✅ 就緒" if camera_ready else "⚠️ 不可用"}')

if camera_ready:
    print('\n🚀 系統完全就緒，可以開始即時檢測測試！')
    user_input = input('\n💡 是否啟動即時檢測演示？(y/n): ').lower().strip()
    if user_input in ['y', 'yes']:
        print('🎬 正在啟動即時檢測...')
        print('💡 請確保您的臉部在攝像頭視野內')
        print('⌨️ 操作提示: 按 q 鍵退出，按 s 鍵截圖')
        
        # 啟動即時檢測
        try:
            from ai_engine.modules.real_time_detector import RealTimeEmotionDetector, RealTimeConfig
            
            rt_config = RealTimeConfig(
                camera_device_id=0,
                camera_width=640,
                camera_height=480,
                target_fps=30,
                detection_method='haar',
                show_fps=True,
                show_confidence=True
            )
            
            detector = RealTimeEmotionDetector(rt_config)
            print('✅ 即時檢測器初始化成功')
            
            # 3秒倒數
            import time
            for i in range(3, 0, -1):
                print(f'⏰ {i}秒後開始...')
                time.sleep(1)
            
            detector.start_detection()
            detector.wait_for_completion()
            
        except KeyboardInterrupt:
            print('\n⏹️ 用戶中斷檢測')
        except Exception as e:
            print(f'\n❌ 即時檢測失敗: {e}')
            import traceback
            traceback.print_exc()
        finally:
            try:
                detector.stop_detection()
            except:
                pass
            print('🛑 檢測已停止')
    else:
        print('📊 測試完成，系統已就緒')
else:
    print('\n📊 基礎功能測試完成')
    print('💡 攝像頭不可用，但核心功能已驗證正常')

print('\n🎊 LivePilotAI 實例測試完成！')
