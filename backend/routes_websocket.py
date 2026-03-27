# routes_websocket.py
# This is the real-time endpoint — the core of Authlytixs
# A browser connects here and streams behavior events
# We score them instantly and send back a trust score

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal
from models import Session, TrustScoreHistory, Alert
from datetime import datetime
import json, sys, os

# Tell Python where to find our ML code
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
from inference import score_from_events

router = APIRouter(tags=["WebSocket"])

ALERT_THRESHOLD = 40  # if trust score drops below 40, fire an alert


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    The browser connects here and keeps the connection open.
    Every 250ms the browser sends a batch of events.
    We score them and send back the trust score instantly.
    """
    await websocket.accept()
    print(f"🔌 WebSocket connected: session {session_id}")

    db: DBSession = SessionLocal()

    try:
        # Check the session exists
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            await websocket.send_json({
                "error": "Session not found",
                "session_id": session_id
            })
            await websocket.close()
            return

        # Send a welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Authlytixs monitoring started",
            "session_id": session_id,
            "current_trust_score": session.trust_score
        })

        # Keep listening for events until connection closes
        async for message in websocket.iter_text():
            try:
                # Parse the incoming data
                payload = json.loads(message)
                events = payload.get("events", [])

                if not events:
                    continue

                # 🧠 Score the behavior using ML
                result = score_from_events(events)
                trust_score = result["trust_score"]

                # Save score to history (for the timeline chart)
                history = TrustScoreHistory(
                    session_id=session_id,
                    trust_score=trust_score,
                    is_anomaly=result["is_anomaly"],
                    raw_score=result["raw_score"],
                    recorded_at=datetime.utcnow()
                )
                db.add(history)

                # Update the session's current trust score
                session.trust_score = trust_score
                session.updated_at = datetime.utcnow()

                # 🚨 Fire an alert if trust score is too low
                if trust_score < ALERT_THRESHOLD and not session.is_flagged:
                    session.is_flagged = True

                    alert = Alert(
                        session_id=session_id,
                        user_email=session.user_email,
                        trust_score=trust_score,
                        reason=f"Trust score dropped to {trust_score} — possible session hijacking detected",
                        severity="critical" if trust_score < 20 else "warning",
                        is_acknowledged=False,
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)
                    print(f"🚨 ALERT fired for {session.user_email} — trust score: {trust_score}")

                db.commit()

                # Send the trust score back to the browser instantly
                await websocket.send_json({
                    "type": "trust_update",
                    "session_id": session_id,
                    "trust_score": trust_score,
                    "is_anomaly": result["is_anomaly"],
                    "risk_level": result["risk_level"],
                    "event_count": len(events)
                })

            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: session {session_id}")

    finally:
        # Always close the database connection
        db.close()