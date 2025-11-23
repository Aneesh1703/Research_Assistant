# 📚 Research Assistant API

A powerful FastAPI-based REST API for document ingestion, management, and querying. Built to support RAG (Retrieval-Augmented Generation) workflows with a clean, modular architecture.

## ✨ Features

- **📄 Multi-Format Document Ingestion**
  - PDF file uploads with text extraction
  - URL scraping and content extraction
  - Direct text input
  
- **🗂️ Document Management**
  - List documents with pagination and filtering
  - Retrieve full document details
  - Delete documents
  
- **🔍 Smart Processing**
  - Automatic text cleaning and normalization
  - Word count calculation
  - Content preview generation
  
- **🛡️ Robust Error Handling**
  - Custom exception handlers
  - Structured error responses
  - File validation (type, size)
  
- **📖 Interactive Documentation**
  - Swagger UI at `/docs`
  - ReDoc at `/redoc`
  - Auto-generated API specs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   cd "d:\Research Assistant\research_assistant"
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   GEMINI_API_KEY=
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Health Check
- `GET /api/v1/health` - Check API status

### Document Ingestion
- `POST /api/v1/documents/upload` - Upload PDF files
- `POST /api/v1/documents/url` - Ingest from URL
- `POST /api/v1/documents/text` - Submit text directly

### Document Management
- `GET /api/v1/documents` - List all documents (with pagination & filters)
- `GET /api/v1/documents/{document_id}` - Get specific document
- `DELETE /api/v1/documents/{document_id}` - Delete document

## 💡 Usage Examples

### Upload a PDF
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Ingest from URL
```bash
curl -X POST "http://localhost:8000/api/v1/documents/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "metadata": {"source": "web"}
  }'
```

### Submit Text
```bash
curl -X POST "http://localhost:8000/api/v1/documents/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your research text here...",
    "title": "Research Notes",
    "metadata": {"author": "John Doe"}
  }'
```

### List Documents
```bash
curl "http://localhost:8000/api/v1/documents?limit=10&offset=0"
```

### Get Document by ID
```bash
curl "http://localhost:8000/api/v1/documents/{document_id}"
```

### Delete Document
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}"
```

## 📁 Project Structure

```
research_assistant/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py       # Health check endpoint
│   │   │   │   └── documents.py    # Document CRUD endpoints
│   │   │   └── schemas.py          # Pydantic models
│   │   └── dependencies.py         # Shared dependencies
│   ├── core/
│   │   ├── config.py               # Configuration settings
│   │   ├── document_store.py       # In-memory document storage
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── logger.py               # Logging configuration
│   │   └── utils.py                # Utility functions
│   ├── ingestion/
│   │   ├── pdf_parser.py           # PDF text extraction
│   │   ├── web_scraper.py          # URL content scraping
│   │   └── cleaner.py              # Text cleaning utilities
│   ├── processing/
│   │   ├── text_splitter.py        # Text chunking (future)
│   │   └── summarizer.py           # Text summarization (future)
│   ├── rag/
│   │   ├── embedding.py            # Embeddings (future)
│   │   ├── vector_store.py         # Vector DB (future)
│   │   └── llm.py                  # LLM integration (future)
│   └── tests/
│       ├── test_ingestion.py       # Ingestion tests
│       └── test_query.py           # Query tests
├── data/
│   ├── raw/                        # Uploaded files
│   ├── processed/                  # Processed documents
│   ├── cache/                      # Cache storage
│   └── embeddings/                 # Vector embeddings
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
└── README.md                       # This file
```

## ⚙️ Configuration

Configuration is managed through environment variables and `app/core/config.py`.

### Key Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Research Assistant | Application name |
| `APP_VERSION` | 0.1.0 | API version |
| `DEBUG` | True | Debug mode |
| `API_HOST` | 127.0.0.1 | Server host |
| `API_PORT` | 8000 | Server port |
| `MAX_UPLOAD_SIZE` | 10MB | Maximum file upload size |
| `ALLOWED_EXTENSIONS` | .pdf, .txt, .md | Allowed file types |

## 🧪 Testing

Run tests with pytest:
```bash
pytest app/tests/ -v
```

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic
- **PDF Processing**: PyMuPDF (fitz)
- **Web Scraping**: BeautifulSoup4, Requests
- **Text Processing**: NLTK, tiktoken
- **Future**: LangChain, ChromaDB, Sentence Transformers

## 📝 Response Formats

### Success Response (Document Ingestion)
```json
{
  "document_id": "uuid-string",
  "document_type": "pdf|url|text",
  "status": "completed",
  "filename": "example.pdf",
  "content_preview": "First 200 characters...",
  "word_count": 1234,
  "created_at": "2025-11-23T07:00:00.000Z",
  "message": "Document ingested successfully."
}
```

### Error Response
```json
{
  "error": "Document Not Found",
  "detail": "Document with ID 'xxx' not found",
  "timestamp": "2025-11-23T07:00:00.000Z"
}
```

## 🔒 Security Features

- CORS middleware configured
- File type validation
- File size limits
- Input sanitization
- Error message sanitization in production

## 🚧 Roadmap

- [ ] Query endpoint with mock RAG
- [ ] Real RAG implementation with LangChain
- [ ] Vector database integration (ChromaDB/FAISS)
- [ ] Authentication & authorization (JWT)
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Async processing with Celery
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- PyMuPDF for PDF processing
- BeautifulSoup for web scraping
- The open-source community

---

**Built with ❤️ using FastAPI**
