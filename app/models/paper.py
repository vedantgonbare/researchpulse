# app/models/paper.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Paper(Base):
    """
    This class = 'papers' table in PostgreSQL.
    Stores academic papers fetched from arXiv.
    """
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    tags = Column(String, default="")         # comma-separated tags
    notes = Column(Text, default="")          # user's personal notes
    is_read = Column(Boolean, default=False)  # reading tracker
    ai_summary = Column(Text, default="")     # AI generated summary
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key → links paper to a user
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="papers")