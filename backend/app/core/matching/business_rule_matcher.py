class BusinessRuleMatcher:
    def match(self, req_industry: str | None, candidate_industry: str | None,
              req_scale: str | None, candidate_scale: str | None) -> float:
        score = 100.0
        if req_industry and candidate_industry:
            if req_industry != candidate_industry:
                score -= 40
        if req_scale and candidate_scale:
            scale_map = {"\u521d\u521b": 1, "\u4e2d\u5c0f": 2, "\u5927\u578b": 3, "\u96c6\u56e2": 4}
            diff = abs(
                scale_map.get(req_scale, 0) - scale_map.get(candidate_scale, 0)
            )
            score -= diff * 10
        return max(score, 0.0)
