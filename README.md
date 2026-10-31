# Website Uptime Monitor

A Flask web app that checks whether websites are up, measures response time, and shows the results on a responsive dashboard. Built as a beginner-friendly DevOps portfolio project.

## Features

- Monitors multiple websites in parallel
- Shows **UP / DOWN**, HTTP status code and response time (ms)
- Handles timeouts and connection errors
- Responsive dashboard with summary cards, colour-coded status and a manual refresh button (also auto-refreshes every 30 seconds)
- REST API: `GET /api/status` and `GET /health`
- Site list and timeout configurable through environment variables
- Automated tests with Pytest

## Project Status

| Phase | Topic | Status |
|---|---|---|
| 1 | Python app, dashboard, Pytest | Done |
| 2 | Linux and Bash scripts | Planned |
| 3 | Docker and Docker Compose | Planned |
| 4 | Kubernetes (Minikube) | Planned |
| 5 | GitHub Actions CI/CD | Planned |
| 6 | Terraform and Ansible | Planned |

This README will be updated as each phase is completed and tested.

## Tech Stack

- **Backend:** Python, Flask, Requests
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** Pytest
- **DevOps (planned):** Docker, Kubernetes, GitHub Actions, Terraform, Ansible

## Architecture

```
Browser
   |
   |  GET /            -> dashboard (HTML, CSS, JS)
   |  GET /api/status  -> live checks, returns JSON
   v
Flask app (app.py)
   |
   v
monitor.py  --- HTTP requests --->  Monitored websites
```

## Folder Structure

```
website-uptime-monitor/
├── app.py              # Flask routes
├── monitor.py          # Website checking logic
├── requirements.txt    # Python dependencies (pinned)
├── pytest.ini          # Pytest settings
├── templates/
│   └── index.html      # Dashboard page
├── static/
│   ├── style.css       # Dashboard styling
│   └── app.js          # Fetches /api/status and renders the table
└── tests/
    ├── test_monitor.py # Tests for checking logic
    └── test_app.py     # Tests for API routes
```

## Run Locally (Windows PowerShell)

Requires Python 3.10 or newer.

```powershell
cd website-uptime-monitor
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

If PowerShell blocks the activate script, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Run Locally (Linux / macOS)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Run the Tests

```powershell
pytest -v
```

The tests mock `requests.get`, so they run offline. The application itself always makes real requests.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MONITOR_SITES` | 4 built-in sites | Comma-separated list of URLs to monitor |
| `MONITOR_TIMEOUT` | `5` | Request timeout in seconds |
| `HOST` | `127.0.0.1` | Interface the app listens on |
| `PORT` | `5000` | Port the app listens on |
| `FLASK_DEBUG` | off | Set to `1` for debug mode (development only) |

Example (PowerShell):

```powershell
$env:MONITOR_SITES = "https://github.com,https://example.com"
$env:MONITOR_TIMEOUT = "3"
python app.py
```

## API

### `GET /health`

Liveness check.

```json
{"status": "healthy"}
```

### `GET /api/status`

Runs live checks and returns the results.

```json
{
  "checked_at": "2026-10-31T14:21:39+00:00",
  "summary": {"total": 4, "up": 3, "down": 1},
  "websites": [
    {
      "name": "github.com",
      "url": "https://github.com",
      "status": "UP",
      "status_code": 200,
      "response_time_ms": 97,
      "error": null,
      "checked_at": "2026-10-31T14:21:38+00:00"
    }
  ]
}
```

A site is **UP** when it returns an HTTP status below 400. It is **DOWN** for status 400 and above, timeouts and connection failures (the `error` field explains why).

## Security Notes

- No credentials or API keys are stored in the code.
- Keep secrets in environment variables or a `.env` file. `.env` is listed in `.gitignore`.
- The dashboard builds the table with `textContent`, not `innerHTML`, to avoid HTML injection.
- `python app.py` uses Flask's development server. Production serving (Gunicorn) is added in the Docker phase.

## License

MIT (add a LICENSE file before publishing).
