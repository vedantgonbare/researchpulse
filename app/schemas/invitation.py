from pydantic import BaseModel, EmailStr
from datetime import datetime

class InvitationCreate(BaseModel):
    student_email: EmailStr


class InvitationResponse(BaseModel):
    id: int
    student_email: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InvitationPublicResponse(BaseModel):
    professor_name: str
    professor_email: str
    student_email: str
    status: str

