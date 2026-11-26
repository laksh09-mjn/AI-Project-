"""
ai .py — Legacy entry point (kept for compatibility)
------------------------------------------------------
The project has been refactored into a clean multi-file structure.
Please run  `app.py`  instead:

    python app.py

File layout
-----------
app.py              ← NEW entry point (run this)
config.py           ← All settings & constants
backend/
    __init__.py
    data.py         ← Synthetic data generator
    detector.py     ← AI anomaly detection engine (Z-score, IQR, heuristics)
    routes.py       ← Flask API blueprints & endpoints
frontend/
    index.html      ← Dashboard UI
    style.css       ← Styling
    app.js          ← Frontend logic & Chart.js charts
"""

# Forward to the new entry point for convenience
import runpy, os, sys

entry = os.path.join(os.path.dirname(__file__), "app.py")
sys.argv[0] = entry
runpy.run_path(entry, run_name="__main__")
