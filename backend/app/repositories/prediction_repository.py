from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_for_review(self, review_db_id: int) -> Prediction | None:
        return (
            self.db.query(Prediction)
            .filter(Prediction.review_id == review_db_id)
            .order_by(Prediction.created_at.desc())
            .first()
        )

    def get_by_id(self, prediction_id: int) -> Prediction | None:
        return self.db.query(Prediction).filter(Prediction.id == prediction_id).first()

    def list_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Prediction], int]:
        query = self.db.query(Prediction).order_by(Prediction.created_at.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def create(self, **kwargs) -> Prediction:
        prediction = Prediction(**kwargs)
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def count_by_classification(self, classification: str) -> int:
        return self.db.query(Prediction).filter(Prediction.classification == classification).count()

    def list_all(self) -> list[Prediction]:
        return self.db.query(Prediction).all()
