# FastAPI imports
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional

# Schemas
from app.api.v1.schemas import (
    DocumentIngestResponse,
    URLIngestRequest,
    TextIngestRequest,
    DocumentListResponse,
    DocumentMetadata,
    DocumentDetail,
    DocumentDeleteResponse,
    DocumentType,
    DocumentStatus
)

# Core utilities
from app.core.document_store import document_store
from app.core.utils import (
    save_uploaded_file,
    calculate_word_count,
    get_content_preview,
    generate_document_id
)
from app.core.config import settings
from app.core.exceptions import (
    DocumentNotFoundError,
    UnsupportedFileTypeError,
    FileTooLargeError,
    DocumentProcessingError
)

# Ingestion modules
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.web_scraper import scrape_url
from app.ingestion.cleaner import clean_text  

# Standard library
import os
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["ingestion"])

@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint to upload and ingest a PDF document."""
    file_path = None
    try:
        # Save uploaded file to raw data directory
        file_path = await save_uploaded_file(file, settings.RAW_DATA_DIR)

        # Parse PDF to extract text
        text = parse_pdf(file_path)

        if not text or not text.strip():
            raise DocumentProcessingError("No text extracted from PDF.")

        text = clean_text(text)

        # Generate document metadata
        word_count = calculate_word_count(text)
        content_preview = get_content_preview(text)

        document_data = {
            "document_type": DocumentType.PDF,  # Use .PDF not .pdf
            "status": DocumentStatus.COMPLETED,  # Use .COMPLETED not .processed
            "filename": file.filename,
            "url": None,
            "title": os.path.splitext(file.filename)[0],
            "content": text,
            "word_count": word_count,
            "metadata": {}
        }

        # Store document in the document store (returns document_id)
        document_id = document_store.add_document(document_data)

        return DocumentIngestResponse(
            document_id=document_id,
            document_type=DocumentType.PDF,
            status=DocumentStatus.COMPLETED,
            filename=file.filename,
            url=None,
            content_preview=content_preview,
            word_count=word_count,
            message="PDF document ingested successfully."
        )
    
    except (UnsupportedFileTypeError, FileTooLargeError, DocumentProcessingError) as e:
        # Clean up file if it was saved
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Clean up file if it was saved
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/url", response_model=DocumentIngestResponse)
async def ingest_url(request: URLIngestRequest):
    """Endpoint to ingest a document from a URL."""
    try:
        # Scrape the URL to extract content
        result = scrape_url(str(request.url))  # Convert HttpUrl to string

        content = result.get("content", "")
        title = result.get("title", "Untitled")

        if not content or not content.strip():
            raise DocumentProcessingError("No content extracted from URL.")

        content = clean_text(content)

        # Generate document metadata
        word_count = calculate_word_count(content)
        content_preview = get_content_preview(content)

        document_data = {
            "document_type": DocumentType.URL,
            "status": DocumentStatus.COMPLETED,
            "filename": None,
            "url": str(request.url),  # Convert to string
            "title": title,
            "content": content,
            "word_count": word_count,
            "metadata": request.metadata or {}  # Include user-provided metadata
        }

        # Store document in the document store (returns document_id)
        document_id = document_store.add_document(document_data)

        return DocumentIngestResponse(
            document_id=document_id,
            document_type=DocumentType.URL,
            status=DocumentStatus.COMPLETED,
            filename=None,
            url=str(request.url),  # Convert to string
            content_preview=content_preview,
            word_count=word_count,
            message="URL document ingested successfully."
        )
    
    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/text", response_model=DocumentIngestResponse)
async def ingest_text(request: TextIngestRequest):
    #endpoint to ingest text as it is 

    try:

        if not request.content or not request.content.strip():
            raise DocumentProcessingError("Text content is empty")
        request.content = clean_text(request.content)

        # Generate document metadata
        word_count = calculate_word_count(request.content)
        content_preview = get_content_preview(request.content)

        document_data = {
            "document_type": DocumentType.TEXT,
            "status": DocumentStatus.COMPLETED,
            "filename": None,
            "url": None,
            "title": request.title,
            "content": request.content,
            "word_count": word_count,
            "metadata": request.metadata or {}  # Include user-provided metadata
        }

        # Store document in the document store (returns document_id)
        document_id = document_store.add_document(document_data)

        return DocumentIngestResponse(
            document_id=document_id,
            document_type=DocumentType.TEXT,
            status=DocumentStatus.COMPLETED,
            filename=None,
            url=None,
            content_preview=content_preview,
            word_count=word_count,
            message="Text document ingested successfully."
        )
    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    document_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None
):
    """List all documents with optional filtering and pagination."""
    # Get documents from store
    documents = document_store.list_documents(
        limit=limit,
        offset=offset,
        document_type=document_type.value if document_type else None,
        status=status.value if status else None
    )
    
    # Get total count
    total = document_store.get_total_count()
    
    # Convert to DocumentMetadata objects
    document_metadata_list = [
        DocumentMetadata(
            document_id=doc["document_id"],
            document_type=DocumentType(doc["document_type"]),
            status=DocumentStatus(doc["status"]),
            filename=doc.get("filename"),
            url=doc.get("url"),
            title=doc.get("title"),
            word_count=doc["word_count"],
            created_at=doc["created_at"],
            processed_at=doc.get("processed_at"),
            metadata=doc.get("metadata", {})
        )
        for doc in documents
    ]
    
    return DocumentListResponse(
        total=total,
        documents=document_metadata_list
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str):
    """Get a specific document by ID."""
    document = document_store.get_document(document_id)
    
    if not document:
        raise DocumentNotFoundError(document_id)
    
    return DocumentDetail(
        document_id=document["document_id"],
        document_type=DocumentType(document["document_type"]),
        status=DocumentStatus(document["status"]),
        filename=document.get("filename"),
        url=document.get("url"),
        title=document.get("title"),
        content=document["content"],
        word_count=document["word_count"],
        created_at=document["created_at"],
        processed_at=document.get("processed_at"),
        metadata=document.get("metadata", {})
    )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """Delete a document by ID."""
    # Get document first to check if it exists and get file path
    document = document_store.get_document(document_id)
    
    if not document:
        raise DocumentNotFoundError(document_id)
    
    # Delete from store
    success = document_store.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    # Delete associated file if it's a PDF
    if document.get("filename") and document["document_type"] == "pdf":
        file_path = os.path.join(settings.RAW_DATA_DIR, f"{document_id}.pdf")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Failed to delete file {file_path}: {e}")
    
    return DocumentDeleteResponse(
        document_id=document_id,
        message="Document deleted successfully"
    )
    