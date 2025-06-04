# LivePilotAI 專案結構初始化腳本
# 創建標準化的開發專案目錄結構

$projectRoot = "d:\AI_Park\Workspace\dev_projects\ai\LivePilotAI"

# 主要開發目錄
$directories = @(
    # 源代碼目錄
    "src\ai_engine",           # AI核心引擎
    "src\api",                 # 後端API
    "src\frontend",            # 前端介面
    "src\obs_integration",     # OBS整合
    "src\effects",             # 特效系統
    "src\utils",               # 工具函數
    
    # 測試目錄
    "tests\unit",              # 單元測試
    "tests\integration",       # 整合測試
    "tests\performance",       # 效能測試
    
    # 文檔目錄
    "docs\api",                # API文檔
    "docs\architecture",       # 架構文檔
    "docs\user_guide",         # 使用手冊
    "docs\development",        # 開發文檔
    
    # 配置目錄
    "config\dev",              # 開發環境配置
    "config\prod",             # 生產環境配置
    "config\test",             # 測試環境配置
    
    # 資源目錄
    "assets\models",           # AI模型文件
    "assets\effects",          # 特效資源
    "assets\icons",            # 圖標資源
    "assets\audio",            # 音效資源
    
    # 腳本目錄
    "scripts\build",           # 建置腳本
    "scripts\deploy",          # 部署腳本
    "scripts\dev",             # 開發輔助腳本
    
    # 環境目錄
    "envs",                    # 虛擬環境
    
    # 日誌目錄
    "logs",                    # 應用日誌
    
    # 工具目錄
    "tools",                   # 開發工具
    
    # 專案管理
    "project_management\requirements",  # 需求文檔
    "project_management\design",        # 設計文檔
    "project_management\planning"       # 規劃文檔
)

Write-Host "🚀 正在創建 LivePilotAI 專案目錄結構..." -ForegroundColor Green

foreach ($dir in $directories) {
    $fullPath = Join-Path $projectRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✅ 創建目錄: $dir" -ForegroundColor Cyan
    } else {
        Write-Host "⏭️  目錄已存在: $dir" -ForegroundColor Yellow
    }
}

Write-Host "🎉 專案目錄結構創建完成！" -ForegroundColor Green
Write-Host "📁 專案根目錄: $projectRoot" -ForegroundColor White
