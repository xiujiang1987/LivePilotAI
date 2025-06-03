"""
LivePilotAI 情感檢測引擎 - 簡化測試版本
專注於測試依賴檢查功能
"""

import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Tuple, Optional, Any
import time

# 設置基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
            logger.info("沒有需要安裝的包")
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
        installed, missing = DependencyManager.check_dependencies()
        
        if missing:
            logger.error(f"仍有缺失的依賴: {', '.join(missing)}")
            return False
        
        logger.info("所有依賴檢查通過！")
        return True


def startup_dependency_check(auto_install: bool = True) -> bool:
    """
    啟動時執行依賴檢查
    
    Args:
        auto_install: 是否自動安裝缺失的依賴
        
    Returns:
        bool: 依賴檢查是否通過
        
    Raises:
        DependencyCheckError: 依賴檢查失敗時拋出
    """
    logger.info("="*50)
    logger.info("LivePilotAI 情感檢測引擎 - 依賴檢查")
    logger.info("="*50)
    
    # 檢查依賴
    installed, missing = DependencyManager.check_dependencies()
    
    if not missing:
        logger.info("✓ 所有依賴已就緒！")
        return True
    
    logger.warning(f"發現 {len(missing)} 個缺失的依賴項: {', '.join(missing)}")
    
    if not auto_install:
        error_msg = f"缺失依賴項: {', '.join(missing)}，請手動安裝"
        logger.error(error_msg)
        raise DependencyCheckError(error_msg)
    
    # 嘗試自動安裝
    logger.info("嘗試自動安裝缺失的依賴...")
    if DependencyManager.install_missing_packages(missing):
        # 重新驗證
        if DependencyManager.verify_installation():
            logger.info("✓ 依賴安裝和驗證完成！")
            return True
        else:
            error_msg = "依賴安裝後驗證失敗"
            logger.error(error_msg)
            raise DependencyCheckError(error_msg)
    else:
        error_msg = "依賴自動安裝失敗"
        logger.error(error_msg)
        raise DependencyCheckError(error_msg)


def test_dependency_system():
    """測試依賴系統"""
    print("\n🧪 測試依賴檢查系統")
    print("="*40)
    
    try:
        # 測試依賴檢查
        print("\n1. 檢查當前依賴狀態...")
        installed, missing = DependencyManager.check_dependencies()
        
        print(f"\n已安裝的包 ({len(installed)}):")
        for pkg in installed:
            print(f"  ✓ {pkg}")
        
        print(f"\n缺失的包 ({len(missing)}):")
        for pkg in missing:
            print(f"  ✗ {pkg}")
        
        # 測試啟動依賴檢查
        print("\n2. 執行啟動依賴檢查...")
        result = startup_dependency_check(auto_install=True)
        
        if result:
            print("\n✅ 依賴檢查系統測試成功！")
            return True
        else:
            print("\n❌ 依賴檢查系統測試失敗")
            return False
            
    except DependencyCheckError as e:
        print(f"\n⚠️ 依賴檢查錯誤: {e}")
        print("\n手動安裝指令:")
        print("pip install opencv-python numpy tensorflow Pillow")
        return False
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        return False


def main():
    """主函數"""
    print("🚀 LivePilotAI 依賴檢查系統測試")
    print("="*50)
    
    # 顯示系統資訊
    print(f"\nPython 版本: {sys.version}")
    print(f"執行路徑: {sys.executable}")
    
    # 執行測試
    success = test_dependency_system()
    
    if success:
        print("\n🎉 恭喜！依賴檢查系統已正常運作")
        print("現在可以安全地啟動情感檢測引擎了")
        
        # 嘗試導入已安裝的包
        print("\n🔍 驗證導入功能...")
        try:
            import numpy as np
            print(f"✓ NumPy 版本: {np.__version__}")
        except ImportError:
            print("✗ NumPy 導入失敗")
        
        try:
            import cv2
            print(f"✓ OpenCV 版本: {cv2.__version__}")
        except ImportError:
            print("✗ OpenCV 導入失敗")
        
        try:
            import tensorflow as tf
            print(f"✓ TensorFlow 版本: {tf.__version__}")
        except ImportError:
            print("✗ TensorFlow 導入失敗")
        
        try:
            from PIL import Image
            print(f"✓ Pillow 可用")
        except ImportError:
            print("✗ Pillow 導入失敗")
            
        return True
    else:
        print("\n❌ 依賴檢查系統需要修復")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
