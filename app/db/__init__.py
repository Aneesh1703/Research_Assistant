# app/db/__init__.py
from .database import get_db, init_db
from .models import Document

__all__ = ["get_db", "init_db", "Document"]
