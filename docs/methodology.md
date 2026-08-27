# Methodology

ReviewShield AI uses evidence-based multi-modal risk assessment.

## Modalities

1. **NLP**: Lexical diversity, promotional language, sentiment proxy
2. **Behavior**: Review volume, rating patterns, product diversity
3. **Temporal**: Burst detection, posting intervals
4. **Similarity**: TF-IDF cosine similarity for duplicates/paraphrases
5. **Graph**: NetworkX reviewer-product network analysis

## Fusion

Weighted combination of modality risk scores with configurable thresholds.

## Classification

- Genuine: probability < 0.4
- Suspicious: 0.4 - 0.7
- Potentially Fake: > 0.7
