"""
backend/data.py — Synthetic government expenditure data generator
Public Scheme Expenditure Anomaly & Fraud Screening
CS 276 | Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)

Generates a reproducible in-memory dataset of 200 public scheme
expenditure records, injecting realistic anomaly patterns in ~15 % of them.
"""

import sys, os, random
from datetime import datetime, timedelta

# Ensure project root is on sys.path regardless of how this file is run
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import (
    RANDOM_SEED, NUM_RECORDS, FRAUD_PROBABILITY,
    SCHEMES, DEPARTMENTS, STATES,
)

# Anomaly types and their human-readable labels
ANOMALY_TYPES = {
    "high_spike" : "Unusually high expenditure spike",
    "low_dip"    : "Near-zero spending in active quarter",
    "duplicate"  : "Potential duplicate payment",
    "irregular"  : "Irregular expenditure pattern",
}


def _make_record(idx: int, rng: random.Random, base_date: datetime) -> dict:
    """Create one expenditure record (normal or anomalous)."""
    scheme = rng.choice(SCHEMES)
    dept   = rng.choice(DEPARTMENTS)
    state  = rng.choice(STATES)

    base_amount = rng.uniform(1_000_000, 50_000_000)   # ₹10 L – ₹500 L
    is_fraud    = rng.random() < FRAUD_PROBABILITY

    if is_fraud:
        atype = rng.choice(list(ANOMALY_TYPES))
        if atype == "high_spike":
            amount = base_amount * rng.uniform(5, 20)
        elif atype == "low_dip":
            amount = base_amount * rng.uniform(0.01, 0.05)
        elif atype == "duplicate":
            amount = base_amount                           # exact repeat
        else:                                              # irregular
            amount = base_amount * rng.uniform(2, 4)
        note = ANOMALY_TYPES[atype]
    else:
        atype  = "normal"
        amount = base_amount * rng.uniform(0.8, 1.2)
        note   = ""

    date_offset = timedelta(days=rng.randint(0, 364))
    record_date = base_date + date_offset
    quarter     = f"Q{(record_date.month - 1) // 3 + 1} {record_date.year}"

    return {
        "id"          : idx + 1,
        "scheme"      : scheme,
        "department"  : dept,
        "state"       : state,
        "amount"      : round(amount, 2),
        "date"        : record_date.strftime("%Y-%m-%d"),
        "quarter"     : quarter,
        "is_anomaly"  : is_fraud,
        "anomaly_type": atype,
        "note"        : note,
        "officer"     : f"Officer-{rng.randint(100, 999)}",
        "voucher_id"  : f"VCH-{rng.randint(10_000, 99_999)}",
    }


def generate_records(n: int = NUM_RECORDS) -> list[dict]:
    """Return a reproducible list of *n* expenditure records."""
    rng        = random.Random(RANDOM_SEED)
    base_date  = datetime(2024, 1, 1)
    return [_make_record(i, rng, base_date) for i in range(n)]


# Module-level singleton — imported by other modules
RECORDS: list[dict] = generate_records()
