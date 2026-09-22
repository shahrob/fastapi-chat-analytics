from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings — loaded from environment variables / .env file."""

    # ── Project metadata ───────────────────────────────────────────────────────
    PROJECT_NAME: str = "FastAPI Chat Analytics"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise-grade chat agent application with AI integration"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"  # development | staging | production

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL

    # ── Relational Database (SQLite / PostgreSQL) ──────────────────────────────
    DATABASE_URL: str = "sqlite:///./chatapp.db"

    # ── MongoDB ────────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "vissioon"

    # ── Security / JWT ─────────────────────────────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OpenAI ─────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 500

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── Server ─────────────────────────────────────────────────────────────────
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://192.168.1.7:8000",
        "*",
    ]

    # ── Pagination defaults ────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
