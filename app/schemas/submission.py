# app/schemas/submission.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.submission import SubmissionStage


class SubmissionCreate(BaseModel):
    stage: SubmissionStage
    text_content: Optional[str] = None
    file_url: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    stage: SubmissionStage
    text_content: Optional[str]
    file_url: Optional[str]
    submitted_at: datetime

    model_config = {"from_attributes": True}