import json
from sqlalchemy.orm import Session
from app.core.agents.state import AgentState
from app.core.gateway.router import GatewayRouter
from app.core.knowledge.retriever import CompanyRetriever
from app.core.knowledge.embedder import EmbeddingService
from app.core.matching.engine import MatchingEngine
from app.models.company import Company
from app.config import get_settings

DATA_COLLECTION_PROMPT = """从以下用户需求中提取结构化信息，返回JSON:
{{
  "text": "原文本",
  "tags": ["标签1", "标签2"],
  "industry": "行业",
  "scale": "规模"
}}

用户需求: {requirement}"""

PROFILE_PROMPT = """根据以下企业信息，提取关键特征摘要（100字以内）:

企业: {company_info}

返回JSON: {{"profile": "摘要文本", "key_tags": ["标签"], "strengths": ["优势"]}}"""

QUALITY_PROMPT = """评估以下匹配结果的质量，给出0-100的综合质量分。

需求: {requirement}
匹配结果: {results}

返回JSON: {{"quality_score": 85, "passed": true, "feedback": "评价"}}"""


async def data_collection_node(state: AgentState, db: Session):
    router = GatewayRouter()
    retriever = CompanyRetriever()

    # Parse requirement with LLM
    resp, _, _ = await router.chat_completion(
        messages=[{"role": "user", "content": DATA_COLLECTION_PROMPT.format(
            requirement=state["user_requirement"]
        )}],
        model="qwen-turbo",
        temperature=0.1,
    )
    content = resp["choices"][0]["message"]["content"]
    requirement_parsed = json.loads(content.strip())

    # Retrieve candidate companies via semantic search
    candidates = retriever.retrieve(requirement_parsed.get("text", state["user_requirement"]))

    # Enrich with DB data
    company_ids = list({c["company_id"] for c in candidates})
    db_companies = db.query(Company).filter(Company.id.in_(company_ids)).all()
    db_map = {c.id: c for c in db_companies}

    enriched = []
    for c in candidates:
        comp = db_map.get(c["company_id"])
        if comp:
            enriched.append({
                "id": comp.id,
                "name": comp.name,
                "industry": comp.industry,
                "scale": comp.scale,
                "description": comp.description,
                "tags": comp.tags,
            })

    return {
        "requirement_parsed": requirement_parsed,
        "candidate_companies": enriched,
    }


async def profile_building_node(state: AgentState, db: Session):
    router = GatewayRouter()

    profiles = []
    for company in state.get("candidate_companies", []):
        info = json.dumps({
            "name": company.get("name"),
            "industry": company.get("industry"),
            "description": company.get("description"),
            "tags": company.get("tags"),
        }, ensure_ascii=False)

        resp, _, _ = await router.chat_completion(
            messages=[{"role": "user", "content": PROFILE_PROMPT.format(
                company_info=info
            )}],
            model="qwen-turbo",
            temperature=0.1,
        )
        content = resp["choices"][0]["message"]["content"]
        profile = json.loads(content.strip())
        profile["company_id"] = company["id"]
        profiles.append(profile)

    return {"company_profiles": profiles}


async def matching_analysis_node(state: AgentState, db: Session):
    engine = MatchingEngine(db)
    requirement = state.get("requirement_parsed", {})
    requirement["text"] = state["user_requirement"]

    results = await engine.evaluate(requirement, state.get("candidate_companies", []))
    top_n = state.get("top_n", 5)
    return {"match_results": results[:top_n]}


async def quality_check_node(state: AgentState, db: Session):
    router = GatewayRouter()
    settings = get_settings()

    results_str = json.dumps(state.get("match_results", []), ensure_ascii=False)
    resp, _, _ = await router.chat_completion(
        messages=[{"role": "user", "content": QUALITY_PROMPT.format(
            requirement=state["user_requirement"],
            results=results_str,
        )}],
        model="qwen-turbo",
        temperature=0.1,
    )
    content = resp["choices"][0]["message"]["content"]
    quality = json.loads(content.strip())

    passed = quality.get("passed", False) or quality.get("quality_score", 0) >= settings.matching_quality_threshold
    return {
        "quality_score": quality.get("quality_score", 0),
        "quality_passed": passed,
        "final_results": state.get("match_results", []),
    }


def should_retry(state: AgentState) -> str:
    settings = get_settings()
    retries = state.get("retry_count", 0)
    if not state.get("quality_passed", False) and retries < settings.matching_max_retries:
        return "retry"
    return "done"
