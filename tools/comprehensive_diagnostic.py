#!/usr/bin/env python3
"""
LivePilotAI 問題診斷工具
Comprehensive diagnostics for LivePilotAI launcher issues
"""

import sys
import os
import subprocess
import traceback
from pathlib import Path

def write_to_file(content):
    """寫入診斷結果到檔案，避免終端輸出問題"""
    with open("diagnostic_report.txt", "w", encoding="utf-8") as f:
        f.write(content)

def run_diagnostic():
    """運行完整診斷"""
    report = []
    report.append("=" * 60)
    report.append("LivePilotAI 問題診斷報告")
    report.append("=" * 60)
    
    # 1. 基本系統檢查
    report.append("\n1. 基本系統資訊:")
    report.append(f"   Python 版本: {sys.version}")
    report.append(f"   當前目錄: {os.getcwd()}")
    report.append(f"   Python 路徑: {sys.executable}")
    
    # 2. 檢查關鍵檔案
    report.append("\n2. 關鍵檔案檢查:")
    key_files = [
        "main_day5.py",
        "main_fixed.py", 
        "launcher_fixed.py",
        "basic_test.py",
        "obs_test_simple.py",
        "requirements.txt"
    ]
    
    for file in key_files:
        if Path(file).exists():
            try:
                size = Path(file).stat().st_size
                report.append(f"   [✓] {file} - 存在 ({size} bytes)")
            except Exception as e:
                report.append(f"   [×] {file} - 存在但無法讀取: {e}")
        else:
            report.append(f"   [×] {file} - 不存在")
    
    # 3. 檢查 src 目錄結構
    report.append("\n3. src 目錄結構檢查:")
    src_path = Path("src")
    if src_path.exists():
        try:
            for item in src_path.rglob("*.py"):
                report.append(f"   [✓] {item}")
        except Exception as e:
            report.append(f"   [×] 無法讀取 src 目錄: {e}")
    else:
        report.append("   [×] src 目錄不存在")
    
    # 4. 模組導入測試
    report.append("\n4. 關鍵模組導入測試:")
    modules_to_test = [
        "tkinter",
        "threading", 
        "subprocess",
        "pathlib",
        "json",
        "logging",
        "asyncio"
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            report.append(f"   [✓] {module} - 可導入")
        except ImportError as e:
            report.append(f"   [×] {module} - 導入失敗: {e}")
    
    # 5. 嘗試導入專案特定模組
    report.append("\n5. 專案模組導入測試:")
    sys.path.insert(0, str(Path.cwd() / "src"))
    
    project_modules = [
        "obs_integration.obs_manager",
        "core.scene_controller", 
        "ai_engine.emotion_detector",
        "ai_engine.emotion_mapper",
        "core.camera_manager"
    ]
    
    for module in project_modules:
        try:
            __import__(module)
            report.append(f"   [✓] {module} - 可導入")
        except ImportError as e:
            report.append(f"   [×] {module} - 導入失敗: {e}")
        except Exception as e:
            report.append(f"   [×] {module} - 其他錯誤: {e}")
    
    # 6. 嘗試執行主程式的導入部分
    report.append("\n6. 主程式導入測試:")
    try:
        # 模擬 main_day5.py 的導入
        exec("""
try:
    from obs_integration.obs_manager import OBSManager
    from core.scene_controller import SceneController
    from ai_engine.emotion_detector import EmotionDetector
    from ai_engine.emotion_mapper import EmotionMapper
    from core.camera_manager import CameraManager
    result = "主程式模組導入成功"
except ImportError as e:
    result = f"主程式模組導入失敗: {e}"
except Exception as e:
    result = f"主程式模組其他錯誤: {e}"
""")
        report.append(f"   結果: {locals().get('result', '未知錯誤')}")
    except Exception as e:
        report.append(f"   [×] 執行測試失敗: {e}")
    
    # 7. 嘗試執行基本測試
    report.append("\n7. 基本功能測試:")
    test_files = ["basic_test.py", "simple_test.py", "day5_simple_test.py"]
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=Path.cwd()
                )
                if result.returncode == 0:
                    report.append(f"   [✓] {test_file} - 執行成功")
                    if result.stdout:
                        report.append(f"       輸出: {result.stdout[:200]}...")
                else:
                    report.append(f"   [×] {test_file} - 執行失敗 (退出碼: {result.returncode})")
                    if result.stderr:
                        report.append(f"       錯誤: {result.stderr[:300]}...")
                break
            except subprocess.TimeoutExpired:
                report.append(f"   [×] {test_file} - 執行超時")
            except Exception as e:
                report.append(f"   [×] {test_file} - 執行錯誤: {e}")
        else:
            report.append(f"   [×] {test_file} - 檔案不存在")
    
    # 8. OBS 相關檢查
    report.append("\n8. OBS 相關檢查:")
    try:
        import obswebsocket
        report.append("   [✓] obswebsocket 模組可導入")
    except ImportError:
        report.append("   [×] obswebsocket 模組無法導入 - 可能需要安裝")
    
    # 9. 推薦解決方案
    report.append("\n" + "=" * 60)
    report.append("問題分析與解決建議:")
    report.append("=" * 60)
    
    if not Path("src").exists():
        report.append("\n❌ 問題 1: src 目錄不存在")
        report.append("   解決方案: 確保專案結構完整，src 目錄包含所有核心模組")
    
    report.append("\n❌ 問題 2: 模組導入失敗")
    report.append("   解決方案: ")
    report.append("   1. 檢查 requirements.txt 並安裝所有依賴")
    report.append("   2. 執行: pip install -r requirements.txt")
    report.append("   3. 確保 src 目錄下的所有模組都存在")
    
    report.append("\n❌ 問題 3: OBS 整合問題")
    report.append("   解決方案: ")
    report.append("   1. 安裝 OBS WebSocket: pip install obs-websocket-py")
    report.append("   2. 確保 OBS Studio 已安裝並啟用 WebSocket 伺服器")
    
    report.append("\n" + "=" * 60)
    report.append("建議的修復步驟:")
    report.append("=" * 60)
    report.append("1. 首先運行: pip install -r requirements.txt")
    report.append("2. 檢查並創建缺失的 src 模組檔案")
    report.append("3. 使用修復版啟動器: python launcher_fixed.py")
    report.append("4. 如果仍有問題，使用單獨測試: python basic_test.py")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        diagnostic_report = run_diagnostic()
        write_to_file(diagnostic_report)
        print("診斷完成！請檢查 diagnostic_report.txt 檔案查看詳細報告。")
    except Exception as e:
        error_msg = f"診斷過程發生錯誤: {e}\n{traceback.format_exc()}"
        write_to_file(error_msg)
        print("診斷過程發生錯誤，請檢查 diagnostic_report.txt 檔案。")
