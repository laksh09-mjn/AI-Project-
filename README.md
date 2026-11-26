# GovWatch AI — Quick Start

## Public Scheme Expenditure Anomaly & Fraud Screening
**Authors:** Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)  
**Course:** CS 276 | Group: 3P25L

---

## 🚀 How to Run

### 1. Install dependencies
```
pip install flask flask-cors
```

### 2. Start the server
```
python app.py
```

### 3. Open the app in your browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
ai project/
│
├── app.py               ← 🟢 Entry point — run this
├── config.py            ← All settings, thresholds & constants
├── requirements.txt     ← Python dependencies
├── README.md
│
├── backend/             ← Python AI backend package
│   ├── __init__.py
│   ├── data.py          ← Synthetic government expenditure data generator
│   ├── detector.py      ← AI anomaly detection engine (Z-Score, IQR, heuristics)
│   └── routes.py        ← Flask Blueprint with all REST API endpoints
│
└── frontend/            ← Browser UI (served by Flask)
    ├── index.html       ← Dashboard layout & tabs
    ├── style.css        ← Styling
    └── app.js           ← Chart.js charts, API calls, interaction logic
```

---

## 🧠 AI Methods (`backend/detector.py`)

| Method | Description |
|--------|-------------|
| **Z-Score** | Per scheme–state group outlier detection (σ threshold = 3.0) |
| **IQR Fencing** | Tukey fence: flag if > 1.5× IQR outside Q1/Q3 |
| **Heuristic Rules** | Near-zero spend, extreme spikes, irregular patterns |
| **Composite Score** | 0–100 risk score → LOW / MEDIUM / HIGH / CRITICAL |
| **Explainability** | Plain-language reason + recommendation per record |

---

## 🔌 API Endpoints (`backend/routes.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/summary` | GET | Dashboard summary statistics |
| `/api/records` | GET | Paginated records with optional filters |
| `/api/flagged` | GET | Only HIGH/CRITICAL risk records |
| `/api/analyze/<id>` | GET | Deep analysis of one record by ID |
| `/api/analyze/custom` | POST | Analyze a custom record submitted by the user |
| `/api/schemes` | GET | List of all scheme names |
| `/api/states` | GET | List of all state names |

---

## ⚙️ Configuration (`config.py`)

All tunable parameters live in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `Z_SCORE_THRESHOLD` | `3.0` | Z-score above which a record is flagged |
| `IQR_MULTIPLIER` | `1.5` | Tukey fence multiplier |
| `EXTREME_SPIKE_MULT` | `10` | Flag if amount > N× group mean |
| `NEAR_ZERO_AMOUNT` | `₹50,000` | Flag near-zero spend |
| `FRAUD_PROBABILITY` | `0.15` | Synthetic anomaly injection rate |
| `NUM_RECORDS` | `200` | Dataset size |

---

> ⚠️ **Disclaimer:** Anomaly flags are risk signals, not confirmed fraud or wrongdoing.
> All flags require appropriate human verification before any action is taken.
> This is a prototype for CS 276.
