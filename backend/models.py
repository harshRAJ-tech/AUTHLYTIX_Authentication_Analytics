# models.py
# This file defines the "shape" of our database tables
# Think of each class as one table in the database

from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# Base is the parent class all our tables inherit from
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# TABLE 1: Sessions
# Stores each user's active session
class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)        # who is this session for
    user_email = Column(String, nullable=False)     # email of the user
    ip_address = Column(String)                     # their IP address
    user_agent = Column(String)                     # their browser info
    trust_score = Column(Float, default=100.0)      # starts at 100 (fully trusted)
    is_active = Column(Boolean, default=True)       # is session still running
    is_flagged = Column(Boolean, default=False)     # has it been flagged as suspicious
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# TABLE 2: Trust Score History
# Every time trust score updates, we save it here (for the timeline chart)
class TrustScoreHistory(Base):
    __tablename__ = "trust_score_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, nullable=False)     # which session
    trust_score = Column(Float, nullable=False)     # what was the score
    is_anomaly = Column(Boolean, default=False)     # was this an anomaly
    raw_score = Column(Float)                       # raw ML score
    recorded_at = Column(DateTime, default=datetime.utcnow)


# TABLE 3: Alerts
# When trust score drops too low, an alert is created
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    trust_score = Column(Float)                     # score when alert fired
    reason = Column(Text)                           # why the alert fired
    severity = Column(String, default="warning")   # warning / critical
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
