from sqlalchemy.orm import Session

from app.models.fraud_cluster import FraudCluster
from app.models.review_similarity import ReviewSimilarity


class SimilarityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_review(self, review_db_id: int, limit: int = 10) -> list[ReviewSimilarity]:
        return (
            self.db.query(ReviewSimilarity)
            .filter(
                (ReviewSimilarity.review_a_id == review_db_id)
                | (ReviewSimilarity.review_b_id == review_db_id)
            )
            .order_by(ReviewSimilarity.similarity_score.desc())
            .limit(limit)
            .all()
        )

    def create(self, **kwargs) -> ReviewSimilarity:
        record = ReviewSimilarity(**kwargs)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def bulk_create(self, records: list[dict]) -> None:
        self.db.bulk_insert_mappings(ReviewSimilarity, records)
        self.db.commit()


class ClusterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[FraudCluster], int]:
        query = self.db.query(FraudCluster).order_by(FraudCluster.risk_score.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_by_cluster_id(self, cluster_id: str) -> FraudCluster | None:
        return self.db.query(FraudCluster).filter(FraudCluster.cluster_id == cluster_id).first()

    def create(self, **kwargs) -> FraudCluster:
        cluster = FraudCluster(**kwargs)
        self.db.add(cluster)
        self.db.commit()
        self.db.refresh(cluster)
        return cluster

    def suspicious_count(self, threshold: float = 0.6) -> int:
        return self.db.query(FraudCluster).filter(FraudCluster.risk_score >= threshold).count()

    def delete_all(self) -> None:
        self.db.query(FraudCluster).delete()
        self.db.commit()
