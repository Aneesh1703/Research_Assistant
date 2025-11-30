import streamlit as st
import requests
from typing import Optional
import os

# Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Page config
st.set_page_config(
    page_title="Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Helper functions
def upload_document(file) -> Optional[dict]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None

def get_documents() -> list:
    """Get list of all documents."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        response.raise_for_status()
        return response.json().get("documents", [])
    except Exception as e:
        st.error(f"Failed to fetch documents: {str(e)}")
        return []

def query_documents(question: str, top_k: int = 5, score_threshold: float = 0.5, use_mmr: bool = True) -> Optional[dict]:
    """Query the RAG system."""
    try:
        payload = {
            "question": question,
            "top_k": top_k,
            "score_threshold": score_threshold,
            "use_mmr": use_mmr
        }
        response = requests.post(f"{API_BASE_URL}/query/", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return None

def get_stats() -> Optional[dict]:
    """Get RAG system statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/query/stats")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def delete_document(doc_id: str) -> bool:
    """Delete a document."""
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{doc_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Delete failed: {str(e)}")
        return False

# Main UI
st.markdown('<h1 class="main-header">📚 Research Assistant</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # RAG Stats
    stats = get_stats()
    if stats:
        st.metric("Total Chunks", stats.get("total_chunks", 0))
        st.metric("Embedding Model", stats.get("embedding_model", "N/A"))
        st.caption(f"Collection: {stats.get('collection_name', 'N/A')}")
    
    st.divider()
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.session_state.documents = get_documents()
        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["🔍 Query", "📄 Documents", "📊 History"])

# Tab 1: Query Interface
with tab1:
    st.header("Ask Questions")
    
    # Query input
    question = st.text_area(
        "Enter your question:",
        placeholder="What are the main findings in the research papers?",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query_button = st.button("🚀 Search", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if query_button and question:
        with st.spinner("🧠 Analyzing question and searching documents..."):
            result = query_documents(
                question=question,
                top_k=5,  # Will be auto-adjusted by smart system
                score_threshold=0.5,  # Will be auto-adjusted by smart system
                use_mmr=True  # Will be auto-adjusted by smart system
            )
            
            if result:
                # Save to history
                st.session_state.query_history.insert(0, {
                    "question": question,
                    "answer": result.get("answer"),
                    "confidence": result.get("confidence"),
                    "num_sources": result.get("num_sources")
                })
                
                # Display answer
                st.subheader("📝 Answer")
                
                confidence = result.get("confidence", "unknown")
                confidence_class = f"confidence-{confidence}"
                st.markdown(f'<span class="{confidence_class}">Confidence: {confidence.upper()}</span>', unsafe_allow_html=True)
                
                st.markdown(result.get("answer", "No answer generated"))
                
                # Display sources
                st.subheader(f"📚 Sources ({result.get('num_sources', 0)})")
                
                sources = result.get("sources", [])
                for i, source in enumerate(sources, 1):
                    with st.expander(f"Source {i} - Score: {source.get('score', 0):.2f}"):
                        st.markdown(f"**Content:**")
                        st.text(source.get("content", ""))
                        
                        st.markdown(f"**Metadata:**")
                        metadata = source.get("metadata", {})
                        for key, value in metadata.items():
                            st.caption(f"{key}: {value}")

# Tab 2: Document Management
with tab2:
    st.header("Document Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        
        # Upload method tabs
        upload_tab1, upload_tab2, upload_tab3 = st.tabs(["📄 File", "🔗 URL", "✏️ Text"])
        
        # File Upload
        with upload_tab1:
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "txt", "md"],
                help="Upload PDF, TXT, or MD files (up to 100MB)"
            )
            
            if uploaded_file:
                if st.button("Upload File", type="primary", key="upload_file"):
                    with st.spinner("Uploading and indexing..."):
                        result = upload_document(uploaded_file)
                        if result:
                            st.success(f"✅ {result.get('message', 'Document uploaded successfully!')}")
                            st.session_state.documents = get_documents()
                            st.rerun()
        
        # URL Upload
        with upload_tab2:
            url_input = st.text_input(
                "Enter URL",
                placeholder="https://example.com/article",
                help="Paste a URL to scrape and index"
            )
            
            if url_input:
                if st.button("Fetch & Index URL", type="primary", key="upload_url"):
                    with st.spinner("Fetching and indexing URL..."):
                        try:
                            payload = {"url": url_input}
                            response = requests.post(f"{API_BASE_URL}/documents/url", json=payload)
                            response.raise_for_status()
                            result = response.json()
                            st.success(f"✅ {result.get('message', 'URL indexed successfully!')}")
                            st.session_state.documents = get_documents()
                            st.rerun()
                        except Exception as e:
                            st.error(f"URL upload failed: {str(e)}")
        
        # Text Upload
        with upload_tab3:
            text_title = st.text_input(
                "Document Title",
                placeholder="My Research Notes",
                help="Give your text document a title"
            )
            
            text_content = st.text_area(
                "Paste your text here",
                placeholder="Enter or paste your text content...",
                height=200,
                help="Paste any text content to index"
            )
            
            if text_title and text_content:
                if st.button("Index Text", type="primary", key="upload_text"):
                    with st.spinner("Indexing text..."):
                        try:
                            payload = {
                                "title": text_title,
                                "content": text_content
                            }
                            response = requests.post(f"{API_BASE_URL}/documents/text", json=payload)
                            response.raise_for_status()
                            result = response.json()
                            st.success(f"✅ {result.get('message', 'Text indexed successfully!')}")
                            st.session_state.documents = get_documents()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Text upload failed: {str(e)}")
    
    with col2:
        st.subheader("📊 Quick Stats")
        docs = get_documents()
        st.metric("Total Documents", len(docs))
        
        if stats:
            st.metric("Total Chunks", stats.get("total_chunks", 0))
    
    st.divider()
    
    # Document list
    st.subheader("📚 Your Documents")
    
    documents = get_documents()
    
    if documents:
        for doc in documents:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{doc.get('title', 'Untitled')}**")
                    st.caption(f"Type: {doc.get('document_type', 'N/A')} | Words: {doc.get('word_count', 0):,}")
                
                with col2:
                    st.caption(f"Created: {doc.get('created_at', 'N/A')[:10]}")
                
                with col3:
                    if st.button("🗑️", key=f"delete_{doc.get('document_id')}"):
                        if delete_document(doc.get('document_id')):
                            st.success("Deleted!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No documents uploaded yet. Upload your first document above!")

# Tab 3: Query History
with tab3:
    st.header("Query History")
    
    if st.session_state.query_history:
        for i, query in enumerate(st.session_state.query_history[:10], 1):
            with st.expander(f"Query {i}: {query['question'][:50]}..."):
                st.markdown(f"**Question:** {query['question']}")
                st.markdown(f"**Answer:** {query['answer'][:200]}...")
                st.caption(f"Confidence: {query['confidence']} | Sources: {query['num_sources']}")
    else:
        st.info("No queries yet. Try asking a question in the Query tab!")

# Footer
st.divider()
st.caption("🤖 Powered by E5-Base-v2 Embeddings + Gemini 2.0 Flash | Built with Streamlit")
