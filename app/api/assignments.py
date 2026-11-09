# app/api/assignments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.schemas.assignment import AssignmentCreate, AssignmentResponse
from app.schemas.submission import SubmissionCreate, SubmissionResponse

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=AssignmentResponse, dependencies=[Depends(require_role(UserRole.professor))])
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Professor assigns work to one of their own students.
    Guards against assigning to: a student who doesn't exist, isn't a
    student, or isn't *this* professor's student.
    """
    student = db.query(User).filter(
        User.id == payload.student_id,
        User.role == UserRole.student,
        User.professor_id == current_user.id,
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found under your account")

    assignment = Assignment(
        title=payload.title,
        description=payload.description,
        professor_id=current_user.id,
        student_id=payload.student_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/", response_model=list[AssignmentResponse])
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Role-scoped listing: a professor sees assignments they created,
    a student sees assignments assigned to them. Same table, different
    filter column — no separate endpoints needed.
    """
    if current_user.role == UserRole.professor:
        return db.query(Assignment).filter(Assignment.professor_id == current_user.id).all()
    return db.query(Assignment).filter(Assignment.student_id == current_user.id).all()


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Same join-filter pattern as submissions below: ownership check lives
    inside the query, not as a separate check-after-fetch step.
    """
    if current_user.role == UserRole.professor:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.professor_id == current_user.id,
        ).first()
    else:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.student_id == current_user.id,
        ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post(
    "/{assignment_id}/submissions",
    response_model=SubmissionResponse,
    dependencies=[Depends(require_role(UserRole.student))],
)
def submit_stage(
    assignment_id: int,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student submits one stage of their own assignment. The ownership
    check (Assignment.student_id == current_user.id) is inside the same
    query that fetches the assignment — a nonexistent assignment and
    someone else's assignment are indistinguishable from the outside.
    """
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.student_id == current_user.id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    submission = Submission(
        assignment_id=assignment.id,
        stage=payload.stage,
        text_content=payload.text_content,
        file_url=payload.file_url,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{assignment_id}/submissions", response_model=list[SubmissionResponse])
def list_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Both roles can view: the student sees their own submissions, the
    professor sees submissions for assignments they created. Same
    join-filter principle applied per-role.
    """
    if current_user.role == UserRole.professor:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.professor_id == current_user.id,
        ).first()
    else:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.student_id == current_user.id,
        ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return db.query(Submission).filter(Submission.assignment_id == assignment.id).all()