"""Monitoring logic: checks websites and builds a report. No Flask code here."""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

# Real sites used when MONITOR_SITES is not set.
# The last one deliberately answers with HTTP 500 so you can see a real DOWN result.
DEFAULT_SITES = [
    "https://www.google.com",
    "https://github.com",
    "https://www.python.org",
    "https://httpbin.org/status/500",
]
DEFAULT_TIMEOUT = 5  # seconds


def get_sites():
    """Read the site list from the MONITOR_SITES env var (comma separated)."""
    raw = os.getenv("MONITOR_SITES", "")
    sites = [s.strip() for s in raw.split(",") if s.strip()]
    return sites or DEFAULT_SITES


def get_timeout():
    """Read the request timeout (seconds) from MONITOR_TIMEOUT."""
    try:
        return float(os.getenv("MONITOR_TIMEOUT", DEFAULT_TIMEOUT))
    except ValueError:
        return DEFAULT_TIMEOUT


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_website(url, timeout=DEFAULT_TIMEOUT):
    """Check one website and return a dictionary describing the result."""
    result = {
        "name": urlparse(url).netloc or url,
        "url": url,
        "status": "DOWN",
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "checked_at": _now(),
    }

    start = time.perf_counter()
    try:
        response = requests.get(
            url, timeout=timeout, headers={"User-Agent": "UptimeMonitor/1.0"}
        )
        result["response_time_ms"] = round((time.perf_counter() - start) * 1000)
        result["status_code"] = response.status_code
        response.close()

        if response.status_code < 400:
            result["status"] = "UP"
        else:
            result["error"] = f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        result["error"] = f"Timed out after {timeout:g}s"
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection failed (DNS or network error)"
    except requests.exceptions.RequestException as exc:
        result["error"] = f"Request error: {type(exc).__name__}"

    return result


def check_all(urls, timeout=DEFAULT_TIMEOUT):
    """Check many websites at the same time (threads) so one slow site doesn't block the rest."""
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=min(10, len(urls))) as pool:
        return list(pool.map(lambda u: check_website(u, timeout), urls))


def build_report(urls, timeout=DEFAULT_TIMEOUT):
    """Run all checks and return results plus a summary."""
    websites = check_all(urls, timeout)
    up = sum(1 for w in websites if w["status"] == "UP")
    return {
        "checked_at": _now(),
        "summary": {"total": len(websites), "up": up, "down": len(websites) - up},
        "websites": websites,
    }
