# app/services/storage.py
import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configure Cloudinary with our credentials
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_file(file_bytes: bytes, filename: str, folder: str = "researchpulse") -> dict:
    """
    Upload a file to Cloudinary.
    Returns dict with url and public_id.
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        public_id=filename,
        folder=folder,
        resource_type="auto"  # auto detects pdf, image, etc
    )
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "format": result["format"],
        "size": result["bytes"]
    }

def delete_file(public_id: str) -> bool:
    """Delete a file from Cloudinary by public_id."""
    result = cloudinary.uploader.destroy(public_id)
    return result.get("result") == "ok"