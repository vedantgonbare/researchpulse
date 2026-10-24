# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Email
    RESEND_API_KEY: str
    FRONTEND_BASE_URL: str = "http://localhost:5173"

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

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Professor registration gate
    ALLOWED_PROFESSOR_DOMAINS: str = ""

    @property
    def allowed_professor_domains_list(self) -> list[str]:
        """Return approved domains, normalized and trimmed."""
        if not self.ALLOWED_PROFESSOR_DOMAINS.strip():
            return []

        return [
            domain.strip().lower()
            for domain in self.ALLOWED_PROFESSOR_DOMAINS.split(",")
            if domain.strip()
        ]


# Single instance used everywhere
settings = Settings()
