# app/schemas/chat.py
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatSource(BaseModel):
    paper_id: int
    title: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]