# app/api/files.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.storage import upload_file
from app.core.limiter import rate_limit

router = APIRouter(prefix="/files", tags=["Files"])

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
MAX_SIZE_MB = 10

@router.post("/upload", dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60))])
async def upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF or image file to Cloudinary.
    Protected route — requires JWT token.
    Max size: 10MB. Allowed: PDF, PNG, JPG.
    """
    # Check file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: PDF, PNG, JPG"
        )

    # Read file bytes
    file_bytes = await file.read()

    # Check file size
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_SIZE_MB}MB"
        )

    # Upload to Cloudinary
    try:
        filename = f"user_{current_user.id}_{file.filename}"
        result = upload_file(file_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {
        "message": "File uploaded successfully",
        "url": result["url"],
        "public_id": result["public_id"],
        "format": result["format"],
        "size_bytes": result["size"]
    }