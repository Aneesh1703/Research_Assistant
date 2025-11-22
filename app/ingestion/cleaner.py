# app/ingestion/cleaner.py
import re

class TextCleaner:
    """Utility class for cleaning and normalizing text."""

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra spaces, tabs, and newlines."""
        return ' '.join(text.split())

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text."""
        return re.sub(r'http\S+|www\.\S+', '', text)

    @staticmethod
    def remove_special_chars(text: str) -> str:
        """Remove unwanted symbols."""
        return re.sub(r'[^A-Za-z0-9 .,;:\'\"!?()\-\n]', '', text)

    @staticmethod
    def clean_text(text: str) -> str:
        """Composite cleaner that calls other cleaning steps."""
        text = TextCleaner.remove_urls(text)
        text = TextCleaner.remove_special_chars(text)
        text = TextCleaner.remove_extra_whitespace(text)
        return text.strip()
