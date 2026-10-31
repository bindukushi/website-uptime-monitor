"""Unit tests for monitor.py.

We replace requests.get with a mock so tests are fast and don't need internet.
(The mock is only used in tests. The real app always makes real requests.)
"""

from unittest.mock import MagicMock, patch

import requests

import monitor


def fake_response(status_code):
    resp = MagicMock()
    resp.status_code = status_code
    return resp


@patch("monitor.requests.get")
def test_up_on_200(mock_get):
    mock_get.return_value = fake_response(200)
    result = monitor.check_website("https://example.com")
    assert result["status"] == "UP"
    assert result["status_code"] == 200
    assert isinstance(result["response_time_ms"], int)
    assert result["error"] is None


@patch("monitor.requests.get")
def test_down_on_500(mock_get):
    mock_get.return_value = fake_response(500)
    result = monitor.check_website("https://example.com")
    assert result["status"] == "DOWN"
    assert result["status_code"] == 500
    assert result["error"] == "HTTP 500"


@patch("monitor.requests.get", side_effect=requests.exceptions.Timeout)
def test_timeout_is_down(mock_get):
    result = monitor.check_website("https://example.com", timeout=2)
    assert result["status"] == "DOWN"
    assert result["status_code"] is None
    assert "Timed out" in result["error"]


@patch("monitor.requests.get", side_effect=requests.exceptions.ConnectionError)
def test_connection_error_is_down(mock_get):
    result = monitor.check_website("https://example.com")
    assert result["status"] == "DOWN"
    assert "Connection failed" in result["error"]


@patch("monitor.requests.get")
def test_report_summary(mock_get):
    mock_get.side_effect = [fake_response(200), fake_response(503)]
    # Threads may finish in any order, so we only check the totals.
    report = monitor.build_report(["https://a.com", "https://b.com"])
    assert report["summary"] == {"total": 2, "up": 1, "down": 1}


def test_empty_site_list():
    assert monitor.check_all([]) == []


def test_get_sites_from_env(monkeypatch):
    monkeypatch.setenv("MONITOR_SITES", "https://a.com, https://b.com")
    assert monitor.get_sites() == ["https://a.com", "https://b.com"]


def test_get_sites_default(monkeypatch):
    monkeypatch.delenv("MONITOR_SITES", raising=False)
    assert monitor.get_sites() == monitor.DEFAULT_SITES
