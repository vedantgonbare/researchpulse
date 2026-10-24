# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "ResearchPulse API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI
    OPENAI_API_KEY: str = ""

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Professor registration gate: comma-separated list of approved email domains.
    # Empty by default — no domain registers as professor until you set this.
    ALLOWED_PROFESSOR_DOMAINS: str = ""

    model_config = {"env_file": ".env"}

    @property
    def allowed_professor_domains_list(self) -> list[str]:
        """Parsed, lowercased, whitespace-trimmed list — the actual thing to check against."""
        if not self.ALLOWED_PROFESSOR_DOMAINS.strip():
            return []
        return [d.strip().lower() for d in self.ALLOWED_PROFESSOR_DOMAINS.split(",") if d.strip()]

# Single instance used everywhere
settings = Settings()