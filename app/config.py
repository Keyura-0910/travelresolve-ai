"""
Application configuration for TravelResolve AI.
Uses pydantic-settings to safely load settings from environment variables or .env.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
POLICIES_DIR = DATA_DIR / "policies"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
MODELS_DIR = DATA_DIR / "models"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Settings
    APP_NAME: str = "TravelResolve AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # API and UI Ports
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    STREAMLIT_PORT: int = 8501

    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'travelresolve.db'}"

    # LLM Settings
    LLM_PROVIDER: str = "local"  # "local" or "openai"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0

    # Embeddings & RAG
    EMBEDDING_PROVIDER: str = "local"  # "local" or "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_TOP_K: int = 3
    RAG_SCORE_THRESHOLD: float = 0.65

    # Intent Classification
    CLASSIFIER_PATH: str = str(MODELS_DIR / "intent_classifier.joblib")
    CLASSIFIER_METRICS_PATH: str = str(MODELS_DIR / "classifier_metrics.json")
    CONFIDENCE_THRESHOLD_ESCALATION: float = 0.35

    # Priority Rules
    PRIORITY_CRITICAL_CHECKIN_HOURS: int = 24
    PRIORITY_HIGH_CHECKIN_HOURS: int = 72
    VIP_TIERS: list[str] = ["Platinum", "Gold"]

    # LangSmith Tracing
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "travelresolve-ai"


settings = Settings()
