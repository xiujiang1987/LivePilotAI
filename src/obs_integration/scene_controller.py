#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI OBS 場景控制器
Day 5 核心模組 - 智能場景切換與控制
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .obs_manager import OBSWebSocketManager

# 設置日誌
logger = logging.getLogger(__name__)


class TransitionType(Enum):
    """轉場效果類型"""
    CUT = "Cut"
    FADE = "Fade"
    SLIDE = "Slide"
    STINGER = "Stinger"
    SWIPE = "Swipe"
    LUMA_WIPE = "Luma Wipe"


@dataclass
class SceneConfig:
    """場景配置"""
    name: str
    display_name: str = ""
    description: str = ""
    auto_switch: bool = True
    priority: int = 0
    min_duration: float = 2.0  # 最小停留時間(秒)
    emotion_triggers: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class TransitionConfig:
    """轉場配置"""
    transition_type: TransitionType = TransitionType.FADE
    duration: int = 500  # 毫秒
    settings: Dict[str, Any] = field(default_factory=dict)


class SceneController:
    """
    OBS 場景控制器
    
    負責管理 OBS 場景的智能切換，包括：
    - 場景列表管理
    - 自動/手動場景切換
    - 轉場效果控制
    - 場景狀態監控
    - 切換邏輯管理
    """
    
    def __init__(self, obs_manager: OBSWebSocketManager):
        self.obs_manager = obs_manager
        self.scenes: Dict[str, SceneConfig] = {}
        self.current_scene = None
        self.previous_scene = None
        self.scene_history: List[Dict] = []
        self.auto_switch_enabled = True
        self.last_switch_time = 0
        self.switch_cooldown = 1.0  # 切換冷卻時間(秒)
        self.transition_config = TransitionConfig()
        
        # 統計信息
        self.stats = {
            'total_switches': 0,
            'auto_switches': 0,
            'manual_switches': 0,
            'failed_switches': 0,
            'average_scene_duration': 0
        }
        
        # 事件處理器
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """設置 OBS 事件處理器"""
        self.obs_manager.on_event('CurrentProgramSceneChanged', self._on_scene_changed)
        self.obs_manager.on_event('SceneListChanged', self._on_scene_list_changed)
        self.obs_manager.on_event('SceneItemEnableStateChanged', self._on_scene_item_changed)
    
    async def initialize(self):
        """初始化場景控制器"""
        try:
            # 獲取場景列表
            await self.refresh_scene_list()
            
            # 獲取當前場景
            current_scene_info = await self.obs_manager.send_request("GetCurrentProgramScene")
            self.current_scene = current_scene_info.get('responseData', {}).get('currentProgramSceneName')
            
            logger.info(f"✅ 場景控制器初始化完成，當前場景: {self.current_scene}")
            
        except Exception as e:
            logger.error(f"❌ 場景控制器初始化失敗: {e}")
            raise
    
    async def refresh_scene_list(self):
        """刷新場景列表"""
        try:
            response = await self.obs_manager.send_request("GetSceneList")
            scene_list = response.get('responseData', {}).get('scenes', [])
            
            # 更新場景配置
            for scene_info in scene_list:
                scene_name = scene_info.get('sceneName')
                if scene_name and scene_name not in self.scenes:
                    self.scenes[scene_name] = SceneConfig(
                        name=scene_name,
                        display_name=scene_name
                    )
            
            logger.info(f"✅ 已刷新場景列表，共 {len(self.scenes)} 個場景")
            
        except Exception as e:
            logger.error(f"❌ 刷新場景列表失敗: {e}")
    
    async def switch_to_scene(self, scene_name: str, transition_override: TransitionConfig = None, force: bool = False) -> bool:
        """
        切換到指定場景
        
        Args:
            scene_name: 目標場景名稱
            transition_override: 覆蓋的轉場配置
            force: 是否強制切換（忽略冷卻時間）
            
        Returns:
            bool: 切換是否成功
        """
        try:
            # 檢查場景是否存在
            if scene_name not in self.scenes:
                logger.warning(f"場景不存在: {scene_name}")
                return False
            
            # 檢查是否為當前場景
            if scene_name == self.current_scene:
                logger.debug(f"已經在場景 {scene_name}")
                return True
            
            # 檢查冷卻時間
            current_time = time.time()
            if not force and (current_time - self.last_switch_time) < self.switch_cooldown:
                logger.debug(f"場景切換冷卻中，剩餘 {self.switch_cooldown - (current_time - self.last_switch_time):.1f} 秒")
                return False
            
            # 檢查最小停留時間
            scene_config = self.scenes[scene_name]
            if not force and self.current_scene and (current_time - self.last_switch_time) < scene_config.min_duration:
                logger.debug(f"未達到場景最小停留時間: {scene_config.min_duration}秒")
                return False
            
            # 設置轉場效果
            transition_config = transition_override or self.transition_config
            await self._set_transition(transition_config)
            
            # 執行場景切換
            await self.obs_manager.send_request("SetCurrentProgramScene", {
                "sceneName": scene_name
            })
            
            # 更新狀態
            self.previous_scene = self.current_scene
            self.current_scene = scene_name
            self.last_switch_time = current_time
            
            # 記錄歷史
            self._record_scene_switch(scene_name, "manual" if force else "auto")
            
            # 更新統計
            self.stats['total_switches'] += 1
            if force:
                self.stats['manual_switches'] += 1
            else:
                self.stats['auto_switches'] += 1
            
            logger.info(f"✅ 成功切換到場景: {scene_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 切換場景失敗 ({scene_name}): {e}")
            self.stats['failed_switches'] += 1
            return False
    
    async def switch_by_emotion(self, emotion: str, confidence: float = 0.0) -> bool:
        """
        根據情感切換場景
        
        Args:
            emotion: 檢測到的情感
            confidence: 情感檢測信心度
            
        Returns:
            bool: 切換是否成功
        """
        if not self.auto_switch_enabled:
            logger.debug("自動場景切換已禁用")
            return False
        
        # 查找匹配的場景
        matching_scenes = []
        for scene_name, scene_config in self.scenes.items():
            if emotion in scene_config.emotion_triggers and scene_config.auto_switch:
                matching_scenes.append((scene_name, scene_config))
        
        if not matching_scenes:
            logger.debug(f"未找到情感 '{emotion}' 對應的場景")
            return False
        
        # 按優先級排序
        matching_scenes.sort(key=lambda x: x[1].priority, reverse=True)
        target_scene = matching_scenes[0][0]
        
        logger.info(f"🎭 情感 '{emotion}' (信心度: {confidence:.2f}) 觸發場景切換: {target_scene}")
        return await self.switch_to_scene(target_scene)
    
    async def get_scene_list(self) -> List[Dict]:
        """獲取場景列表"""
        try:
            response = await self.obs_manager.send_request("GetSceneList")
            return response.get('responseData', {}).get('scenes', [])
        except Exception as e:
            logger.error(f"❌ 獲取場景列表失敗: {e}")
            return []
    
    async def get_current_scene(self) -> Optional[str]:
        """獲取當前場景名稱"""
        try:
            response = await self.obs_manager.send_request("GetCurrentProgramScene")
            return response.get('responseData', {}).get('currentProgramSceneName')
        except Exception as e:
            logger.error(f"❌ 獲取當前場景失敗: {e}")
            return None
    
    def configure_scene(self, scene_name: str, config: SceneConfig):
        """配置場景"""
        self.scenes[scene_name] = config
        logger.info(f"✅ 已配置場景: {scene_name}")
    
    def add_emotion_trigger(self, scene_name: str, emotion: str):
        """為場景添加情感觸發器"""
        if scene_name in self.scenes:
            if emotion not in self.scenes[scene_name].emotion_triggers:
                self.scenes[scene_name].emotion_triggers.append(emotion)
                logger.info(f"✅ 為場景 '{scene_name}' 添加情感觸發: {emotion}")
        else:
            logger.warning(f"場景不存在: {scene_name}")
    
    def remove_emotion_trigger(self, scene_name: str, emotion: str):
        """移除場景的情感觸發器"""
        if scene_name in self.scenes and emotion in self.scenes[scene_name].emotion_triggers:
            self.scenes[scene_name].emotion_triggers.remove(emotion)
            logger.info(f"✅ 已移除場景 '{scene_name}' 的情感觸發: {emotion}")
    
    def set_auto_switch(self, enabled: bool):
        """設置自動切換開關"""
        self.auto_switch_enabled = enabled
        logger.info(f"✅ 自動場景切換: {'啟用' if enabled else '禁用'}")
    
    def set_auto_switching(self, enabled: bool):
        """設置自動切換開關 (別名方法，與 main_day5.py 兼容)"""
        return self.set_auto_switch(enabled)
    
    def set_transition_config(self, config: TransitionConfig):
        """設置轉場配置"""
        self.transition_config = config
        logger.info(f"✅ 已設置轉場配置: {config.transition_type.value}")
    
    async def _set_transition(self, config: TransitionConfig):
        """設置 OBS 轉場效果"""
        try:
            # 設置當前轉場
            await self.obs_manager.send_request("SetCurrentSceneTransition", {
                "transitionName": config.transition_type.value
            })
            
            # 設置轉場持續時間
            await self.obs_manager.send_request("SetCurrentSceneTransitionDuration", {
                "transitionDuration": config.duration
            })
            
            # 如果有自定義設置，應用它們
            if config.settings:
                await self.obs_manager.send_request("SetCurrentSceneTransitionSettings", {
                    "transitionSettings": config.settings
                })
            
        except Exception as e:
            logger.warning(f"設置轉場效果失敗: {e}")
    
    def _record_scene_switch(self, scene_name: str, switch_type: str):
        """記錄場景切換歷史"""
        switch_record = {
            'timestamp': time.time(),
            'scene_name': scene_name,
            'previous_scene': self.previous_scene,
            'switch_type': switch_type
        }
        
        self.scene_history.append(switch_record)
        
        # 保持歷史記錄在合理範圍內
        if len(self.scene_history) > 100:
            self.scene_history = self.scene_history[-50:]
    
    async def _on_scene_changed(self, event_data: Dict):
        """場景變更事件處理器"""
        scene_name = event_data.get('sceneName')
        if scene_name:
            self.current_scene = scene_name
            logger.info(f"🎬 場景已變更: {scene_name}")
    
    async def _on_scene_list_changed(self, event_data: Dict):
        """場景列表變更事件處理器"""
        logger.info("📝 場景列表已變更，正在刷新...")
        await self.refresh_scene_list()
    
    async def _on_scene_item_changed(self, event_data: Dict):
        """場景項目變更事件處理器"""
        logger.debug(f"🔧 場景項目狀態變更: {event_data}")
    
    def get_scene_stats(self) -> Dict:
        """獲取場景統計信息"""
        stats = self.stats.copy()
        stats['current_scene'] = self.current_scene
        stats['total_scenes'] = len(self.scenes)
        stats['auto_switch_enabled'] = self.auto_switch_enabled
        stats['recent_switches'] = self.scene_history[-10:] if self.scene_history else []
        
        # 計算平均場景停留時間
        if len(self.scene_history) > 1:
            durations = []
            for i in range(1, len(self.scene_history)):
                duration = self.scene_history[i]['timestamp'] - self.scene_history[i-1]['timestamp']
                durations.append(duration)
            stats['average_scene_duration'] = sum(durations) / len(durations) if durations else 0
        
        return stats
    
    def get_scene_configs(self) -> Dict[str, SceneConfig]:
        """獲取所有場景配置"""
        return self.scenes.copy()


# 預設場景配置範本
DEFAULT_SCENE_CONFIGS = {
    "開心場景": SceneConfig(
        name="開心場景",
        display_name="🌟 開心時光",
        description="檢測到快樂情感時的場景",
        emotion_triggers=["happy", "joy"],
        priority=3,
        min_duration=3.0
    ),
    "專注場景": SceneConfig(
        name="專注場景", 
        display_name="🎯 專注模式",
        description="中性或專注狀態的場景",
        emotion_triggers=["neutral", "focused"],
        priority=1,
        min_duration=5.0
    ),
    "互動場景": SceneConfig(
        name="互動場景",
        display_name="💬 互動時間",
        description="驚訝或興奮時的互動場景",
        emotion_triggers=["surprise", "excited"],
        priority=2,
        min_duration=2.0
    ),
    "冷靜場景": SceneConfig(
        name="冷靜場景",
        display_name="😌 冷靜時光",
        description="悲傷或需要冷靜時的場景",
        emotion_triggers=["sad", "calm"],
        priority=2,
        min_duration=4.0
    )
}


async def create_scene_controller(obs_manager: OBSWebSocketManager, use_defaults: bool = True) -> SceneController:
    """
    創建並初始化場景控制器
    
    Args:
        obs_manager: OBS WebSocket 管理器
        use_defaults: 是否使用預設場景配置
        
    Returns:
        SceneController: 已初始化的場景控制器
    """
    controller = SceneController(obs_manager)
    await controller.initialize()
    
    if use_defaults:
        for scene_name, config in DEFAULT_SCENE_CONFIGS.items():
            controller.configure_scene(scene_name, config)
    
    return controller


if __name__ == "__main__":
    # 測試代碼
    async def test_scene_controller():
        from .obs_manager import create_obs_connection
        
        try:
            # 創建 OBS 連接
            obs_manager = await create_obs_connection()
            
            # 創建場景控制器
            controller = await create_scene_controller(obs_manager)
            
            # 獲取場景列表
            scenes = await controller.get_scene_list()
            print(f"可用場景: {[s.get('sceneName') for s in scenes]}")
            
            # 獲取當前場景
            current = await controller.get_current_scene()
            print(f"當前場景: {current}")
            
            # 獲取統計信息
            stats = controller.get_scene_stats()
            print(f"場景統計: {stats}")
            
            await obs_manager.disconnect()
            
        except Exception as e:
            print(f"測試失敗: {e}")
            import traceback
            traceback.print_exc()
    
    # 運行測試
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_scene_controller())
