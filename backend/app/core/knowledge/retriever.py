from app.core.knowledge.embedder import EmbeddingService
from app.core.knowledge.weaviate_store import WeaviateStore
from app.core.knowledge.reranker import RerankerService
from app.config import get_settings


class CompanyRetriever:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.store = WeaviateStore()
        self.reranker = RerankerService()

    def retrieve(self, query: str) -> list[dict]:
        settings = get_settings()
        query_vector = self.embedder.embed_query(query)
        raw_results = self.store.search(
            query_vector, top_k=settings.weaviate_top_k_recall
        )
        if not raw_results:
            return []

        chunks_text = [r["chunk_text"] for r in raw_results]
        reranked = self.reranker.rerank(
            query, chunks_text, top_k=settings.rerank_top_k
        )

        # Map reranked text back to Weaviate results
        seen = set()
        merged = []
        for rr in reranked:
            for raw in raw_results:
                if raw["company_id"] in seen:
                    continue
                if rr["text"] == raw["chunk_text"]:
                    raw["relevance_score"] = rr["relevance_score"]
                    merged.append(raw)
                    seen.add(raw["company_id"])
                    break
        return merged
