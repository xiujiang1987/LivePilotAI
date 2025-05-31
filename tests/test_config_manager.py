"""
測試配置管理系統
"""

import pytest
import yaml
from pathlib import Path
from src.core.config_manager import (
    ConfigManager,
    AppConfig,
    DatabaseConfig,
    Environment
)


class TestConfigManager:
    """配置管理器測試"""
    
    def test_default_config_creation(self):
        """測試預設配置創建"""
        config = AppConfig()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.database is not None
        assert config.ai_models is not None
        assert config.obs is not None
        assert config.api is not None
        assert config.logging is not None
        
    def test_config_manager_initialization(self, temp_dir):
        """測試配置管理器初始化"""
        config_manager = ConfigManager(str(temp_dir))
        
        assert config_manager.config_dir == temp_dir
        assert config_manager.config_dir.exists()
        
    def test_load_default_config(self, temp_dir):
        """測試載入預設配置"""
        config_manager = ConfigManager(str(temp_dir))
        config = config_manager.load_config()
        
        assert isinstance(config, AppConfig)
        assert config.environment == Environment.DEVELOPMENT
        
    def test_save_and_load_config(self, temp_dir, sample_config_data):
        """測試保存和載入配置"""
        config_manager = ConfigManager(str(temp_dir))
        
        # 創建配置
        config = config_manager._create_config_from_dict(sample_config_data)
        
        # 保存配置
        assert config_manager.save_config(config, "test_config.yml")
        
        # 檢查文件是否存在
        config_file = temp_dir / "test_config.yml"
        assert config_file.exists()
        
        # 載入配置
        loaded_config = config_manager.load_config("test_config.yml")
        
        assert loaded_config.environment == Environment.TESTING
        assert loaded_config.debug is True
        assert loaded_config.database.host == "localhost"
        assert loaded_config.database.port == 5432
        
    def test_config_update(self, temp_dir):
        """測試配置更新"""
        config_manager = ConfigManager(str(temp_dir))
        config = config_manager.load_config()
        
        # 更新配置
        config_manager.update_config(debug=False, secret_key="new-key")
        updated_config = config_manager.get_config()
        
        assert updated_config.debug is False
        assert updated_config.secret_key == "new-key"


class TestDatabaseConfig:
    """資料庫配置測試"""
    
    def test_database_config_defaults(self):
        """測試資料庫配置預設值"""
        db_config = DatabaseConfig()
        
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.database == "livepilotai"
        assert db_config.username == "postgres"
        assert db_config.password == ""
        assert db_config.max_connections == 20
        
    def test_database_config_custom(self):
        """測試自定義資料庫配置"""
        db_config = DatabaseConfig(
            host="custom-host",
            port=3306,
            database="custom_db",
            username="custom_user",
            password="custom_pass",
            max_connections=50
        )
        
        assert db_config.host == "custom-host"
        assert db_config.port == 3306
        assert db_config.database == "custom_db"
        assert db_config.username == "custom_user"
        assert db_config.password == "custom_pass"
        assert db_config.max_connections == 50
