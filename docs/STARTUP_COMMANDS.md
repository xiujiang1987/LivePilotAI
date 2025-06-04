# LivePilotAI 啟動指令大全

## 🚀 一鍵啟動方式

### 方式一：批處理文件啟動 (推薦)
```batch
# Windows 用戶直接雙擊
start.bat
```

### 方式二：專業啟動器
```bash
# 命令行啟動主程式
python main.py

# 或帶選項啟動
python main.py --app    # 啟動主應用程式
python main.py --test   # 執行系統測試
python main.py --obs-test  # 測試 OBS 整合
python main.py --help   # 顯示幫助
```

### 方式三：圖形化啟動器
```bash
# 啟動圖形界面選擇器
python launcher.py
```

### 方式四：直接啟動主程式
```bash
# 直接啟動 Day 5 完整版
python main_day5.py
```

## 🧪 測試指令

### 系統狀態檢查
```bash
python system_check.py
```

### OBS 整合測試
```bash
python obs_test_simple.py
```

### 快速功能測試
```bash
python day5_simple_test.py
```

### 完整整合測試
```bash
python day5_integration_test.py
```

### 性能基準測試
```bash
python day5_performance_benchmark.py
```

## 📺 OBS Studio 整合

### 準備工作
1. 安裝 OBS Studio (v28.0+)
2. 啟用 WebSocket 插件
3. 設定連接密碼

### 連接測試
```bash
# 測試 OBS 連接
python obs_integration_test.py

# 簡化版測試
python obs_test_simple.py
```

## 🔧 故障排除

### 常見問題

#### 1. Python 版本問題
```bash
# 檢查 Python 版本
python --version

# 應該是 3.8 或更高版本
```

#### 2. 模組導入錯誤
```bash
# 安裝依賴
pip install -r requirements.txt

# 或使用虛擬環境
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. 編碼問題
```bash
# 在 PowerShell 中設定編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

#### 4. GUI 無法啟動
```bash
# 檢查 tkinter 是否可用
python -c "import tkinter; print('GUI OK')"
```

## 📊 系統監控

### 即時狀態監控
```bash
# 檢查系統資源使用
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"
```

### 日誌檢查
```bash
# 查看應用程式日誌
type logs\livepilotai_day5.log

# 或在 PowerShell 中
Get-Content logs\livepilotai_day5.log -Tail 50
```

## 🎬 Demo 模式

### 展示模式啟動
```bash
# 啟動展示模式 (如果可用)
python main_day5.py --demo

# 或使用圖形啟動器選擇 Demo 模式
python launcher.py
```

## 🔄 更新與維護

### 檢查更新
```bash
# 檢查 Git 狀態
git status
git pull origin main
```

### 重置環境
```bash
# 清理暫存檔案
python -c "
import os, shutil
for item in ['__pycache__', '.pytest_cache']:
    if os.path.exists(item):
        shutil.rmtree(item)
        print(f'Cleaned {item}')
"
```

## 📱 快速啟動腳本

### Windows PowerShell 腳本
創建 `quick_start.ps1`:
```powershell
# LivePilotAI 快速啟動腳本
Write-Host "🎬 LivePilotAI 快速啟動" -ForegroundColor Green

# 檢查 Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python 已安裝" -ForegroundColor Green
    python main.py --app
} else {
    Write-Host "❌ 未找到 Python" -ForegroundColor Red
    Write-Host "請先安裝 Python 3.8+" -ForegroundColor Yellow
}
```

### 執行方式
```powershell
# 設定執行權限並運行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\quick_start.ps1
```

## 🎯 開發模式

### 開發環境啟動
```bash
# 啟動開發模式 (如果有的話)
python main_day5.py --debug

# 或設定環境變數
set DEBUG=1
python main_day5.py
```

### 測試驅動開發
```bash
# 運行所有測試
python -m pytest tests/ -v

# 運行特定測試
python day5_validation_test.py
```

## 📋 啟動檢核清單

- [ ] Python 3.8+ 已安裝
- [ ] 虛擬環境已啟用 (建議)
- [ ] 依賴套件已安裝
- [ ] OBS Studio 已安裝並啟用 WebSocket
- [ ] 攝像頭權限已授予
- [ ] 網路連接正常
- [ ] 系統資源充足 (>4GB RAM)

## 🆘 緊急啟動

如果所有方式都失敗，使用最小化啟動：
```bash
# 最小化系統測試
python -c "
import sys
print('Python:', sys.version)
try:
    import tkinter
    print('GUI: OK')
except:
    print('GUI: FAILED')
"
```

---

**🎉 恭喜！LivePilotAI 已準備就緒！**

選擇上述任一方式啟動您的智能直播導播系統。建議新用戶從圖形化啟動器 (`python launcher.py`) 開始。
