import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "studio-ops-copilot"

def test_telemetry_status_endpoint():
    response = client.get("/api/telemetry/status")
    assert response.status_code == 200
    data = response.json()
    assert "render_farm" in data
    assert "livestream_premiere" in data

def test_scenario_switch_endpoint():
    response = client.post("/api/telemetry/scenario", json={"scenario": "livestream_incident"})
    assert response.status_code == 200
    data = response.json()
    assert data["new_scenario"] == "livestream_incident"

def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "Why is the overnight render queue backed up?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["tools_executed"]) > 0

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "studio_render_queue_depth" in response.text
