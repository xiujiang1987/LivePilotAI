# LivePilotAI 檔案重構計畫
## 從 Day命名 轉向 語義化命名

### 🚨 目前的問題
- `main_day5.py` → 應該叫什麼？
- `day5_simple_test.py` → 功能不明確
- `demo_day4.py` → 版本號沒有意義

### ✅ 建議的新命名結構

#### 主程式檔案
- `main_day5.py` → `main.py` 或 `livepilot_main.py`
- `launcher.py` → 保持不變（已經語義化）

#### 測試檔案
- `day5_simple_test.py` → `integration_test.py`
- `day5_validation_test.py` → `validation_test.py`
- `day5_performance_benchmark.py` → `performance_benchmark.py`
- `day5_integration_test.py` → `system_integration_test.py`
- `day5_readiness_check.py` → `readiness_check.py`

#### 演示檔案
- `demo_day4.py` → `demo_basic.py`
- `demo_day4_features.py` → `demo_features.py`

#### 測試檔案
- `test_day4_simple.py` → `unit_test_basic.py`
- `test_day4_features.py` → `unit_test_features.py`

### 🎯 版本控制策略

#### 使用 Git Tags 代替檔名版本
```bash
# 代替 day1, day2, day3...
git tag v0.1.0-alpha    # 初期版本
git tag v0.2.0-beta     # 功能完整版本
git tag v0.3.0-rc1      # 候選發布版本
git tag v1.0.0          # 正式發布版本
```

#### 使用 Git Branches 管理功能
```bash
git checkout -b feature/emotion-detection
git checkout -b feature/obs-integration
git checkout -b feature/ui-improvements
git checkout -b hotfix/import-errors
```

### 📁 建議的新檔案結構
```
LivePilotAI/
├── main.py                    # 主程式入口
├── launcher.py                # 圖形化啟動器
├── requirements.txt           # 依賴管理
├── README.md                  # 專案說明
├── 
├── src/                       # 核心源碼
├── tests/                     # 測試檔案
│   ├── unit_test_basic.py
│   ├── integration_test.py
│   ├── performance_benchmark.py
│   └── validation_test.py
├── demos/                     # 演示檔案
│   ├── demo_basic.py
│   └── demo_features.py
├── tools/                     # 工具腳本
│   ├── readiness_check.py
│   ├── debug_launcher.py
│   └── comprehensive_diagnostic.py
└── docs/                      # 文檔
    ├── QUICK_START.md
    ├── API_REFERENCE.md
    └── DEPLOYMENT_GUIDE.md
```

### 🔧 重構執行計畫

#### 階段1：主要檔案重命名
1. `main_day5.py` → `main.py`
2. 更新所有引用這個檔案的地方
3. 測試確保功能正常

#### 階段2：測試檔案重構
1. 移動到 `tests/` 目錄
2. 使用功能性命名
3. 更新測試腳本

#### 階段3：建立版本標籤
1. 為當前狀態建立 Git tag
2. 清理歷史 day 命名的 commit
3. 建立新的分支策略

### 💡 即時執行建議

要立即改善，我們可以：
1. 建立符號連結保持相容性
2. 逐步更新引用
3. 最終移除舊檔案

這樣既保持了功能，又改善了專案結構！
