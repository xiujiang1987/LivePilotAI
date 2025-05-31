# LivePilotAI - AI智慧直播特效系統

## 📋 專案概述

LivePilotAI 是一個基於人工智能的即時情緒檢測與直播特效系統，能夠即時分析主播情緒並自動觸發相應的視覺特效，提升直播互動體驗。

## 🎯 核心功能

- **即時情緒檢測**: 使用深度學習模型分析人臉情緒（7種情緒分類）
- **動態視覺特效**: 基於情緒狀態自動觸發對應特效
- **OBS直播整合**: 無縫整合OBS Studio，支援即時直播
- **多人檢測**: 同時檢測多個人臉的情緒狀態
- **自訂配置**: 支援特效強度、觸發條件等個人化設定

## 🏗️ 技術架構

```
Frontend (React) ←→ Backend API (FastAPI) ←→ AI Engine (TensorFlow)
                                    ↕
                              OBS Integration
```

## 📁 專案結構

```
LivePilotAI/
├── src/                    # 源代碼
│   ├── ai_engine/         # AI核心引擎
│   ├── api/               # 後端API
│   ├── frontend/          # 前端介面
│   ├── obs_integration/   # OBS整合
│   ├── effects/           # 特效系統
│   └── utils/             # 工具函數
├── tests/                 # 測試代碼
├── docs/                  # 技術文檔
├── config/                # 配置文件
├── assets/                # 資源文件
├── scripts/               # 建置與部署腳本
└── project_management/    # 專案管理文檔
```

## 🚀 快速開始

### 環境需求
- Python 3.9+
- Node.js 18+
- OBS Studio 28+
- 支援的作業系統: Windows 10/11

### 安裝步驟

1. **克隆專案**
```bash
git clone <repository-url>
cd LivePilotAI
```

2. **建立Python虛擬環境**
```bash
python -m venv envs/dev
envs/dev/Scripts/activate  # Windows
pip install -r requirements.txt
```

3. **安裝前端依賴**
```bash
cd src/frontend
npm install
```

4. **運行開發環境**
```bash
# 啟動後端API
python src/api/main.py

# 啟動前端開發伺服器
cd src/frontend && npm start
```

## 📈 開發路線圖

### Phase 1: 核心功能 (Week 1-2)
- [x] 專案架構設計
- [ ] 情緒檢測引擎實作
- [ ] 基礎API開發
- [ ] 前端原型開發

### Phase 2: 特效系統 (Week 3-4)
- [ ] 即時特效渲染
- [ ] 情緒觸發邏輯
- [ ] 特效參數調整
- [ ] 效能優化

### Phase 3: 整合測試 (Week 5-6)
- [ ] OBS插件開發
- [ ] 系統整合測試
- [ ] 使用者體驗優化
- [ ] 文檔完善

### Phase 4: 部署準備 (Week 7-8)
- [ ] 打包與部署
- [ ] 效能調校
- [ ] 使用者手冊
- [ ] 商業化準備

## 🛠️ 開發工具

- **IDE**: VS Code
- **版本控制**: Git
- **包管理**: pip (Python), npm (Node.js)
- **測試框架**: pytest, Jest
- **CI/CD**: GitHub Actions
- **文檔**: Markdown, Sphinx

## 📊 技術指標目標

- 情緒檢測準確率: > 85%
- 即時處理延遲: < 100ms
- 系統穩定運行: > 4小時
- 記憶體使用: < 1GB
- CPU使用率: < 60%

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 創建 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 📞 聯絡方式

- 專案負責人: [Your Name]
- Email: [your.email@example.com]
- 專案主頁: [Project URL]

## 🙏 致謝

感謝所有為此專案做出貢獻的開發者和使用者！

---

**🎯 讓我們一起用AI技術改變直播體驗！** 🚀✨
