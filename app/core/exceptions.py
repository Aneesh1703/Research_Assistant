"""Custom exceptions for the Research Assistant API."""


class ResearchAssistantException(Exception):
    """Base exception for all custom exceptions."""
    pass


class DocumentNotFoundError(ResearchAssistantException):
    """Raised when a document is not found."""
    def __init__(self, document_id: str):
        self.document_id = document_id
        super().__init__(f"Document with ID '{document_id}' not found")


class InvalidDocumentTypeError(ResearchAssistantException):
    """Raised when an invalid document type is provided."""
    def __init__(self, document_type: str):
        self.document_type = document_type
        super().__init__(f"Invalid document type: '{document_type}'")


class FileTooLargeError(ResearchAssistantException):
    """Raised when uploaded file exceeds size limit."""
    def __init__(self, file_size: int, max_size: int):
        self.file_size = file_size
        self.max_size = max_size
        super().__init__(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )


class UnsupportedFileTypeError(ResearchAssistantException):
    """Raised when file type is not supported."""
    def __init__(self, filename: str, allowed_extensions: list):
        self.filename = filename
        self.allowed_extensions = allowed_extensions
        super().__init__(
            f"File type not supported. Allowed extensions: {', '.join(allowed_extensions)}"
        )


class DocumentProcessingError(ResearchAssistantException):
    """Raised when document processing fails."""
    def __init__(self, message: str):
        super().__init__(f"Document processing failed: {message}")


class InvalidQueryError(ResearchAssistantException):
    """Raised when query is invalid."""
    def __init__(self, message: str):
        super().__init__(f"Invalid query: {message}")
