from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("reviewers.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    rating: Mapped[float] = mapped_column(Float)
    review_text: Mapped[str] = mapped_column(Text)
    review_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    verified_purchase: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    review_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_demo: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    reviewer = relationship("Reviewer", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    predictions = relationship("Prediction", back_populates="review")
