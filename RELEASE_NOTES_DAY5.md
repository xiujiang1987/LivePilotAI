# LivePilotAI - Day 5 優化成果報告 (v0.5.0)

## 📌 專案狀態概覽
本次優化專注於 **安全性 (Security)**、**使用者體驗 (UX)** 與 **系統穩定性 (Stability)**。經測試，應用程式已可穩定運行於無 GPU 加速與缺少部分依賴的環境。

### 🛡️ 1. 安全性加固 (Security Hardening)
- **YAML 漏洞修復**: 
  - 移除了設定檔 (`config/current.yml`) 中 Python 特有的 `!!python/tuple` 標籤。
  - 重構 `src/core/config_manager.py`，將危險的 `yaml.full_load` 替換為標準安全的 `yaml.safe_load`。
  - **成果**: 消除潛在的遠端代碼執行 (RCE) 風險。

### ⚡ 2. 啟動體驗升級 (Splash Screen)
- **視覺回饋**: 
  - 實作了原生的 Tkinter **啟動畫面 (Splash Screen)**。
  - 在主視窗顯示前，即時顯示載入進度（"Loading Core Config...", "Loading AI Engine..."）。
- **延遲載入 (Lazy Loading)**:
  - 將 TensorFlow、MediaPipe 等重型函式庫移至背景執行緒載入。
  - **成果**: 應用程式點擊後 **<1秒** 內即有反應，大幅減少使用者對「程式當機」的焦慮。

### 🧩 3. 架構重構 (Architecture Refactoring)
- **依賴注入 (Dependency Injection)**:
  - 重寫了 `AIDirector`, `RealTimeEmotionDetector`, `MainPanel` 的初始化邏輯。
  - 組件不再自行實例化重複的子系統，而是透過參數傳遞共享實例。
  - **成果**: 記憶體佔用降低，並解決了初始化時的 `TypeError` 多重參數錯誤。
- **模組解耦**:
  - 修正了 `main.py` 與 `src.core` 的循環匯入問題。

### 🔧 4. 容錯機制 (Fault Tolerance)
- **AI 模型備援**:
  - **MediaPipe**: 若無法載入，自動禁用手勢識別並記錄警告，不影響主程式。
  - **Face Detection**: 若 Haar Cascade 或 DNN 模型其一缺失，自動切換至可用方案。

---

## 🚀 如何執行
在終端機執行以下指令啟動應用程式：
```bash
python main.py
```
