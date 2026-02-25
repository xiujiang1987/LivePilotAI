# LivePilotAI v1.1.0 - AI智慧導播暨個人化直播助理平台

> **🎉 最新版本**: v1.1.0 包含多人臉追蹤、情感強度分析與獨立執行檔發布

## 📋 專案概述

LivePilotAI 是一個基於人工智能的智慧導播系統，能夠即時分析主播情緒並自動執行場景切換、特效觸發等導播操作，打造個人化的智慧直播助理平台。

## ⚡ 快速開始

### 方式一：使用獨立執行檔 (推薦一般用戶)

1. 前往 `dist/` 資料夾
2. 雙擊 `LivePilotAI.exe` 直接啟動

### 方式二：開發者模式

```powershell
# 🎯 主要啟動方式
uv run python main.py

# 🚀 進階功能示範 (v1.1.0)
uv run python demos/demo_advanced.py

# 🧪 系統驗證
uv run python tools/readiness_check.py
```

### 方式三：使用 Docker

```bash
docker build -t livepilotai .
# 注意：GUI 程式在 Docker 容器中執行需要額外的 X11 設置
```

## 🎯 核心功能

### ✨ v1.1.0 新增功能

- **多人臉穩定追蹤**: 解決 ID 跳變問題，支持長時追蹤
- **情感強度分析**: 計算情感的強度、穩定性和變化速率
- **進階視覺化**: 全新的即時標註引擎和狀態顯示
- **無需安裝部署**: 提供 Windows 獨立執行檔 (.exe)

### ✨ 既有功能

- **即時情緒檢測**: 7種基礎情緒分類
- **OBS Studio 智慧整合**: 自動場景切換與控制
- **專業級使用者介面**: 即時預覽與參數控制

## 🏗️ 技術架構

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

## 🗂️ 專案結構

```
LivePilotAI/
├── main.py                    🎯 主要應用程式入口
├── dist/                      📦 打包完成的執行檔 (.exe)
├── src/                       📦 核心源碼
│   ├── ai_engine/            🤖 AI 情緒檢測引擎
│   │   ├── emotion_detector.py  (Facade)
│   │   └── modules/          🔧 核心模組
│   │       ├── emotion_smoother.py
│   │       ├── annotation_renderer.py
│   │       ├── face_detector.py
│   │       ├── camera_manager.py
│   │       └── ai_director.py
│   ├── obs_integration/      🎬 OBS Studio 整合
│   ├── effects/              ✨ 特效控制系統
│   ├── ui/                   🖼️ 使用者介面
│   ├── core/                 ⚙️ 核心基礎設施
│   └── utils/                🛠️ 工具函數
├── tests/                    🧪 測試檔案
│   ├── unit/                    單元測試
│   ├── integration/             整合測試
│   └── performance/             效能基準
├── .context/                 📖 AI 開發知識庫
├── demos/                    🎮 示範檔案
├── tools/                    🛠️ 工具腳本
├── config/                   ⚙️ 配置文件
├── docs/                     📚 技術文檔
└── project_management/       📋 專案管理文檔
```

## 🏗️ 構建指南

若需自行打包專案為 .exe：

```powershell
uv pip install pyinstaller
uv run pyinstaller LivePilotAI.spec
```

## 📊 技術指標目標

| 指標 | 目標 |
|------|------|
| 情緒檢測準確率 | > 85% |
| 即時處理延遲 | < 100ms |
| 系統穩定運行 | > 4 小時 |
| 記憶體使用 | < 1GB |
| CPU 使用率 | < 60% |

## 📈 開發路線圖

### Phase 1: 核心功能 ✅

- [x] 專案架構設計
- [x] 情緒檢測引擎實作
- [x] 基礎 UI 開發
- [x] OBS WebSocket 整合

### Phase 2: 進階功能 ✅

- [x] 多人臉穩定追蹤
- [x] 情感強度分析
- [x] 進階視覺化引擎
- [x] 獨立執行檔打包

### Phase 3: 架構優化 🔄

- [x] God Class 拆分 (EmotionDetector → 模組化)
- [x] 測試目錄整理
- [ ] API 端點開發
- [ ] 前端介面整合

### Phase 4: 部署準備

- [ ] 效能調校
- [ ] 使用者手冊完善
- [ ] 商業化準備

## 🛠️ 開發環境

| 工具 | 版本 |
|------|------|
| Python | 3.9+ |
| OBS Studio | 28+ |
| OS | Windows 10/11 |
| 包管理 | uv / pip |
| 測試框架 | pytest |
| CI/CD | GitHub Actions |

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 創建 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

---

**🎯 讓我們一起用AI技術改變直播體驗！** 🚀✨
