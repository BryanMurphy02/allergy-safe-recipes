"""
tests/test_health.py

Tests for GET /health and GET /ready.
"""
from unittest.mock import patch

from sqlalchemy.exc import OperationalError


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


def test_wait_for_db_retries_on_failure():
    """
    Confirms wait_for_db() retries the connection rather than
    failing immediately when the database isn't ready.
    """
    from database import wait_for_db
    from sqlalchemy import create_engine
    from unittest.mock import MagicMock

    call_count = 0

    def flaky_connect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise OperationalError("connection refused", None, None)
        return MagicMock().__enter__.return_value

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = flaky_connect

    with patch("database.engine", mock_engine):
        with patch("database.time.sleep"):
            wait_for_db(retries=5, delay=0)


def test_wait_for_db_raises_after_max_retries():
    """
    Confirms wait_for_db() raises RuntimeError if the database
    never becomes available within the retry limit.
    """
    import pytest
    from database import wait_for_db
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = OperationalError("connection refused", None, None)

    with patch("database.engine", mock_engine):
        with patch("database.time.sleep"):
            with pytest.raises(RuntimeError, match="Could not connect"):
                wait_for_db(retries=3, delay=0)