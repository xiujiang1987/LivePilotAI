"""
LivePilotAI 模組化架構測試
測試新的狀態機架構和模組化設計
"""

import asyncio
import sys
import logging
from pathlib import Path

# 添加 src 到路徑
sys.path.append(str(Path(__file__).parent / "src"))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_modular_architecture():
    """測試模組化架構"""
    
    logger.info("="*60)
    logger.info("LivePilotAI 模組化架構測試開始")
    logger.info("="*60)
    
    try:
        # 測試 1: 導入狀態模組
        logger.info("測試 1: 導入狀態定義...")
        from ai_engine.states import EmotionDetectorState, StateTransitionError
        logger.info("✓ 狀態模組導入成功")
        
        # 測試 2: 導入依賴管理器
        logger.info("測試 2: 導入依賴管理器...")
        from ai_engine.modules import DependencyManager
        logger.info("✓ 依賴管理器導入成功")
        
        # 測試 3: 測試依賴檢查
        logger.info("測試 3: 執行依賴檢查...")
        installed, missing = DependencyManager.check_dependencies()
        logger.info(f"✓ 已安裝: {', '.join(installed) if installed else '無'}")
        logger.info(f"✓ 缺失: {', '.join(missing) if missing else '無'}")
        
        # 測試 4: 導入情感檢測器
        logger.info("測試 4: 導入情感檢測器...")
        from ai_engine.modules import EmotionDetector, DetectionConfig
        logger.info("✓ 情感檢測器導入成功")
        
        # 測試 5: 測試情感檢測器初始化
        logger.info("測試 5: 初始化情感檢測器...")
        emotion_detector = EmotionDetector()
        model_info = emotion_detector.get_model_info()
        logger.info(f"✓ 情感檢測器初始化完成: {model_info}")
        
        # 測試 6: 導入簡化狀態機
        logger.info("測試 6: 導入簡化狀態機...")
        from ai_engine.simple_emotion_state_machine import (
            SimpleEmotionDetectorStateMachine,
            SimpleEmotionDetectorConfig
        )
        logger.info("✓ 簡化狀態機導入成功")
        
        # 測試 7: 創建和運行狀態機
        logger.info("測試 7: 創建並運行狀態機...")
        config = SimpleEmotionDetectorConfig()
        state_machine = SimpleEmotionDetectorStateMachine(config)
        
        # 運行狀態機（異步）
        logger.info("開始運行狀態機...")
        result = await state_machine.run()
        
        # 獲取最終狀態
        final_status = state_machine.get_status()
        logger.info(f"狀態機運行結果: {result}")
        logger.info(f"最終狀態: {final_status['current_state']}")
        logger.info(f"運行統計: {final_status['stats']}")
        
        logger.info("="*60)
        logger.info("✅ 所有測試通過！模組化架構工作正常")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        logger.error("="*60)
        import traceback
        traceback.print_exc()
        return False


async def test_individual_modules():
    """測試各個模組"""
    
    logger.info("\n" + "="*60)
    logger.info("個別模組功能測試")
    logger.info("="*60)
    
    try:
        # 測試狀態枚舉
        logger.info("測試狀態枚舉...")
        from ai_engine.states import EmotionDetectorState
        
        states = list(EmotionDetectorState)
        logger.info(f"✓ 狀態數量: {len(states)}")
        for state in states:
            logger.info(f"  - {state.name}: {state.value}")
        
        # 測試依賴管理器詳細功能
        logger.info("\n測試依賴管理器詳細功能...")
        from ai_engine.modules import DependencyManager
        
        # 驗證安裝
        verification_result = DependencyManager.verify_installation()
        logger.info(f"✓ 依賴驗證結果: {verification_result}")
        
        # 測試情感檢測器詳細功能
        logger.info("\n測試情感檢測器詳細功能...")
        from ai_engine.modules import EmotionDetector, DetectionConfig
        
        # 創建檢測器
        config = DetectionConfig()
        detector = EmotionDetector(config)
        
        # 獲取模型信息
        model_info = detector.get_model_info()
        logger.info(f"✓ 模型信息: {model_info}")
        
        # 測試模型載入
        load_result = detector.load_models()
        logger.info(f"✓ 模型載入結果: {load_result}")
        
        if load_result:
            # 測試人臉檢測（使用模擬數據）
            import numpy as np
            mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            faces = detector.detect_faces(mock_frame)
            logger.info(f"✓ 人臉檢測結果: 檢測到 {len(faces)} 個人臉")
            
            # 測試情感檢測
            results = detector.detect_emotions(mock_frame)
            logger.info(f"✓ 情感檢測結果: 檢測到 {len(results)} 個情感")
        
        # 清理
        detector.cleanup()
        logger.info("✓ 模組清理完成")
        
        logger.info("="*60)
        logger.info("✅ 個別模組測試完成")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 個別模組測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_with_original():
    """與原始架構比較"""
    
    logger.info("\n" + "="*60)
    logger.info("架構比較分析")
    logger.info("="*60)
    
    # 統計原始檔案
    original_file = Path("src/ai_engine/emotion_detector_engine.py")
    if original_file.exists():
        with open(original_file, 'r', encoding='utf-8') as f:
            original_lines = len(f.readlines())
        logger.info(f"原始檔案行數: {original_lines}")
    else:
        logger.warning("找不到原始檔案")
        return
    
    # 統計新架構檔案
    new_files = [
        "src/ai_engine/states.py",
        "src/ai_engine/modules/dependency_manager.py",
        "src/ai_engine/modules/emotion_detector.py",
        "src/ai_engine/simple_emotion_state_machine.py"
    ]
    
    total_new_lines = 0
    for file_path in new_files:
        file_obj = Path(file_path)
        if file_obj.exists():
            with open(file_obj, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            logger.info(f"{file_path}: {lines} 行")
            total_new_lines += lines
        else:
            logger.warning(f"找不到檔案: {file_path}")
    
    logger.info(f"\n總計:")
    logger.info(f"原始架構: {original_lines} 行 (單一檔案)")
    logger.info(f"新架構: {total_new_lines} 行 (分散在 {len(new_files)} 個檔案)")
    logger.info(f"程式碼減少: {original_lines - total_new_lines} 行 ({((original_lines - total_new_lines) / original_lines * 100):.1f}%)")
    
    logger.info("\n架構優勢:")
    logger.info("✓ 模組化設計，易於維護")
    logger.info("✓ 狀態機模式，邏輯清晰")
    logger.info("✓ 單一責任原則，降低耦合")
    logger.info("✓ 易於測試和除錯")
    logger.info("✓ 可重用組件")
    
    logger.info("="*60)


async def main():
    """主測試函數"""
    logger.info("LivePilotAI 模組化重構驗證測試")
    
    # 執行主要架構測試
    main_test_result = await test_modular_architecture()
    
    if main_test_result:
        # 執行個別模組測試
        module_test_result = await test_individual_modules()
        
        # 架構比較
        compare_with_original()
        
        if module_test_result:
            logger.info("\n🎉 恭喜！模組化重構成功完成！")
            logger.info("新架構已準備就緒，可以替代原始的單體檔案。")
        else:
            logger.warning("\n⚠️ 主架構測試通過，但個別模組測試有問題。")
    else:
        logger.error("\n❌ 模組化架構測試失敗，需要進一步修復。")


if __name__ == "__main__":
    asyncio.run(main())
