# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import answer_question
from app.core.limiter import rate_limit

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse, dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60))])
def chat_with_papers(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ask a question grounded in the current user's own saved papers.
    Embeds the question, retrieves the most relevant saved papers,
    and generates an answer using only their content.
    """
    if not chat_request.question or not chat_request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answer_question(db, owner_id=current_user.id, question=chat_request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

    return result