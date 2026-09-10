from __future__ import annotations

import numpy as np

from ml.similarity.embeddings import create_embedding_backend
from ml.similarity.vector_index import create_vector_index

_backend = None
_index = None
_review_ids: list[str] = []
_backend_name = "tfidf"
_index_name = "numpy"


def reset_similarity_state() -> None:
    global _backend, _index, _review_ids, _backend_name, _index_name
    _backend = None
    _index = None
    _review_ids = []
    _backend_name = "tfidf"
    _index_name = "numpy"


def similarity_runtime() -> dict[str, str]:
    return {"embedding_backend": _backend_name, "vector_index": _index_name}


def build_similarity_index(reviews: list[dict]) -> None:
    global _backend, _index, _review_ids, _backend_name, _index_name
    if not reviews:
        reset_similarity_state()
        return

    _review_ids = [str(review["review_id"]) for review in reviews]
    texts = [str(review.get("review_text") or "") for review in reviews]
    _backend = create_embedding_backend()
    _backend.fit(texts)
    embeddings = _backend.encode(texts)
    _index = create_vector_index()
    _index.build(_review_ids, embeddings)
    _backend_name = getattr(_backend, "name", "tfidf")
    _index_name = getattr(_index, "name", "numpy")


def _encode_query(review_text: str) -> np.ndarray:
    if _backend is None:
        return np.zeros((1, 1), dtype=np.float32)
    return _backend.encode([review_text])


def find_similar_reviews(
    review_id: str,
    review_text: str,
    threshold: float = 0.6,
    top_k: int = 10,
) -> list[dict]:
    if _index is None or not _review_ids:
        return []

    query = _encode_query(review_text)
    matches = _index.search(query, top_k=top_k + 1, threshold=threshold)
    results = []
    for match_id, score in matches:
        if match_id == review_id:
            continue
        results.append(
            {
                "review_id": match_id,
                "similarity_score": float(score),
                "similarity_type": "exact" if score > 0.95 else "semantic",
            }
        )
        if len(results) >= top_k:
            break
    return results


def pairwise_similarity_risk(review_id: str, review_text: str) -> tuple[float, list[dict]]:
    matches = find_similar_reviews(review_id, review_text, threshold=0.5)
    if not matches:
        return 0.0, []
    max_score = max(match["similarity_score"] for match in matches)
    risk = min(max_score * 0.8 + len(matches) * 0.05, 1.0)
    return risk, matches


def compute_all_pairs_efficient(reviews: list[dict], threshold: float = 0.7) -> list[dict]:
    build_similarity_index(reviews)
    pairs = []
    seen: set[tuple[str, str]] = set()
    for review in reviews:
        matches = find_similar_reviews(
            review["review_id"],
            review["review_text"],
            threshold=threshold,
        )
        for match in matches:
            pair_key = tuple(sorted([review["review_id"], match["review_id"]]))
            if pair_key in seen:
                continue
            seen.add(pair_key)
            pairs.append(
                {
                    "review_a_id": pair_key[0],
                    "review_b_id": pair_key[1],
                    "similarity_score": match["similarity_score"],
                    "similarity_type": match["similarity_type"],
                }
            )
    return pairs
