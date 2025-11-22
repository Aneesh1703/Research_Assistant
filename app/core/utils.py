"""Utility functions for the Research Assistant API."""
import uuid
import os
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeError, FileTooLargeError


def generate_document_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())


def calculate_word_count(text: str) -> int:
    """
    Calculate word count in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of words
    """
    if not text:
        return 0
    return len(text.split())


def get_content_preview(text: str, length: int = 200) -> str:
    """
    Get a preview of the content.
    
    Args:
        text: Full text content
        length: Maximum length of preview
        
    Returns:
        Preview string
    """
    if not text:
        return ""
    
    preview = text[:length]
    if len(text) > length:
        preview += "..."
    
    return preview


def validate_file_extension(filename: str) -> bool:
    """
    Validate if file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if valid, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


async def save_uploaded_file(file: UploadFile, directory: str) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        file: The uploaded file
        directory: Directory to save the file
        
    Returns:
        Path to the saved file
        
    Raises:
        UnsupportedFileTypeError: If file type is not allowed
        FileTooLargeError: If file is too large
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise UnsupportedFileTypeError(file.filename, settings.ALLOWED_EXTENSIONS)
    
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate unique filename
    file_id = generate_document_id()
    ext = get_file_extension(file.filename)
    new_filename = f"{file_id}{ext}"
    file_path = os.path.join(directory, new_filename)
    
    # Read and validate file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise FileTooLargeError(len(content), settings.MAX_UPLOAD_SIZE)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    Extract simple keywords from text (basic implementation).
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    # Simple word frequency approach
    words = text.lower().split()
    
    # Filter out common stop words (basic list)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                  'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                  'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        # Clean word (remove punctuation)
        word = ''.join(c for c in word if c.isalnum())
        if word and word not in stop_words and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]
