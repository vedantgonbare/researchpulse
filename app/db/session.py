# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create DB engine — this is the connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function — FastAPI injects this into route functions.
    Opens a DB session, yields it, then closes it after request done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()