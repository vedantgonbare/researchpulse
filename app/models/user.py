# app/models/user.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UserRole(str, enum.Enum):
    student = "student"
    professor = "professor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Existing: papers relationship (ResearchPulse's original core feature)
    papers = relationship("Paper", back_populates="owner")

    # New: self-referential professor <-> students link
    professor = relationship("User", remote_side=[id], backref="students")