from .vector_store import VectorStore

class Retriever:
    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve(self, query, top_k=5):
        return self.store.search(None, top_k=top_k)
