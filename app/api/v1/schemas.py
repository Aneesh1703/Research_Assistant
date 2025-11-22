# app/api/v1/schemas.py
from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum



class DocumentType(str, Enum):
    PDF = "pdf"
    URL = "url"
    TEXT = "text"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"



class HealthResponse(BaseModel):
    app: str
    version: str
    status: str
    debug: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)



class URLIngestRequest(BaseModel):
    url: HttpUrl
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "metadata": {"source": "research", "category": "AI"}
            }
        }


class TextIngestRequest(BaseModel):
    content: str = Field(..., min_length=1)
    title: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "This is my research text...",
                "title": "Research Notes",
                "metadata": {"author": "John Doe"}
            }
        }


class DocumentIngestResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    status: DocumentStatus
    filename: Optional[str] = None
    url: Optional[str] = None
    content_preview: str = Field(..., description="First 200 characters of content")
    word_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: str = "Document ingested successfully"



class DocumentMetadata(BaseModel):
    document_id: str
    document_type: DocumentType
    status: DocumentStatus
    filename: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    word_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentMetadata]


class DocumentDetail(BaseModel):
    document_id: str
    document_type: DocumentType
    status: DocumentStatus
    filename: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    content: str
    word_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class DocumentDeleteResponse(BaseModel):
    document_id: str
    message: str = "Document deleted successfully"

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)
    include_sources: bool = Field(default=True)
    
    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main findings about climate change?",
                "max_results": 5,
                "include_sources": True
            }
        }


class Source(BaseModel):
    document_id: str
    filename: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    excerpt: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
