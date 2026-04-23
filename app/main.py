# app/main.py
from fastapi import FastAPI
from app.api import auth
from app.models.user import User
from app.models.paper import Paper

app = FastAPI(
    title="ResearchPulse API",
    description="Academic paper tracking and AI summarization backend",
    version="1.0.0"
)

# Register auth routes
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "ResearchPulse API is running"}