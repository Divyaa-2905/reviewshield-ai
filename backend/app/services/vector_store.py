from __future__ import annotations

import json
from typing import Any

from ml.similarity.embeddings import create_embedding_backend
from ml.similarity.engine import build_similarity_index, similarity_runtime
from ml.similarity.vector_index import create_vector_index
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.review_embedding import ReviewEmbedding


class VectorStore:
    """FAISS/numpy runtime index with optional pgvector persistence on Postgres."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def _is_postgres(self) -> bool:
        return self.settings.database_url.startswith("postgresql")

    def ensure_pgvector(self) -> bool:
        if not self._is_postgres():
            return False
        try:
            self.db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            self.db.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS review_vectors (
                        review_id VARCHAR(100) PRIMARY KEY,
                        embedding vector,
                        model_name VARCHAR(100),
                        dim INTEGER
                    )
                    """
                )
            )
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def persist_embeddings(self, reviews: list[dict[str, Any]], backend_name: str) -> None:
        if not reviews:
            return
        backend = create_embedding_backend()
        texts = [str(review.get("review_text") or "") for review in reviews]
        backend.fit(texts)
        embeddings = backend.encode(texts)
        use_pgvector = self.ensure_pgvector()

        for review, vector in zip(reviews, embeddings, strict=False):
            review_id = str(review["review_id"])
            values = [float(v) for v in vector.tolist()]
            existing = (
                self.db.query(ReviewEmbedding)
                .filter(ReviewEmbedding.review_id == review_id)
                .first()
            )
            if existing:
                existing.embedding = values
                existing.model_name = backend_name
                existing.dim = len(values)
            else:
                self.db.add(
                    ReviewEmbedding(
                        review_id=review_id,
                        embedding=values,
                        model_name=backend_name,
                        dim=len(values),
                    )
                )
            if use_pgvector:
                self.db.execute(
                    text(
                        """
                        INSERT INTO review_vectors (review_id, embedding, model_name, dim)
                        VALUES (:review_id, CAST(:embedding AS vector), :model_name, :dim)
                        ON CONFLICT (review_id) DO UPDATE
                        SET embedding = EXCLUDED.embedding,
                            model_name = EXCLUDED.model_name,
                            dim = EXCLUDED.dim
                        """
                    ),
                    {
                        "review_id": review_id,
                        "embedding": "[" + ",".join(str(v) for v in values) + "]",
                        "model_name": backend_name,
                        "dim": len(values),
                    },
                )
        self.db.commit()

    def rebuild_runtime_index(self, reviews: list[dict[str, Any]], persist: bool = False) -> dict[str, str]:
        build_similarity_index(reviews)
        runtime = similarity_runtime()
        if persist:
            self.persist_embeddings(reviews, runtime["embedding_backend"])
        return runtime

    def search_pgvector(self, query_embedding: list[float], top_k: int = 10) -> list[dict]:
        if not self.ensure_pgvector():
            return []
        literal = "[" + ",".join(str(float(v)) for v in query_embedding) + "]"
        rows = self.db.execute(
            text(
                """
                SELECT review_id, 1 - (embedding <=> CAST(:query AS vector)) AS score
                FROM review_vectors
                ORDER BY embedding <=> CAST(:query AS vector)
                LIMIT :top_k
                """
            ),
            {"query": literal, "top_k": top_k},
        ).mappings()
        return [{"review_id": row["review_id"], "similarity_score": float(row["score"])} for row in rows]


def embeddings_from_json(value: object) -> list[float]:
    if isinstance(value, list):
        return [float(v) for v in value]
    if isinstance(value, str):
        parsed = json.loads(value)
        return [float(v) for v in parsed]
    return []


def local_index_from_stored(db: Session):
    rows = db.query(ReviewEmbedding).all()
    if not rows:
        return None
    ids = [row.review_id for row in rows]
    matrix = [embeddings_from_json(row.embedding) for row in rows]
    index = create_vector_index()
    import numpy as np

    index.build(ids, np.asarray(matrix, dtype=np.float32))
    return index
