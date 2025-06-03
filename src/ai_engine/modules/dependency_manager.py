"""
LivePilotAI 依賴管理模組
負責檢查和安裝必要的依賴包
"""

import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Tuple, Optional


logger = logging.getLogger(__name__)


class DependencyCheckError(Exception):
    """依賴檢查失敗異常"""
    pass


class DependencyManager:
    """依賴管理器 - 負責檢查和安裝必要的依賴包"""
    
    REQUIRED_PACKAGES = {
        'cv2': 'opencv-python',
        'numpy': 'numpy', 
        'tensorflow': 'tensorflow',
        'PIL': 'Pillow'
    }
    
    @staticmethod
    def check_dependencies() -> Tuple[List[str], List[str]]:
        """
        檢查所有必要的依賴項
        
        Returns:
            Tuple[List[str], List[str]]: (已安裝的包, 缺失的包)
        """
        installed = []
        missing = []
        
        for import_name, package_name in DependencyManager.REQUIRED_PACKAGES.items():
            try:
                importlib.import_module(import_name)
                installed.append(package_name)
                logger.info(f"✓ {package_name} 已安裝")
            except ImportError:
                missing.append(package_name)
                logger.warning(f"✗ {package_name} 未安裝")
        
        return installed, missing
    
    @staticmethod
    def install_missing_packages(packages: List[str]) -> bool:
        """
        自動安裝缺失的包
        
        Args:
            packages: 需要安裝的包列表
            
        Returns:
            bool: 安裝是否成功
        """
        if not packages:
            return True
        
        logger.info(f"開始安裝缺失的依賴: {', '.join(packages)}")
        
        try:
            for package in packages:
                logger.info(f"正在安裝 {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"✓ {package} 安裝成功")
                else:
                    logger.error(f"✗ {package} 安裝失敗: {result.stderr}")
                    return False
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("安裝超時")
            return False
        except Exception as e:
            logger.error(f"安裝過程中發生錯誤: {e}")
            return False
    
    @staticmethod
    def verify_installation() -> bool:
        """
        驗證所有依賴是否已正確安裝
        
        Returns:
            bool: 所有依賴是否可用
        """
        try:
            installed, missing = DependencyManager.check_dependencies()
            
            if missing:
                logger.error(f"仍有缺失的依賴: {', '.join(missing)}")
                return False
                
            logger.info("所有依賴檢查通過")
            return True
            
        except Exception as e:
            logger.error(f"依賴驗證失敗: {e}")
            return False
    
    @staticmethod
    def auto_install_dependencies() -> bool:
        """
        自動檢查並安裝所有缺失的依賴
        
        Returns:
            bool: 是否成功安裝所有依賴
        """
        try:
            logger.info("開始依賴自動安裝流程...")
            
            # 第一次檢查
            installed, missing = DependencyManager.check_dependencies()
            
            if not missing:
                logger.info("所有依賴已安裝")
                return True
            
            # 安裝缺失的依賴
            if not DependencyManager.install_missing_packages(missing):
                return False
            
            # 驗證安裝結果
            return DependencyManager.verify_installation()
            
        except Exception as e:
            logger.error(f"依賴自動安裝失敗: {e}")
            return False
