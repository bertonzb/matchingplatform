from typing import TypedDict, NotRequired


class AgentState(TypedDict):
    user_requirement: str
    top_n: int
    requirement_parsed: NotRequired[dict]
    candidate_companies: NotRequired[list[dict]]
    company_profiles: NotRequired[list[dict]]
    match_results: NotRequired[list[dict]]
    quality_score: NotRequired[float]
    quality_passed: NotRequired[bool]
    retry_count: NotRequired[int]
    final_results: NotRequired[list[dict]]
