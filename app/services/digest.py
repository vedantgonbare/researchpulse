# app/services/digest.py
from sqlalchemy.orm import Session
from app.models.paper import Paper
from app.models.user import User

def generate_digest(user_id: int, db: Session) -> dict:
    """
    Generate a weekly digest for a user.
    Finds all unread papers → builds summary report.
    """
    # Get all unread papers for this user
    unread_papers = db.query(Paper).filter(
        Paper.owner_id == user_id,
        Paper.is_read == False
    ).all()

    if not unread_papers:
        return {
            "user_id": user_id,
            "total_unread": 0,
            "message": "No unread papers. You are all caught up!",
            "papers": []
        }

    # Build digest list
    digest_papers = []
    for paper in unread_papers:
        digest_papers.append({
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "url": paper.url,
            "tags": paper.tags,
            "ai_summary": paper.ai_summary if paper.ai_summary else "No summary yet — use /summarize endpoint",
            "saved_on": paper.created_at.strftime("%Y-%m-%d")
        })

    return {
        "user_id": user_id,
        "total_unread": len(unread_papers),
        "message": f"You have {len(unread_papers)} unread paper(s) this week.",
        "papers": digest_papers
    }


def mark_all_read(user_id: int, db: Session) -> int:
    """Mark all papers as read for a user. Returns count updated."""
    papers = db.query(Paper).filter(
        Paper.owner_id == user_id,
        Paper.is_read == False
    ).all()

    for paper in papers:
        paper.is_read = True

    db.commit()
    return len(papers)