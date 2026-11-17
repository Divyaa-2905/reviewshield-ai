from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PredictionFeedback(Base):
    __tablename__ = "prediction_feedback"
    __table_args__ = (UniqueConstraint("prediction_id", name="uq_prediction_feedback_prediction_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), index=True)
    analyst_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    decision: Mapped[Literal["correct", "incorrect", "needs_correction"]] = mapped_column(
        String(30), index=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    prediction = relationship("Prediction")
    analyst = relationship("User")
