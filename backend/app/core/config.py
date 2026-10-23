"""Application settings loaded from environment / .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]  # project root
BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-opus-5-5"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    MAX_UPLOAD_MB: int = 25

    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"
    GENERATED_DIR: Path = BACKEND_DIR / "generated"
    MODELS_DIR: Path = BACKEND_DIR / "generated" / "models"
    REPORTS_DIR: Path = BACKEND_DIR / "generated" / "reports"
    DB_PATH: Path = BACKEND_DIR / "app.db"
    KNOWLEDGE_DIR: Path = BACKEND_DIR / "app" / "rag" / "knowledge"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for d in (settings.UPLOAD_DIR, settings.GENERATED_DIR, settings.MODELS_DIR, settings.REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    return settings
