"""
config.py — Project-wide settings and constants
Public Scheme Expenditure Anomaly & Fraud Screening
CS 276 | Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)
"""

import os

# ── Server ────────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# ── Data Generation ───────────────────────────────────────────
RANDOM_SEED       = 42
NUM_RECORDS       = 200
FRAUD_PROBABILITY = 0.15          # ~15 % of records are injected anomalies

# ── AI Thresholds ─────────────────────────────────────────────
Z_SCORE_THRESHOLD  = 3.0          # Flag if |Z| > this
IQR_MULTIPLIER     = 1.5          # Standard Tukey fence
EXTREME_SPIKE_MULT = 10           # Flag if amount > N × group mean
NEAR_ZERO_AMOUNT   = 50_000       # (₹) Flag near-zero spend

# ── Risk Score Bands (0-100) ──────────────────────────────────
RISK_CRITICAL = 70
RISK_HIGH     = 50
RISK_MEDIUM   = 25

# ── Government Domain Data ────────────────────────────────────
SCHEMES = [
    "PM Awas Yojana", "MGNREGA", "PM Kisan", "Jal Jeevan Mission",
    "Swachh Bharat Mission", "PM Poshan", "Ayushman Bharat",
    "PMGSY", "Digital India", "Skill India",
]

DEPARTMENTS = [
    "Rural Development", "Agriculture", "Health & Family Welfare",
    "Education", "Housing & Urban Affairs", "Water Resources",
    "Road Transport", "Electronics & IT", "Labour & Employment", "Finance",
]

STATES = [
    "Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh",
    "Rajasthan", "Tamil Nadu", "Karnataka", "Gujarat", "Andhra Pradesh",
    "Telangana", "Odisha", "Kerala", "Jharkhand", "Assam",
]
