from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FraudCluster(Base):
    __tablename__ = "fraud_clusters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cluster_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    reviewer_count: Mapped[int] = mapped_column(Integer, default=0)
    product_count: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    reviewers: Mapped[list] = mapped_column(JSON, default=list)
    products: Mapped[list] = mapped_column(JSON, default=list)
    temporal_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    similarity_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    graph_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
