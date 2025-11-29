import tiktoken
from typing import Optional
class TokenCounter:
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.encoding_name = encoding_name
    
    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return len(text) // 4
    
    def count_tokens_batch(self, texts: list[str]) -> list[int]:
        return [self.count_tokens(text) for text in texts]
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:

        if not text:
            return ""
        
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        

        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    def estimate_cost(
        self,
        text: str,
        input_cost_per_million: float,
        output_tokens: int = 0,
        output_cost_per_million: float = 0
    ) -> float:
        input_tokens = self.count_tokens(text)
        
        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million
        
        return input_cost + output_cost

_counter = TokenCounter()
def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return _counter.count_tokens(text)
def count_tokens_batch(texts: list[str]) -> list[int]:
    """Count tokens for multiple texts."""
    return _counter.count_tokens_batch(texts)
def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to max tokens."""
    return _counter.truncate_to_tokens(text, max_tokens)