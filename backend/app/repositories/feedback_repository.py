from sqlalchemy.orm import Session, joinedload

from app.models.prediction import Prediction
from app.models.prediction_feedback import PredictionFeedback
from app.models.review import Review


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_prediction_id(self, prediction_id: int) -> PredictionFeedback | None:
        return (
            self.db.query(PredictionFeedback)
            .options(
                joinedload(PredictionFeedback.prediction)
                .joinedload(Prediction.review)
                .joinedload(Review.product),
                joinedload(PredictionFeedback.analyst),
            )
            .filter(PredictionFeedback.prediction_id == prediction_id)
            .first()
        )

    def list_paginated(
        self,
        page: int,
        page_size: int,
        decision: str | None = None,
    ) -> tuple[list[PredictionFeedback], int]:
        query = self.db.query(PredictionFeedback).options(
            joinedload(PredictionFeedback.prediction)
            .joinedload(Prediction.review)
            .joinedload(Review.product),
            joinedload(PredictionFeedback.analyst),
        )
        if decision:
            query = query.filter(PredictionFeedback.decision == decision)
        total = query.count()
        items = (
            query.order_by(PredictionFeedback.updated_at.desc(), PredictionFeedback.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def list_all(self, decision: str | None = None) -> list[PredictionFeedback]:
        query = self.db.query(PredictionFeedback).options(
            joinedload(PredictionFeedback.prediction)
            .joinedload(Prediction.review)
            .joinedload(Review.product),
            joinedload(PredictionFeedback.analyst),
        )
        if decision:
            query = query.filter(PredictionFeedback.decision == decision)
        return query.order_by(PredictionFeedback.updated_at.desc(), PredictionFeedback.id.desc()).all()
