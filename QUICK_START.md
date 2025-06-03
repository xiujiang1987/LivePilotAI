# LivePilotAI 情感檢測引擎 - 快速啟動參考

## 🚀 一鍵啟動

### Windows PowerShell
```powershell
# 執行完整測試
.\test_engine_startup.ps1

# 或分別測試
python test_dependency_system.py    # 依賴檢查測試
python test_emotion_engine.py       # 引擎啟動測試
python simple_test.py               # 簡單狀態檢查
```

## 📦 手動安裝依賴（如果自動安裝失敗）

```bash
pip install opencv-python numpy tensorflow Pillow
```

## 💻 程式碼使用

### 基本使用
```python
from src.ai_engine.emotion_detector_engine import create_emotion_detector_engine
import asyncio

async def main():
    # 創建引擎（自動處理依賴）
    engine = create_emotion_detector_engine()
    
    # 初始化（包含依賴驗證）
    if await engine.initialize():
        print("✅ 引擎就緒！")
        
        # 處理影像
        import numpy as np
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = await engine.process(test_image)
        
        if result.success:
            print(f"檢測到 {len(result.data['emotions'])} 張人臉")
        
        # 清理
        await engine.cleanup()
    else:
        print("❌ 引擎初始化失敗")

asyncio.run(main())
```

### 檢查引擎狀態
```python
status = engine.get_engine_status()
print(f"依賴驗證: {status['dependencies_verified']}")
print(f"模型已載入: {status['model_loaded']}")
```

## 🔧 故障排除

### 問題：依賴安裝失敗
**解決方案**：
1. 升級 pip: `python -m pip install --upgrade pip`
2. 手動安裝: `pip install opencv-python numpy tensorflow Pillow`
3. 使用 conda: `conda install opencv numpy tensorflow pillow`

### 問題：TensorFlow 載入錯誤
**解決方案**：
1. 檢查版本: `pip show tensorflow`
2. 重新安裝: `pip uninstall tensorflow && pip install tensorflow`

### 問題：OpenCV 人臉檢測器失敗
**解決方案**：
1. 重新安裝 OpenCV: `pip uninstall opencv-python && pip install opencv-python`

## 📁 重要文件

- `emotion_detector_engine.py` - 主引擎文件
- `test_dependency_system.py` - 依賴檢查測試
- `EMOTION_ENGINE_GUIDE.md` - 完整使用指南
- `DEPENDENCY_CHECK_COMPLETION_REPORT.md` - 功能完成報告

## ✅ 功能確認

- [x] 啟動時自動依賴檢查
- [x] 自動依賴安裝
- [x] 運行時依賴驗證
- [x] 增強錯誤處理
- [x] 完整測試工具
- [x] 詳細文檔說明
