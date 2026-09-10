from datetime import datetime

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.explainability.explainer import explain_prediction
from ml.fusion.model import fuse_modalities
from ml.graph.intelligence import analyze_graph, build_review_graph
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.similarity.engine import pairwise_similarity_risk, similarity_runtime
from ml.temporal.analyzer import analyze_temporal_patterns
from sqlalchemy.orm import Session

import app.bootstrap  # noqa: F401
from app.core.config import get_settings
from app.repositories.review_repository import ReviewRepository
from app.services.vector_store import VectorStore


class MLService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.review_repo = ReviewRepository(db)
        self.vector_store = VectorStore(db)

    def _review_payload(self, review) -> dict:
        return {
            "review_id": review.review_id,
            "reviewer_id": str(review.reviewer.reviewer_id if review.reviewer else review.reviewer_id),
            "product_id": str(review.product.product_id if review.product else review.product_id),
            "rating": review.rating,
            "review_text": review.review_text,
            "review_timestamp": review.review_timestamp,
        }

    def _get_reviewer_reviews(self, reviewer_db_id: int) -> list[dict]:
        from app.models.review import Review

        reviews = self.db.query(Review).filter(Review.reviewer_id == reviewer_db_id).all()
        return [self._review_payload(review) for review in reviews]

    def _corpus(self) -> list[dict]:
        return [self._review_payload(review) for review in self.review_repo.list_all()]

    def analyze_review(
        self,
        review_text: str,
        rating: float,
        reviewer_db_id: int | None = None,
        review_id: str = "adhoc",
        review_timestamp: datetime | None = None,
    ):
        text_features = analyze_text(review_text)
        text_risk = text_risk_score(text_features)
        text_observations = []
        if text_risk > 0.3:
            text_observations.append("Review text shows suspicious linguistic patterns.")

        reviewer_reviews = self._get_reviewer_reviews(reviewer_db_id) if reviewer_db_id else []
        history_available = bool(reviewer_db_id and reviewer_reviews)

        behavior_risk = 0.0
        behavior_observations = []
        temporal_risk = 0.0
        temporal_observations = []
        if history_available:
            from app.models.reviewer import Reviewer

            reviewer = self.db.query(Reviewer).filter(Reviewer.id == reviewer_db_id).first()
            behavior = analyze_reviewer_behavior(
                reviewer_reviews,
                reviewer.account_created_at if reviewer else None,
            )
            behavior_risk = behavior["behavior_risk"]
            behavior_observations = behavior["observations"]
            temporal = analyze_temporal_patterns(reviewer_reviews)
            temporal_risk = temporal["temporal_risk"]
            temporal_observations = temporal["observations"]
        else:
            behavior_observations.append(
                "Reviewer history unavailable; behavior and temporal weights were redistributed."
            )

        all_reviews = self._corpus()
        runtime = (
            self.vector_store.rebuild_runtime_index(all_reviews, persist=False)
            if all_reviews
            else similarity_runtime()
        )
        similarity_risk, similarity_matches = pairwise_similarity_risk(review_id, review_text)

        graph = build_review_graph(all_reviews)
        graph_analysis = analyze_graph(graph)
        graph_risk = graph_analysis["graph_risk"]
        graph_observations = graph_analysis["observations"]

        result = fuse_modalities(
            text_risk=text_risk,
            behavior_risk=behavior_risk,
            temporal_risk=temporal_risk,
            similarity_risk=similarity_risk,
            graph_risk=graph_risk,
            model_version=self.settings.ml_model_version,
            history_available=history_available,
        )
        result.similarity_backend = runtime.get("embedding_backend", "tfidf")

        explained = explain_prediction(
            result,
            observations={
                "text": text_observations,
                "behavior": behavior_observations,
                "temporal": temporal_observations,
                "graph": graph_observations,
            },
            similarity_matches=similarity_matches,
        )
        return explained

    def analyze_and_store(self, review_db_id: int):
        from app.repositories.prediction_repository import PredictionRepository

        review = self.review_repo.get_by_id(review_db_id)
        if not review:
            return None

        result = self.analyze_review(
            review_text=review.review_text,
            rating=review.rating,
            reviewer_db_id=review.reviewer_id,
            review_id=review.review_id,
            review_timestamp=review.review_timestamp,
        )

        prediction = PredictionRepository(self.db).create(
            review_id=review.id,
            fraud_probability=result.fraud_probability,
            classification=result.classification,
            model_version=result.model_version,
            text_risk=result.modality_scores.text_risk,
            behavior_risk=result.modality_scores.behavior_risk,
            temporal_risk=result.modality_scores.temporal_risk,
            similarity_risk=result.modality_scores.similarity_risk,
            graph_risk=result.modality_scores.graph_risk,
            explanation=result.explanation,
        )
        return prediction
