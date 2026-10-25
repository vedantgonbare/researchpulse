from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.invitation import InviteStatus

class InvitationCreate(BaseModel):
    student_email: EmailStr

class InvitationResponse(BaseModel):
    id: int
    student_email: str
    status: InviteStatus
    created_at: datetime

    model_config = {"from_attributes": True}