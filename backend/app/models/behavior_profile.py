from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("reviewers.id"), unique=True, index=True)
    behavioural_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    temporal_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    rating_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    anomaly_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    observations: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    reviewer = relationship("Reviewer", back_populates="behavior_profile")
