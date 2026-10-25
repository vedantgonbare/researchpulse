# app/api/professors.py
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.invitation import Invitation, InviteStatus
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.services.email import send_invitation_email

router = APIRouter(prefix="/professors", tags=["Professors"])


@router.post("/invite", response_model=InvitationResponse)
def invite_student(
    invite_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.professor)),
):
    """
    Professor-only: invite a student by email. Generates a unique token,
    stores it as a pending Invitation, and emails the student a signup
    link containing that token.
    """
    # Generate a random, URL-safe token — not guessable, not sequential
    token = secrets.token_urlsafe(32)

    invitation = Invitation(
        professor_id=current_user.id,
        student_email=invite_data.student_email,
        token=token,
        status=InviteStatus.pending,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    try:
        send_invitation_email(invite_data.student_email, token)
    except Exception as e:
        # The invitation record is already saved — don't lose it just
        # because the email failed to send. Flag it, don't crash.
        print(f"Failed to send invitation email to {invite_data.student_email}: {e}")

    return invitation