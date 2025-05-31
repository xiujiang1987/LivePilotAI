"""
LivePilotAI - 核心 AI 引擎基礎架構
提供統一的 AI 處理接口和管理框架
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import asyncio
from enum import Enum
from dataclasses import dataclass
import time


class EngineState(Enum):
    """AI引擎狀態枚舉"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ProcessingResult:
    """AI處理結果數據類"""
    success: bool
    data: Dict[str, Any]
    timestamp: float
    processing_time: float
    error_message: Optional[str] = None


class AIEngineBase(ABC):
    """AI引擎基礎抽象類"""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.state = EngineState.IDLE
        self.logger = logging.getLogger(f"AIEngine.{engine_id}")
        self._last_result: Optional[ProcessingResult] = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化引擎，載入模型和資源"""
        pass
        
    @abstractmethod
    async def process(self, input_data: Any) -> ProcessingResult:
        """處理輸入數據並返回結果"""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """清理資源"""
        pass
        
    def get_state(self) -> EngineState:
        """獲取當前引擎狀態"""
        return self.state
        
    def get_last_result(self) -> Optional[ProcessingResult]:
        """獲取最後一次處理結果"""
        return self._last_result


class AIEngineManager:
    """AI引擎管理器 - 統一管理所有AI引擎"""
    
    def __init__(self):
        self.engines: Dict[str, AIEngineBase] = {}
        self.logger = logging.getLogger("AIEngineManager")
        self._running = False
        
    async def register_engine(self, engine: AIEngineBase) -> bool:
        """註冊AI引擎"""
        try:
            if engine.engine_id in self.engines:
                self.logger.warning(f"引擎 {engine.engine_id} 已存在，將被覆蓋")
                
            # 初始化引擎
            if await engine.initialize():
                self.engines[engine.engine_id] = engine
                self.logger.info(f"成功註冊引擎: {engine.engine_id}")
                return True
            else:
                self.logger.error(f"引擎初始化失敗: {engine.engine_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"註冊引擎失敗 {engine.engine_id}: {e}")
            return False
            
    async def unregister_engine(self, engine_id: str) -> bool:
        """註銷AI引擎"""
        if engine_id in self.engines:
            try:
                await self.engines[engine_id].cleanup()
                del self.engines[engine_id]
                self.logger.info(f"成功註銷引擎: {engine_id}")
                return True
            except Exception as e:
                self.logger.error(f"註銷引擎失敗 {engine_id}: {e}")
                return False
        else:
            self.logger.warning(f"引擎不存在: {engine_id}")
            return False
            
    async def process_with_engine(self, engine_id: str, input_data: Any) -> ProcessingResult:
        """使用指定引擎處理數據"""
        if engine_id not in self.engines:
            return ProcessingResult(
                success=False,
                data={},
                timestamp=time.time(),
                processing_time=0,
                error_message=f"引擎不存在: {engine_id}"
            )
            
        try:
            engine = self.engines[engine_id]
            if engine.get_state() == EngineState.ERROR:
                return ProcessingResult(
                    success=False,
                    data={},
                    timestamp=time.time(),
                    processing_time=0,
                    error_message=f"引擎處於錯誤狀態: {engine_id}"
                )
                
            result = await engine.process(input_data)
            return result
            
        except Exception as e:
            self.logger.error(f"引擎處理失敗 {engine_id}: {e}")
            return ProcessingResult(
                success=False,
                data={},                timestamp=time.time(),
                processing_time=0,
                error_message=str(e)
            )
            
    def get_engine_status(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有引擎狀態"""
        status = {}
        for engine_id, engine in self.engines.items():
            engine_state = engine.get_state()
            state_value = engine_state.value if hasattr(engine_state, 'value') else str(engine_state)
            
            status[engine_id] = {
                "state": state_value,
                "last_result": engine.get_last_result(),
                "config": engine.config
            }
        return status
        
    def get_available_engines(self) -> List[str]:
        """獲取可用引擎列表"""
        return [
            engine_id for engine_id, engine in self.engines.items()
            if engine.get_state() not in [EngineState.ERROR, EngineState.STOPPED]
        ]
        
    async def start_all_engines(self) -> None:
        """啟動所有引擎"""
        self._running = True
        self.logger.info("啟動所有AI引擎")
        
        for engine_id, engine in self.engines.items():
            try:
                if engine.get_state() == EngineState.IDLE:
                    await engine.initialize()
                    self.logger.info(f"引擎 {engine_id} 已啟動")
            except Exception as e:
                self.logger.error(f"啟動引擎失敗 {engine_id}: {e}")
                
    async def stop_all_engines(self) -> None:
        """停止所有引擎"""
        self._running = False
        self.logger.info("停止所有AI引擎")
        
        for engine_id, engine in self.engines.items():
            try:
                await engine.cleanup()
                self.logger.info(f"引擎 {engine_id} 已停止")
            except Exception as e:
                self.logger.error(f"停止引擎失敗 {engine_id}: {e}")
                
    def is_running(self) -> bool:
        """檢查管理器是否正在運行"""
        return self._running


# 全局AI引擎管理器實例
ai_manager = AIEngineManager()
