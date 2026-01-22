# LivePilotAI 專案結構說明

## 📁 根目錄結構
```
LivePilotAI/
├── main.py                   # 🚀 主要程式入口點
├── requirements.txt          # 📦 Python依賴套件列表
├── pyproject.toml           # ⚙️ Python專案配置文件
├── README.md                # 📖 專案說明文件
├── .env                     # 🔒 環境變數配置
├── .gitignore              # 🚫 Git忽略文件配置
├── src/                    # 💻 核心源代碼
├── config/                 # ⚙️ 配置文件目錄
├── tests/                  # 🧪 測試代碼目錄
├── docs/                   # 📚 專案文檔
├── scripts/                # 🔧 工具腳本
├── tools/                  # 🛠️ 開發工具
├── assets/                 # 🎨 靜態資源
├── demos/                  # 🎬 示例演示
├── logs/                   # 📝 日誌文件
└── project_management/     # 📋 專案管理文件
```

## 🎯 核心入口
- **main.py**: 應用程式的主要啟動點，包含所有核心邏輯整合

## 📦 依賴管理
- **requirements.txt**: 生產環境依賴套件
- **pyproject.toml**: 專案元數據和配置

## 🏗️ 模組化架構
- **src/**: 所有核心業務邏輯
  - `ai_engine/`: AI情感識別引擎
  - `obs_integration/`: OBS整合模組
  - `ui/`: 用戶介面組件
  - `utils/`: 通用工具函數

## 🧪 測試體系
- **tests/**: 完整的測試套件
  - `unit/`: 單元測試
  - `integration/`: 整合測試
  - `performance/`: 性能測試

## 📚 文檔與管理
- **docs/**: 技術文檔和使用指南
- **project_management/archives/**: 開發歷史存檔

## 🛠️ 開發工具
- **scripts/**: 開發和部署腳本
- **tools/**: 輔助開發工具

---
*專案已完成模組化重構，結構清晰，便於維護和擴展*
