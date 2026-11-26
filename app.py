"""
app.py — Application entry point
Public Scheme Expenditure Anomaly & Fraud Screening
CS 276 | Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)

Run:
    python app.py

Then open:  http://localhost:5000
"""

import sys, os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Always run from the project root so all imports resolve correctly
_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config         import HOST, PORT, DEBUG, FRONTEND_DIR
from backend.routes import api_bp


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__, static_folder=FRONTEND_DIR)
    CORS(app)

    # Register the API blueprint (all routes under /api/...)
    app.register_blueprint(api_bp)

    # Serve the frontend for every non-API request
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path: str):
        import os
        target = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(target):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("  GovWatch AI — Public Scheme Fraud Screening")
    print("  Authors : Laksh Mahajan & Sankalp Jeet Singh")
    print(f"  Server  : http://localhost:{PORT}")
    print("=" * 60)
    app.run(host=HOST, port=PORT, debug=DEBUG)
