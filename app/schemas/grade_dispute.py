# app/schemas/grade_dispute.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.grade_dispute import DisputeStatus


class DisputeCreate(BaseModel):
    reason: str


class DisputeResolve(BaseModel):
    resolution_note: str
    new_score: Optional[int] = None
    new_feedback: Optional[str] = None


class DisputeResponse(BaseModel):
    id: int
    grade_id: int
    reason: str
    status: DisputeStatus
    resolution_note: Optional[str]
    new_grade_id: Optional[int]
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}