import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100))
    scale: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text())
    tags: Mapped[str | None] = mapped_column(Text())  # JSON array string
    weaviate_uuid: Mapped[str | None] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4())
    )
    entity_type: Mapped[str] = mapped_column(String(20), default="company")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.getdate()
    )
