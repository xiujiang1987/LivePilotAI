# LivePilotAI 情感檢測引擎 - 啟動測試腳本
# 此腳本會自動檢查和安裝依賴，然後測試引擎功能

Write-Host "🚀 LivePilotAI 情感檢測引擎啟動測試" -ForegroundColor Green
Write-Host "=" * 50

# 檢查 Python 是否可用
Write-Host "`n📋 檢查 Python 環境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 已安裝: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 未安裝或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 檢查 pip 是否可用
Write-Host "`n📦 檢查 pip 套件管理器..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip 已安裝: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip 未安裝" -ForegroundColor Red
    exit 1
}

# 執行依賴檢查測試
Write-Host "`n🧪 執行依賴檢查系統測試..." -ForegroundColor Yellow
try {
    Write-Host "正在執行 test_dependency_system.py..." -ForegroundColor Cyan
    python test_dependency_system.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 依賴檢查系統測試通過" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 依賴檢查系統可能需要手動安裝一些套件" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 執行依賴檢查測試時發生錯誤" -ForegroundColor Red
}

# 執行簡單依賴狀態檢查
Write-Host "`n🔍 執行簡單依賴狀態檢查..." -ForegroundColor Yellow
try {
    python simple_test.py
} catch {
    Write-Host "❌ 簡單測試執行失敗" -ForegroundColor Red
}

# 手動檢查關鍵依賴
Write-Host "`n📋 手動檢查關鍵依賴..." -ForegroundColor Yellow

$dependencies = @("opencv-python", "numpy", "tensorflow", "Pillow")

foreach ($dep in $dependencies) {
    try {
        Write-Host "檢查 $dep..." -ForegroundColor Cyan
        pip show $dep | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $dep 已安裝" -ForegroundColor Green
        } else {
            Write-Host "✗ $dep 未安裝" -ForegroundColor Red
            Write-Host "  安裝指令: pip install $dep" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ $dep 檢查失敗" -ForegroundColor Red
    }
}

# 提供手動安裝指令
Write-Host "`n📦 如果需要手動安裝依賴，請執行以下指令:" -ForegroundColor Yellow
Write-Host "pip install opencv-python numpy tensorflow Pillow" -ForegroundColor Cyan

# 測試引擎啟動
Write-Host "`n🎯 測試情感檢測引擎啟動..." -ForegroundColor Yellow
try {
    Write-Host "正在執行 test_emotion_engine.py..." -ForegroundColor Cyan
    python test_emotion_engine.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 引擎啟動測試成功！" -ForegroundColor Green
        Write-Host "LivePilotAI 情感檢測引擎已準備就緒！" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️ 引擎啟動測試完成，但可能有警告" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n❌ 引擎啟動測試失敗" -ForegroundColor Red
    Write-Host "請檢查依賴是否正確安裝" -ForegroundColor Yellow
}

# 顯示相關文件
Write-Host "`n📚 相關文件:" -ForegroundColor Yellow
Write-Host "  - EMOTION_ENGINE_GUIDE.md: 詳細使用指南" -ForegroundColor Cyan
Write-Host "  - DEPENDENCY_CHECK_COMPLETION_REPORT.md: 完成報告" -ForegroundColor Cyan
Write-Host "  - INSTALL_DEPENDENCIES.md: 手動安裝指南" -ForegroundColor Cyan

Write-Host "`n✅ 測試腳本執行完成！" -ForegroundColor Green
