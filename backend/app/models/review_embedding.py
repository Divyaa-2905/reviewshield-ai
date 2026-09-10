from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base


class ReviewEmbedding(Base):
    __tablename__ = "review_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    embedding: Mapped[list] = mapped_column(JSON().with_variant(SQLITE_JSON, "sqlite"))
    model_name: Mapped[str] = mapped_column(String(100), default="tfidf")
    dim: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
