# LivePilotAI - 情感檢測引擎依賴項安裝指南

## 需要安裝的Python套件

為了讓情感檢測引擎正常運作，您需要安裝以下套件：

```bash
# 安裝基本套件
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install tensorflow==2.13.0

# 或者安裝 TensorFlow GPU 版本（如果有支援的GPU）
# pip install tensorflow-gpu==2.13.0
```

## 或者使用 requirements.txt

將以下內容保存到 `requirements.txt` 檔案中：

```
opencv-python==4.8.1.78
numpy==1.24.3
tensorflow==2.13.0
asyncio
typing
dataclasses
logging
```

然後執行：
```bash
pip install -r requirements.txt
```

## 驗證安裝

安裝完成後，可以執行以下Python代碼來驗證：

```python
import cv2
import numpy as np
import tensorflow as tf

print(f"OpenCV版本: {cv2.__version__}")
print(f"NumPy版本: {np.__version__}")
print(f"TensorFlow版本: {tf.__version__}")
print("所有依賴項已成功安裝！")
```

## 注意事項

1. **OpenCV**: 用於影像處理和人臉檢測
2. **NumPy**: 用於數值運算和陣列操作
3. **TensorFlow**: 用於深度學習模型和情感識別
4. **其他套件**: asyncio, typing, dataclasses, logging 是Python標準庫的一部分，通常不需要額外安裝

如果遇到安裝問題，請確保您的Python版本在3.8-3.11之間。
