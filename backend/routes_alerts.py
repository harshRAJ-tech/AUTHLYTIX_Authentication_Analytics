# routes_alerts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models import Alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_all_alerts(db: DBSession = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    return {
        "total": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "session_id": a.session_id,
                "user_email": a.user_email,
                "trust_score": a.trust_score,
                "reason": a.reason,
                "severity": a.severity,
                "is_acknowledged": a.is_acknowledged,
                "created_at": a.created_at,
            }
            for a in alerts
        ]
    }

@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: DBSession = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_acknowledged = True
    db.commit()
    return {"message": "Alert acknowledged", "alert_id": alert_id}