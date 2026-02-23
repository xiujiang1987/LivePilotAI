"""
LivePilotAI Web控制台
提供直觀的網頁界面來控制和監控OBS實況畫面系統
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn
from pydantic import BaseModel

# 導入相關模組
from ..obs_integration.livepilot_bridge import LivePilotAIBridge, StreamingConfig
from ..obs_integration.ai_layout_engine import ViewerMetrics, ContextData, ContentType

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(
    title="LivePilotAI Control Panel",
    description="AI驅動的OBS實況畫面控制系統",
    version="1.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局變量
bridge: Optional[LivePilotAIBridge] = None
connected_clients: List[WebSocket] = []

# Pydantic模型
class SystemStatus(BaseModel):
    """系統狀態模型"""
    is_running: bool
    obs_connected: bool
    camera_active: bool
    emotion_queue_size: int
    viewer_metrics_queue_size: int
    stats: Dict

class EmotionData(BaseModel):
    """情緒數據模型"""
    emotion: str
    confidence: float
    timestamp: str

class ViewerMetricsData(BaseModel):
    """觀眾數據模型"""
    viewer_count: int
    chat_messages_per_minute: float
    average_message_length: float
    emoji_usage_rate: float
    follow_rate: float
    donation_frequency: float

class LayoutChangeData(BaseModel):
    """佈局變更數據模型"""
    from_scene: str
    to_scene: str
    timestamp: str
    trigger: str

class ConfigUpdate(BaseModel):
    """配置更新模型"""
    obs_host: str = "localhost"
    obs_port: int = 4444
    obs_password: str = ""
    camera_index: int = 0
    enable_auto_layout: bool = True
    enable_emotion_overlay: bool = True
    emotion_detection_interval: float = 0.5
    layout_decision_interval: float = 5.0

# 靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """獲取主控制台頁面"""
    return HTMLResponse(content=get_dashboard_html(), status_code=200)

def get_dashboard_html() -> str:
    """生成控制台HTML"""
    return """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LivePilotAI 控制台</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.1rem;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #dc3545;
        }
        
        .status-indicator.active {
            background: #28a745;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .panel h3 {
            margin-bottom: 15px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }
        
        .emotion-display {
            text-align: center;
        }
        
        .emotion-icon {
            font-size: 4rem;
            margin-bottom: 10px;
        }
        
        .emotion-text {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: capitalize;
        }
        
        .confidence-text {
            font-size: 1.1rem;
            color: #666;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .metric-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .layout-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .layout-btn {
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .layout-btn:hover {
            border-color: #667eea;
            background: #f0f0f0;
        }
        
        .layout-btn.active {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }
        
        .log-container {
            background: #343a40;
            color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 3px;
        }
        
        .log-entry.info {
            background: rgba(23, 162, 184, 0.2);
        }
        
        .log-entry.warning {
            background: rgba(255, 193, 7, 0.2);
        }
        
        .log-entry.error {
            background: rgba(220, 53, 69, 0.2);
        }
        
        .bottom-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        
        .config-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input,
        .form-group select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .bottom-grid {
                grid-template-columns: 1fr;
            }
            
            .config-form {
                grid-template-columns: 1fr;
            }
            
            .status-bar {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 標題區域 -->
        <div class="header">
            <h1>🎬 LivePilotAI 控制台</h1>
            <p class="subtitle">AI驅動的OBS實況畫面智能管理系統</p>
        </div>
        
        <!-- 狀態欄 -->
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator" id="systemStatus"></div>
                <span>系統狀態</span>
            </div>
            <div class="status-item">
                <div class="status-indicator" id="obsStatus"></div>
                <span>OBS連接</span>
            </div>
            <div class="status-item">
                <div class="status-indicator" id="cameraStatus"></div>
                <span>攝影機</span>
            </div>
            <div class="status-item">
                <div class="status-indicator" id="aiStatus"></div>
                <span>AI引擎</span>
            </div>
        </div>
        
        <!-- 主要控制面板 -->
        <div class="main-grid">
            <!-- 情緒檢測面板 -->
            <div class="panel">
                <h3>🎭 即時情緒檢測</h3>
                <div class="emotion-display">
                    <div class="emotion-icon" id="emotionIcon">😐</div>
                    <div class="emotion-text" id="emotionText">neutral</div>
                    <div class="confidence-text" id="confidenceText">0% 信心度</div>
                </div>
            </div>
            
            <!-- 觀眾數據面板 -->
            <div class="panel">
                <h3>👥 觀眾互動數據</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="viewerCount">0</div>
                        <div class="metric-label">觀眾數</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="chatRate">0</div>
                        <div class="metric-label">聊天頻率</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="followRate">0</div>
                        <div class="metric-label">追蹤率</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="interactionLevel">Low</div>
                        <div class="metric-label">互動程度</div>
                    </div>
                </div>
            </div>
            
            <!-- 系統控制面板 -->
            <div class="panel">
                <h3>⚙️ 系統控制</h3>
                <div class="controls">
                    <button class="btn btn-success" id="startBtn">啟動系統</button>
                    <button class="btn btn-danger" id="stopBtn">停止系統</button>
                    <button class="btn btn-primary" id="restartBtn">重新啟動</button>
                    <button class="btn btn-secondary" id="exportBtn">匯出報告</button>
                </div>
            </div>
        </div>
        
        <!-- 底部面板 -->
        <div class="bottom-grid">
            <!-- 佈局控制與日誌 -->
            <div class="panel">
                <h3>🎨 手動佈局控制</h3>
                <div class="layout-grid">
                    <div class="layout-btn" data-layout="gaming">🎮 遊戲</div>
                    <div class="layout-btn" data-layout="chatting">💬 聊天</div>
                    <div class="layout-btn" data-layout="showcase">📺 展示</div>
                    <div class="layout-btn" data-layout="focused">🎯 專注</div>
                    <div class="layout-btn" data-layout="high_energy">🔥 高能</div>
                </div>
                
                <h3 style="margin-top: 20px;">📊 系統日誌</h3>
                <div class="log-container" id="logContainer"></div>
            </div>
            
            <!-- 配置面板 -->
            <div class="panel">
                <h3>🔧 系統配置</h3>
                <div class="config-form">
                    <div class="form-group">
                        <label>OBS主機</label>
                        <input type="text" id="obsHost" value="localhost">
                    </div>
                    <div class="form-group">
                        <label>OBS端口</label>
                        <input type="number" id="obsPort" value="4444">
                    </div>
                    <div class="form-group">
                        <label>OBS密碼</label>
                        <input type="password" id="obsPassword" value="">
                    </div>
                    <div class="form-group">
                        <label>攝影機索引</label>
                        <input type="number" id="cameraIndex" value="0">
                    </div>
                    <div class="form-group">
                        <label>情緒檢測間隔(秒)</label>
                        <input type="number" id="emotionInterval" value="0.5" step="0.1">
                    </div>
                    <div class="form-group">
                        <label>佈局決策間隔(秒)</label>
                        <input type="number" id="layoutInterval" value="5.0" step="0.5">
                    </div>
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="autoLayout" checked>
                        <label>自動佈局</label>
                    </div>
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="emotionOverlay" checked>
                        <label>情緒覆蓋</label>
                    </div>
                </div>
                <div style="margin-top: 15px;">
                    <button class="btn btn-primary" id="updateConfigBtn">更新配置</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket連接
        let ws = null;
        let isConnected = false;
        
        // 情緒圖標映射
        const emotionIcons = {
            'angry': '😠',
            'disgust': '🤢', 
            'fear': '😨',
            'happy': '😊',
            'sad': '😢',
            'surprise': '😲',
            'neutral': '😐',
            'focused': '🎯',
            'excited': '🤩',
            'relaxed': '😌'
        };
        
        // 初始化WebSocket連接
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                isConnected = true;
                addLog('WebSocket連接已建立', 'info');
                updateConnectionStatus();
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = function(event) {
                isConnected = false;
                addLog('WebSocket連接已關閉', 'warning');
                updateConnectionStatus();
                
                // 嘗試重新連接
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                addLog(`WebSocket錯誤: ${error}`, 'error');
            };
        }
        
        // 處理WebSocket消息
        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'emotion_update':
                    updateEmotionDisplay(data.data);
                    break;
                case 'viewer_metrics':
                    updateViewerMetrics(data.data);
                    break;
                case 'system_status':
                    updateSystemStatus(data.data);
                    break;
                case 'layout_change':
                    handleLayoutChange(data.data);
                    break;
                case 'log':
                    addLog(data.message, data.level);
                    break;
            }
        }
        
        // 更新情緒顯示
        function updateEmotionDisplay(emotionData) {
            const icon = document.getElementById('emotionIcon');
            const text = document.getElementById('emotionText');
            const confidence = document.getElementById('confidenceText');
            
            icon.textContent = emotionIcons[emotionData.emotion] || '😐';
            text.textContent = emotionData.emotion;
            confidence.textContent = `${Math.round(emotionData.confidence * 100)}% 信心度`;
        }
        
        // 更新觀眾數據
        function updateViewerMetrics(metrics) {
            document.getElementById('viewerCount').textContent = metrics.viewer_count;
            document.getElementById('chatRate').textContent = metrics.chat_messages_per_minute.toFixed(1);
            document.getElementById('followRate').textContent = metrics.follow_rate.toFixed(1);
            document.getElementById('interactionLevel').textContent = metrics.interaction_level;
        }
        
        // 更新系統狀態
        function updateSystemStatus(status) {
            updateStatusIndicator('systemStatus', status.is_running);
            updateStatusIndicator('obsStatus', status.obs_connected);
            updateStatusIndicator('cameraStatus', status.camera_active);
            updateStatusIndicator('aiStatus', status.is_running);
        }
        
        // 更新狀態指示器
        function updateStatusIndicator(elementId, isActive) {
            const indicator = document.getElementById(elementId);
            if (isActive) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        }
        
        // 處理佈局變更
        function handleLayoutChange(data) {
            addLog(`佈局已切換: ${data.from_scene} → ${data.to_scene}`, 'info');
            
            // 更新佈局按鈕狀態
            document.querySelectorAll('.layout-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            const newLayoutBtn = document.querySelector(`[data-layout="${data.to_scene}"]`);
            if (newLayoutBtn) {
                newLayoutBtn.classList.add('active');
            }
        }
        
        // 添加日誌
        function addLog(message, level = 'info') {
            const logContainer = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${level}`;
            logEntry.textContent = `[${timestamp}] ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // 限制日誌條目數量
            while (logContainer.children.length > 100) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        // 發送WebSocket消息
        function sendMessage(type, data) {
            if (ws && isConnected) {
                ws.send(JSON.stringify({type: type, data: data}));
            }
        }
        
        // 更新連接狀態
        function updateConnectionStatus() {
            // 這裡可以更新UI來顯示連接狀態
        }
        
        // 事件監聽器
        document.addEventListener('DOMContentLoaded', function() {
            // 連接WebSocket
            connectWebSocket();
            
            // 系統控制按鈕
            document.getElementById('startBtn').addEventListener('click', function() {
                sendMessage('start_system', {});
                addLog('正在啟動系統...', 'info');
            });
            
            document.getElementById('stopBtn').addEventListener('click', function() {
                sendMessage('stop_system', {});
                addLog('正在停止系統...', 'info');
            });
            
            document.getElementById('restartBtn').addEventListener('click', function() {
                sendMessage('restart_system', {});
                addLog('正在重新啟動系統...', 'info');
            });
            
            document.getElementById('exportBtn').addEventListener('click', function() {
                sendMessage('export_report', {});
                addLog('正在匯出報告...', 'info');
            });
            
            // 佈局控制按鈕
            document.querySelectorAll('.layout-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const layout = this.dataset.layout;
                    sendMessage('switch_layout', {layout: layout});
                    addLog(`手動切換佈局: ${layout}`, 'info');
                });
            });
            
            // 配置更新按鈕
            document.getElementById('updateConfigBtn').addEventListener('click', function() {
                const config = {
                    obs_host: document.getElementById('obsHost').value,
                    obs_port: parseInt(document.getElementById('obsPort').value),
                    obs_password: document.getElementById('obsPassword').value,
                    camera_index: parseInt(document.getElementById('cameraIndex').value),
                    emotion_detection_interval: parseFloat(document.getElementById('emotionInterval').value),
                    layout_decision_interval: parseFloat(document.getElementById('layoutInterval').value),
                    enable_auto_layout: document.getElementById('autoLayout').checked,
                    enable_emotion_overlay: document.getElementById('emotionOverlay').checked
                };
                
                sendMessage('update_config', config);
                addLog('配置已更新', 'info');
            });
            
            // 定期請求系統狀態
            setInterval(function() {
                if (isConnected) {
                    sendMessage('get_status', {});
                }
            }, 2000);
        });
    </script>
</body>
</html>
"""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端點"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_websocket_message(websocket, message)
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info("客戶端斷開連接")

async def handle_websocket_message(websocket: WebSocket, message: Dict):
    """處理WebSocket消息"""
    global bridge
    
    message_type = message.get("type")
    data = message.get("data", {})
    
    try:
        if message_type == "start_system":
            await start_system()
            
        elif message_type == "stop_system":
            await stop_system()
            
        elif message_type == "restart_system":
            await restart_system()
            
        elif message_type == "switch_layout":
            await switch_layout(data.get("layout"))
            
        elif message_type == "update_config":
            await update_config(data)
            
        elif message_type == "get_status":
            await send_system_status()
            
        elif message_type == "export_report":
            await export_report()
            
    except Exception as e:
        logger.error(f"處理WebSocket消息錯誤: {e}")
        await broadcast_message({
            "type": "log",
            "message": f"錯誤: {str(e)}",
            "level": "error"
        })

async def broadcast_message(message: Dict):
    """廣播消息給所有連接的客戶端"""
    if connected_clients:
        message_json = json.dumps(message, ensure_ascii=False)
        for client in connected_clients.copy():
            try:
                await client.send_text(message_json)
            except:
                connected_clients.remove(client)

async def start_system():
    """啟動系統"""
    global bridge
    
    try:
        if bridge is None:
            config = StreamingConfig()
            bridge = LivePilotAIBridge(config)
            
            # 添加回調函數
            bridge.add_emotion_callback(on_emotion_detected)
            bridge.add_layout_change_callback(on_layout_changed)
        
        if await bridge.initialize():
            # 在背景任務中啟動分析
            asyncio.create_task(bridge.start_streaming_analysis())
            
            await broadcast_message({
                "type": "log",
                "message": "系統已成功啟動",
                "level": "info"
            })
            
            await send_system_status()
        
    except Exception as e:
        logger.error(f"啟動系統失敗: {e}")
        await broadcast_message({
            "type": "log",
            "message": f"啟動系統失敗: {str(e)}",
            "level": "error"
        })

async def stop_system():
    """停止系統"""
    global bridge
    
    try:
        if bridge:
            await bridge.stop()
            bridge = None
            
        await broadcast_message({
            "type": "log",
            "message": "系統已停止",
            "level": "info"
        })
        
        await send_system_status()
        
    except Exception as e:
        logger.error(f"停止系統失敗: {e}")
        await broadcast_message({
            "type": "log",
            "message": f"停止系統失敗: {str(e)}",
            "level": "error"
        })

async def restart_system():
    """重新啟動系統"""
    await stop_system()
    await asyncio.sleep(2)
    await start_system()

async def switch_layout(layout: str):
    """切換佈局"""
    global bridge
    
    if bridge and bridge.obs_manager:
        try:
            # 手動切換場景
            scene_name = f"AI_{layout}"
            success = bridge.obs_manager.switch_scene(scene_name)
            
            if success:
                await broadcast_message({
                    "type": "layout_change",
                    "data": {
                        "from_scene": "manual",
                        "to_scene": layout,
                        "timestamp": datetime.now().isoformat(),
                        "trigger": "manual"
                    }
                })
            
        except Exception as e:
            logger.error(f"切換佈局失敗: {e}")

async def update_config(config_data: Dict):
    """更新配置"""
    global bridge
    
    try:
        # 如果系統正在運行，需要重新啟動
        if bridge:
            await stop_system()
        
        # 更新配置（這裡應該保存到配置文件）
        await broadcast_message({
            "type": "log",
            "message": "配置已更新，請重新啟動系統",
            "level": "info"
        })
        
    except Exception as e:
        logger.error(f"更新配置失敗: {e}")

async def send_system_status():
    """發送系統狀態"""
    global bridge
    
    if bridge:
        status = bridge.get_current_status()
        await broadcast_message({
            "type": "system_status",
            "data": status
        })
    else:
        await broadcast_message({
            "type": "system_status",
            "data": {
                "is_running": False,
                "obs_connected": False,
                "camera_active": False,
                "emotion_queue_size": 0,
                "viewer_metrics_queue_size": 0
            }
        })

async def export_report():
    """匯出報告"""
    global bridge
    
    if bridge:
        try:
            report = bridge.export_session_report()
            
            # 這裡可以將報告保存到文件或發送給客戶端
            await broadcast_message({
                "type": "log",
                "message": "報告已匯出",
                "level": "info"
            })
            
        except Exception as e:
            logger.error(f"匯出報告失敗: {e}")

def on_emotion_detected(emotion_result):
    """情緒檢測回調"""
    asyncio.create_task(broadcast_message({
        "type": "emotion_update",
        "data": {
            "emotion": emotion_result.emotion,
            "confidence": emotion_result.confidence,
            "timestamp": datetime.now().isoformat()
        }
    }))

def on_layout_changed(from_scene: str, to_scene: str):
    """佈局變更回調"""
    asyncio.create_task(broadcast_message({
        "type": "layout_change",
        "data": {
            "from_scene": from_scene,
            "to_scene": to_scene,
            "timestamp": datetime.now().isoformat(),
            "trigger": "ai"
        }
    }))

# API端點
@app.get("/api/status")
async def get_status():
    """獲取系統狀態"""
    global bridge
    
    if bridge:
        return bridge.get_current_status()
    else:
        return {
            "is_running": False,
            "obs_connected": False,
            "camera_active": False
        }

@app.post("/api/viewer-metrics")
async def update_viewer_metrics(metrics: ViewerMetricsData):
    """更新觀眾數據"""
    global bridge
    
    if bridge:
        viewer_metrics = ViewerMetrics(
            viewer_count=metrics.viewer_count,
            chat_messages_per_minute=metrics.chat_messages_per_minute,
            average_message_length=metrics.average_message_length,
            emoji_usage_rate=metrics.emoji_usage_rate,
            follow_rate=metrics.follow_rate,
            donation_frequency=metrics.donation_frequency
        )
        
        bridge.update_viewer_metrics(viewer_metrics)
        
        # 廣播更新
        await broadcast_message({
            "type": "viewer_metrics",
            "data": {
                "viewer_count": metrics.viewer_count,
                "chat_messages_per_minute": metrics.chat_messages_per_minute,
                "follow_rate": metrics.follow_rate,
                "interaction_level": viewer_metrics.calculate_interaction_level().value
            }
        })
        
        return {"status": "success"}
    
    return {"status": "error", "message": "系統未運行"}

@app.post("/api/context")
async def update_context(context_data: Dict):
    """更新上下文數據"""
    global bridge
    
    if bridge:
        context = ContextData(
            content_type=ContentType(context_data.get("content_type", "gaming")),
            stream_duration=context_data.get("stream_duration", 0),
            current_game=context_data.get("current_game"),
            current_activity=context_data.get("current_activity")
        )
        
        bridge.update_context_data(context)
        return {"status": "success"}
    
    return {"status": "error", "message": "系統未運行"}

if __name__ == "__main__":
    uvicorn.run(
        "web_control_panel:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
