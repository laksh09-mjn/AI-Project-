"""
backend/routes.py — Flask API route definitions
Public Scheme Expenditure Anomaly & Fraud Screening
CS 276 | Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)

All REST endpoints are registered on a Blueprint so that app.py stays lean.

Endpoints
---------
GET  /api/summary              — Dashboard summary stats
GET  /api/records              — Paginated + filtered record list
GET  /api/flagged              — Only HIGH/CRITICAL risk records
GET  /api/analyze/<id>         — Deep analysis of one record by ID
POST /api/analyze/custom       — Analyze a user-submitted record
GET  /api/schemes              — List of scheme names
GET  /api/states               — List of state names
"""

import sys, os
from datetime import datetime
from flask import Blueprint, jsonify, request

# Ensure project root is on sys.path regardless of how this file is run
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from backend.data     import RECORDS
from backend.detector import AnomalyDetector
from config           import SCHEMES, STATES

# ── Blueprint & Singleton ─────────────────────────────────────
api_bp   = Blueprint("api", __name__, url_prefix="/api")
detector = AnomalyDetector(RECORDS)      # built once at import time


# ── Helpers ───────────────────────────────────────────────────

def _screen_cache() -> dict:
    """Return a fresh screen_all() result (stateless; dataset is fixed)."""
    return detector.screen_all()


# ── Routes ───────────────────────────────────────────────────

@api_bp.route("/summary")
def summary():
    """High-level dashboard statistics."""
    sc = _screen_cache()

    by_scheme: dict = {}
    by_state: dict  = {}

    for r in sc["results"]:
        risk_flagged = r["analysis"]["risk_level"] in ("HIGH", "CRITICAL")

        s = r["scheme"]
        by_scheme.setdefault(s, {"total": 0, "flagged": 0, "spend": 0.0})
        by_scheme[s]["total"]  += 1
        by_scheme[s]["spend"]  += r["amount"]
        if risk_flagged:
            by_scheme[s]["flagged"] += 1

        st = r["state"]
        by_state.setdefault(st, {"total": 0, "flagged": 0, "spend": 0.0})
        by_state[st]["total"]  += 1
        by_state[st]["spend"]  += r["amount"]
        if risk_flagged:
            by_state[st]["flagged"] += 1

    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for r in sc["results"]:
        risk_dist[r["analysis"]["risk_level"]] += 1

    return jsonify({
        "total_records"   : sc["total_records"],
        "total_flagged"   : sc["total_flagged"],
        "total_spend_cr"  : round(sc["total_spend"]   / 1e7, 2),
        "flagged_spend_cr": round(sc["flagged_spend"]  / 1e7, 2),
        "flag_rate_pct"   : sc["flag_rate_pct"],
        "risk_distribution": risk_dist,
        "by_scheme"       : by_scheme,
        "by_state"        : by_state,
        "last_updated"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


@api_bp.route("/records")
def records():
    """
    Paginated list of all records with optional filters.

    Query params:
        scheme, state, risk  — substring / exact filter values
        page                 — 1-based page number  (default: 1)
        per_page             — items per page       (default: 20)
    """
    scheme   = request.args.get("scheme",   "").strip().lower()
    state    = request.args.get("state",    "").strip().lower()
    risk     = request.args.get("risk",     "").strip().upper()
    page     = max(1, int(request.args.get("page",     1)))
    per_page = max(1, int(request.args.get("per_page", 20)))

    results = _screen_cache()["results"]

    if scheme:
        results = [r for r in results if scheme in r["scheme"].lower()]
    if state:
        results = [r for r in results if state  in r["state"].lower()]
    if risk:
        results = [r for r in results if r["analysis"]["risk_level"] == risk]

    total  = len(results)
    start  = (page - 1) * per_page
    paged  = results[start : start + per_page]

    return jsonify({
        "total"   : total,
        "page"    : page,
        "per_page": per_page,
        "records" : paged,
    })


@api_bp.route("/flagged")
def flagged():
    """Return only HIGH and CRITICAL risk records."""
    sc = _screen_cache()
    return jsonify({
        "total_flagged"   : sc["total_flagged"],
        "flagged_spend_cr": round(sc["flagged_spend"] / 1e7, 2),
        "records"         : sc["flagged"],
    })


@api_bp.route("/analyze/<int:record_id>")
def analyze_by_id(record_id: int):
    """Deep analysis for one record by its numeric ID."""
    record = next((r for r in RECORDS if r["id"] == record_id), None)
    if record is None:
        return jsonify({"error": f"Record {record_id} not found"}), 404
    return jsonify({**record, "analysis": detector.analyze(record)})


@api_bp.route("/analyze/custom", methods=["POST"])
def analyze_custom():
    """
    Analyze a user-submitted expenditure record.

    Expected JSON body:
        { "scheme": str, "state": str, "amount": number, "date": "YYYY-MM-DD",
          "department"?: str, "officer"?: str, "voucher_id"?: str }
    """
    data = request.get_json(force=True, silent=True) or {}
    required = ["scheme", "state", "amount", "date"]
    missing  = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    record = {
        "id"          : 9999,
        "scheme"      : str(data["scheme"]),
        "department"  : str(data.get("department", "Unknown")),
        "state"       : str(data["state"]),
        "amount"      : float(data["amount"]),
        "date"        : str(data["date"]),
        "quarter"     : str(data.get("quarter", "Q1 2024")),
        "officer"     : str(data.get("officer",     "Unknown")),
        "voucher_id"  : str(data.get("voucher_id",  "VCH-00000")),
        "is_anomaly"  : False,
        "anomaly_type": "unknown",
        "note"        : "",
    }
    return jsonify({**record, "analysis": detector.analyze(record)})


@api_bp.route("/schemes")
def schemes():
    return jsonify({"schemes": SCHEMES})


@api_bp.route("/states")
def states():
    return jsonify({"states": STATES})
