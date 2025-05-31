# LivePilotAI Development Environment Setup Script

param(
    [switch]$SkipOBSCheck = $false
)

Write-Host "==========================================="
Write-Host "      LivePilotAI Development Setup       "
Write-Host "==========================================="

# Check if running from project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

if (-not (Test-Path "$projectRoot\README.md")) {
    Write-Error "Error: Please run this script from LivePilotAI project root directory"
    exit 1
}

Set-Location $projectRoot
Write-Host "Project Directory: $projectRoot"

# Step 1: Check Python version
Write-Host "`n1. Checking Python installation..."
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not installed"
    }
    
    Write-Host "Found Python version: $pythonVersion"
} catch {
    Write-Error "Python is not installed or not available. Please install Python 3.9+ and add to PATH"
    exit 1
}

# Step 2: Create virtual environment
Write-Host "`n2. Creating Python virtual environment..."
$venvPath = "$projectRoot\envs\dev"

if (Test-Path $venvPath) {
    Write-Host "Virtual environment exists, removing old version..."
    Remove-Item -Recurse -Force $venvPath
}

python -m venv $venvPath
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment"
    exit 1
}

Write-Host "Virtual environment created successfully: $venvPath"

# Step 3: Activate virtual environment and install dependencies
Write-Host "`n3. Activating virtual environment and installing dependencies..."
$activateScript = "$venvPath\Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Error "Cannot find virtual environment activation script"
    exit 1
}

# Activate virtual environment
& $activateScript

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install production dependencies
if (Test-Path "$projectRoot\requirements.txt") {
    Write-Host "Installing production dependencies..."
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found, skipping production dependencies"
}

# Install development dependencies
Write-Host "Installing development dependencies..."
$devDeps = @(
    "black>=23.0.0",
    "pylint>=2.17.0", 
    "mypy>=1.3.0",
    "pytest>=7.3.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pre-commit>=3.3.0",
    "flake8>=6.0.0",
    "isort>=5.12.0"
)

foreach ($package in $devDeps) {
    pip install $package
}

Write-Host "Dependencies installation completed"

# Step 4: Create configuration files
Write-Host "`n4. Creating configuration files..."

# Create .env file
$envContent = @"
# LivePilotAI Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=localhost
API_PORT=8000
WEBSOCKET_PORT=8001

# OBS Configuration
OBS_WEBSOCKET_HOST=localhost
OBS_WEBSOCKET_PORT=4455
OBS_WEBSOCKET_PASSWORD=

# AI Model Configuration
EMOTION_MODEL_PATH=assets/models/emotion_detection.h5
FACE_CASCADE_PATH=assets/models/haarcascade_frontalface_default.xml

# Database Configuration
DATABASE_URL=sqlite:///data/livepilot.db

# Logging Configuration
LOG_FILE=logs/livepilot.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
"@

Set-Content -Path "$projectRoot\.env" -Value $envContent -Encoding UTF8
Write-Host ".env file created"

# Create pyproject.toml
$pyprojectContent = @"
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "livepilot-ai"
version = "0.1.0"
description = "AI-powered real-time emotion detection and live streaming effects system"
authors = [{name = "LivePilotAI Team"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.9"

[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov=src --cov-report=html --cov-report=term-missing"
testpaths = ["tests"]
"@

Set-Content -Path "$projectRoot\pyproject.toml" -Value $pyprojectContent -Encoding UTF8
Write-Host "pyproject.toml file created"

# Step 5: Initialize Git repository if not exists
Write-Host "`n5. Checking Git repository..."

if (-not (Test-Path "$projectRoot\.git")) {
    Write-Host "Initializing Git repository..."
    git init
    
    # Create .gitignore
    $gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
envs/
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
logs/
*.log
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Database
*.db
*.sqlite
*.sqlite3

# Models and large files
assets/models/*.h5
assets/models/*.pb
assets/models/*.onnx

# Temporary files
temp/
tmp/
*.tmp
"@

    Set-Content -Path "$projectRoot\.gitignore" -Value $gitignoreContent -Encoding UTF8
    
    Write-Host "Git repository initialized"
} else {
    Write-Host "Git repository already exists"
}

# Complete
Write-Host "`n==========================================="
Write-Host "      Development Environment Ready!      "
Write-Host "==========================================="

Write-Host "`nNext Steps:"
Write-Host "1. Begin Phase 1 development work"
Write-Host "2. Initialize core architecture"
Write-Host "3. Implement AI engine foundation"

Write-Host "`nDevelopment Environment Info:"
Write-Host "- Virtual environment: envs\dev"
Write-Host "- Configuration file: .env"
Write-Host "- Log directory: logs\"

Write-Host "`nHappy coding! 🚀"