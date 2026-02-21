from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os


class Settings(BaseSettings):
    # =========================
    # App Info
    # =========================
    APP_NAME: str = "Research Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False  # IMPORTANT: False in production

    # =========================
    # Render Port Handling
    # =========================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.getenv("PORT", 10000))  # Render provides PORT
    API_PREFIX: str = "/api/v1"

    # =========================
    # Database (Supabase / Render)
    # =========================
    DATABASE_URL: str  # MUST come from env
    DB_ECHO: bool = False

    # =========================
    # CORS
    # =========================
    CORS_ORIGINS: List[str] = ["*"]  # allow all for now
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # =========================
    # File Upload
    # =========================
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".md"]

    # =========================
    # Paths
    # =========================
    DATA_DIR: str = "data"
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"
    CACHE_DIR: str = "data/cache"
    EMBEDDINGS_DIR: str = "data/embeddings"

    # =========================
    # RAG
    # =========================
    EMBEDDING_MODEL: str = "intfloat/e5-base-v2"
    EMBEDDING_DIM: int = 768
    VECTOR_DB_TYPE: str = "chromadb"
    VECTOR_DB_PATH: str = "data/chromadb"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # =========================
    # LLM
    # =========================
    GEMINI_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # =========================
    # Pydantic config
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",        # used locally
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()