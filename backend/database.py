# database.py
# This file handles connecting to PostgreSQL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base
import os

# Load the .env file we created
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is what we use to talk to the database in our routes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")

def get_db():
    """This gives each request its own database connection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()