from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.rag.pipeline import get_pipeline

router = APIRouter(prefix="/query", tags=["query"])


# Request/Response schemas
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    score_threshold: float = 0.5
    use_mmr: bool = True
    filter_document_id: Optional[str] = None


class Source(BaseModel):
    content: str
    metadata: Dict
    score: float
    id: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: str
    num_sources: int
    model_used: str


@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG.
    
    This endpoint:
    1. Searches vector database for relevant chunks
    2. Reranks with MMR for diversity
    3. Generates answer using Gemini
    4. Returns answer with citations
    """
    try:
        pipeline = get_pipeline()
        
        # Build filter if document_id specified
        filter_metadata = None
        if request.filter_document_id and request.filter_document_id != "string":
            filter_metadata = {"document_id": request.filter_document_id}
        
        # Query RAG system
        result = pipeline.query(
            question=request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            use_mmr=request.use_mmr,
            mmr_diversity=0.3,
            tier="auto",
            include_citations=True,
            filter_metadata=filter_metadata
        )
        
        return QueryResponse(
            answer=result.get("answer", "No answer generated"),
            sources=result.get("sources", []),
            confidence=result.get("confidence", "unknown"),
            num_sources=len(result.get("sources", [])),
            model_used=result.get("model_used", "unknown")
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Query error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics."""
    pipeline = get_pipeline()
    stats = pipeline.get_stats()
    return stats
