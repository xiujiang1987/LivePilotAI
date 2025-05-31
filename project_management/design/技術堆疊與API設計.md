# LivePilotAI 技術堆疊與API設計

## 1. 技術堆疊確認

### 1.1 後端技術棧

#### 核心開發語言
```yaml
主要語言: Python 3.9+
原因: 
  - 豐富的AI/ML生態系統
  - OpenCV, TensorFlow等成熟套件
  - 快速原型開發
  - 社群支援度高

次要語言: JavaScript (前端)
原因:
  - React/Electron桌面應用開發
  - 豐富的UI元件庫
  - WebSocket即時通訊
```

#### Web框架
```yaml
API框架: FastAPI
版本: 0.104+
優勢:
  - 自動API文檔生成
  - 高效能 (基於Starlette)
  - 原生async/await支援
  - 型別檢查和驗證
  - WebSocket內建支援

替代方案: Flask + Flask-SocketIO
考量: 如果FastAPI學習曲線過陡
```

#### 資料庫
```yaml
主要資料庫: SQLite
用途: 本地設定、使用者偏好、日誌存儲
優勢: 
  - 無需額外安裝
  - 檔案型資料庫
  - 適合桌面應用

擴展選項: PostgreSQL
用途: 未來雲端服務或企業版
```

### 1.2 AI/ML技術棧

#### 電腦視覺
```yaml
OpenCV: 4.8+
用途: 影像處理、人臉檢測、基礎電腦視覺
安裝: pip install opencv-python

MediaPipe: 0.10+
用途: 手勢識別、姿態檢測、人體關鍵點
安裝: pip install mediapipe

dlib: 19.24+ (可選)
用途: 高精度人臉特徵點檢測
安裝: pip install dlib
```

#### 深度學習框架
```yaml
TensorFlow: 2.13+
用途: 情緒檢測模型、自定義模型訓練
安裝: pip install tensorflow

Keras: (內建於TensorFlow)
用途: 高階模型API、快速原型

替代方案: PyTorch 2.0+
考量: 如果需要更靈活的模型開發
```

#### 音訊處理
```yaml
Librosa: 0.10+
用途: 音訊特徵提取、頻譜分析
安裝: pip install librosa

PyAudio: 0.2.11+
用途: 即時音訊輸入/輸出
安裝: pip install pyaudio

SoundFile: 0.12+
用途: 音訊文件讀寫
安裝: pip install soundfile
```

### 1.3 前端技術棧

#### 桌面應用框架
```yaml
Electron: 26+
用途: 跨平台桌面應用包裝
優勢: Web技術開發桌面應用

React: 18+
用途: 使用者介面開發
狀態管理: Redux Toolkit

UI框架: Ant Design 或 Material-UI
用途: 現成的UI元件庫
```

#### 即時通訊
```yaml
Socket.IO Client
用途: 與後端WebSocket通訊
安裝: npm install socket.io-client

WebSocket API (原生)
用途: 如果不需要Socket.IO的額外功能
```

### 1.4 整合技術

#### OBS整合
```yaml
obs-websocket: 5.0+
協定: WebSocket
文檔: https://github.com/obsproject/obs-websocket

Python客戶端: obs-websocket-py
安裝: pip install obs-websocket-py
用途: Python與OBS通訊
```

#### 開發工具
```yaml
版本控制: Git
倉庫: GitHub
CI/CD: GitHub Actions
測試: pytest, unittest
代碼品質: pylint, black, mypy
文檔: Sphinx, MkDocs
```

## 2. API設計規範

### 2.1 RESTful API設計

#### 基礎URL結構
```
Base URL: http://localhost:8000/api/v1
```

#### 端點設計規範

##### 2.1.1 AI引擎控制
```yaml
# 啟動AI分析
POST /ai/start
Request: 
  {
    "camera_index": 0,
    "audio_device": "default",
    "settings": {
      "emotion_sensitivity": 0.7,
      "voice_sensitivity": 0.6
    }
  }
Response: 
  {
    "status": "success",
    "message": "AI analysis started",
    "session_id": "uuid-string"
  }

# 停止AI分析
POST /ai/stop
Request: 
  {
    "session_id": "uuid-string"
  }
Response: 
  {
    "status": "success",
    "message": "AI analysis stopped"
  }

# 取得分析狀態
GET /ai/status
Response:
  {
    "is_running": true,
    "session_id": "uuid-string",
    "uptime": 120,
    "performance": {
      "fps": 28,
      "cpu_usage": 45.2,
      "memory_usage": 1024
    }
  }
```

##### 2.1.2 OBS控制
```yaml
# 連接OBS
POST /obs/connect
Request:
  {
    "host": "localhost",
    "port": 4444,
    "password": "optional-password"
  }
Response:
  {
    "status": "success",
    "message": "Connected to OBS",
    "obs_version": "29.1.0"
  }

# 取得場景列表
GET /obs/scenes
Response:
  {
    "current_scene": "Main Scene",
    "scenes": [
      {
        "name": "Main Scene",
        "sources": ["Camera", "Overlay"]
      },
      {
        "name": "Gaming Scene", 
        "sources": ["Game Capture", "Webcam"]
      }
    ]
  }

# 切換場景
POST /obs/scenes/switch
Request:
  {
    "scene_name": "Gaming Scene",
    "transition": "fade",
    "duration": 300
  }
Response:
  {
    "status": "success",
    "previous_scene": "Main Scene",
    "current_scene": "Gaming Scene"
  }
```

##### 2.1.3 特效管理
```yaml
# 取得可用特效
GET /effects
Response:
  {
    "effects": [
      {
        "id": "happy-confetti",
        "name": "Happy Confetti",
        "type": "visual",
        "triggers": ["emotion:happy"],
        "duration": 3000
      },
      {
        "id": "applause-sound",
        "name": "Applause Sound",
        "type": "audio", 
        "triggers": ["gesture:clap"],
        "duration": 2000
      }
    ]
  }

# 手動觸發特效
POST /effects/trigger
Request:
  {
    "effect_id": "happy-confetti",
    "intensity": 0.8,
    "duration": 5000
  }
Response:
  {
    "status": "success",
    "effect_id": "happy-confetti",
    "triggered_at": "2025-06-01T10:30:00Z"
  }

# 取得特效歷史
GET /effects/history?limit=50
Response:
  {
    "effects": [
      {
        "effect_id": "happy-confetti",
        "triggered_at": "2025-06-01T10:30:00Z",
        "trigger_source": "emotion:happy",
        "confidence": 0.92
      }
    ],
    "total": 150,
    "page": 1
  }
```

##### 2.1.4 配置管理
```yaml
# 取得使用者配置
GET /config/user
Response:
  {
    "ai_settings": {
      "emotion_sensitivity": 0.7,
      "voice_sensitivity": 0.6,
      "gesture_sensitivity": 0.8
    },
    "obs_settings": {
      "auto_connect": true,
      "host": "localhost",
      "port": 4444
    },
    "ui_preferences": {
      "theme": "dark",
      "language": "zh-TW",
      "notifications": true
    }
  }

# 更新使用者配置
PUT /config/user
Request:
  {
    "ai_settings": {
      "emotion_sensitivity": 0.8
    }
  }
Response:
  {
    "status": "success",
    "message": "Configuration updated",
    "updated_fields": ["ai_settings.emotion_sensitivity"]
  }
```

### 2.2 WebSocket API設計

#### 2.2.1 連接與認證
```yaml
連接URL: ws://localhost:8000/ws
認證方式: 連接時發送token或在query parameter中提供

連接訊息:
{
  "type": "connect",
  "client_id": "web-ui-client",
  "version": "1.0.0"
}

認證回應:
{
  "type": "auth_success", 
  "session_id": "uuid-string",
  "server_version": "1.0.0"
}
```

#### 2.2.2 即時資料推送

##### AI分析結果推送
```yaml
訊息類型: analysis_result
頻率: 30fps (每33ms)
格式:
{
  "type": "analysis_result",
  "timestamp": "2025-06-01T10:30:00.123Z",
  "session_id": "uuid-string",
  "data": {
    "emotion": {
      "type": "happy",
      "confidence": 0.92,
      "intensity": 0.75,
      "face_coordinates": [100, 50, 200, 150]
    },
    "voice": {
      "tone": "excited",
      "volume_level": 0.68,
      "pitch_change": 0.15
    },
    "gesture": {
      "type": "thumbs_up",
      "confidence": 0.87,
      "hand_position": [0.6, 0.4]
    }
  }
}
```

##### 特效觸發通知
```yaml
訊息類型: effect_triggered
格式:
{
  "type": "effect_triggered",
  "timestamp": "2025-06-01T10:30:00.123Z",
  "effect": {
    "id": "happy-confetti",
    "name": "Happy Confetti",
    "type": "visual",
    "duration": 3000,
    "trigger_source": "emotion:happy",
    "confidence": 0.92
  }
}
```

##### 系統狀態更新
```yaml
訊息類型: system_status
頻率: 每5秒
格式:
{
  "type": "system_status",
  "timestamp": "2025-06-01T10:30:00.123Z",
  "status": {
    "ai_engine": {
      "running": true,
      "fps": 28,
      "cpu_usage": 45.2,
      "memory_usage": 1024
    },
    "obs_connection": {
      "connected": true,
      "current_scene": "Main Scene",
      "recording": false,
      "streaming": true
    }
  }
}
```

#### 2.2.3 客戶端控制訊息

##### 訂閱特定資料流
```yaml
請求:
{
  "type": "subscribe",
  "channels": ["analysis_result", "effect_triggered", "system_status"],
  "options": {
    "analysis_result": {
      "fps_limit": 15  // 降低頻率以節省頻寬
    }
  }
}

回應:
{
  "type": "subscription_confirmed",
  "channels": ["analysis_result", "effect_triggered", "system_status"]
}
```

##### 即時設定調整
```yaml
請求:
{
  "type": "update_settings",
  "settings": {
    "emotion_sensitivity": 0.8,
    "effect_cooldown": 2000
  }
}

回應:
{
  "type": "settings_updated",
  "status": "success",
  "applied_settings": {
    "emotion_sensitivity": 0.8,
    "effect_cooldown": 2000
  }
}
```

### 2.3 錯誤處理

#### HTTP錯誤碼規範
```yaml
200: 請求成功
201: 資源創建成功
400: 請求參數錯誤
401: 未授權
404: 資源不存在
409: 資源衝突
429: 請求過於頻繁
500: 伺服器內部錯誤
503: 服務暫時不可用
```

#### 錯誤回應格式
```yaml
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "emotion_sensitivity must be between 0.0 and 1.0",
    "details": {
      "field": "emotion_sensitivity",
      "provided_value": 1.5,
      "valid_range": [0.0, 1.0]
    },
    "timestamp": "2025-06-01T10:30:00Z",
    "request_id": "uuid-string"
  }
}
```

#### WebSocket錯誤處理
```yaml
{
  "type": "error",
  "error": {
    "code": "CONNECTION_LOST",
    "message": "Connection to OBS lost",
    "severity": "warning",
    "auto_retry": true,
    "retry_in": 5000
  }
}
```

## 3. 資料模型設計

### 3.1 資料庫Schema

#### 使用者設定表 (user_settings)
```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    data_type TEXT NOT NULL, -- 'string', 'number', 'boolean', 'json'
    category TEXT NOT NULL,  -- 'ai', 'obs', 'ui', 'effects'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 特效歷史表 (effect_history)
```sql
CREATE TABLE effect_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    effect_id TEXT NOT NULL,
    effect_name TEXT NOT NULL,
    trigger_source TEXT NOT NULL, -- 'emotion:happy', 'gesture:wave'
    trigger_confidence REAL NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER NOT NULL, -- milliseconds
    success BOOLEAN DEFAULT TRUE
);
```

#### 系統日誌表 (system_logs)
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,      -- 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    category TEXT NOT NULL,   -- 'ai_engine', 'obs_controller', 'api', 'ui'
    message TEXT NOT NULL,
    details TEXT,             -- JSON格式的詳細資訊
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 效能指標表 (performance_metrics)
```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage INTEGER NOT NULL, -- MB
    gpu_usage REAL,
    fps REAL NOT NULL,
    frame_processing_time REAL, -- milliseconds
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 配置檔案結構

#### 主配置檔案 (config/app.yaml)
```yaml
app:
  name: "LivePilotAI"
  version: "1.0.0"
  environment: "development"  # development, production
  
api:
  host: "localhost"
  port: 8000
  cors_origins: ["http://localhost:3000"]
  
database:
  path: "data/livepilot.db"
  backup_interval: 3600  # seconds
  
logging:
  level: "INFO"
  file_path: "logs/app.log"
  max_size_mb: 100
  backup_count: 5
```

#### AI引擎配置 (config/ai_engine.yaml)
```yaml
emotion_detection:
  model_path: "models/emotion_model.h5"
  confidence_threshold: 0.7
  face_detection:
    cascade_path: "models/haarcascade_frontalface_default.xml"
    scale_factor: 1.1
    min_neighbors: 5
    min_size: [30, 30]
  
voice_analysis:
  sample_rate: 16000
  frame_length: 2048
  hop_length: 512
  features: ["mfcc", "spectral_centroid", "zero_crossing_rate"]
  
gesture_recognition:
  mediapipe:
    model_complexity: 1
    min_detection_confidence: 0.5
    min_tracking_confidence: 0.5
  gestures:
    - name: "thumbs_up"
      threshold: 0.8
    - name: "peace_sign"
      threshold: 0.7
    - name: "wave"
      threshold: 0.6
```

#### 特效配置 (config/effects.yaml)
```yaml
effects:
  - id: "happy-confetti"
    name: "Happy Confetti"
    type: "visual"
    file_path: "assets/effects/confetti.png"
    triggers:
      - condition: "emotion == 'happy'"
        confidence_threshold: 0.8
    properties:
      duration: 3000
      position: "center"
      scale: 1.0
      animation: "fade_in_out"
    cooldown: 5000
    
  - id: "applause-sound"
    name: "Applause Sound"
    type: "audio"
    file_path: "assets/audio/applause.wav"
    triggers:
      - condition: "gesture == 'clap'"
        confidence_threshold: 0.7
    properties:
      volume: 0.8
      loop: false
    cooldown: 3000
    
rules:
  global_cooldown: 1000  # milliseconds between any effects
  max_concurrent_effects: 3
  priority_system: true
```

## 4. 安全性設計

### 4.1 API安全
- 輸入驗證和清理
- 請求速率限制
- CORS政策設定
- 敏感資料不記錄日誌

### 4.2 資料隱私
- 本地資料加密
- 不上傳個人影像/音訊
- 使用者同意機制
- 資料保留政策

### 4.3 系統安全
- 檔案路徑驗證
- 執行權限控制
- 錯誤資訊不洩露系統資訊
- 定期安全更新

---

**文件版本:** 1.0  
**最後更新:** 2025年5月31日  
**負責人:** LivePilotAI 開發團隊
