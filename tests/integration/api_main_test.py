import pytest
import time
import requests
import threading

def test_api_integration_with_main_app():
    """Test that the API server starts and runs properly inside LivePilotAIApp"""
    # Import inside the test to avoid Tkinter issues during collection
    from main import LivePilotAIApp
    import tkinter as tk
    
    # Initialize basic app structure without launching full mainloop
    root = tk.Tk()
    
    try:
        app = LivePilotAIApp()
        
        # We only call _start_api_server instead of initialize to avoid
        # loading heavylifting camera/AI components inside tests
        # Bind root manually
        app.root = root
        
        # 模擬 _init_components 的一些行為，避免依賴模型權重
        from src.api.server import app as fastapi_app
        fastapi_app.state.main_app = app
        app.is_running = True
        
        # Start API server directly
        app._start_api_server()
        
        # Wait for the server to start (max 5 seconds)
        max_retries = 10
        api_ready = False
        
        for _ in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/api/v1/health")
                if response.status_code == 200:
                    api_ready = True
                    # Validate that is_running is reflecting state correctly
                    data = response.json()
                    assert data["is_running"] is True
                    break
            except requests.ConnectionError:
                pass
            time.sleep(0.5)
            
        assert api_ready, "API server did not start in the background thread within timeout"
        
    finally:
        # Proper cleanup
        root.destroy()
