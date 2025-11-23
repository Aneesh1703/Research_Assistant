# app/db/crud.py
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentTypeEnum, DocumentStatusEnum
from typing import List, Optional
from datetime import datetime


def create_document(db: Session, document_data: dict) -> Document:
    """Create a new document."""
    db_document = Document(**document_data)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: str) -> Optional[Document]:
    """Get document by ID."""
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    document_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Document]:
    """List documents with filters."""
    query = db.query(Document)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if status:
        query = query.filter(Document.status == status)
    
    return query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()


def get_total_count(db: Session) -> int:
    """Get total document count."""
    return db.query(Document).count()


def delete_document(db: Session, document_id: str) -> bool:
    """Delete document by ID."""
    document = get_document(db, document_id)
    if document:
        db.delete(document)
        db.commit()
        return True
    return False


def update_document(db: Session, document_id: str, updates: dict) -> Optional[Document]:
    """Update document fields."""
    document = get_document(db, document_id)
    if document:
        for key, value in updates.items():
            setattr(document, key, value)
        db.commit()
        db.refresh(document)
        return document
    return None


def search_documents(db: Session, query: str, max_results: int = 5) -> List[dict]:
    """Search documents by content (simple text search)."""
    documents = db.query(Document).filter(
        Document.content.ilike(f"%{query}%")
    ).limit(max_results).all()
    
    results = []
    for doc in documents:
        content_lower = doc.content.lower()
        query_lower = query.lower()
        score = content_lower.count(query_lower) * 0.1
        
        results.append({
            'document': doc,
            'relevance_score': min(score, 1.0)
        })
    
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
