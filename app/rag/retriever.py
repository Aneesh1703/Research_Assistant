from typing import List, Dict, Optional
from app.rag.vector_store import get_vector_store
from app.rag.embedding import get_embedder
import logging
logger = logging.getLogger(__name__)
class AdvancedRetriever:
    """Advanced semantic retriever with reranking and filtering."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embedder = get_embedder()
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None,
        score_threshold: float = 0.0,
        use_mmr: bool = False,
        mmr_diversity: float = 0.3
    ) -> List[Dict]:
        query_embedding = self.embedder.embed_query(query)
        
    
        initial_k = top_k * 2 if use_mmr else top_k
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=initial_k,
            filter_metadata=filter_metadata
        )
        
    
        chunks = self._format_results(results)
        
    
        chunks = self._filter_by_score(chunks, score_threshold)
        

        if use_mmr and len(chunks) > top_k:
            chunks = self._mmr_rerank(chunks, query_embedding, top_k, mmr_diversity)
        else:
            chunks = chunks[:top_k]
        
        chunks = self._deduplicate(chunks)
        
        logger.info(f"Retrieved {len(chunks)} chunks for query: '{query[:50]}...'")
        return chunks
    
    def retrieve_with_context_window(
        self,
        query: str,
        max_tokens: int = 4000,
        **kwargs
    ) -> List[Dict]:
        """Retrieve chunks that fit within token limit."""
        chunks = self.retrieve(query, **kwargs)
        
        filtered_chunks = []
        total_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = len(chunk["content"].split()) 
            if total_tokens + chunk_tokens <= max_tokens:
                filtered_chunks.append(chunk)
                total_tokens += chunk_tokens
            else:
                break
        
        logger.info(f"Filtered to {len(filtered_chunks)} chunks (~{total_tokens} tokens)")
        return filtered_chunks
    
    def _format_results(self, results: Dict) -> List[Dict]:
        """Format search results into chunks."""
        chunks = []
        for i in range(len(results["documents"])):
            # Convert distance to similarity score (0-1)
            distance = results["distances"][i]
            similarity = 1 - distance  # Cosine distance to similarity
            
            chunks.append({
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
                "score": similarity,
                "id": results["ids"][i]
            })
        
        return chunks
    
    def _filter_by_score(self, chunks: List[Dict], threshold: float) -> List[Dict]:
        """Filter chunks by minimum score."""
        if threshold <= 0:
            return chunks
        
        filtered = [c for c in chunks if c["score"] >= threshold]
        logger.info(f"Filtered {len(chunks)} → {len(filtered)} chunks (threshold: {threshold})")
        return filtered
    
    def _mmr_rerank(
        self,
        chunks: List[Dict],
        query_embedding: List[float],
        top_k: int,
        diversity: float
    ) -> List[Dict]:
        """Maximal Marginal Relevance reranking for diversity.
        
        MMR balances relevance and diversity to avoid redundant results.
        """
        import numpy as np
        
        if len(chunks) <= top_k:
            return chunks
        
        # Get embeddings for all chunks
        chunk_texts = [c["content"] for c in chunks]
        chunk_embeddings = self.embedder.embed_batch(chunk_texts, is_query=False)
        
        query_emb = np.array(query_embedding)
        chunk_embs = np.array(chunk_embeddings)
        
        # MMR algorithm
        selected_indices = []
        remaining_indices = list(range(len(chunks)))
        
        # Select first (most similar to query)
        similarities = np.dot(chunk_embs, query_emb)
        first_idx = np.argmax(similarities)
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # Select remaining using MMR
        while len(selected_indices) < top_k and remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # Relevance to query
                relevance = similarities[idx]
                
                # Max similarity to already selected
                selected_embs = chunk_embs[selected_indices]
                redundancy = np.max(np.dot(selected_embs, chunk_embs[idx]))
                
                # MMR score
                mmr = diversity * relevance - (1 - diversity) * redundancy
                mmr_scores.append((idx, mmr))
            
            # Select best MMR score
            best_idx = max(mmr_scores, key=lambda x: x[1])[0]
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Return reranked chunks
        reranked = [chunks[i] for i in selected_indices]
        logger.info(f"MMR reranked {len(chunks)} → {len(reranked)} chunks")
        return reranked
    
    def _deduplicate(self, chunks: List[Dict]) -> List[Dict]:
        """Remove duplicate or very similar chunks."""
        if len(chunks) <= 1:
            return chunks
        
        unique_chunks = []
        seen_content = set()
        
        for chunk in chunks:
            # Simple deduplication by content hash
            content_hash = hash(chunk["content"][:100])  # First 100 chars
            
            if content_hash not in seen_content:
                unique_chunks.append(chunk)
                seen_content.add(content_hash)
        
        if len(unique_chunks) < len(chunks):
            logger.info(f"Deduplicated {len(chunks)} → {len(unique_chunks)} chunks")
        
        return unique_chunks
# Singleton
_retriever = None
def get_retriever() -> AdvancedRetriever:
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = AdvancedRetriever()
    return _retriever