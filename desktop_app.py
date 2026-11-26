"""
desktop_app.py — Standalone Desktop Application Launcher
Scheme Anomaly Screen (Public Scheme Expenditure Anomaly & Fraud Screening)
Authors: Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)

Starts the Flask backend and opens the UI as a separate standalone
application window (no browser tabs or address bar).
"""

import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
import urllib.request
import webbrowser

_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import PORT
from app import create_app


APP_URL = f"http://127.0.0.1:{PORT}"


def _is_server_up() -> bool:
    try:
        with urllib.request.urlopen(f"{APP_URL}/api/summary", timeout=1.2) as res:
            return res.status == 200
    except Exception:
        return False


def _start_backend_thread() -> None:
    flask_app = create_app()

    def _run():
        flask_app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    for _ in range(40):
        if _is_server_up():
            return
        time.sleep(0.25)


def _find_browser_exe() -> str | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("msedge"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def main() -> None:
    if not _is_server_up():
        print("Starting Scheme Anomaly Screen backend...")
        _start_backend_thread()

    exe = _find_browser_exe()
    if exe:
        profile_dir = os.path.join(tempfile.gettempdir(), "SchemeAnomalyScreenApp")
        os.makedirs(profile_dir, exist_ok=True)
        print(f"Launching standalone application window ({os.path.basename(exe)})...")
        proc = subprocess.Popen([
            exe,
            f"--app={APP_URL}",
            f"--user-data-dir={profile_dir}",
            "--window-size=1380,880",
            "--no-first-run",
            "--no-default-browser-check",
        ])
        proc.wait()
    else:
        print(f"Opening {APP_URL} in default browser...")
        webbrowser.open(APP_URL)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
