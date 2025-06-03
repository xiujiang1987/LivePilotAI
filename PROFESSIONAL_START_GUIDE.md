# LivePilotAI - 專業啟動指南
*語義化重構後的新架構*

## 🚀 快速啟動

### 主程式啟動
```bash
# 新的語義化啟動方式
python main.py

# 支援的模式
python main.py --mode=test
python main.py --mode=demo
python main.py --help
```

### 📁 新的專案結構

```
LivePilotAI/
├── main.py                           # 🎯 主程式（新）
├── main_day5.py                      # 📦 舊版本（保留相容性）
├── launcher.py                       # 🖥️ 圖形化啟動器
├── 
├── src/                              # 💻 核心源碼
│   ├── ai_engine/                    # 🤖 AI引擎
│   ├── ui/                           # 🎨 使用者介面
│   └── obs_integration/              # 📹 OBS整合
├── 
├── tests/                            # ✅ 測試檔案（新目錄）
│   ├── integration_test.py           # 📊 整合測試
│   ├── validation_test.py            # ✔️ 驗證測試
│   ├── performance_benchmark.py      # ⚡ 效能測試
│   └── system_integration_test.py    # 🔗 系統測試
├── 
├── demos/                            # 🎪 演示檔案（新目錄）
│   ├── demo_basic.py                 # 🎬 基礎演示
│   └── demo_features.py              # ⭐ 功能演示
├── 
├── tools/                            # 🔧 工具腳本（新目錄）
│   ├── readiness_check.py            # 📋 準備度檢查
│   ├── debug_launcher.py             # 🐛 調試啟動器
│   └── comprehensive_diagnostic.py   # 🔍 綜合診斷
└── 
└── docs/                             # 📚 文檔
    ├── QUICK_START.md
    └── REFACTORING_PLAN.md
```

## 🎯 運行不同模式

### 1. 標準模式
```bash
python main.py
```
啟動完整的 LivePilotAI 應用程式

### 2. 測試模式  
```bash
python main.py --mode=test
```
以測試配置啟動，適合開發調試

### 3. 演示模式
```bash
python main.py --mode=demo  
```
演示模式，適合產品展示

## 🧪 執行測試

### 整合測試
```bash
python tests/integration_test.py
```

### 系統驗證
```bash
python tests/validation_test.py
```

### 效能測試
```bash
python tests/performance_benchmark.py
```

### 系統整合測試
```bash
python tests/system_integration_test.py
```

## 🎪 運行演示

### 基礎功能演示
```bash
python demos/demo_basic.py
```

### 進階功能演示
```bash
python demos/demo_features.py
```

## 🔧 診斷工具

### 準備度檢查
```bash
python tools/readiness_check.py
```

### 調試啟動
```bash
python tools/debug_launcher.py
```

### 綜合診斷
```bash
python tools/comprehensive_diagnostic.py
```

## ⚡ 版本控制

### Git 標籤策略
```bash
# 檢視目前版本
git tag

# 建立新版本標籤
git tag v1.0.0
git tag v1.1.0-beta
git tag v1.2.0-rc1
```

### 分支策略
```bash
# 功能開發
git checkout -b feature/new-feature

# 錯誤修復
git checkout -b hotfix/bug-fix

# 發布準備
git checkout -b release/v1.0.0
```

## 🔄 相容性支援

在重構期間，我們保留了舊的檔案以確保相容性：

```bash
# 舊的啟動方式（仍然有效）
python main_day5.py

# 新的啟動方式（推薦）
python main.py
```

## 🎉 優勢

### ✅ 改善後的優點
- **語義化命名** - 檔名清楚表達功能
- **模組化結構** - 測試、演示、工具分離
- **專業規範** - 符合軟體工程最佳實踐
- **版本控制** - 使用 Git 標籤管理版本
- **易於維護** - 清晰的目錄結構

### 🚀 立即開始
```bash
python main.py
```

歡迎使用重構後的 LivePilotAI！ 🎊
