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

---

Built with ❤️ — from zero coding experience to a real cybersecurity product.
```

Save with `Ctrl+S`.

---

## Step 5 — Create a requirements.txt

This tells anyone who downloads your project which Python packages to install.

In VS Code → `backend` folder → New File → `requirements.txt`:
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib
redis
python-dotenv
websockets
pydantic
```

Save with `Ctrl+S`.

---

## Step 6 — Upload to GitHub

Now open your terminal. Go to the root authlytixs folder:
```
cd C:\Users\pqp28\Desktop\Authlytixs
```

Run these commands **one by one**, pressing Enter after each:

**Tell Git who you are** (use your GitHub email):
```
git config --global user.email "your@email.com"
git config --global user.name "Your Name"
```

**Initialize Git in your project:**
```
git init
```

**Stage all your files:**
```
git add .
```

**Save a snapshot (your first commit):**
```
git commit -m "Initial commit — Authlytixs MVP complete"
```

**Set the branch name:**
```
git branch -M main
```

**Connect to your GitHub repo** (replace `YOUR_USERNAME` with your GitHub username):
```
git remote add origin https://github.com/YOUR_USERNAME/authlytixs.git
```

**Upload everything:**
```
git push -u origin main
```

---

## Step 7 — GitHub will ask you to log in

A window will pop up asking for your GitHub credentials. Log in with your GitHub username and password.

If it asks for a **Personal Access Token** instead of password:
1. Go to `https://github.com/settings/tokens`
2. Click **Generate new token (classic)**
3. Give it a name, tick **repo** checkbox
4. Click **Generate token**
5. Copy the token and paste it as your password

---

## What you should see
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Writing objects: 100% (25/25), done.
Branch 'main' set up to track remote origin/main.
