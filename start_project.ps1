# LivePilotAI Project Launcher
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Menu {
    Clear-Host
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "         LivePilotAI 撠?敹恍???
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "?嗅??桅?: $PWD"
    Write-Host ""
    
    # Check Python
    $pythonCmd = "python"
    # Try to find the venv relative to the script location
    $venvPath = Join-Path (Get-Location) "..\..\..\.venv_new\Scripts\python.exe"
    if (Test-Path $venvPath) {
        $pythonCmd = $venvPath
    }
    
    Write-Host "雿輻 Python: $pythonCmd" -ForegroundColor Gray
    try {
        & $pythonCmd --version
    } catch {
        Write-Host "??Python ?啣?瑼Ｘ憭望?" -ForegroundColor Red
        return
    }

    Write-Host ""
    Write-Host "[3] ?舐??:" -ForegroundColor Yellow
    Write-Host "   1. ??銝餌?撘?(Main Panel)"
    Write-Host "   2. 皜祈岫?湔蝞∠???
    Write-Host "   3. ??摰蝟餌絞皜祈岫"
    Write-Host "   4. 摰?靘陷??
    Write-Host "   5. ?亦?撠????
    Write-Host "   6. ??撠?鞈?憭?
    Write-Host "   0. ???
    Write-Host ""
    
    $choice = Read-Host "隢??雿?(1-6, 0)"
    
    switch ($choice) {
        "1" { 
            Write-Host "`n?? ??銝餌?撘?.." -ForegroundColor Green
            & $pythonCmd main.py
            Pause
        }
        "2" {
            Write-Host "`n?妒 皜祈岫?湔蝞∠???.." -ForegroundColor Green
            & $pythonCmd src\obs_integration\scene_manager.py
            Pause
        }
        "3" {
            Write-Host "`n?? ??摰蝟餌絞皜祈岫..." -ForegroundColor Green
            & $pythonCmd test_system.py
            Pause
        }
        "4" {
            Write-Host "`n? 摰?靘陷??.." -ForegroundColor Green
            & $pythonCmd -m pip install -r requirements.txt
            Write-Host "??靘陷??鋆??? -ForegroundColor Green
            Pause
        }
        "5" {
            Write-Host "`n?? 撠????" -ForegroundColor Green
            Write-Host "   撠?雿蔭: $PWD"
            Write-Host "   Python?: " -NoNewline
            & $pythonCmd --version
            Write-Host "   Git???"
            git status --porcelain
            Pause
        }
        "6" {
            Write-Host "`n?? ??撠?鞈?憭?.." -ForegroundColor Green
            Invoke-Item .
        }
        "0" {
            Write-Host "`n?? ??雿輻 LivePilotAI嚗? -ForegroundColor Cyan
            exit
        }
        Default {
            Write-Host "???⊥??豢?嚗??頛詨" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}

# Main Loop
while ($true) {
    Show-Menu
}


