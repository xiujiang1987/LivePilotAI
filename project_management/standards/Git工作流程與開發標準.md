# LivePilotAI Git工作流程與開發標準

## 1. Git工作流程設計

### 1.1 分支策略 (Git Flow)

#### 主要分支結構
```
main (主分支)
├── develop (開發分支)
├── feature/* (功能分支)
├── release/* (發布分支)
├── hotfix/* (熱修復分支)
└── docs/* (文檔分支)
```

#### 分支命名規範
```yaml
主分支:
  - main: 生產環境穩定版本
  - develop: 開發整合分支

功能分支:
  - feature/ai-engine-emotion-detection
  - feature/obs-websocket-integration  
  - feature/ui-control-panel
  - feature/effect-management-system

發布分支:
  - release/v1.0.0
  - release/v1.1.0-beta

熱修復分支:
  - hotfix/critical-memory-leak
  - hotfix/obs-connection-issue

文檔分支:
  - docs/api-documentation
  - docs/user-manual
```

### 1.2 提交規範 (Conventional Commits)

#### 提交訊息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 提交類型 (type)
```yaml
feat: 新功能
fix: 錯誤修復
docs: 文檔更新
style: 代碼格式調整
refactor: 代碼重構
test: 測試相關
chore: 建構工具、輔助工具更新
perf: 效能優化
ci: CI/CD相關
```

#### 範圍 (scope) 規範
```yaml
ai-engine: AI引擎相關
obs-controller: OBS控制器相關
api: API相關
ui: 使用者介面相關
effects: 特效系統相關
config: 配置管理相關
database: 資料庫相關
docs: 文檔相關
tests: 測試相關
```

#### 提交訊息範例
```bash
# 功能新增
feat(ai-engine): add emotion detection with OpenCV
- Implement face detection using Haar cascades
- Add emotion classification with pre-trained model
- Support real-time emotion analysis pipeline

Closes #12

# 錯誤修復
fix(obs-controller): resolve WebSocket connection timeout
- Increase connection timeout to 10 seconds
- Add automatic reconnection with exponential backoff
- Handle connection lost gracefully

Fixes #25

# 文檔更新
docs(api): update WebSocket API documentation
- Add real-time analysis result format
- Include error handling examples
- Update authentication flow

# 效能優化
perf(ai-engine): optimize frame processing performance
- Reduce memory allocation in emotion detection
- Implement frame buffering for smoother processing
- Achieve 15% performance improvement

# 重構
refactor(effects): restructure effect management system
- Extract rule engine into separate module
- Improve effect priority handling
- Simplify effect configuration format
```

### 1.3 工作流程步驟

#### 功能開發流程
```bash
# 1. 從develop分支創建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/ai-engine-emotion-detection

# 2. 開發功能並提交
git add .
git commit -m "feat(ai-engine): implement basic emotion detection"

# 3. 定期同步develop分支
git checkout develop
git pull origin develop
git checkout feature/ai-engine-emotion-detection
git rebase develop

# 4. 推送功能分支
git push origin feature/ai-engine-emotion-detection

# 5. 創建Pull Request
# 通過GitHub網頁介面創建PR，指向develop分支

# 6. 代碼審查通過後合併
# PR合併後刪除功能分支
git checkout develop
git pull origin develop
git branch -d feature/ai-engine-emotion-detection
git push origin --delete feature/ai-engine-emotion-detection
```

#### 發布流程
```bash
# 1. 從develop創建發布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. 更新版本號和文檔
# 修改version.py, package.json等版本資訊
git commit -m "chore(release): bump version to 1.0.0"

# 3. 測試和修復
# 進行最終測試，修復發現的問題
git commit -m "fix(release): resolve minor UI issues"

# 4. 合併到main和develop
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

git checkout develop  
git merge --no-ff release/v1.0.0

# 5. 推送和清理
git push origin main
git push origin develop
git push origin v1.0.0
git branch -d release/v1.0.0
```

### 1.4 Pull Request 規範

#### PR模板
```markdown
## 變更描述
簡要描述此PR的變更內容

## 變更類型
- [ ] 新功能 (feature)
- [ ] 錯誤修復 (bugfix)
- [ ] 效能優化 (performance)
- [ ] 重構 (refactoring)
- [ ] 文檔更新 (documentation)
- [ ] 測試 (testing)

## 測試
- [ ] 已執行相關單元測試
- [ ] 已執行整合測試
- [ ] 已進行手動測試
- [ ] 測試覆蓋率未降低

## 檢查清單
- [ ] 代碼符合專案風格指南
- [ ] 已更新相關文檔
- [ ] 已處理所有TODO和FIXME
- [ ] 無console.log或print調試語句
- [ ] 變更向後相容

## 相關議題
Closes #(issue number)

## 螢幕截圖 (如適用)
```

#### PR審查清單
```yaml
代碼品質:
  - [ ] 代碼可讀性良好
  - [ ] 函數和類別命名恰當
  - [ ] 註解充分且有意義
  - [ ] 無重複代碼

功能性:
  - [ ] 功能實現符合需求
  - [ ] 邊界情況處理適當
  - [ ] 錯誤處理完善
  - [ ] 效能符合要求

測試:
  - [ ] 測試案例充分
  - [ ] 測試可通過
  - [ ] 覆蓋率符合標準
  - [ ] 模擬適當使用

安全性:
  - [ ] 無安全漏洞
  - [ ] 輸入驗證適當
  - [ ] 權限檢查正確
  - [ ] 敏感資料保護
```

## 2. 代碼風格與品質標準

### 2.1 Python代碼風格 (PEP 8)

#### 基本格式規範
```python
# 行長度: 最大88字符 (使用black formatter)
# 縮排: 4個空格
# 編碼: UTF-8

# 導入順序
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import cv2
from fastapi import FastAPI

from src.ai_engine import EmotionDetector
from src.config import settings

# 類別定義
class EmotionDetector:
    """情緒檢測器類別。
    
    提供即時的人臉情緒檢測功能，支援多種情緒分類。
    
    Attributes:
        model_path: 模型檔案路徑
        confidence_threshold: 信心度閾值
        
    Example:
        detector = EmotionDetector("models/emotion.h5")
        result = detector.detect_emotion(frame)
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.7) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model = None
    
    def detect_emotion(self, frame: np.ndarray) -> Dict[str, float]:
        """檢測圖像中的情緒。
        
        Args:
            frame: 輸入圖像 (BGR格式)
            
        Returns:
            包含情緒機率的字典
            
        Raises:
            ValueError: 當輸入圖像格式不正確時
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid input frame")
            
        # 處理邏輯
        return {"happy": 0.9, "sad": 0.1}

# 函數定義
def process_image(
    image_path: str, 
    output_path: Optional[str] = None,
    resize: bool = True
) -> bool:
    """處理圖像檔案。
    
    Args:
        image_path: 輸入圖像路徑
        output_path: 輸出路徑，預設為None
        resize: 是否調整大小
        
    Returns:
        處理是否成功
    """
    # 實現細節
    pass

# 常數定義
DEFAULT_EMOTION_THRESHOLD = 0.7
SUPPORTED_EMOTIONS = ["happy", "sad", "angry", "surprised", "neutral"]
CONFIG_FILE_PATH = "config/emotion_detection.yaml"
```

#### 類型提示規範
```python
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 列舉類型
class EmotionType(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"

# 資料類別
@dataclass
class EmotionResult:
    emotion: EmotionType
    confidence: float
    face_coordinates: Tuple[int, int, int, int]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotion": self.emotion.value,
            "confidence": self.confidence,
            "face_coordinates": self.face_coordinates,
            "timestamp": self.timestamp
        }

# 複雜類型提示
def analyze_emotions(
    frames: List[np.ndarray],
    settings: Dict[str, Union[str, float, bool]]
) -> List[Optional[EmotionResult]]:
    """分析多幀圖像的情緒。"""
    pass
```

### 2.2 JavaScript/TypeScript代碼風格

#### 基本格式規範 (ESLint + Prettier)
```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'no-console': 'warn',
    'prefer-const': 'error'
  }
};

// TypeScript介面定義
interface EmotionResult {
  emotion: string;
  confidence: number;
  faceCoordinates: [number, number, number, number];
  timestamp: number;
}

interface AIEngineConfig {
  emotionSensitivity: number;
  voiceSensitivity: number;
  gestureEnabled: boolean;
}

// React元件範例
import React, { useState, useEffect } from 'react';
import { Button, Card, Slider } from 'antd';

interface ControlPanelProps {
  onStart: () => void;
  onStop: () => void;
  isRunning: boolean;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  onStart,
  onStop,
  isRunning
}) => {
  const [sensitivity, setSensitivity] = useState<number>(0.7);

  useEffect(() => {
    // 副作用處理
  }, [sensitivity]);

  const handleSensitivityChange = (value: number): void => {
    setSensitivity(value);
  };

  return (
    <Card title="AI Control Panel">
      <div className="control-section">
        <Button 
          type="primary" 
          onClick={isRunning ? onStop : onStart}
          disabled={false}
        >
          {isRunning ? 'Stop' : 'Start'} AI Analysis
        </Button>
        
        <div className="sensitivity-control">
          <label>Emotion Sensitivity:</label>
          <Slider
            min={0}
            max={1}
            step={0.1}
            value={sensitivity}
            onChange={handleSensitivityChange}
          />
        </div>
      </div>
    </Card>
  );
};

export default ControlPanel;
```

### 2.3 代碼品質工具配置

#### Python工具設定

##### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.pylint]
max-line-length = 88
disable = [
    "C0103",  # Invalid name
    "R0903",  # Too few public methods
    "R0913",  # Too many arguments
]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

##### requirements-dev.txt
```txt
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
```

##### pre-commit配置 (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### JavaScript/TypeScript工具設定

##### package.json scripts
```json
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,json,css,md}\"",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
```

### 2.4 測試標準

#### 測試結構
```
tests/
├── unit/              # 單元測試
│   ├── ai_engine/
│   ├── obs_controller/
│   ├── effects/
│   └── api/
├── integration/       # 整合測試
│   ├── test_ai_obs_integration.py
│   └── test_api_integration.py
├── performance/       # 效能測試
│   └── test_real_time_processing.py
├── fixtures/          # 測試資料
│   ├── test_images/
│   ├── test_audio/
│   └── test_configs/
└── conftest.py       # pytest配置
```

#### 測試案例範例
```python
# tests/unit/ai_engine/test_emotion_detector.py
import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.ai_engine.emotion_detector import EmotionDetector, EmotionResult
from src.exceptions import ModelNotLoadedError

class TestEmotionDetector:
    """情緒檢測器測試類別。"""
    
    @pytest.fixture
    def detector(self):
        """創建測試用的情緒檢測器實例。"""
        return EmotionDetector("test_model.h5", confidence_threshold=0.7)
    
    @pytest.fixture
    def sample_frame(self):
        """創建測試用的圖像幀。"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_init_with_valid_parameters(self):
        """測試使用有效參數初始化。"""
        detector = EmotionDetector("model.h5", 0.8)
        assert detector.model_path == "model.h5"
        assert detector.confidence_threshold == 0.8
    
    def test_init_with_invalid_threshold(self):
        """測試使用無效閾值初始化。"""
        with pytest.raises(ValueError, match="Confidence threshold must be"):
            EmotionDetector("model.h5", 1.5)
    
    @patch('src.ai_engine.emotion_detector.cv2.detectMultiScale')
    def test_detect_faces_success(self, mock_detect, detector, sample_frame):
        """測試成功檢測人臉。"""
        mock_detect.return_value = np.array([[100, 100, 150, 150]])
        
        faces = detector.detect_faces(sample_frame)
        
        assert len(faces) == 1
        assert faces[0] == (100, 100, 150, 150)
        mock_detect.assert_called_once()
    
    def test_detect_faces_no_faces(self, detector, sample_frame):
        """測試未檢測到人臉的情況。"""
        with patch('src.ai_engine.emotion_detector.cv2.detectMultiScale') as mock_detect:
            mock_detect.return_value = np.array([])
            
            faces = detector.detect_faces(sample_frame)
            
            assert len(faces) == 0
    
    def test_analyze_emotion_without_model(self, detector, sample_frame):
        """測試在未載入模型時分析情緒。"""
        face_region = sample_frame[100:250, 100:250]
        
        with pytest.raises(ModelNotLoadedError):
            detector.analyze_emotion(face_region)
    
    @patch('src.ai_engine.emotion_detector.EmotionDetector.load_model')
    def test_analyze_emotion_success(self, mock_load, detector, sample_frame):
        """測試成功分析情緒。"""
        # 模擬模型載入和預測
        mock_model = Mock()
        mock_model.predict.return_value = np.array([[0.1, 0.9, 0.0, 0.0, 0.0]])
        detector._model = mock_model
        
        face_region = sample_frame[100:250, 100:250]
        result = detector.analyze_emotion(face_region)
        
        assert isinstance(result, EmotionResult)
        assert result.emotion == "happy"
        assert result.confidence == 0.9
    
    def test_preprocess_face(self, detector):
        """測試人臉預處理。"""
        face_image = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
        
        processed = detector.preprocess_face(face_image)
        
        assert processed.shape == (48, 48, 1)  # 模型輸入尺寸
        assert processed.dtype == np.float32
        assert 0 <= processed.max() <= 1  # 正規化檢查

# 整合測試範例
# tests/integration/test_ai_obs_integration.py
@pytest.mark.integration
class TestAIObsIntegration:
    """AI引擎與OBS整合測試。"""
    
    @pytest.fixture
    def ai_engine(self):
        return AIEngine()
    
    @pytest.fixture  
    def obs_controller(self):
        return OBSController("localhost", 4444)
    
    @pytest.mark.asyncio
    async def test_emotion_triggers_effect(self, ai_engine, obs_controller):
        """測試情緒檢測觸發OBS特效。"""
        # 設定測試場景
        await obs_controller.connect()
        
        # 模擬情緒檢測結果
        emotion_result = EmotionResult("happy", 0.9, (100, 100, 200, 200), time.time())
        
        # 觸發特效
        effect = ai_engine.effect_manager.select_effect(emotion_result)
        success = await obs_controller.execute_effect(effect)
        
        assert success
        assert effect.name == "happy-confetti"
```

#### 測試覆蓋率目標
```yaml
總體覆蓋率: ≥ 80%
核心模組覆蓋率: ≥ 90%
  - ai_engine: ≥ 90%
  - obs_controller: ≥ 85%
  - effect_manager: ≥ 90%
  - api: ≥ 85%

分支覆蓋率: ≥ 75%
功能覆蓋率: ≥ 95%
```

## 3. CI/CD流程

### 3.1 GitHub Actions工作流程

#### 主要工作流程 (.github/workflows/main.yml)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=88
    
    - name: Check code formatting
      run: |
        black --check src tests
        isort --check-only src tests
    
    - name: Type checking
      run: mypy src
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=html
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
    
    - name: Build application
      run: |
        pip install build
        python -m build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: distribution
        path: dist/

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: distribution
        path: dist/
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

### 3.2 開發環境設定腳本

#### 環境設定腳本 (scripts/setup_dev_env.ps1)
```powershell
# LivePilotAI 開發環境設定腳本

Write-Host "LivePilotAI 開發環境設定開始..." -ForegroundColor Green

# 檢查Python版本
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python未安裝或不在PATH中"
    exit 1
}

Write-Host "檢測到Python版本: $pythonVersion" -ForegroundColor Yellow

# 創建虛擬環境
if (!(Test-Path "venv")) {
    Write-Host "創建Python虛擬環境..." -ForegroundColor Yellow
    python -m venv venv
}

# 啟動虛擬環境
Write-Host "啟動虛擬環境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 升級pip
Write-Host "升級pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 安裝依賴
Write-Host "安裝生產依賴..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "安裝開發依賴..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

# 設定pre-commit hooks
Write-Host "設定pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

# 創建配置文件
if (!(Test-Path "config/local.yaml")) {
    Write-Host "創建本地配置文件..." -ForegroundColor Yellow
    Copy-Item "config/default.yaml" "config/local.yaml"
}

# 創建資料目錄
$dataDirs = @("data", "logs", "models", "assets/effects", "assets/audio")
foreach ($dir in $dataDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "創建目錄: $dir" -ForegroundColor Yellow
    }
}

# 檢查OBS是否安裝
$obsPath = Get-Command "obs64.exe" -ErrorAction SilentlyContinue
if ($obsPath) {
    Write-Host "檢測到OBS Studio: $($obsPath.Source)" -ForegroundColor Green
} else {
    Write-Warning "未檢測到OBS Studio，請確保已安裝OBS Studio"
}

Write-Host "開發環境設定完成！" -ForegroundColor Green
Write-Host "使用 'pytest' 運行測試" -ForegroundColor Cyan
Write-Host "使用 'python -m src.main' 啟動應用" -ForegroundColor Cyan
```

### 3.3 代碼品質檢查腳本

#### 品質檢查腳本 (scripts/check_quality.ps1)
```powershell
# 代碼品質檢查腳本

Write-Host "開始代碼品質檢查..." -ForegroundColor Green

# 檢查代碼格式
Write-Host "檢查代碼格式..." -ForegroundColor Yellow
black --check src tests
if ($LASTEXITCODE -ne 0) {
    Write-Error "代碼格式檢查失敗，請運行 'black src tests' 修復"
    $failed = $true
}

# 檢查導入排序
Write-Host "檢查導入排序..." -ForegroundColor Yellow
isort --check-only src tests
if ($LASTEXITCODE -ne 0) {
    Write-Error "導入排序檢查失敗，請運行 'isort src tests' 修復"
    $failed = $true
}

# 執行pylint
Write-Host "執行pylint檢查..." -ForegroundColor Yellow
pylint src
$pylintScore = $LASTEXITCODE

# 執行mypy類型檢查
Write-Host "執行類型檢查..." -ForegroundColor Yellow
mypy src
if ($LASTEXITCODE -ne 0) {
    Write-Warning "類型檢查發現問題"
    $failed = $true
}

# 執行測試
Write-Host "執行測試套件..." -ForegroundColor Yellow
pytest tests/ --cov=src --cov-report=term-missing
if ($LASTEXITCODE -ne 0) {
    Write-Error "測試失敗"
    $failed = $true
}

# 檢查安全性
Write-Host "執行安全性檢查..." -ForegroundColor Yellow
bandit -r src/
if ($LASTEXITCODE -ne 0) {
    Write-Warning "安全性檢查發現問題"
}

if ($failed) {
    Write-Error "代碼品質檢查失敗，請修復上述問題"
    exit 1
} else {
    Write-Host "代碼品質檢查通過！" -ForegroundColor Green
}
```

## 4. 版本管理策略

### 4.1 語義化版本控制 (SemVer)
```
版本格式: MAJOR.MINOR.PATCH

MAJOR: 不向後相容的API變更
MINOR: 向後相容的功能新增
PATCH: 向後相容的錯誤修復

範例:
1.0.0 - 初始穩定版本
1.1.0 - 新增語音分析功能
1.1.1 - 修復情緒檢測錯誤
2.0.0 - 重大架構變更
```

### 4.2 標籤策略
```bash
# 發布標籤
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release"
git tag -a v1.1.0-beta -m "Beta release with voice analysis"
git tag -a v1.1.0-rc.1 -m "Release candidate 1 for version 1.1.0"

# 推送標籤
git push origin v1.0.0
git push origin --tags
```

### 4.3 變更日誌維護 (CHANGELOG.md)
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 新功能準備中

### Changed
- 改進的功能

### Fixed
- 修復的錯誤

## [1.0.0] - 2025-08-30

### Added
- 即時情緒檢測功能
- OBS WebSocket整合
- 視覺特效系統
- Web API介面
- 使用者控制面板

### Security
- 實施輸入驗證
- 添加速率限制
```

---

**文件版本:** 1.0  
**最後更新:** 2025年5月31日  
**負責人:** LivePilotAI 開發團隊
