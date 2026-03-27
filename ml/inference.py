# ml/inference.py
# This is called in real-time to score every user's behavior
# Input: 18 numbers describing behavior
# Output: trust score 0-100 + anomaly flag

import numpy as np
import joblib
import os

# Load models once when the file is imported (fast!)
_model = None
_scaler = None
_features = None

def _load():
    global _model, _scaler, _features
    if _model is None:
        base = os.path.dirname(__file__)
        _model    = joblib.load(os.path.join(base, "models/isolation_forest.pkl"))
        _scaler   = joblib.load(os.path.join(base, "models/scaler.pkl"))
        _features = joblib.load(os.path.join(base, "models/feature_columns.pkl"))
        print("✅ ML models loaded into memory")


def compute_trust_score(feature_vector: list) -> dict:
    """
    Takes a list of 18 floats (behavior features).
    Returns a trust score from 0 (danger) to 100 (safe).
    """
    _load()

    X = np.array(feature_vector).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    # decision_function returns a score:
    # more negative = more anomalous (dangerous)
    # more positive = more normal (safe)
    raw_score = _model.decision_function(X_scaled)[0]
    is_anomaly = _model.predict(X_scaled)[0] == -1

    # Convert raw score to 0-100 trust score
    # Raw score typically ranges from -0.5 to +0.5
    trust_score = int(np.clip((raw_score + 0.5) * 100, 0, 100))

    return {
        "trust_score": trust_score,
        "is_anomaly": bool(is_anomaly),
        "raw_score": round(float(raw_score), 4),
        "risk_level": (
            "critical" if trust_score < 30 else
            "high"     if trust_score < 50 else
            "medium"   if trust_score < 70 else
            "low"
        )
    }


def score_from_events(events: list) -> dict:
    """
    Takes raw browser events (keystrokes, mouse moves)
    and converts them into a trust score.
    This is what the WebSocket endpoint will call.
    """
    _load()

    if len(events) < 5:
        # Not enough data yet — give benefit of the doubt
        return {
            "trust_score": 85,
            "is_anomaly": False,
            "raw_score": 0.35,
            "risk_level": "low",
            "note": "insufficient data — using default score"
        }

    # Extract features from raw events
    keydown_events = [e for e in events if e.get("type") == "ks_down"]
    mouseMove_events = [e for e in events if e.get("type") == "mm"]
    click_events = [e for e in events if e.get("type") == "click"]

    # Keystroke features
    flights = [e.get("flight", 150) for e in keydown_events if e.get("flight", 0) > 0]
    ks_mean_flight   = np.mean(flights) if flights else 180
    ks_std_flight    = np.std(flights)  if flights else 50
    ks_mean_dwell    = ks_mean_flight * 0.65   # estimate dwell from flight
    ks_std_dwell     = ks_std_flight * 0.4
    ks_burst_ratio   = min(len([f for f in flights if f < 100]) / max(len(flights), 1), 1)
    ks_error_rate    = 0.05  # default — will improve with real data

    # Mouse features
    velocities = []
    for i in range(1, len(mouseMove_events)):
        dx = mouseMove_events[i].get("x", 0) - mouseMove_events[i-1].get("x", 0)
        dy = mouseMove_events[i].get("y", 0) - mouseMove_events[i-1].get("y", 0)
        dt = mouseMove_events[i].get("ts", 1) - mouseMove_events[i-1].get("ts", 0)
        if dt > 0:
            velocities.append(np.sqrt(dx**2 + dy**2) / dt)

    ms_mean_velocity  = np.mean(velocities) if velocities else 0.8
    ms_std_velocity   = np.std(velocities)  if velocities else 0.3
    ms_mean_curvature = 0.05   # simplified for MVP
    ms_idle_fraction  = max(0, 1 - len(mouseMove_events) / max(len(events), 1))

    click_times = [e.get("ts", 0) for e in click_events]
    click_gaps  = [click_times[i] - click_times[i-1]
                   for i in range(1, len(click_times))]
    ms_click_regularity = np.std(click_gaps) if click_gaps else 200
    ms_scroll_velocity  = 2.5   # default

    # Context features (defaults — real values come from session metadata)
    ctx_hour_norm       = 0.5
    ctx_day_norm        = 0.5
    ctx_ip_changed      = 0.0
    ctx_ua_changed      = 0.0
    ctx_timezone_delta  = 0.0
    ctx_session_age     = 1.0

    feature_vector = [
        ks_mean_dwell, ks_std_dwell, ks_mean_flight, ks_std_flight,
        ks_burst_ratio, ks_error_rate,
        ms_mean_velocity, ms_std_velocity, ms_mean_curvature,
        ms_idle_fraction, ms_click_regularity, ms_scroll_velocity,
        ctx_hour_norm, ctx_day_norm, ctx_ip_changed, ctx_ua_changed,
        ctx_timezone_delta, ctx_session_age,
    ]

    return compute_trust_score(feature_vector)
