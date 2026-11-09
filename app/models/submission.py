# app/models/submission.py
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class SubmissionStage(str, enum.Enum):
    proposal = "proposal"
    draft = "draft"
    final = "final"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    stage = Column(SAEnum(SubmissionStage), nullable=False)

    text_content = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)  # Cloudinary URL, if a file was attached

    submitted_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="submissions")