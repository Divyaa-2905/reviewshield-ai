# ML Pipeline

## Modules

| Module | Path | Purpose |
|--------|------|---------|
| NLP | `ml/nlp/` | Linguistic feature extraction |
| Behavior | `ml/behavior/` | Reviewer profiling |
| Temporal | `ml/temporal/` | Burst and sync detection |
| Similarity | `ml/similarity/` | TF-IDF cosine similarity |
| Graph | `ml/graph/` | NetworkX analysis |
| Fusion | `ml/fusion/` | Weighted risk combination |
| Explainability | `ml/explainability/` | Human-readable evidence |

## Inference

`MLService.analyze_review()` orchestrates all modalities and stores predictions.
