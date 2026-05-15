from sqlalchemy.orm import Session
from app.core.matching.tag_matcher import TagMatcher
from app.core.matching.semantic_matcher import SemanticMatcher
from app.core.matching.business_rule_matcher import BusinessRuleMatcher
from app.core.matching.llm_scorer import LLMScorer

WEIGHTS = {
    "tag": 0.3,
    "semantic": 0.4,
    "rule": 0.2,
    "llm": 0.1,
}

class MatchingEngine:
    def __init__(self, db: Session):
        self.db = db
        self.tag_matcher = TagMatcher()
        self.semantic_matcher = SemanticMatcher()
        self.rule_matcher = BusinessRuleMatcher()
        self.llm_scorer = LLMScorer(db)

    async def evaluate(self, requirement: dict, candidates: list[dict]) -> list[dict]:
        req_text = requirement.get("text", "")
        req_tags = requirement.get("tags", [])
        req_industry = requirement.get("industry")
        req_scale = requirement.get("scale")

        # Pre-compute requirement embedding
        req_embedding = self.semantic_matcher.embedder.embed_query(req_text)

        results = []
        for candidate in candidates:
            tag_score = self.tag_matcher.match(req_tags, candidate.get("tags"))
            semantic_score = self.semantic_matcher.match(
                req_embedding, candidate.get("description", "")
            )
            rule_score = self.rule_matcher.match(
                req_industry, candidate.get("industry"),
                req_scale, candidate.get("scale"),
            )

            llm_result = await self.llm_scorer.score(
                req_text, candidate, tag_score, semantic_score, rule_score
            )

            total_score = (
                tag_score * WEIGHTS["tag"]
                + semantic_score * WEIGHTS["semantic"]
                + rule_score * WEIGHTS["rule"]
                + llm_result["score"] * WEIGHTS["llm"]
            )

            results.append({
                "company_name": candidate.get("name", ""),
                "company_id": candidate.get("id"),
                "total_score": round(total_score, 2),
                "dimensions": {
                    "tag_overlap": round(tag_score, 2),
                    "semantic_similarity": round(semantic_score, 2),
                    "business_rule": round(rule_score, 2),
                    "llm_score": llm_result["score"],
                },
                "explanation": llm_result["explanation"],
                "confidence": llm_result["confidence"],
            })

        results.sort(key=lambda x: x["total_score"], reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1

        return results
