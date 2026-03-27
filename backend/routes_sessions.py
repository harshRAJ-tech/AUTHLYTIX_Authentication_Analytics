# routes_sessions.py
# These are the API endpoints for managing sessions

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models import Session, Alert
from pydantic import BaseModel
from datetime import datetime
import uuid

# A router is like a mini app — we'll plug it into main.py
router = APIRouter(prefix="/sessions", tags=["Sessions"])


# --- This defines what data we expect when creating a session ---
class CreateSessionRequest(BaseModel):
    user_email: str
    ip_address: str = "unknown"
    user_agent: str = "unknown"


# --- CREATE a new session ---
# When a user logs in to your app, call this endpoint
@router.post("/")
def create_session(request: CreateSessionRequest, db: DBSession = Depends(get_db)):
    new_session = Session(
        id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),  # in real app this comes from your auth system
        user_email=request.user_email,
        ip_address=request.ip_address,
        user_agent=request.user_agent,
        trust_score=100.0,          # everyone starts fully trusted
        is_active=True,
        is_flagged=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "message": "Session created successfully",
        "session_id": new_session.id,
        "user_email": new_session.user_email,
        "trust_score": new_session.trust_score,
        "created_at": new_session.created_at,
    }


# --- GET all sessions ---
# The dashboard calls this to show all active sessions
@router.get("/")
def get_all_sessions(db: DBSession = Depends(get_db)):
    sessions = db.query(Session).filter(Session.is_active == True).all()

    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": s.id,
                "user_email": s.user_email,
                "trust_score": s.trust_score,
                "is_flagged": s.is_flagged,
                "ip_address": s.ip_address,
                "created_at": s.created_at,
            }
            for s in sessions
        ]
    }


# --- GET one specific session by ID ---
@router.get("/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.id,
        "user_email": session.user_email,
        "trust_score": session.trust_score,
        "is_flagged": session.is_flagged,
        "is_active": session.is_active,
        "ip_address": session.ip_address,
        "user_agent": session.user_agent,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


# --- END a session (user logs out) ---
@router.delete("/{session_id}")
def end_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.is_active = False
    session.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Session ended", "session_id": session_id}