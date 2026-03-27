# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from routes_sessions import router as sessions_router
from routes_websocket import router as ws_router
from routes_alerts import router as alerts_router

app = FastAPI(title="Authlytixs API", version="0.1.0")

# Allow the frontend (port 3000) to call the backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(ws_router)
app.include_router(alerts_router)

@app.on_event("startup")
def startup():
    create_tables()
    print("🚀 Authlytixs API started!")

@app.get("/health")
def health_check():
    return {
        "status": "Authlytixs is running!",
        "version": "0.1.0",
        "database": "connected"
    }
