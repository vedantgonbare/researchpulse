# app/api/grades.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.grade import Grade
from app.models.grade_dispute import GradeDispute, DisputeStatus
from app.schemas.grade import GradeCreate, GradeResponse
from app.schemas.grade_dispute import DisputeCreate, DisputeResolve, DisputeResponse

router = APIRouter(tags=["Grading"])


@router.post(
    "/submissions/{submission_id}/grade",
    response_model=GradeResponse,
    dependencies=[Depends(require_role(UserRole.professor))],
)
def grade_submission(
    submission_id: int,
    payload: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    One-time grading action. A submission can only ever be graded once
    directly — any later score change must go through the dispute-resolve
    flow, which is the only other place a Grade row gets created.
    """
    submission = (
        db.query(Submission)
        .join(Assignment)
        .filter(Submission.id == submission_id, Assignment.professor_id == current_user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    existing_grade = db.query(Grade).filter(Grade.submission_id == submission_id).first()
    if existing_grade:
        raise HTTPException(
            status_code=400,
            detail="This submission has already been graded. Score changes must go through a dispute.",
        )

    grade = Grade(submission_id=submission_id, score=payload.score, feedback=payload.feedback)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@router.post(
    "/submissions/{submission_id}/dispute",
    response_model=DisputeResponse,
    dependencies=[Depends(require_role(UserRole.student))],
)
def dispute_grade(
    submission_id: int,
    payload: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    A student disputes the grade on their own submission. Requires an
    existing grade, and — enforced here at the app level for a clean
    error, backed by a DB unique constraint underneath — only one
    dispute per grade, ever.
    """
    submission = (
        db.query(Submission)
        .join(Assignment)
        .filter(Submission.id == submission_id, Assignment.student_id == current_user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    grade = db.query(Grade).filter(Grade.submission_id == submission_id).first()
    if not grade:
        raise HTTPException(status_code=400, detail="This submission has not been graded yet")

    existing_dispute = db.query(GradeDispute).filter(GradeDispute.grade_id == grade.id).first()
    if existing_dispute:
        raise HTTPException(status_code=400, detail="This grade has already been disputed")

    dispute = GradeDispute(grade_id=grade.id, reason=payload.reason)
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    return dispute


@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=DisputeResponse,
    dependencies=[Depends(require_role(UserRole.professor))],
)
def resolve_dispute(
    dispute_id: int,
    payload: DisputeResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    The only sanctioned path to a new Grade after the first one. If
    new_score is omitted, the original stands and new_grade_id stays
    null — the dispute is resolved, nothing changed, but it's on record.
    """
    dispute = (
        db.query(GradeDispute)
        .join(Grade, GradeDispute.grade_id == Grade.id)
        .join(Submission, Grade.submission_id == Submission.id)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .filter(GradeDispute.id == dispute_id, Assignment.professor_id == current_user.id)
        .first()
    )
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.status != DisputeStatus.open:
        raise HTTPException(status_code=400, detail="This dispute has already been resolved")

    if payload.new_score is not None:
        new_grade = Grade(
            submission_id=dispute.grade.submission_id,
            score=payload.new_score,
            feedback=payload.new_feedback,
        )
        db.add(new_grade)
        db.flush()  # get new_grade.id before committing, without a second round-trip
        dispute.new_grade_id = new_grade.id

    dispute.resolution_note = payload.resolution_note
    dispute.status = DisputeStatus.resolved
    dispute.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(dispute)
    return dispute