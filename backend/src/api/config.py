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

    # Database configuration
    mysql_host: str = Field(
        default=os.getenv("MYSQL_HOST", "localhost"),
        description="MySQL host",
    )
    mysql_port: int = Field(
        default=int(os.getenv("MYSQL_PORT", "3306")),
        description="MySQL port",
    )
    mysql_user: str = Field(
        default=os.getenv("MYSQL_USER", "root"),
        description="MySQL username",
    )
    mysql_password: str = Field(
        default=os.getenv("MYSQL_PASSWORD", ""),
    )  # nosec - From env
    mysql_db: str = Field(
        default=os.getenv("MYSQL_DB", "healthcare_ai"),
        description="MySQL database name",
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
        """Construct SQLAlchemy MySQL URL."""
        # Using PyMySQL driver for compatibility in many environments
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

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
