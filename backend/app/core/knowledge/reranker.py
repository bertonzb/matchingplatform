from FlagEmbedding import FlagReranker
from app.config import get_settings


class RerankerService:
    _model: FlagReranker | None = None

    def _load_model(self):
        if self._model is None:
            self._model = FlagReranker("BAAI/bge-reranker-large", use_fp16=True)
        return self._model

    def rerank(self, query: str, documents: list[str], top_k: int = 5) -> list[dict]:
        model = self._load_model()
        pairs = [[query, doc] for doc in documents]
        scores = model.compute_score(pairs, normalize=True)

        scored = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return [
            {"text": text, "relevance_score": float(score)}
            for text, score in scored[:top_k]
        ]
