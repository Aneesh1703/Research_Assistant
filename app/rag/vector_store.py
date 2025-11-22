class VectorStore:
    def __init__(self):
        self.vectors = []

    def add(self, texts, vectors):
        for t, v in zip(texts, vectors):
            self.vectors.append((t, v))

    def search(self, q_vector, top_k=5):
        # naive returning first top_k
        return [t for t, _ in self.vectors[:top_k]]
