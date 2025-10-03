"""
Configuration and environment variable management for the FastAPI backend.
"""

from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    app_name: str = Field(
        default="Healthcare AI Assistant Backend",
        description="Name of the FastAPI application",
    )
    app_version: str = Field(
        default="1.0.0",
        description="Version of the FastAPI application",
    )
    environment: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="Application environment",
    )

    # Database configuration (SQLite by default for local development)
    database_url_env: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./dev.db"),
        description="SQLAlchemy database URL. Defaults to local SQLite file.",
    )

    # OpenAI API
    openai_api_key: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key",
    )

    # Frontend CORS
    cors_allow_origins: str = Field(
        default=os.getenv("CORS_ALLOW_ORIGINS", "*"),
        description="Comma separated list of origins allowed for CORS",
    )

    @property
    def database_url(self) -> str:
        """
        Construct SQLAlchemy database URL.

        Defaults to SQLite local file for development.
        """
        return self.database_url_env

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as list from comma-separated env value."""
        raw = (self.cors_allow_origins or "").strip()
        if not raw:
            return ["*"]
        parts = [p.strip() for p in raw.split(",")]
        return [p for p in parts if p]


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()
