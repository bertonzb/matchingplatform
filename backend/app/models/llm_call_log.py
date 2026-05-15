from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model: Mapped[str | None] = mapped_column(String(50))
    provider: Mapped[str | None] = mapped_column(String(50))
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 6))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.getdate()
    )
