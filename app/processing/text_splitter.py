from typing import List

def split_text(text: str, chunk_size: int = 500) -> List[str]:
    """Naive splitter by characters."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
