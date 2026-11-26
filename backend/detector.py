"""
backend/detector.py — AI Anomaly Detection Engine
Public Scheme Expenditure Anomaly & Fraud Screening
CS 276 | Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)

Implements unsupervised anomaly detection using three complementary
statistical approaches, combined into a single composite risk score:

  1. Z-Score  — how many standard deviations from the group mean
  2. IQR Fence — Tukey fencing based on interquartile range
  3. Heuristic rules — domain-specific red flags
"""

import sys, os, statistics
from collections import defaultdict

# Ensure project root is on sys.path regardless of how this file is run
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import (
    Z_SCORE_THRESHOLD, IQR_MULTIPLIER, EXTREME_SPIKE_MULT,
    NEAR_ZERO_AMOUNT, RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM,
)


# ─────────────────────────────────────────────────────────────
# Baseline builder
# ─────────────────────────────────────────────────────────────

def _build_baselines(records: list[dict]) -> tuple[dict, float, float]:
    """
    Pre-compute per (scheme, state) group statistics and global fallbacks.
    Returns (baselines_dict, global_mean, global_stdev).
    """
    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in records:
        groups[(r["scheme"], r["state"])].append(r["amount"])

    baselines: dict[tuple, dict] = {}
    for key, amounts in groups.items():
        if len(amounts) < 2:
            continue
        sorted_a = sorted(amounts)
        n        = len(sorted_a)
        mean     = statistics.mean(amounts)
        stdev    = statistics.stdev(amounts) or 1.0
        q1       = sorted_a[n // 4]
        q3       = sorted_a[3 * n // 4]
        iqr      = (q3 - q1) or 1.0
        baselines[key] = {
            "mean" : mean,
            "stdev": stdev,
            "q1"   : q1,
            "q3"   : q3,
            "iqr"  : iqr,
            "count": n,
        }

    all_amounts  = [r["amount"] for r in records]
    global_mean  = statistics.mean(all_amounts)
    global_stdev = statistics.stdev(all_amounts) or 1.0
    return baselines, global_mean, global_stdev


# ─────────────────────────────────────────────────────────────
# Individual scoring helpers
# ─────────────────────────────────────────────────────────────

def _z_score(amount: float, key: tuple, baselines: dict,
             global_mean: float, global_stdev: float) -> float:
    """Absolute Z-score for *amount* relative to its group (or global)."""
    b = baselines.get(key)
    if b:
        return abs((amount - b["mean"]) / b["stdev"])
    return abs((amount - global_mean) / global_stdev)


def _iqr_deviation(amount: float, key: tuple, baselines: dict) -> float:
    """
    Returns how many IQR units outside the Tukey fence the amount is.
    Returns 0.0 if inside the fence.
    """
    b = baselines.get(key)
    if not b:
        return 0.0
    lower = b["q1"] - IQR_MULTIPLIER * b["iqr"]
    upper = b["q3"] + IQR_MULTIPLIER * b["iqr"]
    if amount > upper:
        return (amount - upper) / b["iqr"]
    if amount < lower:
        return (lower - amount) / b["iqr"]
    return 0.0


def _heuristic_flags(amount: float, key: tuple,
                     baselines: dict, global_mean: float) -> list[dict]:
    """Return a list of domain-rule flag dicts."""
    flags: list[dict] = []
    b       = baselines.get(key)
    expected = b["mean"] if b else global_mean

    z   = _z_score(amount, key, baselines, global_mean, 1.0)
    iqr = _iqr_deviation(amount, key, baselines)

    if z > Z_SCORE_THRESHOLD:
        flags.append({
            "type"  : "HIGH_Z_SCORE",
            "detail": f"Z-score = {z:.2f} (threshold: >{Z_SCORE_THRESHOLD})",
        })
    if iqr > IQR_MULTIPLIER:
        flags.append({
            "type"  : "IQR_OUTLIER",
            "detail": f"Amount is {iqr:.1f}× outside the interquartile fence",
        })
    if amount < NEAR_ZERO_AMOUNT:
        flags.append({
            "type"  : "NEAR_ZERO_SPEND",
            "detail": "Expenditure near zero — possible data suppression or misappropriation",
        })
    if expected and amount > expected * EXTREME_SPIKE_MULT:
        flags.append({
            "type"  : "EXTREME_SPIKE",
            "detail": f"Amount is {amount / expected:.1f}× the scheme-state average",
        })
    return flags


# ─────────────────────────────────────────────────────────────
# Risk labelling
# ─────────────────────────────────────────────────────────────

def _risk_label(score: float) -> str:
    if score >= RISK_CRITICAL: return "CRITICAL"
    if score >= RISK_HIGH:     return "HIGH"
    if score >= RISK_MEDIUM:   return "MEDIUM"
    return "LOW"


def _confidence(count: int) -> str:
    if count >= 10: return "HIGH"
    if count >= 5:  return "MEDIUM"
    return "LOW"


# ─────────────────────────────────────────────────────────────
# Explanation & Recommendation generators
# ─────────────────────────────────────────────────────────────

def _explain(record: dict, z: float, iqr_dev: float,
             flags: list[dict], risk_label: str,
             expected: float, dev_pct: float) -> str:
    lines = [
        f"Record #{record['id']} under '{record['scheme']}' in {record['state']} "
        f"reported ₹{record['amount']:,.0f} on {record['date']}.",
        f"The expected spend for this scheme-state group is ~₹{expected:,.0f}. "
        f"This record deviates by {dev_pct:+.1f}%.",
    ]
    if z > Z_SCORE_THRESHOLD:
        lines.append(
            f"Statistical Z-score of {z:.2f} indicates a rare outlier (>{Z_SCORE_THRESHOLD}σ from mean)."
        )
    if iqr_dev > IQR_MULTIPLIER:
        lines.append(f"The amount falls {iqr_dev:.1f}× outside the interquartile fence.")
    for f in flags:
        lines.append(f"⚑ {f['type']}: {f['detail']}")
    lines.append(f"Overall Risk Level: {risk_label}")
    return " ".join(lines)


def _recommend(risk_label: str, flags: list[dict]) -> str:
    base = {
        "CRITICAL": "Immediately escalate to audit authority. Freeze disbursement pending investigation.",
        "HIGH"    : "Flag for senior officer review. Request supporting documents and voucher verification.",
        "MEDIUM"  : "Schedule for routine audit in next cycle. Monitor subsequent quarters.",
        "LOW"     : "No immediate action required. Continue standard monitoring.",
    }[risk_label]

    extras = []
    types  = {f["type"] for f in flags}
    if "NEAR_ZERO_SPEND" in types:
        extras.append("Verify funds were not misappropriated through off-book transfers.")
    if "EXTREME_SPIKE" in types:
        extras.append("Cross-check with physical project completion reports.")
    if "HIGH_Z_SCORE" in types and "EXTREME_SPIKE" not in types:
        extras.append("Compare with same-quarter data from prior years.")

    return base + (" " + " ".join(extras) if extras else "")


# ─────────────────────────────────────────────────────────────
# Public AnomalyDetector class
# ─────────────────────────────────────────────────────────────

class AnomalyDetector:
    """
    Analyses expenditure records for anomalies.

    Usage:
        detector = AnomalyDetector(records)
        result   = detector.analyze(record)   # single record
        summary  = detector.screen_all()       # all records
    """

    def __init__(self, records: list[dict]) -> None:
        self.records = records
        self.baselines, self.global_mean, self.global_stdev = \
            _build_baselines(records)

    # ── Single-record analysis ────────────────────────────────

    def analyze(self, record: dict) -> dict:
        """Return a full anomaly analysis dict for one record."""
        key    = (record["scheme"], record["state"])
        amount = record["amount"]
        b      = self.baselines.get(key, {})

        z       = _z_score(amount, key, self.baselines, self.global_mean, self.global_stdev)
        iqr_dev = _iqr_deviation(amount, key, self.baselines)
        flags   = _heuristic_flags(amount, key, self.baselines, self.global_mean)

        expected   = b.get("mean", self.global_mean)
        dev_pct    = round((amount - expected) / expected * 100, 1) if expected else 0

        # Composite risk score (0-100)
        risk_raw   = min(100.0, z * 10 + iqr_dev * 5 + len(flags) * 10)
        risk_score = round(risk_raw, 1)
        label      = _risk_label(risk_score)

        return {
            "record_id"       : record["id"],
            "risk_score"      : risk_score,
            "risk_level"      : label,
            "z_score"         : round(z, 3),
            "iqr_deviation"   : round(iqr_dev, 3),
            "expected_amount" : round(expected, 2),
            "deviation_percent": dev_pct,
            "flags"           : flags,
            "explanation"     : _explain(record, z, iqr_dev, flags, label, expected, dev_pct),
            "recommendation"  : _recommend(label, flags),
            "confidence"      : _confidence(b.get("count", 0)),
        }

    # ── Batch screening ───────────────────────────────────────

    def screen_all(self) -> dict:
        """Run screening on every record. Returns summary + per-record results."""
        results = [{**r, "analysis": self.analyze(r)} for r in self.records]

        flagged      = [x for x in results if x["analysis"]["risk_level"] in ("HIGH", "CRITICAL")]
        total_spend  = sum(r["amount"] for r in self.records)
        flagged_spend = sum(x["amount"] for x in flagged)

        return {
            "total_records" : len(results),
            "total_flagged" : len(flagged),
            "total_spend"   : round(total_spend, 2),
            "flagged_spend" : round(flagged_spend, 2),
            "flag_rate_pct" : round(len(flagged) / len(results) * 100, 1),
            "results"       : results,
            "flagged"       : flagged,
        }
