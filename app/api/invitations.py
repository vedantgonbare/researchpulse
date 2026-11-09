# app/api/invitations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.invitation import Invitation, InviteStatus
from app.models.user import User
from app.schemas.invitation import InvitationPublicResponse

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.get("/{token}", response_model=InvitationPublicResponse)
def get_invitation(token: str, db: Session = Depends(get_db)):
    """
    Public, unauthenticated lookup — lets the registration frontend show
    'You've been invited by Professor X' before the student has an account.
    Deliberately returns only what's needed to render that message.
    """
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    professor = db.query(User).filter(User.id == invitation.professor_id).first()
    if not professor:
        # Shouldn't happen under normal operation (FK integrity), but don't
        # leak a 500 to an anonymous visitor over a data-consistency edge case.
        raise HTTPException(status_code=404, detail="Invitation not found")

    return InvitationPublicResponse(
        professor_name=professor.username,
        professor_email=professor.email,
        student_email=invitation.student_email,
        status=invitation.status.value,
    )
