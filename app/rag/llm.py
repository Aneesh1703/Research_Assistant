import importlib
from app.core.config import settings
from typing import List, Optional, Literal
import logging
logger = logging.getLogger(__name__)
try:
    genai = importlib.import_module("google.generativeai")
except ModuleNotFoundError:
    genai = None
if genai is not None:
    genai.configure(api_key=settings.GEMINI_API_KEY)
class GeminiLLM:
    """Tiered Gemini LLM with RAG support."""
    
    def __init__(self):
        if genai is None:
            raise RuntimeError("google.generativeai not installed")
        
        self.flash_model = genai.GenerativeModel("gemini-2.5-flash")
        self.pro_model = genai.GenerativeModel("gemini-2.5-pro")
        logger.info("Gemini models initialized (Flash + Pro)")
    
    def generate(
        self,
        prompt: str,
        tier: Literal["flash", "pro", "auto"] = "auto",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response with tier selection."""
        
        # Auto-select tier
        if tier == "auto":
            tier = self._select_tier(prompt)
        
        model = self.pro_model if tier == "pro" else self.flash_model
        
        # Configure generation
        config = {
            "temperature": temperature,
        }
        if max_tokens:
            config["max_output_tokens"] = max_tokens
        
        logger.info(f"Generating with {tier.upper()}")
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    
    def generate_with_context(
        self,
        query: str,
        context_chunks: List[str],
        tier: Literal["flash", "pro", "auto"] = "auto",
        include_citations: bool = True
    ) -> str:
        """Generate answer using retrieved context (RAG)."""
        
        # Build context
        context = self._build_context(context_chunks, include_citations)
        
        # Build RAG prompt
        prompt = f"""You are a helpful research assistant. Answer the question based on the provided context.
Context:
{context}
Question: {query}
Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Be concise but comprehensive
{"- Include source references [1], [2], etc. when citing information" if include_citations else ""}
Answer:"""
        
        return self.generate(prompt, tier=tier)
    
    def _build_context(self, chunks: List[str], include_citations: bool) -> str:
        """Build formatted context from chunks."""
        if include_citations:
            return "\n\n".join([
                f"[{i+1}] {chunk}"
                for i, chunk in enumerate(chunks)
            ])
        else:
            return "\n\n".join(chunks)
    
    def _select_tier(self, prompt: str) -> str:
        # Use Pro for complex/long prompts
        if len(prompt) > 2000:
            return "pro"
        
        # Keywords suggesting complexity
        complex_keywords = [
            "analyze", "compare", "explain in detail",
            "comprehensive", "evaluate", "critique"
        ]
        if any(kw in prompt.lower() for kw in complex_keywords):
            return "pro"
        
        return "flash"
# Singleton
_llm = None
def get_llm() -> GeminiLLM:
    """Get or create LLM instance."""
    global _llm
    if _llm is None:
        _llm = GeminiLLM()
    return _llm
# Backward compatible function
def generate_response(prompt: str) -> str:
    """Generate response using Flash (backward compatible)."""
    return get_llm().generate(prompt, tier="flash")