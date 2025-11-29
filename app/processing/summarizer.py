from app.rag.llm import generate_response
from app.processing.tokenizer_utils import count_tokens, truncate_to_tokens
from typing import Optional, Literal
class DocumentSummarizer:
    """Generate document summaries using Gemini."""
    
    def __init__(self, max_input_tokens: int = 30000):

        self.max_input_tokens = max_input_tokens
    
    def summarize(
        self,
        text: str,
        summary_type: Literal["brief", "detailed", "bullet"] = "brief",
        max_length: Optional[int] = None
    ) -> str:

        if not text or not text.strip():
            return ""
        
        # Truncate if too long
        if count_tokens(text) > self.max_input_tokens:
            text = truncate_to_tokens(text, self.max_input_tokens)
        
        # Build prompt based on type
        prompt = self._build_prompt(text, summary_type, max_length)
        
        # Generate summary
        try:
            summary = generate_response(prompt)
            return summary.strip()
        except Exception as e:
            # Fallback to naive summary
            return text[:200] + "..."
    
    def _build_prompt(
        self,
        text: str,
        summary_type: str,
        max_length: Optional[int]
    ) -> str:
        """Build prompt for summarization."""
        
        length_instruction = ""
        if max_length:
            length_instruction = f"Keep the summary under {max_length} words."
        
        if summary_type == "brief":
            return f"""Provide a brief, concise summary of the following text. {length_instruction}
Text:
{text}
Summary:"""
        
        elif summary_type == "detailed":
            return f"""Provide a comprehensive summary of the following text, covering all key points. {length_instruction}
Text:
{text}
Detailed Summary:"""
        
        elif summary_type == "bullet":
            return f"""Summarize the following text as bullet points, highlighting the main ideas. {length_instruction}
Text:
{text}
Bullet Point Summary:"""
        
        else:
            return f"Summarize this text:\n\n{text}"
    
    def summarize_chunks(
        self,
        chunks: list[dict],
        combine: bool = True
    ) -> str | list[str]:

        if not chunks:
            return "" if combine else []
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = self.summarize(chunk["content"], summary_type="brief")
            chunk_summaries.append(summary)
        
        if not combine:
            return chunk_summaries
        
        # Combine summaries
        combined_text = "\n\n".join(chunk_summaries)
        return self.summarize(combined_text, summary_type="detailed")
# Convenience function (backward compatible)
_summarizer = DocumentSummarizer()
def summarize(text: str) -> str:
    """Generate brief summary of text."""
    return _summarizer.summarize(text, summary_type="brief")