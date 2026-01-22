"""
websocket_client.py - Enhanced WebSocket Client Wrapper

This module provides a robust WebSocket client wrapper with connection management,
message handling, and integration with the OBS Manager for real-time communication.

Author: LivePilotAI Development Team
Date: 2024-12-19
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, Callable, List, Union, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidMessage
import ssl


class MessageType(Enum):
    """WebSocket message types"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class ClientState(Enum):
    """WebSocket client connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSING = "closing"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    message_type: MessageType
    data: Dict[str, Any]
    message_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None


@dataclass
class ConnectionConfig:
    """WebSocket connection configuration"""
    host: str = "localhost"
    port: int = 4455
    password: Optional[str] = None
    protocol: str = "ws"
    path: str = "/"
    
    # Connection settings
    connect_timeout: float = 10.0
    heartbeat_interval: float = 30.0
    response_timeout: float = 5.0
    max_reconnect_attempts: int = 5
    reconnect_delay: float = 2.0
    reconnect_backoff: float = 1.5
    
    # SSL settings
    use_ssl: bool = False
    ssl_context: Optional[ssl.SSLContext] = None
    
    # Message settings
    max_message_size: int = 1024 * 1024  # 1MB
    compression: Optional[str] = None


@dataclass
class ConnectionStats:
    """Connection statistics"""
    connect_time: Optional[float] = None
    disconnect_time: Optional[float] = None
    total_connections: int = 0
    reconnect_attempts: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_heartbeat: Optional[float] = None
    errors: List[str] = field(default_factory=list)


class WebSocketClient:
    """
    Enhanced WebSocket client with robust connection management and OBS integration
    """
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or ConnectionConfig()
        
        # Connection state
        self.state = ClientState.DISCONNECTED
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.stats = ConnectionStats()
        
        # Message handling
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        # Connection management
        self.reconnect_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.message_handler_task: Optional[asyncio.Task] = None
        self.connection_lock = asyncio.Lock()
        
        # Callbacks
        self.state_change_callbacks: List[Callable[[ClientState, ClientState], None]] = []
        self.error_callbacks: List[Callable[[Exception], None]] = []
        
        self.logger.info("WebSocketClient initialized")
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.state == ClientState.CONNECTED and self.websocket is not None
    
    @property
    def connection_url(self) -> str:
        """Get the WebSocket connection URL"""
        protocol = "wss" if self.config.use_ssl else "ws"
        return f"{protocol}://{self.config.host}:{self.config.port}{self.config.path}"
    
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        async with self.connection_lock:
            if self.state in [ClientState.CONNECTING, ClientState.CONNECTED]:
                return self.is_connected
            
            try:
                self._change_state(ClientState.CONNECTING)
                self.logger.info(f"Connecting to {self.connection_url}")                # Prepare connection parameters  
                extra_headers = {}
                if self.config.password:
                    extra_headers["Authorization"] = f"Bearer {self.config.password}"
                  # Establish WebSocket connection with version compatibility
                try:
                    # Try new parameter name first (websockets >= 12.0)
                    self.websocket = await asyncio.wait_for(
                        websockets.connect(
                            self.connection_url,
                            extra_headers=extra_headers,
                            ssl=self.config.ssl_context if self.config.use_ssl else None,
                            max_size=self.config.max_message_size,
                            compression=self.config.compression,
                            ping_interval=None,  # We handle heartbeat manually
                            ping_timeout=None
                        ),
                        timeout=self.config.connect_timeout
                    )
                except TypeError:
                    # Fall back to old parameter name (websockets < 12.0)
                    self.websocket = await asyncio.wait_for(
                        websockets.connect(
                            self.connection_url,
                            extra_headers=extra_headers,
                            ssl=self.config.ssl_context if self.config.use_ssl else None,
                            max_size=self.config.max_message_size,
                            compression=self.config.compression,
                            ping_interval=None,  # We handle heartbeat manually
                            ping_timeout=None
                        ),
                        timeout=self.config.connect_timeout
                    )
                
                # Update statistics
                self.stats.connect_time = time.time()
                self.stats.total_connections += 1
                self.stats.reconnect_attempts = 0
                
                # Change state and start background tasks
                self._change_state(ClientState.CONNECTED)
                await self._start_background_tasks()
                
                self.logger.info("WebSocket connection established")
                return True
                
            except asyncio.TimeoutError:
                self.logger.error("Connection timeout")
                self._change_state(ClientState.ERROR)
                self._record_error("Connection timeout")
                return False
                
            except (ConnectionClosed, InvalidURI, OSError) as e:
                self.logger.error(f"Connection failed: {e}")
                self._change_state(ClientState.ERROR)
                self._record_error(f"Connection failed: {str(e)}")
                return False
                
            except Exception as e:
                self.logger.error(f"Unexpected connection error: {e}")
                self._change_state(ClientState.ERROR)
                self._record_error(f"Unexpected error: {str(e)}")
                return False
    
    async def disconnect(self, graceful: bool = True) -> None:
        """Disconnect from WebSocket server"""
        async with self.connection_lock:
            if self.state == ClientState.DISCONNECTED:
                return
            
            try:
                self._change_state(ClientState.CLOSING)
                
                # Stop background tasks
                await self._stop_background_tasks()
                
                # Close WebSocket connection
                if self.websocket:
                    if graceful:
                        await asyncio.wait_for(
                            self.websocket.close(),
                            timeout=5.0
                        )
                    else:
                        await self.websocket.close()
                    
                    self.websocket = None
                
                # Cancel pending requests
                for future in self.pending_requests.values():
                    if not future.done():
                        future.cancel()
                self.pending_requests.clear()
                
                # Update statistics
                self.stats.disconnect_time = time.time()
                
                self._change_state(ClientState.DISCONNECTED)
                self.logger.info("WebSocket disconnected")
                
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
                self._change_state(ClientState.ERROR)
    
    async def send_message(self, message: WebSocketMessage) -> Optional[str]:
        """Send a message through WebSocket"""
        if not self.is_connected:
            raise ConnectionError("WebSocket not connected")
        
        try:
            # Generate message ID if not provided
            if not message.message_id:
                message.message_id = str(uuid.uuid4())
            
            # Prepare message data
            message_data = {
                'messageType': message.message_type.value,
                'messageId': message.message_id,
                'timestamp': message.timestamp,
                'data': message.data
            }
            
            if message.correlation_id:
                message_data['correlationId'] = message.correlation_id
            
            # Send message
            message_json = json.dumps(message_data)
            await self.websocket.send(message_json)
            
            # Update statistics
            self.stats.messages_sent += 1
            self.stats.bytes_sent += len(message_json.encode())
            
            self.logger.debug(f"Sent message: {message.message_type.value} ({message.message_id})")
            return message.message_id
            
        except ConnectionClosed:
            self.logger.error("Connection closed while sending message")
            await self._handle_connection_loss()
            raise
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self._record_error(f"Send error: {str(e)}")
            raise
    
    async def send_request(self, request_data: Dict[str, Any], 
                          timeout: Optional[float] = None) -> Dict[str, Any]:
        """Send a request and wait for response"""
        if not self.is_connected:
            raise ConnectionError("WebSocket not connected")
        
        message_id = str(uuid.uuid4())
        timeout = timeout or self.config.response_timeout
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[message_id] = response_future
        
        try:
            # Send request
            message = WebSocketMessage(
                message_type=MessageType.REQUEST,
                data=request_data,
                message_id=message_id
            )
            
            await self.send_message(message)
            
            # Wait for response
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout: {message_id}")
            raise
            
        finally:
            # Clean up pending request
            self.pending_requests.pop(message_id, None)
    
    async def send_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Send an event message"""
        message = WebSocketMessage(
            message_type=MessageType.EVENT,
            data={
                'eventName': event_name,
                'eventData': event_data
            }
        )
        await self.send_message(message)
    
    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """Add event handler for specific event type"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Added event handler for: {event_name}")
    
    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """Remove event handler"""
        if event_name in self.event_handlers:
            if handler in self.event_handlers[event_name]:
                self.event_handlers[event_name].remove(handler)
                self.logger.debug(f"Removed event handler for: {event_name}")
    
    def add_state_change_callback(self, callback: Callable[[ClientState, ClientState], None]) -> None:
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Add callback for errors"""
        self.error_callbacks.append(callback)
    
    async def _start_background_tasks(self) -> None:
        """Start background tasks for message handling and heartbeat"""
        try:
            # Start message handler
            self.message_handler_task = asyncio.create_task(self._message_handler())
            
            # Start heartbeat
            if self.config.heartbeat_interval > 0:
                self.heartbeat_task = asyncio.create_task(self._heartbeat_handler())
            
            self.logger.debug("Background tasks started")
            
        except Exception as e:
            self.logger.error(f"Error starting background tasks: {e}")
    
    async def _stop_background_tasks(self) -> None:
        """Stop all background tasks"""
        tasks = [self.message_handler_task, self.heartbeat_task, self.reconnect_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.message_handler_task = None
        self.heartbeat_task = None
        self.reconnect_task = None
        
        self.logger.debug("Background tasks stopped")
    
    async def _message_handler(self) -> None:
        """Handle incoming WebSocket messages"""
        try:
            while self.is_connected and self.websocket:
                try:
                    # Receive message
                    raw_message = await self.websocket.recv()
                    
                    # Update statistics
                    self.stats.messages_received += 1
                    self.stats.bytes_received += len(raw_message.encode() if isinstance(raw_message, str) else raw_message)
                    
                    # Parse message
                    message_data = json.loads(raw_message)
                    await self._process_message(message_data)
                    
                except ConnectionClosed:
                    self.logger.warning("WebSocket connection closed")
                    await self._handle_connection_loss()
                    break
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON message: {e}")
                    self._record_error(f"JSON decode error: {str(e)}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    self._record_error(f"Message processing error: {str(e)}")
                    
        except asyncio.CancelledError:
            self.logger.debug("Message handler cancelled")
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")
    
    async def _process_message(self, message_data: Dict[str, Any]) -> None:
        """Process received WebSocket message"""
        try:
            message_type = MessageType(message_data.get('messageType', 'unknown'))
            message_id = message_data.get('messageId')
            data = message_data.get('data', {})
            
            if message_type == MessageType.RESPONSE:
                # Handle response to pending request
                if message_id in self.pending_requests:
                    future = self.pending_requests[message_id]
                    if not future.done():
                        future.set_result(data)
            
            elif message_type == MessageType.EVENT:
                # Handle event
                event_name = data.get('eventName')
                event_data = data.get('eventData', {})
                
                if event_name and event_name in self.event_handlers:
                    for handler in self.event_handlers[event_name]:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event_data)
                            else:
                                handler(event_data)
                        except Exception as e:
                            self.logger.error(f"Error in event handler: {e}")
            
            elif message_type == MessageType.HEARTBEAT:
                # Handle heartbeat response
                self.stats.last_heartbeat = time.time()
                self.logger.debug("Heartbeat received")
            
            elif message_type == MessageType.ERROR:
                # Handle error message
                error_msg = data.get('message', 'Unknown error')
                self.logger.error(f"Server error: {error_msg}")
                self._record_error(f"Server error: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _heartbeat_handler(self) -> None:
        """Send periodic heartbeat messages"""
        try:
            while self.is_connected:
                try:
                    heartbeat_message = WebSocketMessage(
                        message_type=MessageType.HEARTBEAT,
                        data={'timestamp': time.time()}
                    )
                    
                    await self.send_message(heartbeat_message)
                    self.logger.debug("Heartbeat sent")
                    
                    await asyncio.sleep(self.config.heartbeat_interval)
                    
                except Exception as e:
                    self.logger.error(f"Heartbeat error: {e}")
                    break
                    
        except asyncio.CancelledError:
            self.logger.debug("Heartbeat handler cancelled")
    
    async def _handle_connection_loss(self) -> None:
        """Handle unexpected connection loss"""
        if self.state not in [ClientState.CLOSING, ClientState.DISCONNECTED]:
            self.logger.warning("Connection lost, attempting reconnection")
            self._change_state(ClientState.RECONNECTING)
            
            # Start reconnection task
            if not self.reconnect_task or self.reconnect_task.done():
                self.reconnect_task = asyncio.create_task(self._reconnect_handler())
    
    async def _reconnect_handler(self) -> None:
        """Handle automatic reconnection"""
        try:
            delay = self.config.reconnect_delay
            max_attempts = self.config.max_reconnect_attempts
            
            for attempt in range(max_attempts):
                if self.state != ClientState.RECONNECTING:
                    break
                
                self.logger.info(f"Reconnection attempt {attempt + 1}/{max_attempts}")
                self.stats.reconnect_attempts += 1
                
                try:
                    success = await self.connect()
                    if success:
                        self.logger.info("Reconnection successful")
                        return
                        
                except Exception as e:
                    self.logger.error(f"Reconnection failed: {e}")
                
                # Wait before next attempt with exponential backoff
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)
                    delay *= self.config.reconnect_backoff
            
            # All reconnection attempts failed
            self.logger.error("All reconnection attempts failed")
            self._change_state(ClientState.ERROR)
            
        except asyncio.CancelledError:
            self.logger.debug("Reconnection handler cancelled")
    
    def _change_state(self, new_state: ClientState) -> None:
        """Change client state and notify callbacks"""
        old_state = self.state
        self.state = new_state
        
        self.logger.debug(f"State changed: {old_state.value} -> {new_state.value}")
        
        # Notify callbacks
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
    def _record_error(self, error_message: str) -> None:
        """Record error in statistics"""
        self.stats.errors.append(f"{time.time()}: {error_message}")
        
        # Limit error history size
        if len(self.stats.errors) > 100:
            self.stats.errors = self.stats.errors[-50:]
        
        # Notify error callbacks
        for callback in self.error_callbacks:
            try:
                callback(Exception(error_message))
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        current_time = time.time()
        
        uptime = None
        if self.stats.connect_time and self.state == ClientState.CONNECTED:
            uptime = current_time - self.stats.connect_time
        
        return {
            'state': self.state.value,
            'is_connected': self.is_connected,
            'connection_url': self.connection_url,
            'uptime_seconds': uptime,
            'total_connections': self.stats.total_connections,
            'reconnect_attempts': self.stats.reconnect_attempts,
            'messages_sent': self.stats.messages_sent,
            'messages_received': self.stats.messages_received,
            'bytes_sent': self.stats.bytes_sent,
            'bytes_received': self.stats.bytes_received,
            'last_heartbeat': self.stats.last_heartbeat,
            'pending_requests': len(self.pending_requests),
            'event_handlers': {name: len(handlers) for name, handlers in self.event_handlers.items()},
            'recent_errors': self.stats.errors[-10:] if self.stats.errors else []
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Integration helper for OBS Manager
class OBSWebSocketClient(WebSocketClient):
    """
    Specialized WebSocket client for OBS Studio integration
    """
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: Optional[str] = None):
        config = ConnectionConfig(
            host=host,
            port=port,
            password=password,
            heartbeat_interval=30.0,
            response_timeout=10.0
        )
        super().__init__(config)
        
        # OBS-specific state
        self.obs_version: Optional[str] = None
        self.supported_requests: List[str] = []
        self.session_authenticated: bool = False
    
    async def authenticate(self) -> bool:
        """Authenticate with OBS WebSocket server"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Send identify request
            identify_request = {
                'requestType': 'GetVersion',
                'requestId': str(uuid.uuid4())
            }
            
            response = await self.send_request(identify_request)
            
            if response.get('requestStatus', {}).get('result'):
                self.obs_version = response.get('responseData', {}).get('obsVersion')
                self.session_authenticated = True
                self.logger.info(f"Authenticated with OBS {self.obs_version}")
                return True
            else:
                self.logger.error("OBS authentication failed")
                return False
                
        except Exception as e:
            self.logger.error(f"OBS authentication error: {e}")
            return False
    
    async def send_obs_request(self, request_type: str, request_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send OBS-specific request"""
        obs_request = {
            'requestType': request_type,
            'requestId': str(uuid.uuid4())
        }
        
        if request_data:
            obs_request['requestData'] = request_data
        
        return await self.send_request(obs_request)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_websocket_client():
        """Test the WebSocket client functionality"""
        print("Testing WebSocketClient...")
        
        # Create client with test configuration
        config = ConnectionConfig(
            host="localhost",
            port=4455,
            heartbeat_interval=10.0
        )
        
        client = WebSocketClient(config)
        
        # Add event handlers
        def on_state_change(old_state, new_state):
            print(f"State changed: {old_state.value} -> {new_state.value}")
        
        def on_error(error):
            print(f"Error occurred: {error}")
        
        client.add_state_change_callback(on_state_change)
        client.add_error_callback(on_error)
        
        try:
            # Test connection
            print("Attempting to connect...")
            connected = await client.connect()
            print(f"Connection result: {connected}")
            
            if connected:
                # Test message sending
                test_message = WebSocketMessage(
                    message_type=MessageType.EVENT,
                    data={'test': 'Hello, WebSocket!'}
                )
                
                message_id = await client.send_message(test_message)
                print(f"Sent test message: {message_id}")
                
                # Show statistics
                stats = client.get_statistics()
                print(f"Connection statistics: {stats}")
                
                # Wait a bit
                await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Test error: {e}")
        
        finally:
            # Disconnect
            await client.disconnect()
            print("Disconnected")
    
    # Test OBS client
    async def test_obs_client():
        """Test OBS WebSocket client"""
        print("\nTesting OBSWebSocketClient...")
        
        obs_client = OBSWebSocketClient()
        
        try:
            # Test authentication
            authenticated = await obs_client.authenticate()
            print(f"OBS Authentication: {authenticated}")
            
            if authenticated:
                # Test OBS request
                version_response = await obs_client.send_obs_request('GetVersion')
                print(f"OBS Version: {version_response}")
                
        except Exception as e:
            print(f"OBS test error: {e}")
        
        finally:
            await obs_client.disconnect()
    
    # Run tests
    asyncio.run(test_websocket_client())
    asyncio.run(test_obs_client())
