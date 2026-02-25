"""
LivePilotAI - 配置管理系統
統一管理應用程式配置、環境變數和設定文件
"""

import os
import json
import yaml
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class Environment(Enum):
    """環境類型枚舉"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """資料庫配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "livepilotai"
    username: str = "postgres"
    password: str = ""
    max_connections: int = 20


@dataclass
class AIModelConfig:
    """AI模型配置"""
    emotion_model_path: str = "models/emotion_detection.h5"
    face_cascade_path: str = "models/haarcascade_frontalface_default.xml"
    confidence_threshold: float = 0.7
    input_size: tuple = (48, 48)
    batch_size: int = 32


@dataclass
class OBSConfig:
    """OBS Studio配置"""
    websocket_host: str = "localhost"
    websocket_port: int = 4455
    websocket_password: str = ""
    auto_connect: bool = True
    reconnect_attempts: int = 5
    timeout: int = 10


@dataclass
class APIConfig:
    """API服務配置"""
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    rate_limit: int = 100
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]


@dataclass
class LoggingConfig:
    """日誌配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/livepilotai.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class AppConfig:
    """應用程式主配置"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    secret_key: str = ""
    database: DatabaseConfig = None
    ai_models: AIModelConfig = None
    obs: OBSConfig = None
    api: APIConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.ai_models is None:
            self.ai_models = AIModelConfig()
        if self.obs is None:
            self.obs = OBSConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("ConfigManager")
        self._config: Optional[AppConfig] = None
        
    def load_config(self, config_file: Optional[str] = None) -> AppConfig:
        """載入配置文件"""
        if config_file is None:
            # Check if current.yml exists first (user saved settings)
            if (self.config_dir / "current.yml").exists():
                config_file = "current.yml"
            else:
                # 根據環境變數決定配置文件
                env = os.getenv("LIVEPILOTAI_ENV", "development")
                config_file = f"{env}.yml"
            
        config_path = self.config_dir / config_file
        
        if config_path.exists():
            try:
                # Fix for python/tuple in yaml
                try:
                    yaml.SafeLoader.add_constructor("tag:yaml.org,2002:python/tuple", lambda loader, node: tuple(loader.construct_sequence(node)))
                except ImportError:
                    pass

                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    
                # Post-process config data to convert lists to tuples where expected
                if 'ai_models' in config_data and 'input_size' in config_data['ai_models']:
                    if isinstance(config_data['ai_models']['input_size'], list):
                        config_data['ai_models']['input_size'] = tuple(config_data['ai_models']['input_size'])

                self._config = self._create_config_from_dict(config_data)
                self.logger.info(f"成功載入配置文件: {config_path}")
                
            except Exception as e:
                self.logger.error(f"載入配置文件失敗: {e}")
                self._config = self._load_default_config()
        else:
            self.logger.warning(f"配置文件不存在: {config_path}，使用預設配置")
            self._config = self._load_default_config()
            
        # 從環境變數覆蓋配置
        self._override_from_env()
        
        return self._config
        
    def save_config(self, config: AppConfig, config_file: str = "current.yml") -> bool:
        """保存配置到文件"""
        try:
            config_path = self.config_dir / config_file
            config_dict = asdict(config)
            
            # 處理枚舉類型
            config_dict['environment'] = config.environment.value
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"配置已保存到: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置失敗: {e}")
            return False
            
    def get_config(self) -> AppConfig:
        """獲取當前配置"""
        if self._config is None:
            return self.load_config()
        return self._config
        
    def update_config(self, **kwargs) -> None:
        """更新配置"""
        if self._config is None:
            self._config = self.load_config()
            
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                
    def _create_config_from_dict(self, config_data: Dict[str, Any]) -> AppConfig:
        """從字典創建配置對象"""
        # 處理環境枚舉
        if 'environment' in config_data:
            config_data['environment'] = Environment(config_data['environment'])
            
        # 創建子配置對象
        if 'database' in config_data:
            config_data['database'] = DatabaseConfig(**config_data['database'])
            
        if 'ai_models' in config_data:
            config_data['ai_models'] = AIModelConfig(**config_data['ai_models'])
            
        if 'obs' in config_data:
            config_data['obs'] = OBSConfig(**config_data['obs'])
            
        if 'api' in config_data:
            config_data['api'] = APIConfig(**config_data['api'])
            
        if 'logging' in config_data:
            config_data['logging'] = LoggingConfig(**config_data['logging'])
            
        return AppConfig(**config_data)
        
    def _load_default_config(self) -> AppConfig:
        """載入預設配置"""
        return AppConfig()
        
    def _override_from_env(self) -> None:
        """從環境變數覆蓋配置"""
        if self._config is None:
            return
            
        # API配置覆蓋
        if os.getenv("API_HOST"):
            self._config.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self._config.api.port = int(os.getenv("API_PORT"))
            
        # 資料庫配置覆蓋
        if os.getenv("DB_HOST"):
            self._config.database.host = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            self._config.database.port = int(os.getenv("DB_PORT"))
        if os.getenv("DB_PASSWORD"):
            self._config.database.password = os.getenv("DB_PASSWORD")
            
        # OBS配置覆蓋
        if os.getenv("OBS_HOST"):
            self._config.obs.websocket_host = os.getenv("OBS_HOST")
        if os.getenv("OBS_PORT"):
            self._config.obs.websocket_port = int(os.getenv("OBS_PORT"))
        if os.getenv("OBS_PASSWORD"):
            self._config.obs.websocket_password = os.getenv("OBS_PASSWORD")
            
        # 其他關鍵配置
        if os.getenv("SECRET_KEY"):
            self._config.secret_key = os.getenv("SECRET_KEY")
        if os.getenv("DEBUG"):
            self._config.debug = os.getenv("DEBUG").lower() == "true"


# 全局配置管理器實例
config_manager = ConfigManager()

# 便利函數
def get_config() -> AppConfig:
    """獲取應用程式配置"""
    return config_manager.get_config()

def load_config(config_file: Optional[str] = None) -> AppConfig:
    """載入配置"""
    return config_manager.load_config(config_file)

def save_config(config: AppConfig, config_file: str = "current.yml") -> bool:
    """保存配置"""
    return config_manager.save_config(config, config_file)
