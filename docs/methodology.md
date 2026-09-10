# Methodology

ReviewShield AI uses evidence-based multi-modal risk assessment.

## Modalities

1. **NLP**: Lexical diversity, promotional language, sentiment proxy
2. **Behavior**: Review volume, rating patterns, product diversity
3. **Temporal**: Burst detection, posting intervals
4. **Similarity**: Sentence-Transformers (fallback TF-IDF) + FAISS/numpy nearest neighbors
5. **Graph**: NetworkX reviewer-product network analysis

## Fusion

Weighted combination of modality risk scores. If reviewer history is missing, behavior and temporal weights are set to 0 and redistributed to text, similarity, and graph.

## Evaluation

Labeled Amazon/Yelp (or demo) reviews are scored with precision, recall, F1, ROC-AUC, and PR-AUC on the binary fake-vs-genuine task using `fraud_probability`.

## Classification

- Genuine: probability < 0.4
- Suspicious: 0.4 - 0.7
- Potentially Fake: > 0.7
