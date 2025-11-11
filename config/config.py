"""Application configuration management."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # API Configuration
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Storage Settings
    DATA_DIR: Path = Path(__file__).parent.parent / "data"
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "json")  # json, database, etc.

    # Request Settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    def __init__(self):
        """Initialize settings and create data directory if needed."""
        self.DATA_DIR.mkdir(exist_ok=True)

    def validate(self) -> bool:
        """Validate that required settings are present."""
        if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
            return False
        return True


# Global settings instance
settings = Settings()

