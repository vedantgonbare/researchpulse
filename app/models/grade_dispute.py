# app/models/grade_dispute.py
import enum
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class DisputeStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class GradeDispute(Base):
    __tablename__ = "grade_disputes"

    __table_args__ = (UniqueConstraint("grade_id", name="uq_one_dispute_per_grade"),)

    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SAEnum(DisputeStatus), nullable=False, default=DisputeStatus.open)

    # Filled in only when resolved — the professor's response, and whether
    # a new Grade was issued as a result.
    resolution_note = Column(Text, nullable=True)
    new_grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    grade = relationship("Grade", foreign_keys=[grade_id])
    new_grade = relationship("Grade", foreign_keys=[new_grade_id])
    