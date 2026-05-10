# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.models.user import User
from app.models.paper import Paper
from app.api import auth, papers, files

app = FastAPI(
    title="ResearchPulse API",
    description="Academic paper tracking and AI summarization backend",
    version="1.0.0"
)

# ── Global Exception Handlers ──────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# ── Routers ────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(files.router)

@app.get("/")
def root():
    return {"message": "ResearchPulse API is running"}