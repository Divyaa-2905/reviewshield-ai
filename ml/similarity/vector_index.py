from __future__ import annotations

import numpy as np


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return matrix / norms


class NumpyVectorIndex:
    name = "numpy"

    def __init__(self) -> None:
        self.ids: list[str] = []
        self.matrix: np.ndarray | None = None

    def build(self, ids: list[str], embeddings: np.ndarray) -> None:
        self.ids = list(ids)
        self.matrix = _l2_normalize(np.asarray(embeddings, dtype=np.float32))

    def search(self, query: np.ndarray, top_k: int = 10, threshold: float = 0.5) -> list[tuple[str, float]]:
        if self.matrix is None or not len(self.ids):
            return []
        vector = _l2_normalize(np.asarray(query, dtype=np.float32).reshape(1, -1))[0]
        scores = self.matrix @ vector
        order = np.argsort(-scores)
        results: list[tuple[str, float]] = []
        for idx in order:
            score = float(scores[idx])
            if score < threshold:
                continue
            results.append((self.ids[idx], score))
            if len(results) >= top_k:
                break
        return results


class FaissVectorIndex:
    name = "faiss"

    def __init__(self) -> None:
        import faiss

        self._faiss = faiss
        self.ids: list[str] = []
        self._index = None

    def build(self, ids: list[str], embeddings: np.ndarray) -> None:
        matrix = _l2_normalize(np.asarray(embeddings, dtype=np.float32))
        self.ids = list(ids)
        dim = matrix.shape[1]
        self._index = self._faiss.IndexFlatIP(dim)
        self._index.add(matrix)

    def search(self, query: np.ndarray, top_k: int = 10, threshold: float = 0.5) -> list[tuple[str, float]]:
        if self._index is None or not self.ids:
            return []
        vector = _l2_normalize(np.asarray(query, dtype=np.float32).reshape(1, -1))
        k = min(max(top_k, 1), len(self.ids))
        scores, indices = self._index.search(vector, k)
        results: list[tuple[str, float]] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0:
                continue
            value = float(score)
            if value < threshold:
                continue
            results.append((self.ids[int(idx)], value))
        return results


def create_vector_index():
    try:
        return FaissVectorIndex()
    except ImportError:
        return NumpyVectorIndex()
