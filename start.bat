@echo off
:: LivePilotAI 一鍵啟動腳本
:: Windows Batch File for Quick Launch

title LivePilotAI - 智能直播導播系統

echo ========================================
echo   LivePilotAI - 智能直播導播系統
echo   AI-Powered Live Streaming Director
echo ========================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python！
    echo    請先安裝 Python 3.8+ 
    echo    下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 檢查虛擬環境
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 啟用虛擬環境...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  未找到虛擬環境，使用系統 Python
)

:: 檢查必要文件
if not exist "main.py" (
    echo ❌ 錯誤: 找不到 main.py 文件！
    pause
    exit /b 1
)

:: 顯示選項菜單
echo.
echo 請選擇啟動模式:
echo.
echo 1. 🚀 啟動主應用程式
echo 2. 🧪 執行系統測試  
echo 3. 📺 測試 OBS 整合
echo 4. ❓ 顯示幫助信息
echo 5. 🚪 退出
echo.

set /p choice="請輸入選項 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 正在啟動 LivePilotAI 主應用程式...
    python main.py --app
) else if "%choice%"=="2" (
    echo.
    echo 🧪 正在執行系統測試...
    python main.py --test
) else if "%choice%"=="3" (
    echo.
    echo 📺 正在測試 OBS 整合...
    python main.py --obs-test
) else if "%choice%"=="4" (
    echo.
    python main.py --help
) else if "%choice%"=="5" (
    echo.
    echo 👋 再見！
    exit /b 0
) else (
    echo.
    echo ❌ 無效選項，請重新選擇
    goto :eof
)

echo.
echo ========================================
echo 操作完成！
echo ========================================
pause
