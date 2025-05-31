# LivePilotAI 開發環境設置腳本
# 版本: 1.0
# 日期: 2025-05-31

Write-Host "🚀 LivePilotAI 開發環境設置開始..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# 檢查當前目錄
$currentDir = Get-Location
Write-Host "📂 當前工作目錄: $currentDir" -ForegroundColor Yellow

# 檢查Python是否安裝
Write-Host "🐍 檢查Python環境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 檢測到Python版本: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python未安裝"
    }
} catch {
    Write-Error "❌ Python未安裝或不在PATH中，請先安裝Python 3.9+"
    Write-Host "下載連結: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# 檢查Python版本是否符合要求
$versionString = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$version = [version]$versionString
$minVersion = [version]"3.9"

if ($version -lt $minVersion) {
    Write-Error "❌ Python版本太舊，需要3.9+，當前版本: $versionString"
    exit 1
}

# 創建虛擬環境
Write-Host "🔧 設置Python虛擬環境..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Write-Host "創建新的虛擬環境..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ 虛擬環境創建成功" -ForegroundColor Green
} else {
    Write-Host "✅ 虛擬環境已存在" -ForegroundColor Green
}

# 啟動虛擬環境
Write-Host "🔄 啟動虛擬環境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 升級pip
Write-Host "📦 升級pip到最新版本..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 安裝基礎開發依賴
Write-Host "📦 安裝生產依賴..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "✅ 生產依賴安裝完成" -ForegroundColor Green
} else {
    Write-Warning "⚠️  requirements.txt不存在，跳過生產依賴安裝"
}

# 創建開發依賴文件
Write-Host "📦 創建並安裝開發依賴..." -ForegroundColor Yellow
$devRequirements = @"
# 代碼品質工具
black==23.7.0
isort==5.12.0
pylint==2.17.5
mypy==1.5.1
flake8==6.0.0

# 測試工具
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
pytest-asyncio==0.21.1

# 開發工具
pre-commit==3.3.3
python-dotenv==1.0.0

# 文檔工具
sphinx==7.1.2
sphinx-rtd-theme==1.3.0
"@

$devRequirements | Out-File -FilePath "requirements-dev.txt" -Encoding UTF8
pip install -r requirements-dev.txt
Write-Host "✅ 開發依賴安裝完成" -ForegroundColor Green

# 設定pre-commit hooks
Write-Host "🔗 設置pre-commit hooks..." -ForegroundColor Yellow
if (Test-Path ".pre-commit-config.yaml") {
    pre-commit install
    Write-Host "✅ Pre-commit hooks設置完成" -ForegroundColor Green
} else {
    Write-Warning "⚠️  .pre-commit-config.yaml不存在，跳過pre-commit設置"
}

# 創建環境配置文件
Write-Host "⚙️  創建環境配置文件..." -ForegroundColor Yellow

# 創建.env文件
if (!(Test-Path ".env")) {
    $envContent = @"
# LivePilotAI 環境配置
ENVIRONMENT=development
LOG_LEVEL=INFO
API_HOST=localhost
API_PORT=8000

# OBS配置
OBS_HOST=localhost
OBS_PORT=4444
OBS_PASSWORD=

# AI引擎配置
EMOTION_MODEL_PATH=models/emotion_model.h5
CONFIDENCE_THRESHOLD=0.7
PROCESSING_FPS=30

# 資料庫配置
DATABASE_PATH=data/livepilot.db

# 安全設置
SECRET_KEY=your-secret-key-here
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env文件創建完成" -ForegroundColor Green
}

# 創建必要的目錄結構
Write-Host "📁 創建必要的目錄..." -ForegroundColor Yellow
$directories = @(
    "data",
    "logs", 
    "models",
    "temp",
    "assets/effects",
    "assets/audio",
    "assets/icons",
    "config/dev",
    "config/prod",
    "config/test"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 創建目錄: $dir" -ForegroundColor Cyan
    }
}

# 檢查Git是否初始化
Write-Host "📚 檢查Git倉庫..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    Write-Host "初始化Git倉庫..." -ForegroundColor Cyan
    git init
    git add .
    git commit -m "feat: initial project setup with development environment"
    Write-Host "✅ Git倉庫初始化完成" -ForegroundColor Green
} else {
    Write-Host "✅ Git倉庫已存在" -ForegroundColor Green
}

# 檢查OBS Studio是否安裝
Write-Host "🎥 檢查OBS Studio..." -ForegroundColor Yellow
$obsInstalled = $false
$possibleObsPaths = @(
    "${env:ProgramFiles}\obs-studio\bin\64bit\obs64.exe",
    "${env:ProgramFiles(x86)}\obs-studio\bin\64bit\obs64.exe",
    "${env:LOCALAPPDATA}\Programs\obs-studio\bin\64bit\obs64.exe"
)

foreach ($path in $possibleObsPaths) {
    if (Test-Path $path) {
        Write-Host "✅ 檢測到OBS Studio: $path" -ForegroundColor Green
        $obsInstalled = $true
        break
    }
}

if (!$obsInstalled) {
    Write-Warning "⚠️  未檢測到OBS Studio，請從以下連結下載安裝："
    Write-Host "https://obsproject.com/download" -ForegroundColor Cyan
}

# 創建啟動腳本
Write-Host "🚀 創建快速啟動腳本..." -ForegroundColor Yellow
$startScript = @"
# LivePilotAI 快速啟動腳本
Write-Host "🚀 啟動LivePilotAI開發環境..." -ForegroundColor Green

# 啟動虛擬環境
& "venv\Scripts\Activate.ps1"

# 設置環境變數
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

Write-Host "✅ 開發環境已啟動" -ForegroundColor Green
Write-Host "💡 可用命令:" -ForegroundColor Cyan
Write-Host "  python -m src.main          # 啟動應用" -ForegroundColor White
Write-Host "  pytest                      # 運行測試" -ForegroundColor White
Write-Host "  python scripts/dev_check.py # 開發環境檢查" -ForegroundColor White
"@

$startScript | Out-File -FilePath "start_dev.ps1" -Encoding UTF8

# 設置完成報告
Write-Host ""
Write-Host "🎉 開發環境設置完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📋 設置摘要:" -ForegroundColor Yellow
Write-Host "  ✅ Python虛擬環境" -ForegroundColor White
Write-Host "  ✅ 開發依賴安裝" -ForegroundColor White
Write-Host "  ✅ 代碼品質工具" -ForegroundColor White
Write-Host "  ✅ 目錄結構創建" -ForegroundColor White
Write-Host "  ✅ 環境配置文件" -ForegroundColor White
Write-Host "  ✅ Git倉庫初始化" -ForegroundColor White

Write-Host ""
Write-Host "🚀 下一步:" -ForegroundColor Yellow
Write-Host "  1. 使用 './start_dev.ps1' 啟動開發環境" -ForegroundColor White
Write-Host "  2. 運行 'python scripts/dev_check.py' 檢查環境" -ForegroundColor White
Write-Host "  3. 開始開發核心AI引擎模組" -ForegroundColor White

Write-Host ""
Write-Host "📚 有用的命令:" -ForegroundColor Yellow
Write-Host "  pytest --cov=src            # 運行測試並查看覆蓋率" -ForegroundColor White
Write-Host "  black src tests             # 格式化代碼" -ForegroundColor White
Write-Host "  pylint src                  # 檢查代碼品質" -ForegroundColor White
Write-Host "  mypy src                    # 類型檢查" -ForegroundColor White
