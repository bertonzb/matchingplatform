import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class MatchingTask(Base):
    __tablename__ = "matching_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False,
        default=lambda: str(uuid.uuid4())
    )
    user_requirement: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    top_n: Mapped[int] = mapped_column(Integer, default=5)
    result: Mapped[str | None] = mapped_column(Text())  # JSON string
    celery_task_id: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.getdate()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
