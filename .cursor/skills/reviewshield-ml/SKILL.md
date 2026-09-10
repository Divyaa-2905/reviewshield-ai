---
name: reviewshield-ml
description: Change ReviewShield fusion weights, similarity embeddings, FAISS indexing, or modality scoring. Use when editing ml/, MLService, Sentence-Transformers, or reviewer-history weighting.
---

# ReviewShield ML

## Fusion

Use `resolve_modality_weights()` / `fuse_modalities(..., history_available=False)` when reviewer history is missing. Zero-weight missing modalities and renormalize the rest. Do not leave behavior/temporal at 0.25/0.20 with dummy zeros.

## Similarity

Runtime order:

1. Embeddings: Sentence-Transformers if `SIMILARITY_BACKEND` is `auto` or `sentence-transformers` and the extra is installed; else TF-IDF
2. Index: FAISS `IndexFlatIP` if `faiss` imports; else numpy cosine

Public API stays in `ml/similarity/engine.py`. Tests set `SIMILARITY_BACKEND=tfidf`.

## Persistence

`VectorStore` may write embeddings during seed. Analyze-time scoring rebuilds the in-memory index with `persist=False`.

## Tests

Cover weight redistribution and paraphrase retrieval in `ml/tests/`.
