@echo off
cd /d "%~dp0"

if exist "..\..\..\.venv_new\Scripts\python.exe" (
    "..\..\..\.venv_new\Scripts\python.exe" scripts\launch_menu.py
) else (
    python scripts\launch_menu.py
)

if %errorlevel% neq 0 pause
