import json

def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

class TagMatcher:
    def match(self, requirement_tags: list[str],
              candidate_tags_str: str | None) -> float:
        if not candidate_tags_str:
            return 0.0
        try:
            candidate_tags = set(json.loads(candidate_tags_str))
        except (json.JSONDecodeError, TypeError):
            return 0.0
        req_set = set(requirement_tags)
        return jaccard_similarity(req_set, candidate_tags) * 100
