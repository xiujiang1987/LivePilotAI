import pytest
from fastapi.testclient import TestClient
from src.api.server import create_app

@pytest.fixture
def api_client():
    """Fixture to provide a TestClient instance for the FastAPI app."""
    app = create_app()
    return TestClient(app)

def test_health_check(api_client):
    """Test the /api/v1/health endpoint."""
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
