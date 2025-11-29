from typing import Dict, List, Optional
from app.rag.embedding import get_embedder
from app.rag.vector_store import get_vector_store
from app.rag.retriever import get_retriever
from app.rag.llm import get_llm
from app.processing.text_splitter import DocumentChunker
import logging
logger = logging.getLogger(__name__)
class RAGPipeline:

    
    def __init__(self):
        """Initialize all components."""
        self.embedder = get_embedder()
        self.vector_store = get_vector_store()
        self.retriever = get_retriever()
        self.llm = get_llm()
        self.chunker = DocumentChunker()
        
        logger.info("pipeline initialized")
    
  
    
    def index_document(
        self,
        content: str,
        document_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        try:
            logger.info(f"Indexing document: {document_id}")
            
            #Chunk document
            chunks = self.chunker.chunk_document(
                content=content,
                document_id=document_id,
                metadata=metadata or {}
            )
            
            if not chunks:
                logger.warning(f"No chunks created for {document_id}")
                return {"success": False, "error": "No chunks created"}
            
            #Generate embeddings
            embeddings = self.embedder.embed_chunks(chunks)
            
            #Store in vector database
            self.vector_store.add_chunks(chunks, embeddings)
            
            # Return stats
            stats = {
                "success": True,
                "document_id": document_id,
                "total_chunks": len(chunks),
                "avg_chunk_length": sum(len(c["content"]) for c in chunks) / len(chunks),
                "embedding_dim": len(embeddings[0]) if embeddings else 0
            }
            
            logger.info(f" Indexed {document_id}: {len(chunks)} chunks")
            return stats
            
        except Exception as e:
            logger.error(f"Error indexing {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def index_batch(
        self,
        documents: List[Dict]
    ) -> List[Dict]:
        results = []
        
        for doc in documents:
            result = self.index_document(
                content=doc["content"],
                document_id=doc["document_id"],
                metadata=doc.get("metadata")
            )
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"Batch indexed: {successful}/{len(documents)} successful")
        
        return results
    
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        use_mmr: bool = True,
        mmr_diversity: float = 0.3,
        tier: str = "auto",
        include_citations: bool = True,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        try:
            logger.info(f"Query: '{question[:50]}...'")
            
            # 1. Retrieve relevant chunks
            chunks = self.retriever.retrieve(
                query=question,
                top_k=top_k,
                filter_metadata=filter_metadata,
                score_threshold=score_threshold,
                use_mmr=use_mmr,
                mmr_diversity=mmr_diversity
            )
            
            if not chunks:
                logger.warning("No relevant chunks found")
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # 2. Extract context
            context_chunks = [chunk["content"] for chunk in chunks]
            
            # 3. Generate answer with LLM
            answer = self.llm.generate_with_context(
                query=question,
                context_chunks=context_chunks,
                tier=tier,
                include_citations=include_citations
            )
            
            # 4. Build response
            response = {
                "answer": answer,
                "sources": [
                    {
                        "content": chunk["content"][:200] + "...",
                        "metadata": chunk["metadata"],
                        "score": chunk["score"],
                        "id": chunk["id"]
                    }
                    for chunk in chunks
                ],
                "confidence": self._calculate_confidence(chunks),
                "model_used": tier if tier != "auto" else "flash/pro",
                "num_sources": len(chunks)
            }
            
            logger.info(f"generated answer using {len(chunks)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Error in query pipeline: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "confidence": "error"
            }
    
    def query_with_context_window(
        self,
        question: str,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict:
        
        # Retrieve chunks that fit in context window
        chunks = self.retriever.retrieve_with_context_window(
            query=question,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Generate answer
        context_chunks = [chunk["content"] for chunk in chunks]
        answer = self.llm.generate_with_context(
            query=question,
            context_chunks=context_chunks,
            tier=kwargs.get("tier", "auto")
        )
        
        return {
            "answer": answer,
            "sources": chunks,
            "tokens_used": sum(len(c["content"].split()) for c in chunks)
        }
    
    def _calculate_confidence(self, chunks: List[Dict]) -> str:
        if not chunks:
            return "none"
        
        avg_score = sum(c["score"] for c in chunks) / len(chunks)
        
        if avg_score >= 0.8:
            return "high"
        elif avg_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def delete_document(self, document_id: str) -> Dict:
        try:
            deleted_count = self.vector_store.delete_document(document_id)
            return {
                "success": True,
                "document_id": document_id,
                "chunks_deleted": deleted_count
            }
        except Exception as e:
            logger.error(f"Error deleting {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict:
        vector_stats = self.vector_store.get_stats()
        
        return {
            "total_chunks": vector_stats["total_chunks"],
            "collection_name": vector_stats["collection_name"],
            "embedding_model": "E5-Base-v2",
            "embedding_dim": 768,
            "llm_models": ["gemini-1.5-flash", "gemini-1.5-pro"]
        }
# Singleton
_pipeline = None
def get_pipeline() -> RAGPipeline:
    """Get or create pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
