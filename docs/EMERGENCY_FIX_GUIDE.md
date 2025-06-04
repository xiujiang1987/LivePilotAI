# LivePilotAI 啟動問題解決指南

## 問題診斷：為什麼三個選項都失敗？

根據分析，您遇到的問題主要是由以下原因造成的：

### 🔍 **主要問題原因**

1. **模組導入失敗**
   - `src` 目錄下的核心模組可能缺失或損壞
   - Python 無法找到必要的專案模組

2. **依賴項缺失**
   - 某些必要的 Python 套件沒有安裝
   - OBS 相關的依賴可能未正確安裝

3. **檔案結構不完整**
   - 專案的核心檔案或目錄可能缺失
   - `__init__.py` 檔案可能缺失導致模組無法導入

4. **路徑解析問題**
   - 相對路徑無法正確解析
   - 工作目錄設置不正確

## 🚀 **立即解決方案**

### 方案一：使用緊急修復啟動器（推薦）

1. **雙擊執行** `emergency_fix.bat`
   ```
   或者在命令列執行：
   python emergency_launcher.py
   ```

2. **按順序執行修復步驟：**
   - 點擊 "1. 自動修復系統" - 修復檔案結構
   - 點擊 "2. 安裝依賴項" - 安裝必要套件
   - 點擊 "3. 執行簡單測試" - 驗證修復結果
   - 點擊 "4. 啟動應用程式" - 啟動 LivePilotAI

### 方案二：手動修復（進階用戶）

1. **檢查並創建目錄結構：**
   ```
   mkdir src
   mkdir src\obs_integration
   mkdir src\core
   mkdir src\ai_engine
   mkdir logs
   mkdir config
   ```

2. **安裝依賴項：**
   ```
   pip install -r requirements.txt
   ```
   
   如果沒有 requirements.txt，安裝基本依賴：
   ```
   pip install opencv-python Pillow tkinter obs-websocket-py
   ```

3. **創建基本模組檔案：**
   在相應目錄下創建 `__init__.py` 和基本實現檔案

4. **測試修復結果：**
   ```
   python basic_test.py
   ```

## 🛠️ **詳細修復步驟**

### 步驟 1：驗證 Python 環境
```bash
python --version
pip --version
```

### 步驟 2：檢查專案結構
確保以下目錄和檔案存在：
```
LivePilotAI/
├── src/
│   ├── __init__.py
│   ├── obs_integration/
│   │   ├── __init__.py
│   │   └── obs_manager.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scene_controller.py
│   │   └── camera_manager.py
│   └── ai_engine/
│       ├── __init__.py
│       ├── emotion_detector.py
│       └── emotion_mapper.py
├── main_day5.py
├── basic_test.py
└── requirements.txt
```

### 步驟 3：修復模組導入
確保每個目錄都有 `__init__.py` 檔案：
```python
# src/__init__.py
# Auto-generated init file

# src/obs_integration/__init__.py  
# Auto-generated init file

# src/core/__init__.py
# Auto-generated init file

# src/ai_engine/__init__.py
# Auto-generated init file
```

### 步驟 4：創建基本實現
如果核心檔案缺失，創建基本實現以確保導入不會失敗。

## 🔧 **常見錯誤和解決方案**

### 錯誤 1：ModuleNotFoundError
**解決方案：**
- 確保 `src` 目錄在 Python 路徑中
- 檢查 `__init__.py` 檔案是否存在
- 使用緊急修復器的 "自動修復系統" 功能

### 錯誤 2：ImportError
**解決方案：**
- 安裝缺失的依賴項
- 使用緊急修復器的 "安裝依賴項" 功能

### 錯誤 3：FileNotFoundError
**解決方案：**
- 檢查檔案路徑是否正確
- 確保在正確的工作目錄下執行

### 錯誤 4：Permission Error
**解決方案：**
- 以管理員身份運行
- 檢查檔案權限

## 📋 **驗證修復結果**

修復完成後，依次測試：

1. **基本模組導入測試：**
   ```python
   python -c "import sys; sys.path.insert(0, 'src'); from obs_integration.obs_manager import OBSManager"
   ```

2. **執行簡單測試：**
   ```
   python basic_test.py
   ```

3. **啟動主應用程式：**
   ```
   python main_day5.py
   ```

## 🎯 **成功指標**

修復成功的標誌：
- ✅ 所有基本模組可以正常導入
- ✅ `basic_test.py` 執行無錯誤
- ✅ 圖形啟動器三個選項都能正常工作
- ✅ 主應用程式可以啟動

## 📞 **如果仍有問題**

如果按照上述步驟仍然無法解決問題：

1. **重新檢查 Python 版本** - 建議使用 Python 3.8 或更高版本
2. **清理 Python 快取** - 刪除 `__pycache__` 目錄
3. **重新克隆專案** - 如果檔案損壞嚴重
4. **檢查系統資源** - 確保有足夠的記憶體和磁碟空間

---

**最後更新：** 2025年6月4日  
**版本：** 緊急修復版 v1.0

使用緊急修復啟動器是最簡單和最有效的解決方案！
