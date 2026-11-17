from datetime import UTC

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.evaluation.evaluate import evaluate_predictions
from ml.fusion.model import fuse_modalities
from ml.graph.intelligence import analyze_graph, build_review_graph
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.similarity.engine import (
    compute_all_pairs_efficient,
    pairwise_similarity_risk,
    reset_similarity_state,
)
from ml.temporal.analyzer import analyze_temporal_patterns
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.review import Review
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
        reviews = self.review_repo.list_all()
        training_reviews, test_reviews = self._chronological_split(reviews)
        training_payloads = [self._review_payload(review) for review in training_reviews]
        test_payloads = [self._review_payload(review) for review in test_reviews]

        scored_test = []
        try:
            similarity_pairs = compute_all_pairs_efficient(training_payloads, threshold=0.5)
            graph_analysis = analyze_graph(build_review_graph(training_payloads, similarity_pairs))
            for review, payload in zip(test_reviews, test_payloads):
                history = [
                    training_payload
                    for training_review, training_payload in zip(training_reviews, training_payloads)
                    if training_review.reviewer_id == review.reviewer_id
                ]
                history_available = bool(history)
                behavior_risk = 0.0
                temporal_risk = 0.0
                if history_available:
                    behavior = analyze_reviewer_behavior(
                        history,
                        review.reviewer.account_created_at if review.reviewer else None,
                    )
                    temporal = analyze_temporal_patterns(history)
                    behavior_risk = behavior["behavior_risk"]
                    temporal_risk = temporal["temporal_risk"]

                similarity_risk, _ = pairwise_similarity_risk(
                    payload["review_id"],
                    payload["review_text"],
                )
                result = fuse_modalities(
                    text_risk=text_risk_score(analyze_text(payload["review_text"])),
                    behavior_risk=behavior_risk,
                    temporal_risk=temporal_risk,
                    similarity_risk=similarity_risk,
                    graph_risk=graph_analysis["graph_risk"],
                    model_version=get_settings().ml_model_version,
                    history_available=history_available,
                )
                scored_test.append(
                    {
                        "review_pk": review.id,
                        "classification": result.classification,
                        "fraud_probability": result.fraud_probability,
                        "text_risk": result.modality_scores.text_risk,
                        "behavior_risk": result.modality_scores.behavior_risk,
                        "temporal_risk": result.modality_scores.temporal_risk,
                        "similarity_risk": result.modality_scores.similarity_risk,
                        "graph_risk": result.modality_scores.graph_risk,
                    }
                )
        finally:
            reset_similarity_state()

        test_labels = {
            review.id: {
                "review_id": review.review_id,
                "review_label": review.review_label,
            }
            for review in test_reviews
        }
        evaluation = evaluate_predictions(scored_test, test_labels)
        evaluation_details = dict(evaluation)
        modality_names = (
            "text_risk",
            "behavior_risk",
            "temporal_risk",
            "similarity_risk",
            "graph_risk",
        )
        evaluation.update(
            {
                "total_reviews": len(reviews),
                "training_reviews": len(training_reviews),
                "test_reviews": len(test_reviews),
                "evaluation_protocol": (
                    "Chronological holdout: the earliest portion (target 80%) provides historical "
                    "context; reviews at or after the cutoff are evaluated."
                ),
                "evaluation_note": (
                    "This system uses fixed heuristics and does not fit a model. Each test review is "
                    "scored as the current input using earlier records only; other test reviews and "
                    "all test labels are excluded from feature context. Unlabeled test reviews are "
                    "not included in performance metrics."
                ),
                "data_source": self._data_source(test_reviews),
                "avg_fraud_probability": self._average(scored_test, "fraud_probability"),
                "modality_averages": {
                    name: self._average(scored_test, name) for name in modality_names
                },
                "threshold": evaluation.get("threshold", 0.4),
                "evaluation": evaluation_details,
            }
        )
        return evaluation

    @staticmethod
    def _timestamp_key(review: Review) -> float:
        timestamp = review.review_timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return timestamp.timestamp()

    @classmethod
    def _chronological_split(cls, reviews: list[Review]) -> tuple[list[Review], list[Review]]:
        ordered = sorted(reviews, key=cls._timestamp_key)
        if len(ordered) < 2:
            return ordered, []
        split_at = min(len(ordered) - 1, max(1, int(len(ordered) * 0.8)))
        cutoff = cls._timestamp_key(ordered[split_at])
        training = [review for review in ordered if cls._timestamp_key(review) < cutoff]
        test = [review for review in ordered if cls._timestamp_key(review) >= cutoff]
        return training, test

    @staticmethod
    def _review_payload(review: Review) -> dict:
        return {
            "review_id": review.review_id,
            "reviewer_id": review.reviewer.reviewer_id if review.reviewer else str(review.reviewer_id),
            "product_id": review.product.product_id if review.product else str(review.product_id),
            "rating": review.rating,
            "review_text": review.review_text,
            "review_timestamp": review.review_timestamp,
        }

    @staticmethod
    def _average(rows: list[dict], key: str) -> float:
        return sum(float(row[key]) for row in rows) / len(rows) if rows else 0.0

    @staticmethod
    def _data_source(reviews: list[Review]) -> str:
        if not reviews:
            return "no labeled holdout data"
        demo_count = sum(bool(review.is_demo) for review in reviews)
        if demo_count == len(reviews):
            return "demo/sample"
        if demo_count:
            return "mixed demo and stored data"
        return "stored review data"
