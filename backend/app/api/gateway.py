from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.llm_call_log import LLMCallLog

router = APIRouter(prefix="/api/v1/gateway", tags=["gateway"])


@router.get("/models")
def list_models():
    return {
        "models": [
            {"id": "qwen-turbo", "provider": "qwen"},
            {"id": "qwen-plus", "provider": "qwen"},
            {"id": "deepseek-chat", "provider": "deepseek"},
            {"id": "deepseek-reasoner", "provider": "deepseek"},
        ]
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(LLMCallLog.id)).scalar() or 0
    total_cost = db.query(func.sum(LLMCallLog.cost)).scalar() or 0
    avg_latency = db.query(func.avg(LLMCallLog.latency_ms)).scalar() or 0
    total_tokens = (
        db.query(func.sum(LLMCallLog.prompt_tokens)).scalar() or 0
        + db.query(func.sum(LLMCallLog.completion_tokens)).scalar() or 0
    )

    by_provider = db.query(
        LLMCallLog.provider,
        func.count(LLMCallLog.id),
        func.sum(LLMCallLog.cost),
    ).group_by(LLMCallLog.provider).all()

    return {
        "total_calls": total,
        "total_cost": round(float(total_cost), 6),
        "average_latency_ms": round(float(avg_latency), 1),
        "total_tokens": total_tokens,
        "by_provider": [
            {"provider": p, "calls": c, "cost": round(float(s), 6) if s else 0}
            for p, c, s in by_provider
        ],
    }
