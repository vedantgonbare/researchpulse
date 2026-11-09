# app/models/grade.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission")