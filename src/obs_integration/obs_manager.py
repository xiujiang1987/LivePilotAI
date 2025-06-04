#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI OBS WebSocket 連接管理器
Day 5 核心模組 - 處理與 OBS Studio 的 WebSocket 連接
"""

import asyncio
import json
import logging
import time
import traceback
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum

try:
    import websockets
    from websockets.exceptions import ConnectionClosed, InvalidURI
except ImportError:
    print("警告: websockets 套件未安裝，請執行: pip install websockets")
    websockets = None

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """連接狀態枚舉"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class OBSConfig:
    """OBS 連接配置"""
    host: str = "localhost"
    port: int = 4455
    password: str = ""
    auto_reconnect: bool = True
    reconnect_interval: int = 5
    connection_timeout: int = 10
    heartbeat_interval: int = 30


class OBSWebSocketManager:
    """
    OBS WebSocket 連接管理器
    
    負責管理與 OBS Studio 的 WebSocket 連接，包括：
    - 連接建立與維護
    - 自動重連機制
    - 心跳檢測
    - 消息發送與接收
    - 事件處理
    """
    
    def __init__(self, config: OBSConfig = None):
        self.config = config or OBSConfig()
        self.websocket = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.request_handlers: Dict[str, asyncio.Future] = {}
        self.request_id_counter = 0
        self.heartbeat_task = None
        self.receive_task = None
        self.stats = {
            'connected_time': None,
            'messages_sent': 0,
            'messages_received': 0,
            'reconnection_count': 0,
            'last_error': None
        }
        
    @property
    def is_connected(self) -> bool:
        """檢查是否已連接"""
        return self.connection_state == ConnectionState.CONNECTED
    
    @property
    def connection_url(self) -> str:
        """獲取連接 URL"""
        return f"ws://{self.config.host}:{self.config.port}"
    
    async def connect(self) -> bool:
        """
        連接到 OBS Studio
        
        Returns:
            bool: 連接是否成功
        """
        if self.is_connected:
            logger.warning("已經連接到 OBS Studio")
            return True
            
        try:
            self.connection_state = ConnectionState.CONNECTING
            logger.info(f"正在連接到 OBS Studio: {self.connection_url}")
            
            # 建立 WebSocket 連接
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.connection_url,
                    extra_headers={"Sec-WebSocket-Protocol": "obswebsocket.json"}
                ),
                timeout=self.config.connection_timeout
            )
            
            # 啟動消息接收任務
            self.receive_task = asyncio.create_task(self._receive_messages())
            
            # 執行握手
            if await self._perform_handshake():
                self.connection_state = ConnectionState.CONNECTED
                self.stats['connected_time'] = time.time()
                logger.info("✅ 成功連接到 OBS Studio")
                
                # 啟動心跳檢測
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # 觸發連接事件
                await self._trigger_event('ConnectionOpened', {})
                
                return True
            else:
                await self.disconnect()
                return False
                
        except asyncio.TimeoutError:
            self.connection_state = ConnectionState.ERROR
            self.stats['last_error'] = "連接超時"
            logger.error("❌ 連接 OBS Studio 超時")
            return False
            
        except InvalidURI:
            self.connection_state = ConnectionState.ERROR  
            self.stats['last_error'] = "無效的連接地址"
            logger.error(f"❌ 無效的 OBS WebSocket 地址: {self.connection_url}")
            return False
            
        except Exception as e:
            self.connection_state = ConnectionState.ERROR
            self.stats['last_error'] = str(e)
            logger.error(f"❌ 連接 OBS Studio 失敗: {e}")
            return False
    
    async def disconnect(self):
        """斷開連接"""
        logger.info("正在斷開 OBS Studio 連接...")
        
        # 取消任務
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
            
        if self.receive_task:
            self.receive_task.cancel()
            self.receive_task = None
        
        # 關閉 WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        self.connection_state = ConnectionState.DISCONNECTED
        logger.info("✅ 已斷開 OBS Studio 連接")
        
        # 觸發斷開事件
        await self._trigger_event('ConnectionClosed', {})
    
    async def send_request(self, request_type: str, request_data: Dict = None, timeout: int = 5) -> Dict:
        """
        發送請求到 OBS
        
        Args:
            request_type: 請求類型
            request_data: 請求數據
            timeout: 超時時間
            
        Returns:
            Dict: 響應數據
        """
        if not self.is_connected:
            raise ConnectionError("未連接到 OBS Studio")
            
        request_id = str(self.request_id_counter)
        self.request_id_counter += 1
        
        request = {
            "op": 6,  # Request
            "d": {
                "requestType": request_type,
                "requestId": request_id,
                "requestData": request_data or {}
            }
        }
        
        # 創建 Future 等待響應
        future = asyncio.Future()
        self.request_handlers[request_id] = future
        
        try:
            # 發送請求
            await self.websocket.send(json.dumps(request))
            self.stats['messages_sent'] += 1
            logger.debug(f"發送請求: {request_type}")
            
            # 等待響應
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"請求超時: {request_type}")
            raise
        finally:
            # 清理請求處理器
            self.request_handlers.pop(request_id, None)
    
    def on_event(self, event_type: str, handler: Callable):
        """
        註冊事件處理器
        
        Args:
            event_type: 事件類型
            handler: 處理函數
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"註冊事件處理器: {event_type}")
    
    async def _perform_handshake(self) -> bool:
        """執行 WebSocket 握手"""
        try:
            # 等待 Hello 消息
            hello_message = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=5
            )
            
            hello_data = json.loads(hello_message)
            if hello_data.get("op") != 0:  # Hello
                logger.error("未收到 Hello 消息")
                return False
                
            # 發送 Identify 消息
            identify_message = {
                "op": 1,  # Identify
                "d": {
                    "rpcVersion": 1,
                    "authentication": self.config.password if self.config.password else None,
                    "eventSubscriptions": 33  # 訂閱所有事件
                }
            }
            
            await self.websocket.send(json.dumps(identify_message))
            
            # 等待 Identified 消息
            identified_message = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=5
            )
            
            identified_data = json.loads(identified_message)
            if identified_data.get("op") != 2:  # Identified
                logger.error("握手失敗")
                return False
                
            logger.info("✅ WebSocket 握手成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 握手失敗: {e}")
            return False
    
    async def _receive_messages(self):
        """接收消息的後台任務"""
        try:
            while self.websocket and not self.websocket.closed:
                try:
                    message = await self.websocket.recv()
                    self.stats['messages_received'] += 1
                    await self._handle_message(json.loads(message))
                    
                except ConnectionClosed:
                    logger.warning("WebSocket 連接已關閉")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"解析消息失敗: {e}")
                except Exception as e:
                    logger.error(f"處理消息時出錯: {e}")
                    
        except Exception as e:
            logger.error(f"接收消息任務出錯: {e}")
        
        # 如果配置了自動重連，嘗試重連
        if self.config.auto_reconnect and self.connection_state != ConnectionState.DISCONNECTED:
            asyncio.create_task(self._auto_reconnect())
    
    async def _handle_message(self, message: Dict):
        """處理接收到的消息"""
        op_code = message.get("op")
        
        if op_code == 5:  # Event
            event_data = message.get("d", {})
            event_type = event_data.get("eventType")
            await self._trigger_event(event_type, event_data.get("eventData", {}))
            
        elif op_code == 7:  # RequestResponse
            response_data = message.get("d", {})
            request_id = response_data.get("requestId")
            
            if request_id in self.request_handlers:
                future = self.request_handlers[request_id]
                if not future.done():
                    future.set_result(response_data)
    
    async def _trigger_event(self, event_type: str, event_data: Dict):
        """觸發事件處理器"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                except Exception as e:
                    logger.error(f"事件處理器出錯 ({event_type}): {e}")
    
    async def _heartbeat_loop(self):
        """心跳檢測循環"""
        try:
            while self.is_connected:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if self.is_connected:
                    try:
                        await self.send_request("GetVersion", timeout=3)
                        logger.debug("💓 心跳檢測正常")
                    except Exception as e:
                        logger.warning(f"❤️‍🩹 心跳檢測失敗: {e}")
                        break
                        
        except asyncio.CancelledError:
            logger.debug("心跳任務已取消")
        except Exception as e:
            logger.error(f"心跳檢測出錯: {e}")
    
    async def _auto_reconnect(self):
        """自動重連"""
        if self.connection_state == ConnectionState.RECONNECTING:
            return
            
        self.connection_state = ConnectionState.RECONNECTING
        self.stats['reconnection_count'] += 1
        
        logger.info(f"🔄 開始自動重連 (第 {self.stats['reconnection_count']} 次)")
        
        while self.config.auto_reconnect and not self.is_connected:
            try:
                await asyncio.sleep(self.config.reconnect_interval)
                
                if await self.connect():
                    logger.info("✅ 自動重連成功")
                    return
                else:
                    logger.warning("❌ 自動重連失敗，繼續嘗試...")
                    
            except Exception as e:
                logger.error(f"自動重連出錯: {e}")
                await asyncio.sleep(self.config.reconnect_interval)
    
    def get_connection_stats(self) -> Dict:
        """獲取連接統計信息"""
        stats = self.stats.copy()
        stats['connection_state'] = self.connection_state.value
        stats['uptime'] = time.time() - self.stats['connected_time'] if self.stats['connected_time'] else 0
        return stats


# 便捷函數和別名
# 為兼容性提供 OBSManager 別名
OBSManager = OBSWebSocketManager

async def create_obs_connection(host: str = "localhost", port: int = 4455, password: str = "") -> OBSWebSocketManager:
    """
    創建並連接 OBS WebSocket 管理器
    
    Args:
        host: OBS 主機地址
        port: WebSocket 端口
        password: 連接密碼
        
    Returns:
        OBSWebSocketManager: 已連接的管理器實例
    """
    config = OBSConfig(host=host, port=port, password=password)
    manager = OBSWebSocketManager(config)
    
    if await manager.connect():
        return manager
    else:
        raise ConnectionError("無法連接到 OBS Studio")


if __name__ == "__main__":
    # 測試代碼
    async def test_obs_connection():
        try:
            manager = await create_obs_connection()
            
            # 測試獲取版本信息
            version_info = await manager.send_request("GetVersion")
            print(f"OBS 版本: {version_info}")
            
            # 獲取連接統計
            stats = manager.get_connection_stats()
            print(f"連接統計: {stats}")
            
            await manager.disconnect()
            
        except Exception as e:
            print(f"測試失敗: {e}")
            traceback.print_exc()
    
    # 運行測試
    if websockets:
        asyncio.run(test_obs_connection())
    else:
        print("請安裝 websockets 套件來運行測試")
