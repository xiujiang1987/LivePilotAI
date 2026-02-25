# LivePilotAI - 架構概覽

## 定位

AI 智慧導播暨個人化直播助理平台。即時分析主播情緒並自動執行場景切換、特效觸發。

## 分層架構

```
┌──────────────────────────────────────────────────────┐
│  UI Layer (src/ui/)                                  │
│  ├── MainPanel       ├── PreviewWindow               │
│  ├── SettingsDialog  └── StatusIndicators             │
├──────────────────────────────────────────────────────┤
│  OBS Integration (src/obs_integration/)               │
│  ├── OBSWebSocketManager  ├── SceneController         │
│  ├── EmotionMapper        └── WebSocketClient         │
├──────────────────────────────────────────────────────┤
│  AI Engine (src/ai_engine/)                           │
│  ├── EmotionDetector (facade)                         │
│  │   ├── modules/emotion_smoother.py                  │
│  │   ├── modules/annotation_renderer.py               │
│  │   ├── modules/face_detector.py                     │
│  │   ├── modules/camera_manager.py                    │
│  │   ├── modules/real_time_detector.py                │
│  │   └── modules/ai_director.py                       │
├──────────────────────────────────────────────────────┤
│  Effects (src/effects/)                               │
│  └── effect_controller.py                             │
├──────────────────────────────────────────────────────┤
│  Core (src/core/)                                     │
│  ├── ConfigManager   ├── Logging                      │
│  └── Performance     └── Error Handling               │
└──────────────────────────────────────────────────────┘
```

## 關鍵設計決策

### 1. Facade Pattern (emotion_detector.py)

`EmotionDetector` 作為 AI Engine 的公開 API 門面，內部委託給：

- `EmotionSmoother` — 滑動窗口平滑
- `AnnotationRenderer` — 影像標註繪製
保持所有外部 import 不變。

### 2. Model Loading Strategy

優先順序：TFLite Runtime → TensorFlow Lite → Keras H5 → Dummy Model
每個 fallback 層級都有獨立的 logger 記錄。

### 3. Face Detection Fallback

優先使用 MediaPipe，失敗時自動切換至 Haar Cascade。

## 依賴關係

- **必要**：cv2, numpy, mediapipe
- **可選**：tensorflow / tflite_runtime (無則使用 Dummy Model)
- **可選**：websockets (OBS 整合)

## 測試結構

```
tests/
├── conftest.py          # 共用 fixtures
├── unit/                # 單元測試 (12 files)
├── integration/         # 整合測試 (4 files)
├── performance/         # 效能基準 (1 file)
└── _archived/           # 過時/實驗性測試 (21 files)
```
