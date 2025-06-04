# LivePilotAI 情感檢測引擎 - 依賴項安裝腳本
# 請以管理員身份執行此腳本

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "LivePilotAI 情感檢測引擎依賴項安裝" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 檢查Python是否已安裝
Write-Host "檢查Python安裝狀態..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "找到Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "錯誤: 未找到Python。請先安裝Python 3.8-3.11版本。" -ForegroundColor Red
    exit 1
}

# 檢查pip是否可用
Write-Host "檢查pip可用性..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "找到pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "錯誤: 未找到pip。請確保pip已正確安裝。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "開始安裝依賴項..." -ForegroundColor Yellow
Write-Host ""

# 安裝依賴項
$dependencies = @(
    "opencv-python==4.8.1.78",
    "numpy==1.24.3", 
    "tensorflow==2.13.0"
)

foreach ($package in $dependencies) {
    Write-Host "正在安裝 $package..." -ForegroundColor Cyan
    pip install $package
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $package 安裝成功" -ForegroundColor Green
    } else {
        Write-Host "✗ $package 安裝失敗" -ForegroundColor Red
    }
    Write-Host ""
}

# 驗證安裝
Write-Host "驗證安裝結果..." -ForegroundColor Yellow
Write-Host ""

$verifyScript = @"
try:
    import cv2
    import numpy as np
    import tensorflow as tf
    
    print(f"✓ OpenCV版本: {cv2.__version__}")
    print(f"✓ NumPy版本: {np.__version__}")
    print(f"✓ TensorFlow版本: {tf.__version__}")
    print("✓ 所有依賴項已成功安裝並可正常使用！")
    
except ImportError as e:
    print(f"✗ 導入錯誤: {e}")
    print("✗ 某些依賴項可能未正確安裝")
"@

python -c $verifyScript

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "安裝完成！" -ForegroundColor Green
Write-Host "您現在可以使用情感檢測引擎了。" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
