from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReviewSimilarity(Base):
    __tablename__ = "review_similarities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_a_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    review_b_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    similarity_score: Mapped[float] = mapped_column(Float)
    similarity_type: Mapped[str] = mapped_column(String(50))
    same_product: Mapped[bool] = mapped_column(default=False)
    same_reviewer: Mapped[bool] = mapped_column(default=False)
    time_difference_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
