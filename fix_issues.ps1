# LivePilotAI 問題修復與依賴安裝腳本 (PowerShell版本)

Write-Host "================================================" -ForegroundColor Green
Write-Host "    LivePilotAI 問題修復與依賴安裝腳本" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# 檢查Python
Write-Host "[1/4] 檢查Python環境..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    try {
        $pythonVersion = & py --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $pythonVersion (使用 py 命令)" -ForegroundColor Green
            Set-Alias python py
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "❌ Python未正確安裝或未添加到PATH" -ForegroundColor Red
        Write-Host "請先安裝Python 3.8+並添加到系統PATH" -ForegroundColor Red
        Read-Host "按Enter鍵退出"
        exit 1
    }
}

# 安裝依賴
Write-Host "[2/4] 安裝核心依賴..." -ForegroundColor Yellow
$packages = @(
    "obsws-python",
    "fastapi", 
    "uvicorn",
    "websockets",
    "pydantic",
    "opencv-python",
    "numpy",
    "pillow",
    "python-dotenv",
    "pyyaml",
    "dataclasses-json"
)

& python -m pip install --upgrade pip

foreach ($package in $packages) {
    Write-Host "安裝 $package..." -ForegroundColor Cyan
    & python -m pip install $package
}

Write-Host ""
Write-Host "[3/4] 驗證安裝..." -ForegroundColor Yellow

# 驗證安裝
$testCommands = @{
    "obsws-python" = "import obsws_python; print('✅ obsws-python 安裝成功')"
    "FastAPI" = "import fastapi; print('✅ FastAPI 安裝成功')"
    "OpenCV" = "import cv2; print('✅ OpenCV 安裝成功')"
    "NumPy" = "import numpy; print('✅ NumPy 安裝成功')"
}

foreach ($name in $testCommands.Keys) {
    try {
        & python -c $testCommands[$name] 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host $testCommands[$name].Split(';')[1].Trim("print('").Trim("')") -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ $name 可能安裝失敗" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[4/4] 運行系統測試..." -ForegroundColor Yellow
if (Test-Path "src\obs_integration\scene_manager_fix.py") {
    & python src\obs_integration\scene_manager_fix.py
} else {
    Write-Host "⚠️ 找不到測試檔案，請檢查專案結構" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "          修復完成！系統已就緒" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步選項:" -ForegroundColor Cyan
Write-Host "1. 運行完整系統: python test_system.py" -ForegroundColor White
Write-Host "2. 啟動網頁控制台: python src\web_interface\web_control_panel.py" -ForegroundColor White
Write-Host "3. 查看故障排除指南: Get-Content TROUBLESHOOTING.md" -ForegroundColor White
Write-Host ""
Read-Host "按Enter鍵結束"
