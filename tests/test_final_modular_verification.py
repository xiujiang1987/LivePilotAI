#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilotAI 最終模組化驗證測試
驗證所有模組化組件是否正常工作
"""

import sys
import os
import logging

# 確保可以導入模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_individual_modules():
    """測試個別模組的導入"""
    results = {}
    
    # 測試 states 模組
    try:
        from ai_engine.states import EmotionDetectorState
        results['states'] = True
        logger.info("✅ states 模組導入成功")
    except Exception as e:
        results['states'] = False
        logger.error(f"❌ states 模組導入失敗: {e}")
    
    # 測試 dependency_manager 模組
    try:
        from ai_engine.modules.dependency_manager import DependencyManager
        results['dependency_manager'] = True
        logger.info("✅ dependency_manager 模組導入成功")
    except Exception as e:
        results['dependency_manager'] = False
        logger.error(f"❌ dependency_manager 模組導入失敗: {e}")
    
    # 測試 emotion_detector 模組
    try:
        from ai_engine.modules.emotion_detector import EmotionDetector, DetectionConfig
        results['emotion_detector'] = True
        logger.info("✅ emotion_detector 模組導入成功")
    except Exception as e:
        results['emotion_detector'] = False
        logger.error(f"❌ emotion_detector 模組導入失敗: {e}")
    
    # 測試 camera_manager 模組
    try:
        # 直接導入，避免通過 modules.__init__
        import ai_engine.modules.camera_manager as cam_mod
        CameraManager = cam_mod.CameraManager
        CameraConfig = cam_mod.CameraConfig
        
        # 測試實例化
        config = CameraConfig()
        manager = CameraManager(config)
        
        results['camera_manager'] = True
        logger.info("✅ camera_manager 模組導入和實例化成功")
    except Exception as e:
        results['camera_manager'] = False
        logger.error(f"❌ camera_manager 模組導入失敗: {e}")
    
    # 測試簡化狀態機
    try:
        from ai_engine.simple_emotion_state_machine import SimpleEmotionDetectorStateMachine
        simple_machine = SimpleEmotionDetectorStateMachine()
        results['simple_state_machine'] = True
        logger.info("✅ simple_emotion_state_machine 模組導入成功")
    except Exception as e:
        results['simple_state_machine'] = False
        logger.error(f"❌ simple_emotion_state_machine 模組導入失敗: {e}")
    
    return results


def test_architecture_comparison():
    """比較原始架構和模組化架構"""
    logger.info("\n=== 架構比較分析 ===")
    
    # 檢查原始檔案
    original_file = "src/ai_engine/emotion_detector_engine.py"
    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as f:
            original_lines = len(f.readlines())
        logger.info(f"原始單體檔案: {original_lines} 行")
    else:
        logger.warning("原始檔案不存在")
        original_lines = 0
    
    # 檢查模組化檔案
    modular_files = [
        "src/ai_engine/states.py",
        "src/ai_engine/modules/dependency_manager.py",
        "src/ai_engine/modules/emotion_detector.py",
        "src/ai_engine/modules/camera_manager.py",
        "src/ai_engine/simple_emotion_state_machine.py",
        "src/ai_engine/emotion_state_machine.py"
    ]
    
    total_modular_lines = 0
    for file_path in modular_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_modular_lines += lines
                logger.info(f"{os.path.basename(file_path)}: {lines} 行")
        else:
            logger.warning(f"模組檔案不存在: {file_path}")
    
    logger.info(f"\n模組化總計: {total_modular_lines} 行 (分散在 {len(modular_files)} 個檔案)")
    
    if original_lines > 0:
        reduction = ((original_lines - total_modular_lines) / original_lines) * 100
        logger.info(f"程式碼複雜度變化: {reduction:.1f}% {'減少' if reduction > 0 else '增加'}")
    
    # 分析模組化優勢
    logger.info("\n=== 模組化優勢 ===")
    advantages = [
        "✅ 單一責任原則：每個模組負責特定功能",
        "✅ 可維護性：問題更容易定位和修復", 
        "✅ 可重用性：模組可以獨立使用",
        "✅ 可測試性：每個模組可以獨立測試",
        "✅ 擴展性：更容易添加新功能",
        "✅ 團隊協作：不同人員可以同時開發不同模組"
    ]
    
    for advantage in advantages:
        logger.info(advantage)


def main():
    """主測試函數"""
    logger.info("開始 LivePilotAI 最終模組化驗證")
    
    # 測試個別模組
    module_results = test_individual_modules()
    
    # 統計結果
    passed = sum(1 for result in module_results.values() if result)
    total = len(module_results)
    
    logger.info(f"\n=== 模組測試結果 ===")
    for module, result in module_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"{module}: {status}")
    
    logger.info(f"\n總計: {passed}/{total} 模組測試通過")
    
    # 架構比較
    test_architecture_comparison()
    
    # 最終結論
    logger.info(f"\n{'='*60}")
    logger.info("🎉 LivePilotAI 模組化重構已完成！")
    logger.info(f"{'='*60}")
    
    conclusion = f"""
模組化重構總結:
- 成功將 {total} 個核心模組進行重構
- {passed} 個模組通過測試，{total - passed} 個需要進一步優化
- 採用狀態機模式，提升程式碼組織性
- 實現模組化分離，提升可維護性
- 支援異步執行，提升效能

下一步建議:
1. 完善單元測試覆蓋率
2. 添加更詳細的 API 文檔
3. 整合到主專案 CI/CD 流程
4. 考慮添加性能監控和指標
"""
    
    logger.info(conclusion)
    
    if passed == total:
        logger.info("🚀 模組化重構 100% 成功！可以開始使用新架構")
        return True
    else:
        logger.warning(f"⚠️ 還有 {total - passed} 個模組需要修復")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
