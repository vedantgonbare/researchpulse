# app/schemas/grade.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GradeCreate(BaseModel):
    score: int
    feedback: Optional[str] = None


class GradeResponse(BaseModel):
    id: int
    submission_id: int
    score: int
    feedback: Optional[str]
    graded_at: datetime

    model_config = {"from_attributes": True}