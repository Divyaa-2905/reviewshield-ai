# ML Pipeline

## Modules

| Module | Path | Purpose |
|--------|------|---------|
| NLP | `ml/nlp/` | Linguistic feature extraction |
| Behavior | `ml/behavior/` | Reviewer profiling |
| Temporal | `ml/temporal/` | Burst and sync detection |
| Similarity | `ml/similarity/` | Sentence-Transformers or TF-IDF + FAISS/numpy |
| Graph | `ml/graph/` | NetworkX analysis |
| Fusion | `ml/fusion/` | Weighted risk combination with missing-history reweighting |
| Explainability | `ml/explainability/` | Human-readable evidence |
| Evaluation | `ml/evaluation/` | Precision, recall, F1, ROC-AUC, PR-AUC |

## Inference

`MLService.analyze_review()` orchestrates all modalities. `POST /predictions/analyze` returns the score without inserting database rows. Use `analyze_and_store()` or seed jobs to persist predictions.

## Similarity

Set `SIMILARITY_BACKEND=auto` (default), `sentence-transformers`, or `tfidf`. FAISS is used when installed; otherwise numpy cosine. Docker Postgres uses the `pgvector/pgvector` image for optional vector persistence.
