# Authlytixs 🛡️

**Continuous Identity Integrity Platform for Zero Trust Environments**

Authlytixs continuously verifies user identity during active sessions using 
behavioral biometrics and ML-based anomaly detection — detecting session 
hijacking and identity drift in real-time.

---

## What it does

- 🧠 **ML Trust Scoring** — Isolation Forest model scores user behavior 0–100
- ⚡ **Real-time** — WebSocket streams behavioral events, scores in <50ms  
- 🚨 **Auto Alerts** — fires when trust score drops below threshold
- 📊 **Live Dashboard** — React UI showing all sessions and alerts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| ML | scikit-learn (Isolation Forest) |
| Frontend | Next.js + React |
| Realtime | WebSockets |
| Infra | Docker |

---

## Project Structure
```
authlytixs/
├── backend/          # FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── routes_sessions.py
│   ├── routes_websocket.py
│   └── routes_alerts.py
├── ml/               # ML pipeline
│   ├── train.py
│   └── inference.py
├── frontend/         # Next.js dashboard
└── docker-compose.yml
```

---

## Quick Start

### 1. Start the database
```bash
docker-compose up -d
```

### 2. Train the ML model
```bash
cd ml
python train.py
```

### 3. Start the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Start the dashboard
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`


