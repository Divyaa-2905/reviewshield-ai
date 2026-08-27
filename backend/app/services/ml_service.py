from datetime import datetime

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.explainability.explainer import explain_prediction
from ml.fusion.model import fuse_modalities
from ml.graph.intelligence import analyze_graph, build_review_graph
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.similarity.engine import build_similarity_index, pairwise_similarity_risk
from ml.temporal.analyzer import analyze_temporal_patterns
from sqlalchemy.orm import Session

import app.bootstrap  # noqa: F401
from app.core.config import get_settings
from app.repositories.review_repository import ReviewRepository


class MLService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.review_repo = ReviewRepository(db)

    def _get_reviewer_reviews(self, reviewer_db_id: int) -> list[dict]:
        from app.models.review import Review

        reviews = self.db.query(Review).filter(Review.reviewer_id == reviewer_db_id).all()
        return [
            {
                "review_id": r.review_id,
                "reviewer_id": str(r.reviewer_id),
                "product_id": str(r.product_id),
                "rating": r.rating,
                "review_text": r.review_text,
                "review_timestamp": r.review_timestamp,
            }
            for r in reviews
        ]

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

        behavior_risk = 0.0
        behavior_observations = []
        if reviewer_db_id:
            from app.models.reviewer import Reviewer

            reviewer = self.db.query(Reviewer).filter(Reviewer.id == reviewer_db_id).first()
            if reviewer:
                revs = self._get_reviewer_reviews(reviewer_db_id)
                behavior = analyze_reviewer_behavior(revs, reviewer.account_created_at)
                behavior_risk = behavior["behavior_risk"]
                behavior_observations = behavior["observations"]

        temporal_risk = 0.0
        temporal_observations = []
        if reviewer_db_id:
            revs = self._get_reviewer_reviews(reviewer_db_id)
            temporal = analyze_temporal_patterns(revs)
            temporal_risk = temporal["temporal_risk"]
            temporal_observations = temporal["observations"]

        all_reviews = [
            {
                "review_id": r.review_id,
                "reviewer_id": str(r.reviewer_id),
                "product_id": str(r.product_id),
                "rating": r.rating,
                "review_text": r.review_text,
                "review_timestamp": r.review_timestamp,
            }
            for r in self.review_repo.list_all()
        ]
        build_similarity_index(all_reviews)
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
        )

        return explain_prediction(
            result,
            observations={
                "text": text_observations,
                "behavior": behavior_observations,
                "temporal": temporal_observations,
                "graph": graph_observations,
            },
            similarity_matches=similarity_matches,
        )

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
