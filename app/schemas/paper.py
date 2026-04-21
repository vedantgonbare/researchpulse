# app/schemas/paper.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaperCreate(BaseModel):
    """User sends arXiv ID → we fetch and save"""
    arxiv_id: str

class PaperUpdate(BaseModel):
    """User can update tags, notes, read status"""
    tags: Optional[str] = None
    notes: Optional[str] = None
    is_read: Optional[bool] = None

class PaperResponse(BaseModel):
    """Full paper data sent back to user"""
    id: int
    arxiv_id: str
    title: str
    authors: str
    abstract: str
    url: str
    tags: str
    notes: str
    is_read: bool
    ai_summary: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True