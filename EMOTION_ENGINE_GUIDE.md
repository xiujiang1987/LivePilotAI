# LivePilotAI 情感檢測引擎 - 增強版使用指南

## 概述

這個增強版的情感檢測引擎具備以下關鍵特性：

- ✅ **啟動時自動依賴檢查**
- ✅ **自動依賴安裝**
- ✅ **增強的錯誤處理**
- ✅ **效能監控與優化**
- ✅ **完整的日誌記錄**

## 核心功能

### 1. 啟動時依賴檢查

引擎在啟動時會自動檢查所有必需的依賴包：

```python
# 必需的依賴包
REQUIRED_PACKAGES = {
    'cv2': 'opencv-python',
    'numpy': 'numpy', 
    'tensorflow': 'tensorflow',
    'PIL': 'Pillow'
}
```

### 2. 自動依賴安裝

如果發現缺失的依賴，引擎會嘗試自動安裝：

```python
# 啟動時執行依賴檢查
startup_dependency_check(auto_install=True)
```

### 3. 增強的初始化流程

引擎初始化過程包含多重驗證：

1. 依賴檢查
2. 模型載入
3. 人臉檢測器初始化
4. 運行時驗證

## 快速開始

### 方法一：使用測試腳本

```bash
# 執行完整的啟動測試
cd /path/to/LivePilotAI
python test_emotion_engine.py
```

### 方法二：程式碼整合

```python
import asyncio
from src.ai_engine.emotion_detector_engine import create_emotion_detector_engine

async def main():
    # 創建引擎實例
    engine = create_emotion_detector_engine()
    
    # 初始化引擎（會自動檢查依賴）
    if await engine.initialize():
        print("引擎已就緒！")
        
        # 處理影像
        import numpy as np
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = await engine.process(test_image)
        
        if result.success:
            print("處理成功！")
            print(f"檢測到 {len(result.data['emotions'])} 張人臉")
        
        # 清理資源
        await engine.cleanup()
    else:
        print("引擎初始化失敗")

# 執行
asyncio.run(main())
```

## 配置選項

### 依賴檢查配置

```python
config = {
    "dependency_check": {
        "auto_install": True,      # 是否自動安裝缺失依賴
        "verify_on_init": True     # 初始化時是否重新驗證依賴
    }
}
```

### 效能配置

```python
config = {
    "performance": {
        "max_faces": 5,           # 最多處理的人臉數量
        "target_fps": 30          # 目標 FPS
    }
}
```

### 平滑處理配置

```python
config = {
    "smoothing": {
        "enabled": True,          # 是否啟用平滑處理
        "history_size": 5,        # 歷史記錄大小
        "threshold": 0.6          # 置信度閾值
    }
}
```

## 錯誤處理

### 依賴檢查失敗

如果依賴檢查失敗，引擎會提供詳細的錯誤訊息：

```python
try:
    startup_dependency_check(auto_install=True)
except DependencyCheckError as e:
    print(f"依賴檢查錯誤: {e}")
    print("請手動安裝依賴:")
    print("pip install opencv-python numpy tensorflow Pillow")
```

### 引擎初始化失敗

```python
engine = create_emotion_detector_engine()
if not await engine.initialize():
    status = engine.get_engine_status()
    print(f"初始化失敗，引擎狀態: {status['state']}")
```

## 狀態監控

### 獲取引擎狀態

```python
status = engine.get_engine_status()
print(f"引擎ID: {status['engine_id']}")
print(f"狀態: {status['state']}")
print(f"依賴驗證: {status['dependencies_verified']}")
print(f"模型已載入: {status['model_loaded']}")
print(f"人臉檢測器就緒: {status['face_detector_ready']}")
print(f"平均處理時間: {status['performance']['avg_processing_time']:.3f}秒")
print(f"預估FPS: {status['performance']['estimated_fps']:.1f}")
```

### 處理結果監控

```python
result = await engine.process(image)
if result.success:
    # 檢查系統狀態
    system_status = result.data['system_status']
    print(f"依賴驗證: {system_status['dependencies_verified']}")
    print(f"模型狀態: {system_status['model_loaded']}")
    
    # 檢查效能指標
    performance = result.data['performance']
    print(f"處理時間: {performance['processing_time']:.3f}秒")
    print(f"當前FPS: {performance['fps']:.1f}")
```

## 故障排除

### 問題 1: 依賴安裝失敗

**症狀**: 自動依賴安裝失敗

**解決方案**:
```bash
# 手動安裝依賴
pip install --upgrade pip
pip install opencv-python numpy tensorflow Pillow

# 如果仍有問題，嘗試使用 conda
conda install opencv numpy tensorflow pillow
```

### 問題 2: TensorFlow 載入錯誤

**症狀**: TensorFlow 模型載入失敗

**解決方案**:
```python
# 檢查 TensorFlow 版本
import tensorflow as tf
print(f"TensorFlow 版本: {tf.__version__}")

# 如果版本過舊，升級
pip install --upgrade tensorflow
```

### 問題 3: OpenCV 人臉檢測器失敗

**症狀**: 人臉檢測器初始化失敗

**解決方案**:
```python
# 檢查 OpenCV 資料路徑
import cv2
print(f"OpenCV 資料路徑: {cv2.data.haarcascades}")

# 如果路徑不存在，重新安裝 OpenCV
pip uninstall opencv-python
pip install opencv-python
```

## 進階使用

### 自定義依賴檢查

```python
from src.ai_engine.emotion_detector_engine import DependencyManager

# 添加自定義依賴
DependencyManager.REQUIRED_PACKAGES['matplotlib'] = 'matplotlib'

# 手動檢查依賴
installed, missing = DependencyManager.check_dependencies()
print(f"已安裝: {installed}")
print(f"缺失: {missing}")
```

### 批次處理模式

```python
async def batch_process_images(engine, image_list):
    results = []
    for image in image_list:
        result = await engine.process(image)
        if result.success:
            results.append(result.data)
        else:
            print(f"處理失敗: {result.error_message}")
    return results
```

### 即時攝影機整合

```python
import cv2

async def live_emotion_detection():
    engine = create_emotion_detector_engine()
    await engine.initialize()
    
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 處理當前畫面
            result = await engine.process(frame)
            
            if result.success:
                # 繪製情感檢測結果
                from src.ai_engine.emotion_detector_engine import draw_emotion_results
                annotated_frame = draw_emotion_results(frame, result.data['emotions'])
                cv2.imshow('Live Emotion Detection', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        await engine.cleanup()
```

## 效能優化建議

1. **調整處理參數**:
   - 減少 `max_faces` 以提高速度
   - 降低輸入影像解析度
   - 調整人臉檢測參數

2. **使用 GPU 加速**:
   ```bash
   # 安裝 GPU 版本的 TensorFlow
   pip install tensorflow-gpu
   ```

3. **批次處理**:
   - 累積多個畫面後一次處理
   - 使用非同步處理管道

## 整合到現有系統

### Django/Flask 整合

```python
from flask import Flask, request, jsonify
import asyncio
import base64
import cv2
import numpy as np

app = Flask(__name__)
emotion_engine = None

@app.before_first_request
def init_engine():
    global emotion_engine
    emotion_engine = create_emotion_detector_engine()
    asyncio.run(emotion_engine.initialize())

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    # 接收 base64 編碼的影像
    image_data = request.json['image']
    image_bytes = base64.b64decode(image_data)
    
    # 轉換為 OpenCV 格式
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 處理影像
    result = asyncio.run(emotion_engine.process(image))
    
    return jsonify({
        'success': result.success,
        'emotions': result.data.get('emotions', []),
        'processing_time': result.processing_time
    })
```

這個增強版的情感檢測引擎現在提供了完整的依賴管理和錯誤處理功能，確保在各種環境下都能穩定運行。
