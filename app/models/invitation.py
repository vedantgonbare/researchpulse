# app/models/invitation.py
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from datetime import datetime
from app.db.base import Base


class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_email = Column(String, nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(InviteStatus), nullable=False, default=InviteStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)