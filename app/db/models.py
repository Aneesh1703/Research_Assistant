# app/db/models.py
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class DocumentTypeEnum(str, enum.Enum):
    PDF = "pdf"
    URL = "url"
    TEXT = "text"


class DocumentStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_type = Column(Enum(DocumentTypeEnum), nullable=False)
    status = Column(Enum(DocumentStatusEnum), nullable=False, default=DocumentStatusEnum.COMPLETED)
    filename = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    extra_metadata = Column(JSON, nullable=True, default={})  # Renamed from 'metadata' (reserved word)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_documents_type', 'document_type'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_created_at', 'created_at'),
        Index('idx_documents_type_status', 'document_type', 'status'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, title={self.title})>"
