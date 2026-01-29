"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ARGENT_",
        extra="ignore",
    )

    # Required
    anthropic_api_key: str = Field(
        ...,
        validation_alias="ANTHROPIC_API_KEY",
        description="Anthropic API key for Claude access",
    )

    # Optional API keys
    alpha_vantage_api_key: str | None = Field(
        default=None,
        validation_alias="ALPHA_VANTAGE_API_KEY",
        description="Alpha Vantage API key for additional market data",
    )
    fred_api_key: str | None = Field(
        default=None,
        validation_alias="FRED_API_KEY",
        description="FRED API key for economic data",
    )

    # Model configuration
    model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Default Claude model for analysis",
    )
    fast_model: str = Field(
        default="claude-haiku-3-5-20241022",
        description="Fast Claude model for simple tasks",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///data/argent.db",
        description="SQLAlchemy database URL",
    )

    # Rate limiting
    max_retries: int = Field(default=3, description="Maximum API retry attempts")
    retry_delay: float = Field(default=1.0, description="Base delay between retries in seconds")

    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        path = Path("data")
        path.mkdir(exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
