from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from typing import List, Dict, Optional
class DocumentChunker:
    """Chunk documents using LlamaIndex."""
    
    def __init__(self, chunk_size=500, chunk_overlap=50, document_type="text"):
        """Initialize chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.document_type = document_type
        
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=" "
        )
    
    def chunk_document(self, content, document_id, metadata=None):
        if not content or not content.strip():
            return []
        if not document_id:
            raise ValueError("document_id required")
        
        doc = Document(
            text=content,
            metadata={
                "document_id": document_id,
                "document_type": self.document_type,
                **(metadata or {})
            }
        )
        
        nodes = self.splitter.get_nodes_from_documents([doc])
        
        chunks = []
        for i, node in enumerate(nodes):
            chunks.append({
                "content": node.text,
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(nodes),
                "node_id": node.node_id,
                "metadata": node.metadata
            })
        
        return chunks
    
    def get_stats(self, chunks):
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_length": 0,
                "min_length": 0,
                "max_length": 0
            }
        
        lengths = [len(c["content"]) for c in chunks]
        return {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths)
        }