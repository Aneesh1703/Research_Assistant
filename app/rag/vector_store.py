import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os
import logging
logger = logging.getLogger(__name__)
class ChromaVectorStore:
    
    def __init__(
        self,
        collection_name: str = "research_documents",
        persist_directory: str = "./data/chromadb"
    ):
        # Create directory if needed
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"chromaDB initialized at {persist_directory}")
        logger.info(f"   Collection: {collection_name}")
        logger.info(f"   Total documents: {self.collection.count()}")
    
    def add_chunks(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> None:
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) "
                "must have same length"
            )
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            # Create unique ID
            chunk_id = f"{chunk['document_id']}_chunk_{chunk['chunk_index']}"
            ids.append(chunk_id)
            
            # Store text content
            documents.append(chunk["content"])
            
            # Store metadata
            metadata = {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"],
                **chunk.get("metadata", {})
            }
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"added {len(chunks)} chunks to vector store")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # ChromaDB returns lists of lists, extract first element
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }
    
    def delete_document(self, document_id: str) -> int:
        # Get all chunks for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"deleted {len(results['ids'])} chunks for document {document_id}")
            return len(results["ids"])
        
        logger.warning(f"No chunks found for document {document_id}")
        return 0
    
    def get_stats(self) -> Dict:
        return {
            "total_chunks": self.collection.count(),
            "collection_name": self.collection.name
        }
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        
        return chunks
# Singleton instance
_vector_store = None
def get_vector_store() -> ChromaVectorStore:
    """Get or create vector store instance (singleton pattern)."""
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store
