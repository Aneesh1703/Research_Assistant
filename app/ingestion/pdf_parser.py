# app/ingestion/pdf_parser.py
import fitz  # PyMuPDF
from pathlib import Path


class PDFParser:
    """A class to parse PDF files and extract text."""

    def __init__(self, input_dir: str, output_dir: str, api_url: str = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.api_url = api_url

    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text("text")
        return text.strip()

    def clean_text(text: str) -> str:
        """Clean extracted text by removing extra whitespace."""
        return ' '.join(text.split())
    
    def extract_metadata(file_path: str) -> dict:
        """Extract metadata from PDF."""
        metadata = {}
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
    

    def send_to_api(text: str, metadata: dict) -> None:
        """Send extracted text and metadata to an external API."""
        import requests

        api_url = "https://example.com/api/upload"
        payload = {
            "text": text,
            "metadata": metadata
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()

    def save_text(self, text: str, output_path: str) -> None:
        """Save extracted text to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def process_pdfs(self) -> None:
        """Process all PDF files in the input directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for pdf_file in self.input_dir.glob("*.pdf"):
            print(f"Processing {pdf_file.name}...")
            text = self.parse_pdf(str(pdf_file))
            cleaned_text = self.clean_text(text)
            metadata = self.extract_metadata(str(pdf_file))

            output_file = self.output_dir / f"{pdf_file.stem}.txt"
            self.save_text(cleaned_text, str(output_file))

            if self.api_url:
                self.send_to_api(cleaned_text, metadata)

            print(f"Finished processing {pdf_file.name}.")

    def validate_pdf(file_path: str) -> bool:
        """Validate if the file is a readable PDF."""
        try:
            with fitz.open(file_path) as pdf:
                return True
        except Exception:
            return False