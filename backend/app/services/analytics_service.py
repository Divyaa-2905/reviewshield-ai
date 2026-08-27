from sqlalchemy.orm import Session

from app.repositories.analysis_repository import ClusterRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.domain import DashboardStats


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.reviewer_repo = ReviewerRepository(db)
        self.cluster_repo = ClusterRepository(db)

    def get_dashboard_stats(self, model_version: str) -> DashboardStats:
        return DashboardStats(
            total_reviews=self.review_repo.count(),
            suspicious_reviews=self.prediction_repo.count_by_classification("Suspicious"),
            potentially_fake_reviews=self.prediction_repo.count_by_classification("Potentially Fake"),
            genuine_reviews=self.prediction_repo.count_by_classification("Genuine"),
            high_risk_reviewers=self.reviewer_repo.high_risk_count(),
            suspicious_clusters=self.cluster_repo.suspicious_count(),
            model_version=model_version,
        )

    def get_model_metrics(self) -> dict:
        predictions = self.prediction_repo.list_all()
        if not predictions:
            return {"message": "No predictions available. Run demo data seeding first."}

        classes = ["Genuine", "Suspicious", "Potentially Fake"]
        distribution = {c: self.prediction_repo.count_by_classification(c) for c in classes}
        return {
            "total_predictions": len(predictions),
            "classification_distribution": distribution,
            "avg_fraud_probability": sum(p.fraud_probability for p in predictions) / len(predictions),
            "modality_averages": {
                "text_risk": sum(p.text_risk for p in predictions) / len(predictions),
                "behavior_risk": sum(p.behavior_risk for p in predictions) / len(predictions),
                "temporal_risk": sum(p.temporal_risk for p in predictions) / len(predictions),
                "similarity_risk": sum(p.similarity_risk for p in predictions) / len(predictions),
                "graph_risk": sum(p.graph_risk for p in predictions) / len(predictions),
            },
        }
