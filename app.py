"""Flask web app: serves the dashboard and the REST API."""

import os

from flask import Flask, jsonify, render_template

from monitor import build_report, get_sites, get_timeout

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """Run live checks now and return the results as JSON."""
    return jsonify(build_report(get_sites(), get_timeout()))


@app.route("/health")
def health():
    """Lightweight liveness check (Docker/Kubernetes will use this later)."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
