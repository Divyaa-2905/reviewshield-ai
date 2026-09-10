from __future__ import annotations

import os
import re
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"


def _tokenize(text: str) -> str:
    return " ".join(re.findall(r"\b\w+\b", str(text).lower()))


class TfidfEmbeddingBackend:
    name = "tfidf"

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        tokenized = [_tokenize(text) for text in texts]
        if not any(tokenized):
            tokenized = ["empty"]
        self._vectorizer.fit(tokenized)
        self._fitted = True

    def encode(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            self.fit(texts)
        matrix = self._vectorizer.transform([_tokenize(text) for text in texts])
        dense = matrix.toarray().astype(np.float32)
        return _l2_normalize(dense)


class SentenceTransformerBackend:
    name = "sentence-transformers"

    def __init__(self, model_name: str = DEFAULT_TRANSFORMER_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def fit(self, texts: list[str]) -> None:
        return None

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return matrix / norms


def configured_backend_name() -> str:
    return os.getenv("SIMILARITY_BACKEND", "auto").strip().lower()


@lru_cache(maxsize=1)
def _load_sentence_transformer(model_name: str) -> SentenceTransformerBackend | None:
    try:
        return SentenceTransformerBackend(model_name)
    except (ImportError, OSError, RuntimeError):
        return None


def create_embedding_backend(
    preferred: str | None = None,
    model_name: str = DEFAULT_TRANSFORMER_MODEL,
):
    choice = (preferred or configured_backend_name()).strip().lower()
    if choice in {"sentence-transformers", "transformer", "st", "auto"}:
        backend = _load_sentence_transformer(model_name)
        if backend is not None:
            return backend
        if choice != "auto":
            raise RuntimeError(
                "SIMILARITY_BACKEND=sentence-transformers but sentence-transformers is unavailable"
            )
    return TfidfEmbeddingBackend()
