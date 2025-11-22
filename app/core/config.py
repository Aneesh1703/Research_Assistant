from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Research Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".txt", ".md"]
    
    # Data Paths
    DATA_DIR: str = "data"
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"
    CACHE_DIR: str = "data/cache"
    EMBEDDINGS_DIR: str = "data/embeddings"
    
    # RAG Configuration (for future use)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_PATH: str = "data/embeddings/faiss_index"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # LLM Configuration (optional for now)
    GEMINI_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
