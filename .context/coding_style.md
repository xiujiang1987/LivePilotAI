# LivePilotAI - 編碼風格指南

## 語言與框架

- **Python 3.9+**，所有程式碼必須使用 **Type Hints**
- GUI：Tkinter + ttk
- AI Engine：TensorFlow / TFLite + MediaPipe
- 串流整合：OBS WebSocket Protocol

## 命名規範

| 類型 | 規範 | 範例 |
|------|------|------|
| 類別 | PascalCase | `EmotionDetector`, `OBSManager` |
| 函式 / 方法 | snake_case | `detect_faces()`, `smooth_emotion()` |
| 常數 | UPPER_SNAKE_CASE | `DEFAULT_COLOR`, `MAX_FACES` |
| 私有方法 | 前綴底線 | `_load_model_sync()` |
| 模組檔案 | snake_case | `emotion_smoother.py` |

## Docstring 格式

使用 **Google Style Docstrings**：

```python
def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    檢測畫面中的人臉

    Args:
        frame: 輸入影像 (BGR 格式)

    Returns:
        人臉邊界框列表 [(x, y, w, h), ...]
    """
```

## 程式碼組織

- 每個類別應遵守 **SRP（單一職責原則）**
- 邏輯拆分為獨立模組，放在對應的子目錄下
- 向後相容的 API 變更使用 facade pattern 委託

## 錯誤處理

- 所有外部調用（模型載入、WebSocket、攝影機）必須使用 try/except
- 錯誤記錄使用 `logging` 模組，禁止直接 `print()` 到 stdout
- 所有 fallback 路徑必須有明確的 logger.warning 記錄

## 測試慣例

- 測試目錄結構：`tests/unit/`、`tests/integration/`、`tests/performance/`
- 使用 `pytest` 作為測試執行器
- 測試檔案命名：`test_<module_name>.py`
