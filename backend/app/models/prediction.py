from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    fraud_probability: Mapped[float] = mapped_column(Float)
    classification: Mapped[str] = mapped_column(String(50))
    model_version: Mapped[str] = mapped_column(String(50))
    text_risk: Mapped[float] = mapped_column(Float, default=0.0)
    behavior_risk: Mapped[float] = mapped_column(Float, default=0.0)
    temporal_risk: Mapped[float] = mapped_column(Float, default=0.0)
    similarity_risk: Mapped[float] = mapped_column(Float, default=0.0)
    graph_risk: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    review = relationship("Review", back_populates="predictions")
