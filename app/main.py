# app/main.py
from fastapi import FastAPI
from app.models.user import User
from app.models.paper import Paper
from app.api import auth

app = FastAPI(
    title="ResearchPulse API",
    description="Academic paper tracking and AI summarization backend",
    version="1.0.0"
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "ResearchPulse API is running"}