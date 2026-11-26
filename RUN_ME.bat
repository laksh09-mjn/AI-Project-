@echo off
title Scheme Anomaly Screen
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python from python.org
    pause
    exit /b 1
)

pip install flask flask-cors --quiet
python desktop_app.py
