import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.api.server import create_app

@pytest.fixture
def api_client():
    app = create_app()
    return TestClient(app)

def test_system_status_without_main_app(api_client):
    """Test /api/v1/status without main app bound"""
    response = api_client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_running"] is False
    assert data["ai_active"] is False

def test_emotion_without_main_app(api_client):
    """Test /api/v1/emotion without main app bound"""
    response = api_client.get("/api/v1/emotion")
    assert response.status_code == 503

def test_emotion_with_mocked_app(api_client):
    """Test /api/v1/emotion with mocked real-time detector data"""
    mock_app = MagicMock()
    mock_app.is_running = True
    
    # Mock real_time_detector and its results
    mock_rt_detector = MagicMock()
    mock_face = MagicMock()
    mock_face.emotion = "happy"
    mock_face.confidence = 0.95
    mock_face.emotions_distribution = {"happy": 0.95, "neutral": 0.05}
    
    mock_rt_detector.get_latest_results.return_value = [mock_face]
    mock_rt_detector.get_performance_stats.return_value = {"current_fps": 24.5}
    
    mock_app.ai_director.real_time_detector = mock_rt_detector
    
    # Bind mock to fastapi state
    api_client.app.state.main_app = mock_app
    
    response = api_client.get("/api/v1/emotion")
    assert response.status_code == 200
    data = response.json()
    assert data["dominant_emotion"] == "happy"
    assert data["confidence"] == 0.95
    assert data["engine_fps"] == 24.5
    assert data["raw_scores"] == {"happy": 0.95, "neutral": 0.05}

def test_system_command_stop_ai(api_client):
    """Test /api/v1/system command to stop AI"""
    mock_app = MagicMock()
    api_client.app.state.main_app = mock_app
    
    response = api_client.post("/api/v1/system", json={"command": "stop_ai"})
    assert response.status_code == 200
    assert response.json() == {"message": "AI Engine stopped successfully"}
    
    # Verify the mock methods were called
    mock_app.camera_manager.stop.assert_called_once()
    mock_app.voice_commander.stop.assert_called_once()
    
def test_system_command_invalid(api_client):
    """Test /api/v1/system with an invalid command"""
    mock_app = MagicMock()
    api_client.app.state.main_app = mock_app
    
    response = api_client.post("/api/v1/system", json={"command": "unknown_cmd"})
    assert response.status_code == 400
    assert "Unknown command" in response.json()["detail"]
