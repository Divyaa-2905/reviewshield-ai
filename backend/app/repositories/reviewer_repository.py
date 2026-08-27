from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.reviewer import Reviewer


class ReviewerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_reviewer_id(self, reviewer_id: str) -> Reviewer | None:
        return self.db.query(Reviewer).filter(Reviewer.reviewer_id == reviewer_id).first()

    def get_by_id(self, reviewer_db_id: int) -> Reviewer | None:
        return self.db.query(Reviewer).filter(Reviewer.id == reviewer_db_id).first()

    def list_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Reviewer], int]:
        query = self.db.query(Reviewer).order_by(Reviewer.suspicious_score.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def high_risk_count(self, threshold: float = 0.7) -> int:
        return self.db.query(Reviewer).filter(Reviewer.suspicious_score >= threshold).count()

    def create(self, **kwargs) -> Reviewer:
        reviewer = Reviewer(**kwargs)
        self.db.add(reviewer)
        self.db.commit()
        self.db.refresh(reviewer)
        return reviewer

    def update_metrics(self, reviewer: Reviewer) -> Reviewer:
        reviews = self.db.query(Review).filter(Review.reviewer_id == reviewer.id).all()
        if not reviews:
            return reviewer
        ratings = [r.rating for r in reviews]
        reviewer.total_reviews = len(reviews)
        reviewer.average_rating = sum(ratings) / len(ratings)
        mean = reviewer.average_rating
        reviewer.rating_variance = sum((r - mean) ** 2 for r in ratings) / len(ratings)
        reviewer.five_star_percentage = sum(1 for r in ratings if r == 5) / len(ratings)
        reviewer.product_count = len({r.product_id for r in reviews})
        self.db.commit()
        self.db.refresh(reviewer)
        return reviewer
