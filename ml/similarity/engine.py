import re
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


_vectorizer: TfidfVectorizer | None = None
_corpus_matrix = None
_review_ids: list[str] = []


def _tokenize(text: str) -> str:
    return " ".join(re.findall(r"\b\w+\b", text.lower()))


def build_similarity_index(reviews: list[dict]) -> None:
    global _vectorizer, _corpus_matrix, _review_ids
    if not reviews:
        _vectorizer = None
        _corpus_matrix = None
        _review_ids = []
        return
    _review_ids = [r["review_id"] for r in reviews]
    texts = [_tokenize(r["review_text"]) for r in reviews]
    _vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    _corpus_matrix = _vectorizer.fit_transform(texts)


def find_similar_reviews(
    review_id: str,
    review_text: str,
    threshold: float = 0.6,
    top_k: int = 10,
) -> list[dict]:
    if _vectorizer is None or _corpus_matrix is None:
        return []

    query = _vectorizer.transform([_tokenize(review_text)])
    scores = cosine_similarity(query, _corpus_matrix).flatten()
    results = []
    for idx, score in enumerate(scores):
        if _review_ids[idx] == review_id:
            continue
        if score >= threshold:
            sim_type = "exact" if score > 0.95 else "semantic"
            results.append({
                "review_id": _review_ids[idx],
                "similarity_score": float(score),
                "similarity_type": sim_type,
            })
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:top_k]


def pairwise_similarity_risk(review_id: str, review_text: str) -> tuple[float, list[dict]]:
    matches = find_similar_reviews(review_id, review_text, threshold=0.5)
    if not matches:
        return 0.0, []
    max_score = max(m["similarity_score"] for m in matches)
    risk = min(max_score * 0.8 + len(matches) * 0.05, 1.0)
    return risk, matches


def compute_all_pairs_efficient(reviews: list[dict], threshold: float = 0.7) -> list[dict]:
    build_similarity_index(reviews)
    pairs = []
    seen = set()
    for review in reviews:
        matches = find_similar_reviews(review["review_id"], review["review_text"], threshold=threshold)
        for match in matches:
            pair_key = tuple(sorted([review["review_id"], match["review_id"]]))
            if pair_key in seen:
                continue
            seen.add(pair_key)
            pairs.append({
                "review_a_id": pair_key[0],
                "review_b_id": pair_key[1],
                "similarity_score": match["similarity_score"],
                "similarity_type": match["similarity_type"],
            })
    return pairs
