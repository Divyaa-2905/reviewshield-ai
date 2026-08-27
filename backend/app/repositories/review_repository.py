from sqlalchemy.orm import Session, joinedload

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_review_id(self, review_id: str) -> Review | None:
        return (
            self.db.query(Review)
            .options(joinedload(Review.reviewer), joinedload(Review.product))
            .filter(Review.review_id == review_id)
            .first()
        )

    def get_by_id(self, review_db_id: int) -> Review | None:
        return (
            self.db.query(Review)
            .options(joinedload(Review.reviewer), joinedload(Review.product))
            .filter(Review.id == review_db_id)
            .first()
        )

    def list_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Review], int]:
        query = (
            self.db.query(Review)
            .options(joinedload(Review.reviewer), joinedload(Review.product))
            .order_by(Review.review_timestamp.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def list_all(self) -> list[Review]:
        return self.db.query(Review).all()

    def create(self, **kwargs) -> Review:
        review = Review(**kwargs)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def count(self) -> int:
        return self.db.query(Review).count()
