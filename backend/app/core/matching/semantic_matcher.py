from app.core.knowledge.embedder import EmbeddingService

class SemanticMatcher:
    def __init__(self):
        self.embedder = EmbeddingService()

    def match(self, requirement_embedding: list[float],
              candidate_text: str) -> float:
        if not candidate_text:
            return 0.0
        candidate_emb = self.embedder.embed([candidate_text])[0]
        dot = sum(a * b for a, b in zip(requirement_embedding, candidate_emb))
        return (dot + 1) / 2 * 100  # cosine -> [0,100]
