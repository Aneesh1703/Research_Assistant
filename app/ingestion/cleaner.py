# app/ingestion/cleaner.py
import re


def remove_extra_whitespace(text: str) -> str:
    """Remove extra spaces, tabs, and newlines."""
    return ' '.join(text.split())


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    return re.sub(r'http\S+|www\.\S+', '', text)


def remove_special_chars(text: str) -> str:
    """Remove unwanted symbols."""
    return re.sub(r'[^A-Za-z0-9 .,;:\'"!?()\-\n]', '', text)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Apply cleaning steps
    text = remove_urls(text)
    text = remove_special_chars(text)
    text = remove_extra_whitespace(text)
    
    return text.strip()
