# ml/train.py
# This creates fake (synthetic) user behavior data and trains our ML model
# In real life, you'd use real user data — but this is perfect for MVP

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

print("🧠 Starting ML training pipeline...")

# ── STEP 1: Generate synthetic behavioral data ──────────────────────────────

def generate_data(n_users=300, sessions_per_user=20):
    """
    Simulate 300 users each with 20 sessions.
    Each user has their own unique typing/mouse style (their biometric fingerprint).
    5% of sessions are 'attacks' — someone else using their account.
    """
    np.random.seed(42)
    records = []

    for user_id in range(n_users):

        # Every user has a personal baseline — their natural behavior
        baseline = {
            "ks_mean_dwell":        np.random.normal(120, 20),   # how long they hold keys
            "ks_std_dwell":         np.random.normal(30, 8),     # how consistent they are
            "ks_mean_flight":       np.random.normal(180, 40),   # time between keystrokes
            "ks_std_flight":        np.random.normal(50, 12),
            "ks_burst_ratio":       np.random.uniform(0.1, 0.5), # fast typing bursts
            "ks_error_rate":        np.random.uniform(0.01, 0.1),# backspace usage

            "ms_mean_velocity":     np.random.normal(0.8, 0.2),  # mouse speed
            "ms_std_velocity":      np.random.normal(0.3, 0.08),
            "ms_mean_curvature":    np.random.normal(0.05, 0.02),# how curved mouse paths are
            "ms_idle_fraction":     np.random.uniform(0.1, 0.4), # time mouse sits still
            "ms_click_regularity":  np.random.normal(200, 60),   # time between clicks
            "ms_scroll_velocity":   np.random.normal(2.5, 0.8),  # scroll speed

            "ctx_hour_norm":        np.random.uniform(0.3, 0.8), # time of day they work
            "ctx_day_norm":         np.random.uniform(0.0, 0.8), # day of week
            "ctx_ip_changed":       0.0,                         # IP same as usual
            "ctx_ua_changed":       0.0,                         # browser same as usual
            "ctx_timezone_delta":   0.0,                         # same timezone
            "ctx_session_age_norm": 1.0,                         # normal session length
        }

        # Normal sessions — slight variation from baseline (everyone varies a little)
        for _ in range(sessions_per_user):
            session = {}
            for key, val in baseline.items():
                noise = abs(val) * 0.1  # 10% natural variation
                session[key] = max(0, np.random.normal(val, noise))
            session["label"] = 0  # 0 = normal, legitimate user
            records.append(session)

        # Attack sessions — attacker has VERY different behavior
        num_attacks = max(1, sessions_per_user // 20)
        for _ in range(num_attacks):
            attack = {}
            for key, val in baseline.items():
                # Attacker's behavior is 1.5x–2.5x different from the real user
                attack[key] = max(0, np.random.normal(
                    val * np.random.uniform(1.5, 2.5),
                    abs(val) * 0.3
                ))
            attack["ctx_ip_changed"] = 1.0    # attacker has different IP
            attack["ctx_ua_changed"] = 1.0    # attacker has different browser
            attack["label"] = 1               # 1 = attack / anomaly
            records.append(attack)

    df = pd.DataFrame(records)
    print(f"✅ Generated {len(df)} sessions ({df['label'].sum()} attacks)")
    return df


# ── STEP 2: Train the model ──────────────────────────────────────────────────

FEATURE_COLUMNS = [
    "ks_mean_dwell", "ks_std_dwell", "ks_mean_flight", "ks_std_flight",
    "ks_burst_ratio", "ks_error_rate",
    "ms_mean_velocity", "ms_std_velocity", "ms_mean_curvature",
    "ms_idle_fraction", "ms_click_regularity", "ms_scroll_velocity",
    "ctx_hour_norm", "ctx_day_norm", "ctx_ip_changed", "ctx_ua_changed",
    "ctx_timezone_delta", "ctx_session_age_norm",
]

def train():
    # Generate data
    df = generate_data()
    X = df[FEATURE_COLUMNS].values

    # Normalize all features to same scale (important for ML!)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("✅ Features normalized")

    # Train Isolation Forest
    # This model learns what NORMAL looks like, then flags anything different
    model = IsolationForest(
        n_estimators=200,      # 200 decision trees
        contamination=0.05,    # we expect ~5% anomalies
        max_features=0.8,      # use 80% of features per tree
        random_state=42,
        n_jobs=-1,             # use all CPU cores
    )
    model.fit(X_scaled)
    print("✅ Isolation Forest trained")

    # Test how well it works
    predictions = model.predict(X_scaled)  # -1 = anomaly, 1 = normal
    actual_attacks = df["label"].values

    true_positives = ((predictions == -1) & (actual_attacks == 1)).sum()
    total_attacks = actual_attacks.sum()
    recall = true_positives / total_attacks * 100

    print(f"✅ Model validation: caught {true_positives}/{total_attacks} attacks ({recall:.1f}% recall)")

    # Save the model and scaler to disk
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/isolation_forest.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(FEATURE_COLUMNS, "models/feature_columns.pkl")

    print("✅ Model saved to ml/models/")
    print("🎉 Training complete!")


if __name__ == "__main__":
    train()