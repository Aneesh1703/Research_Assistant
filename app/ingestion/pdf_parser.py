# app/ingestion/pdf_parser.py
import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    text = ""
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text("text")
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


def extract_metadata(file_path: str) -> dict:
    """
    Extract metadata from PDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    metadata = {}
    try:
        with fitz.open(file_path) as pdf:
            doc_info = pdf.metadata
            metadata = {
                "title": doc_info.get("title", ""),
                "author": doc_info.get("author", ""),
                "subject": doc_info.get("subject", ""),
                "keywords": doc_info.get("keywords", ""),
                "creation_date": doc_info.get("creationDate", ""),
                "modification_date": doc_info.get("modDate", ""),
            }
        return metadata
    except Exception as e:
        return {}


def validate_pdf(file_path: str) -> bool:
    """
    Validate if the file is a readable PDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        True if valid PDF, False otherwise
    """
    try:
        with fitz.open(file_path) as pdf:
            return True
    except Exception:
        return False