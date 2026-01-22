"""
LivePilotAI OBS場景管理器 - 修正版
處理依賴庫缺失問題，提供降級功能
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum

# 處理OBS庫導入問題
try:
    import obsws_python as obs
    OBS_AVAILABLE = True
    print("✅ obsws_python 已載入")
except ImportError:
    print("⚠️  obsws_python 未安裝，OBS功能將在模擬模式下運行")
    print("   安裝指令: pip install obsws-python")
    obs = None
    OBS_AVAILABLE = False


class LayoutType(Enum):
    """佈局類型枚舉"""
    GAMING = "gaming"
    CHATTING = "chatting"
    SHOWCASE = "showcase"
    MINIMAL = "minimal"
    HIGH_ENERGY = "high_energy"
    FOCUSED = "focused"


class EmotionState(Enum):
    """情緒狀態枚舉"""
    EXCITED = "excited"
    FOCUSED = "focused"
    RELAXED = "relaxed"
    INTERACTIVE = "interactive"
    NEUTRAL = "neutral"


@dataclass
class SceneElement:
    """場景元素配置"""
    name: str
    source_type: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    visible: bool = True
    opacity: float = 1.0
    filters: List[str] = field(default_factory=list)


@dataclass
class LayoutConfig:
    """佈局配置"""
    name: str
    layout_type: LayoutType
    canvas_size: Tuple[int, int]
    elements: List[SceneElement]
    transition_duration: float = 0.5
    ai_triggers: List[str] = field(default_factory=list)


class MockOBSClient:
    """模擬OBS客戶端，用於測試環境"""
    
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.connected = False
        self.scenes = ["Main Scene", "Gaming Scene", "Chat Scene"]
        self.current_scene = "Main Scene"
    
    def get_version(self):
        """模擬獲取版本信息"""
        class MockVersion:
            obs_version = "Mock OBS 30.0.0"
        return MockVersion()
    
    def create_scene(self, scene_name: str):
        """模擬創建場景"""
        if scene_name not in self.scenes:
            self.scenes.append(scene_name)
        print(f"[模擬] 創建場景: {scene_name}")
    
    def create_input(self, scene_name: str, input_name: str, input_kind: str, input_settings: Dict):
        """模擬創建輸入源"""
        print(f"[模擬] 在場景 {scene_name} 中創建輸入 {input_name} (類型: {input_kind})")
    
    def set_scene_item_transform(self, scene_name: str, item_name: str, transform: Dict):
        """模擬設置場景項目變換"""
        print(f"[模擬] 設置 {scene_name}/{item_name} 變換: {transform}")
    
    def set_scene_item_enabled(self, scene_name: str, item_name: str, enabled: bool):
        """模擬設置場景項目可見性"""
        print(f"[模擬] 設置 {scene_name}/{item_name} 可見性: {enabled}")
    
    def set_current_program_scene(self, scene_name: str):
        """模擬設置當前場景"""
        self.current_scene = scene_name
        print(f"[模擬] 切換到場景: {scene_name}")
    
    def get_scene_list(self):
        """模擬獲取場景列表"""
        class MockSceneList:
            scenes = [{"sceneName": name} for name in self.scenes]
        return MockSceneList()
    
    def get_current_program_scene(self):
        """模擬獲取當前場景"""
        class MockCurrentScene:
            scene_name = self.current_scene
        return MockCurrentScene()
    
    def get_scene_item_list(self, scene_name: str):
        """模擬獲取場景項目列表"""
        class MockSceneItems:
            scene_items = [
                {"itemName": "Camera", "itemId": 1},
                {"itemName": "Background", "itemId": 2}
            ]
        return MockSceneItems()
    
    def create_source_filter(self, source_name: str, filter_name: str, filter_kind: str, filter_settings: Dict):
        """模擬創建源濾鏡"""
        print(f"[模擬] 為 {source_name} 添加濾鏡 {filter_name} (類型: {filter_kind})")
    
    def disconnect(self):
        """模擬斷開連接"""
        self.connected = False
        print("[模擬] 已斷開OBS連接")


class OBSSceneManager:
    """OBS場景管理器 - 修正版"""
    
    def __init__(self, host: str = "localhost", port: int = 4444, password: str = ""):
        """
        初始化OBS場景管理器
        
        Args:
            host: OBS WebSocket主機地址
            port: OBS WebSocket端口
            password: OBS WebSocket密碼
        """
        self.host = host
        self.port = port
        self.password = password
        self.obs_client: Optional[Union[Any, MockOBSClient]] = None
        self.current_scene = None
        self.layouts: Dict[str, LayoutConfig] = {}
        self.emotion_layout_mapping: Dict[EmotionState, str] = {}
        self.is_mock_mode = not OBS_AVAILABLE
        
        # 設置日誌
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 添加控制台處理器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # 初始化預設佈局
        self._init_default_layouts()
        self._init_emotion_mappings()
        
        if self.is_mock_mode:
            self.logger.warning("在模擬模式下運行 - OBS功能將被模擬")
    
    async def connect(self) -> bool:
        """連接到OBS WebSocket"""
        try:
            if self.is_mock_mode:
                # 使用模擬客戶端
                self.obs_client = MockOBSClient(self.host, self.port, self.password)
                self.obs_client.connected = True
                self.logger.info("使用模擬OBS客戶端連接成功")
                return True
            else:
                # 使用真實的OBS客戶端
                self.obs_client = obs.ReqClient(
                    host=self.host,
                    port=self.port,
                    password=self.password
                )
                
                # 測試連接
                version_info = self.obs_client.get_version()
                self.logger.info(f"成功連接到OBS Studio {version_info.obs_version}")
                
                # 設置事件監聽
                self._setup_event_handlers()
                
                return True
                
        except Exception as e:
            self.logger.error(f"連接OBS失敗: {e}")
            # 降級到模擬模式
            self.is_mock_mode = True
            self.obs_client = MockOBSClient(self.host, self.port, self.password)
            self.obs_client.connected = True
            self.logger.warning("降級到模擬模式")
            return True
    
    def disconnect(self):
        """斷開OBS WebSocket連接"""
        if self.obs_client:
            if hasattr(self.obs_client, 'disconnect'):
                self.obs_client.disconnect()
            self.obs_client = None
            self.logger.info("已斷開OBS連接")
    
    def _setup_event_handlers(self):
        """設置事件處理器"""
        if not self.obs_client or self.is_mock_mode:
            return
            
        try:
            # 場景切換事件（僅在真實OBS模式下）
            if hasattr(self.obs_client, 'callback'):
                self.obs_client.callback.register(self._on_scene_changed)
        except Exception as e:
            self.logger.warning(f"設置事件處理器失敗: {e}")
    
    def _on_scene_changed(self, data):
        """場景切換事件處理"""
        if hasattr(data, 'scene_name'):
            self.current_scene = data.scene_name
            self.logger.info(f"場景已切換到: {self.current_scene}")
    
    def _init_default_layouts(self):
        """初始化預設佈局配置"""
        
        # 遊戲直播佈局
        gaming_layout = LayoutConfig(
            name="Gaming Layout",
            layout_type=LayoutType.GAMING,
            canvas_size=(1920, 1080),
            elements=[
                SceneElement(
                    name="Game Capture",
                    source_type="game_capture",
                    position=(0, 0),
                    size=(1920, 1080)
                ),
                SceneElement(
                    name="Webcam",
                    source_type="video_capture_device",
                    position=(1450, 50),
                    size=(400, 300)
                ),
                SceneElement(
                    name="Chat Box",
                    source_type="browser_source",
                    position=(50, 700),
                    size=(350, 300)
                ),
                SceneElement(
                    name="Brand Logo",
                    source_type="image_source",
                    position=(50, 50),
                    size=(200, 100)
                )
            ],
            ai_triggers=["gaming", "competitive", "focused"]
        )
        
        # 聊天互動佈局
        chatting_layout = LayoutConfig(
            name="Chatting Layout",
            layout_type=LayoutType.CHATTING,
            canvas_size=(1920, 1080),
            elements=[
                SceneElement(
                    name="Webcam",
                    source_type="video_capture_device",
                    position=(200, 100),
                    size=(800, 600)
                ),
                SceneElement(
                    name="Chat Box",
                    source_type="browser_source",
                    position=(1100, 200),
                    size=(700, 700)
                ),
                SceneElement(
                    name="Background",
                    source_type="image_source",
                    position=(0, 0),
                    size=(1920, 1080)
                )
            ],
            ai_triggers=["interactive", "social", "relaxed"]
        )
        
        # 展示佈局
        showcase_layout = LayoutConfig(
            name="Showcase Layout",
            layout_type=LayoutType.SHOWCASE,
            canvas_size=(1920, 1080),
            elements=[
                SceneElement(
                    name="Screen Capture",
                    source_type="display_capture",
                    position=(0, 0),
                    size=(1920, 1080)
                ),
                SceneElement(
                    name="Webcam",
                    source_type="video_capture_device",
                    position=(1400, 50),
                    size=(450, 300),
                    opacity=0.9
                )
            ],
            ai_triggers=["presentation", "showcase", "teaching"]
        )
        
        # 高能量佈局
        high_energy_layout = LayoutConfig(
            name="High Energy Layout",
            layout_type=LayoutType.HIGH_ENERGY,
            canvas_size=(1920, 1080),
            elements=[
                SceneElement(
                    name="Game Capture",
                    source_type="game_capture",
                    position=(0, 0),
                    size=(1920, 1080)
                ),
                SceneElement(
                    name="Webcam",
                    source_type="video_capture_device",
                    position=(1350, 50),
                    size=(500, 400),
                    filters=["Chroma Key", "Color Correction"]
                ),
                SceneElement(
                    name="Energy Effects",
                    source_type="browser_source",
                    position=(0, 0),
                    size=(1920, 1080),
                    opacity=0.3
                )
            ],
            ai_triggers=["excited", "victory", "intense"]
        )
        
        # 專注佈局
        focused_layout = LayoutConfig(
            name="Focused Layout",
            layout_type=LayoutType.FOCUSED,
            canvas_size=(1920, 1080),
            elements=[
                SceneElement(
                    name="Primary Content",
                    source_type="window_capture",
                    position=(300, 150),
                    size=(1320, 780)
                ),
                SceneElement(
                    name="Webcam",
                    source_type="video_capture_device",
                    position=(50, 50),
                    size=(300, 200),
                    opacity=0.8
                )
            ],
            ai_triggers=["focused", "concentration", "study"]
        )
        
        # 儲存佈局配置
        self.layouts = {
            "gaming": gaming_layout,
            "chatting": chatting_layout,
            "showcase": showcase_layout,
            "high_energy": high_energy_layout,
            "focused": focused_layout
        }
    
    def _init_emotion_mappings(self):
        """初始化情緒到佈局的映射"""
        self.emotion_layout_mapping = {
            EmotionState.EXCITED: "high_energy",
            EmotionState.FOCUSED: "focused",
            EmotionState.RELAXED: "chatting",
            EmotionState.INTERACTIVE: "chatting",
            EmotionState.NEUTRAL: "gaming"
        }
    
    def create_scene_from_layout(self, layout_name: str, scene_name: str) -> bool:
        """
        根據佈局配置創建OBS場景
        
        Args:
            layout_name: 佈局名稱
            scene_name: 場景名稱
            
        Returns:
            bool: 創建是否成功
        """
        if not self.obs_client:
            self.logger.error("OBS客戶端未連接")
            return False
        
        if layout_name not in self.layouts:
            self.logger.error(f"未找到佈局配置: {layout_name}")
            return False
        
        layout = self.layouts[layout_name]
        
        try:
            # 創建新場景
            self.obs_client.create_scene(scene_name)
            self.logger.info(f"創建場景: {scene_name}")
            
            # 添加場景元素
            for element in layout.elements:
                self._add_scene_item(scene_name, element)
            
            return True
            
        except Exception as e:
            self.logger.error(f"創建場景失敗: {e}")
            return False
    
    def _add_scene_item(self, scene_name: str, element: SceneElement):
        """添加場景項目"""
        try:
            # 創建來源
            source_settings = self._get_source_settings(element.source_type)
            
            self.obs_client.create_input(
                scene_name=scene_name,
                input_name=element.name,
                input_kind=element.source_type,
                input_settings=source_settings
            )
            
            # 設置位置和大小
            transform = {
                "positionX": element.position[0],
                "positionY": element.position[1],
                "scaleX": element.size[0] / 1920,  # 相對於畫布大小的比例
                "scaleY": element.size[1] / 1080,
                "rotation": 0.0
            }
            
            self.obs_client.set_scene_item_transform(
                scene_name=scene_name,
                item_name=element.name,
                transform=transform
            )
            
            # 設置可見性
            if not element.visible:
                self.obs_client.set_scene_item_enabled(
                    scene_name=scene_name,
                    item_name=element.name,
                    enabled=False
                )
            
            # 添加濾鏡
            for filter_name in element.filters:
                self._add_filter(element.name, filter_name)
            
            self.logger.info(f"添加場景項目: {element.name}")
            
        except Exception as e:
            self.logger.error(f"添加場景項目失敗: {e}")
    
    def _get_source_settings(self, source_type: str) -> Dict:
        """獲取來源設置"""
        settings_map = {
            "video_capture_device": {},
            "audio_input_capture": {},
            "image_source": {},
            "browser_source": {
                "width": 1920,
                "height": 1080,
                "fps": 30
            },
            "game_capture": {
                "capture_mode": "window",
                "priority": 2
            },
            "window_capture": {},
            "display_capture": {
                "monitor": 0
            }
        }
        
        return settings_map.get(source_type, {})
    
    def _add_filter(self, source_name: str, filter_name: str):
        """添加濾鏡到來源"""
        filter_settings_map = {
            "Chroma Key": {
                "filter_kind": "chroma_key_filter",
                "settings": {
                    "key_color": 0x00FF00,
                    "similarity": 400,
                    "smoothness": 80
                }
            },
            "Color Correction": {
                "filter_kind": "color_filter",
                "settings": {
                    "gamma": 0.0,
                    "contrast": 0.0,
                    "brightness": 0.0
                }
            }
        }
        
        if filter_name in filter_settings_map:
            filter_config = filter_settings_map[filter_name]
            try:
                self.obs_client.create_source_filter(
                    source_name=source_name,
                    filter_name=filter_name,
                    filter_kind=filter_config["filter_kind"],
                    filter_settings=filter_config["settings"]
                )
            except Exception as e:
                self.logger.error(f"添加濾鏡失敗: {e}")
    
    def switch_layout_by_emotion(self, emotion: EmotionState, smooth_transition: bool = True) -> bool:
        """
        根據情緒狀態切換佈局
        
        Args:
            emotion: 情緒狀態
            smooth_transition: 是否使用平滑過渡
            
        Returns:
            bool: 切換是否成功
        """
        if emotion not in self.emotion_layout_mapping:
            self.logger.warning(f"未找到情緒映射: {emotion}")
            return False
        
        layout_name = self.emotion_layout_mapping[emotion]
        scene_name = f"AI_{layout_name}_{emotion.value}"
        
        # 如果場景不存在則創建
        if not self._scene_exists(scene_name):
            self.create_scene_from_layout(layout_name, scene_name)
        
        return self.switch_scene(scene_name, smooth_transition)
    
    def switch_scene(self, scene_name: str, smooth_transition: bool = True) -> bool:
        """
        切換到指定場景
        
        Args:
            scene_name: 場景名稱
            smooth_transition: 是否使用平滑過渡
            
        Returns:
            bool: 切換是否成功
        """
        if not self.obs_client:
            self.logger.error("OBS客戶端未連接")
            return False
        
        try:
            self.obs_client.set_current_program_scene(scene_name)
            self.current_scene = scene_name
            self.logger.info(f"切換到場景: {scene_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"切換場景失敗: {e}")
            return False
    
    def _scene_exists(self, scene_name: str) -> bool:
        """檢查場景是否存在"""
        try:
            scenes = self.obs_client.get_scene_list()
            return any(scene["sceneName"] == scene_name for scene in scenes.scenes)
        except Exception:
            return False
    
    def update_element_position(self, scene_name: str, element_name: str, 
                              position: Tuple[int, int], size: Optional[Tuple[int, int]] = None):
        """動態更新元素位置和大小"""
        if not self.obs_client:
            return False
        
        try:
            transform: Dict[str, Union[int, float]] = {
                "positionX": position[0],
                "positionY": position[1]
            }
            
            if size:
                transform["scaleX"] = size[0] / 1920
                transform["scaleY"] = size[1] / 1080
            
            self.obs_client.set_scene_item_transform(
                scene_name=scene_name,
                item_name=element_name,
                transform=transform
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新元素位置失敗: {e}")
            return False
    
    def set_element_visibility(self, scene_name: str, element_name: str, visible: bool):
        """設置元素可見性"""
        if not self.obs_client:
            return False
        
        try:
            self.obs_client.set_scene_item_enabled(
                scene_name=scene_name,
                item_name=element_name,
                enabled=visible
            )
            return True
            
        except Exception as e:
            self.logger.error(f"設置元素可見性失敗: {e}")
            return False
    
    def get_current_scene_info(self) -> Optional[Dict]:
        """獲取當前場景資訊"""
        if not self.obs_client:
            return None
        
        try:
            current_scene = self.obs_client.get_current_program_scene()
            scene_items = self.obs_client.get_scene_item_list(current_scene.scene_name)
            
            return {
                "scene_name": current_scene.scene_name,
                "items": [item for item in scene_items.scene_items]
            }
            
        except Exception as e:
            self.logger.error(f"獲取場景資訊失敗: {e}")
            return None
    
    def get_available_layouts(self) -> List[str]:
        """獲取可用的佈局列表"""
        return list(self.layouts.keys())
    
    def get_layout_info(self, layout_name: str) -> Optional[Dict]:
        """獲取佈局資訊"""
        if layout_name not in self.layouts:
            return None
        
        layout = self.layouts[layout_name]
        return {
            "name": layout.name,
            "type": layout.layout_type.value,
            "canvas_size": layout.canvas_size,
            "element_count": len(layout.elements),
            "ai_triggers": layout.ai_triggers
        }
    
    def is_connected(self) -> bool:
        """檢查是否已連接"""
        if self.obs_client:
            if hasattr(self.obs_client, 'connected'):
                return self.obs_client.connected
            return True
        return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """獲取連接狀態"""
        return {
            "connected": self.is_connected(),
            "mock_mode": self.is_mock_mode,
            "host": self.host,
            "port": self.port,
            "current_scene": self.current_scene,
            "available_layouts": len(self.layouts)
        }


# 測試代碼
if __name__ == "__main__":
    async def test_scene_manager():
        """測試場景管理器"""
        print("🧪 測試OBS場景管理器")
        print("=" * 50)
        
        # 創建場景管理器
        scene_manager = OBSSceneManager(
            host="localhost",
            port=4444,
            password=""
        )
        
        # 測試連接
        print("1. 測試連接...")
        if await scene_manager.connect():
            print("✅ 連接成功")
        else:
            print("❌ 連接失敗")
            return
        
        # 測試獲取連接狀態
        print("\n2. 獲取連接狀態...")
        status = scene_manager.get_connection_status()
        print(f"   狀態: {status}")
        
        # 測試獲取可用佈局
        print("\n3. 獲取可用佈局...")
        layouts = scene_manager.get_available_layouts()
        print(f"   可用佈局: {layouts}")
        
        # 測試創建場景
        print("\n4. 測試創建場景...")
        success = scene_manager.create_scene_from_layout("gaming", "Test Gaming Scene")
        if success:
            print("✅ 場景創建成功")
        else:
            print("❌ 場景創建失敗")
        
        # 測試情緒驅動的場景切換
        print("\n5. 測試情緒驅動場景切換...")
        for emotion in EmotionState:
            success = scene_manager.switch_layout_by_emotion(emotion)
            print(f"   {emotion.value}: {'✅' if success else '❌'}")
        
        # 測試獲取場景資訊
        print("\n6. 獲取當前場景資訊...")
        scene_info = scene_manager.get_current_scene_info()
        if scene_info:
            print(f"   當前場景: {scene_info['scene_name']}")
            print(f"   場景項目數量: {len(scene_info['items'])}")
        
        # 斷開連接
        print("\n7. 斷開連接...")
        scene_manager.disconnect()
        print("✅ 測試完成")
    
    # 運行測試
    asyncio.run(test_scene_manager())
