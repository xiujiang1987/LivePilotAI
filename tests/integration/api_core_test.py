import pytest
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
