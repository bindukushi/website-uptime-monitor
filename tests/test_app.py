"""Tests for the Flask routes."""

from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Website Uptime Monitor" in response.data


def test_api_status_shape(client):
    fake_report = {
        "checked_at": "2026-01-01T00:00:00+00:00",
        "summary": {"total": 1, "up": 1, "down": 0},
        "websites": [{"name": "example.com", "status": "UP"}],
    }
    with patch("app.build_report", return_value=fake_report):
        response = client.get("/api/status")
    data = response.get_json()
    assert response.status_code == 200
    assert set(data) == {"checked_at", "summary", "websites"}
    assert data["summary"]["total"] == 1
