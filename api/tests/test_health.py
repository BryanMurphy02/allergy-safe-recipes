"""
tests/test_health.py

Tests for GET /health and GET /ready.
"""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_ready_returns_200_when_db_connected(client):
    response = client.get("/ready")
    assert response.status_code == 200


def test_ready_returns_connected_status(client):
    response = client.get("/ready")
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"