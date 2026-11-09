# app/schemas/assignment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    student_id: int


class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    professor_id: int
    student_id: int
    created_at: datetime

    model_config = {"from_attributes": True}