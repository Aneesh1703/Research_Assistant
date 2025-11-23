"""Research Assistant API - Main Application Entry Point"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.v1.endpoints import health, documents
from app.core.config import settings
from app.core.exceptions import (
    DocumentNotFoundError,
    UnsupportedFileTypeError,
    FileTooLargeError,
    DocumentProcessingError
)
from app.api.v1.schemas import ErrorResponse
from app.db.database import init_db
import os


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Initializing database...")
    init_db()  # Create database tables
    print("✅ Database initialized!")
    
    os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started successfully!")
    print(f"📚 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    yield
    # Shutdown (if needed)
    print("Shutting down...")



# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Research Assistant API for document ingestion and querying",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Exception handlers
@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Document Not Found",
            detail=str(exc)
        ).model_dump()
    )

@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    return JSONResponse(
        status_code=413,
        content=ErrorResponse(
            error="File Too Large",
            detail=str(exc)
        ).model_dump()
    )

@app.exception_handler(UnsupportedFileTypeError)
async def unsupported_file_handler(request: Request, exc: UnsupportedFileTypeError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Unsupported File Type",
            detail=str(exc)
        ).model_dump()
    )

@app.exception_handler(DocumentProcessingError)
async def document_processing_handler(request: Request, exc: DocumentProcessingError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Document Processing Error",
            detail=str(exc)
        ).model_dump()
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(documents.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Use import string instead of app object
        host=settings.API_HOST, 
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

