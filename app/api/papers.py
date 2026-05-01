# app/api/papers.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.schemas.paper import PaperCreate, PaperResponse
from app.services.arxiv import fetch_paper_by_id, search_papers
from app.schemas.paper import PaperUpdate
from app.services.cache import get_cached, set_cache, delete_cache
from app.services.ai import summarize_abstract

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.post("/", response_model=PaperResponse)
async def add_paper(
    paper_data: PaperCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    User sends arXiv ID → we fetch paper from arXiv → save to DB.
    Protected route — requires JWT token.
    """
    # Check if user already saved this paper
    existing = db.query(Paper).filter(
        Paper.arxiv_id == paper_data.arxiv_id,
        Paper.owner_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Paper already saved")

    # Fetch from arXiv
    paper_info = await fetch_paper_by_id(paper_data.arxiv_id)
    if not paper_info:
        raise HTTPException(status_code=404, detail="Paper not found on arXiv")

    # Save to DB
    new_paper = Paper(
        arxiv_id=paper_info["arxiv_id"],
        title=paper_info["title"],
        authors=paper_info["authors"],
        abstract=paper_info["abstract"],
        url=paper_info["url"],
        owner_id=current_user.id
    )

    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)
    return new_paper


@router.get("/search")
async def search(
    q: str = Query(..., description="Search keyword"),
    max_results: int = Query(5, le=20)
):
    """Search arXiv — results cached in Redis for 1 hour"""
    cache_key = f"search:{q}:{max_results}"

    # Check cache first
    cached = get_cached(cache_key)
    if cached:
        return {"source": "cache", "results": cached}

    # Not in cache — fetch from arXiv
    results = await search_papers(q, max_results)
    if not results:
        raise HTTPException(status_code=404, detail="No papers found")

    # Save to cache
    set_cache(cache_key, results, expire_seconds=3600)
    return {"source": "arxiv", "results": results}


@router.get("/", response_model=list[PaperResponse])
def get_my_papers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all papers saved by current user"""
    papers = db.query(Paper).filter(Paper.owner_id == current_user.id).all()
    return papers


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single paper by ID"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/{paper_id}")
def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved paper"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()
    return {"message": "Paper deleted successfully"}

@router.patch("/{paper_id}", response_model=PaperResponse)
def update_paper(
    paper_id: int,
    update_data: PaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tags, notes, or read status of a saved paper"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Only update fields that were actually sent
    if update_data.tags is not None:
        paper.tags = update_data.tags
    if update_data.notes is not None:
        paper.notes = update_data.notes
    if update_data.is_read is not None:
        paper.is_read = update_data.is_read

    db.commit()
    db.refresh(paper)
    return paper

@router.post("/{paper_id}/summarize", response_model=PaperResponse)
def summarize_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI summary for a saved paper.
    Calls OpenAI GPT with the paper abstract.
    Saves summary to DB + returns updated paper.
    """
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.owner_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Already summarized — return cached version
    if paper.ai_summary:
        return paper

    try:
        summary = summarize_abstract(paper.abstract)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # Save summary to DB
    paper.ai_summary = summary
    db.commit()
    db.refresh(paper)
    return paper