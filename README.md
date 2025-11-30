# 📚 Research Assistant - Intelligent RAG System

An advanced document Q&A system powered by RAG (Retrieval Augmented Generation) with smart auto-optimization, LLM-based document routing, and a beautiful Streamlit UI.

**Ask questions about your documents in natural language and get accurate answers with citations!**

---

## ✨ Key Features

### 🎯 **Smart Auto-Optimization**
- **Automatic Query Classification** - Detects question type and adjusts retrieval parameters
- **LLM-Based Document Routing** - Intelligently identifies which document you're asking about
- **Adaptive Retrieval** - Optimizes for precision vs. recall based on query type
- **Zero Configuration** - Works perfectly out of the box

### 📄 **Multi-Source Document Ingestion**
- **PDF Upload** - Up to 100MB, automatic text extraction
- **URL Scraping** - Fetch and index web content
- **Direct Text Input** - Paste notes, snippets, research findings

### 🧠 **Advanced RAG Pipeline**
- **E5-Base-v2 Embeddings** - High-quality semantic search (768 dimensions)
- **ChromaDB Vector Store** - Persistent, local vector database
- **Gemini 2.0 Flash/Pro** - Tiered LLM with auto-selection
- **MMR Reranking** - Balances relevance and diversity
- **Citation Support** - Answers include source references

### 🎨 **Beautiful Streamlit UI**
- **Query Tab** - Ask questions, get answers with confidence scores
- **Documents Tab** - Upload via File/URL/Text, manage documents
- **History Tab** - Track past queries and answers
- **Real-time Stats** - Monitor chunks, embeddings, collection info

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (running locally or remote)
- Gemini API Key ([Get one free](https://aistudio.google.com/app/apikey))

### Installation

```bash
# 1. Navigate to project
cd "d:\Research Assistant\research_assistant"

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Copy .env.example to .env and fill in:
# - GEMINI_API_KEY (required)
# - DATABASE_URL (PostgreSQL connection)
```

### Running the Application

**Terminal 1 - FastAPI Backend:**
```bash
uvicorn main:app --reload
```
API available at: http://localhost:8000

**Terminal 2 - Streamlit UI:**
```bash
streamlit run streamlit_app.py
```
UI available at: http://localhost:8501

---

## 🎯 How It Works

### 1. **Upload Documents**
```
📄 Upload PDF → 📝 Extract Text → ✂️ Chunk (500 tokens) → 
🧮 Generate Embeddings → 💾 Store in ChromaDB
```

### 2. **Ask Questions**
```
❓ Your Question → 🧠 Classify Query Type → 🎯 Route to Document → 
🔍 Semantic Search → 🔄 MMR Reranking → 🤖 Gemini Generates Answer
```

### 3. **Get Smart Answers**
```
✅ Answer with Citations
✅ Confidence Score (High/Medium/Low)
✅ Source Chunks with Similarity Scores
✅ Auto-Optimized for Your Question Type
```

---

## 🎨 Smart Features Explained

### **Auto Query Classification**

The system detects your question type and optimizes automatically:

| Question Type | Example | Auto Settings |
|--------------|---------|---------------|
| **Factual** | "What is X?" | 3 chunks, high precision |
| **Summary** | "Summarize findings" | 10 chunks, broad coverage |
| **Comparative** | "Compare A vs B" | 8 chunks, diverse results |
| **Analytical** | "Why/How does X?" | 7 chunks, balanced |

**No manual tuning needed!**

### **LLM Document Routing**

**Problem:** Large documents dominate search results  
**Solution:** Gemini automatically identifies which document you're asking about

```
You: "What's in my resume?"
System: 🧠 Detects "resume" → Routes to your CV → Answers from CV only
```

**Handles synonyms:** CV = resume, paper = article, etc.

---

## 📖 API Endpoints

### **Document Management**
- `POST /api/v1/documents/upload` - Upload PDF files
- `POST /api/v1/documents/url` - Ingest from URL
- `POST /api/v1/documents/text` - Submit text directly
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete document

### **Query**
- `POST /api/v1/query/` - Ask questions about your documents
- `GET /api/v1/query/stats` - Get RAG system statistics

### **Health**
- `GET /api/v1/health` - Check API status

**Interactive Docs:** http://localhost:8000/docs

---

## 💡 Usage Examples

### **Via Streamlit UI (Recommended)**

1. **Upload a Document**
   - Go to "Documents" tab
   - Choose File/URL/Text
   - Upload your document

2. **Ask Questions**
   - Go to "Query" tab
   - Type: "What are the main findings?"
   - Get instant answer with sources!

### **Via API**

**Upload PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@research_paper.pdf"
```

**Query:**
```bash
curl -X POST "http://localhost:8000/api/v1/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key findings?",
    "top_k": 5,
    "score_threshold": 0.5,
    "use_mmr": true
  }'
```

**Response:**
```json
{
  "answer": "Based on the research, the key findings are...",
  "sources": [...],
  "confidence": "high",
  "num_sources": 5,
  "model_used": "flash"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI (Port 8501)        │
│  - Query Interface                      │
│  - Document Management                  │
│  - History Tracking                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)        │
│  - Document Ingestion                   │
│  - Query Processing                     │
│  - Smart Routing                        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │  ChromaDB   │
│ (Metadata)  │  │  (Vectors)  │
└─────────────┘  └─────────────┘
       │                │
       └───────┬────────┘
               ▼
       ┌──────────────┐
       │ Gemini 2.0   │
       │ Flash/Pro    │
       └──────────────┘
```

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Async web framework
- PostgreSQL - Document metadata
- ChromaDB - Vector storage
- SQLAlchemy - ORM

**RAG Components:**
- E5-Base-v2 - Embeddings (768-dim)
- LlamaIndex - Text chunking
- Gemini 2.0 - LLM (Flash/Pro)
- tiktoken - Token counting

**Frontend:**
- Streamlit - Interactive UI
- Requests - API client

**Processing:**
- PyPDF2 - PDF parsing
- BeautifulSoup4 - Web scraping
- sentence-transformers - Embeddings

---

## ⚙️ Configuration

**Environment Variables (.env):**

```bash
# Required
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/RA_db

# Optional (defaults provided)
EMBEDDING_MODEL=intfloat/e5-base-v2
VECTOR_DB_PATH=data/chromadb
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_UPLOAD_SIZE=104857600  # 100MB
```

---

## 📊 Performance

**Indexing:**
- ~100 chunks/second
- Depends on document size

**Query Latency:**
- Retrieval: ~100-200ms
- LLM generation: ~1-3 seconds (Flash)
- **Total: ~1.5-3 seconds per query**

**Scalability:**
- Tested with 100+ documents
- 10,000+ chunks
- Sub-second retrieval

---

## 🎓 Use Cases

✅ **Academic Research** - Index papers, compare methodologies  
✅ **Document Q&A** - Upload manuals, get instant answers  
✅ **Knowledge Base** - Build personal knowledge repository  
✅ **Content Analysis** - Analyze multiple documents, summarize findings  

---

## 📁 Project Structure

```
research_assistant/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── documents.py    # Document CRUD + RAG indexing
│   │   ├── query.py        # Query endpoint
│   │   └── health.py       # Health check
│   ├── rag/
│   │   ├── embedding.py    # E5-Base-v2 embedder
│   │   ├── vector_store.py # ChromaDB wrapper
│   │   ├── retriever.py    # Advanced retrieval + MMR
│   │   ├── llm.py          # Gemini Flash/Pro
│   │   └── pipeline.py     # RAG orchestration + smart features
│   ├── processing/
│   │   ├── text_splitter.py    # LlamaIndex chunker
│   │   ├── tokenizer_utils.py  # Token counting
│   │   └── summarizer.py       # Document summarization
│   ├── ingestion/
│   │   ├── pdf_parser.py   # PDF extraction
│   │   ├── web_scraper.py  # URL scraping
│   │   └── cleaner.py      # Text cleaning
│   ├── db/
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── crud.py         # Database operations
│   │   └── database.py     # DB connection
│   └── core/
│       ├── config.py       # Settings
│       └── utils.py        # Utilities
├── streamlit_app.py        # Streamlit UI
├── main.py                 # FastAPI app
└── data/
    ├── chromadb/           # Vector database
    └── raw/                # Uploaded files
```

---

## 🚧 Roadmap

- [x] Multi-source document ingestion
- [x] Smart query classification
- [x] LLM-based document routing
- [x] Advanced RAG pipeline
- [x] Streamlit UI
- [ ] Conversational memory
- [ ] Multi-hop reasoning
- [ ] Document clustering
- [ ] Advanced analytics
- [ ] Mobile app

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 👤 Author

**Aneesh Kulkarni**

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- LlamaIndex for semantic chunking
- ChromaDB for vector storage
- Google for Gemini API
- Streamlit for the beautiful UI
- The open-source community

---

**Built with ❤️ using FastAPI, Streamlit, and Gemini 2.0**

**⭐ Star this repo if you find it useful!**
