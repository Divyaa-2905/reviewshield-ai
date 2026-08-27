from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reviewer(Base):
    __tablename__ = "reviewers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reviewer_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    account_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_variance: Mapped[float] = mapped_column(Float, default=0.0)
    five_star_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    product_count: Mapped[int] = mapped_column(Integer, default=0)
    review_frequency: Mapped[float] = mapped_column(Float, default=0.0)
    suspicious_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_demo: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    reviews = relationship("Review", back_populates="reviewer")
    behavior_profile = relationship("BehaviorProfile", back_populates="reviewer", uselist=False)
