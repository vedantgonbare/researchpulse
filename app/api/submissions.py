from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.grade import Grade
from app.schemas.submission import SubmissionResponse
from app.schemas.grade import GradeResponse

router = APIRouter(tags=["Submissions"])


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Either the student who submitted it, or the professor whose
    assignment it belongs to, can view a submission directly —
    no role restriction, just an ownership check across two possible
    relationships instead of one.
    """
    submission = (
        db.query(Submission)
        .join(Assignment)
        .filter(
            Submission.id == submission_id,
            or_(
                Assignment.student_id == current_user.id,
                Assignment.professor_id == current_user.id,
            ),
        )
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/submissions/{submission_id}/grade", response_model=GradeResponse)
def get_submission_grade(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Same ownership rule as get_submission — either party can view the grade."""
    submission = (
        db.query(Submission)
        .join(Assignment)
        .filter(
            Submission.id == submission_id,
            or_(
                Assignment.student_id == current_user.id,
                Assignment.professor_id == current_user.id,
            ),
        )
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    grade = (
        db.query(Grade)
        .filter(Grade.submission_id == submission_id)
        .order_by(Grade.id.desc())
        .first()
    )
    if not grade:
        raise HTTPException(status_code=404, detail="This submission has not been graded yet")

    return grade