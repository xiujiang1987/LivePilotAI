@echo off
echo ================================================
echo LivePilotAI 緊急修復啟動器
echo ================================================
echo.
echo 正在啟動緊急修復工具...
echo 如果出現任何錯誤，請按任意鍵退出
echo.

cd /d "%~dp0"
python emergency_launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 啟動失敗！錯誤代碼: %ERRORLEVEL%
    echo.
    echo 可能的解決方案:
    echo 1. 確保已安裝 Python
    echo 2. 確保 Python 已加入系統 PATH
    echo 3. 嘗試使用完整路徑啟動 Python
    echo.
    pause
) else (
    echo 程式已正常結束
)
