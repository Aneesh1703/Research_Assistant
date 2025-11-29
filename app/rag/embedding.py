from sentence_transformers import SentenceTransformer
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)
class E5Embedder:
    def __init__(self, model_name: str = "intfloat/e5-base-v2"):

        logger.info(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 768
        logger.info(f"Model loaded! Embedding dimension: {self.embedding_dim}")
    
    def embed_chunks(self, chunks: List[Dict]) -> List[List[float]]:
        if not chunks:
            return []
        
        # Extract text content
        texts = [chunk["content"] for chunk in chunks]
        
        # Add E5 prefix for passages (improves retrieval)
        prefixed_texts = [f"passage: {text}" for text in texts]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            prefixed_texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10,
            batch_size=32
        )
        
        logger.info(f"generated {len(embeddings)} embeddings")
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        # Add E5 prefix for queries
        prefixed_query = f"query: {query}"
        
        embedding = self.model.encode(
            prefixed_query,
            convert_to_numpy=True
        )
        
        return embedding.tolist()
    
    def embed_batch(
        self,
        texts: List[str],
        is_query: bool = False
    ) -> List[List[float]]:
        prefix = "query: " if is_query else "passage: "
        prefixed_texts = [f"{prefix}{text}" for text in texts]
        
        embeddings = self.model.encode(
            prefixed_texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10,
            batch_size=32
        )
        
        return embeddings.tolist()
# Singleton instance for reuse
_embedder = None
def get_embedder() -> E5Embedder:
    """Get or create embedder instance (singleton pattern)."""
    global _embedder
    if _embedder is None:
        _embedder = E5Embedder()
    return _embedder