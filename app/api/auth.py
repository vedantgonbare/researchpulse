# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.invitation import Invitation, InviteStatus
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RegisterWithInviteRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _create_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    role: UserRole = UserRole.student,
    professor_id: int | None = None,
) -> User:
    """
    Shared user-creation path for both plain registration and
    invite-based registration — keeps hashing + uniqueness checks
    in exactly one place.
    """
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        role=role,
        professor_id=professor_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (student or professor, professor gated by domain allowlist upstream)."""
    return _create_user(
        db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role,
    )


@router.post("/register-with-invite", response_model=UserResponse)
def register_with_invite(payload: RegisterWithInviteRequest, db: Session = Depends(get_db)):
    """
    Registration that also consumes an invitation token, linking the new
    student directly to the inviting professor. Always creates a student —
    there is no role field on this request.
    """
    invitation = db.query(Invitation).filter(Invitation.token == payload.invite_token).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if invitation.status != InviteStatus.pending:
        raise HTTPException(status_code=400, detail="Invitation has already been used or has expired")

    if invitation.student_email.lower() != payload.email.lower():
        raise HTTPException(status_code=400, detail="Email does not match the invited address")

    new_user = _create_user(
        db,
        email=payload.email,
        username=payload.username,
        password=payload.password,
        role=UserRole.student,
        professor_id=invitation.professor_id,
    )

    invitation.status = InviteStatus.accepted
    db.commit()

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user