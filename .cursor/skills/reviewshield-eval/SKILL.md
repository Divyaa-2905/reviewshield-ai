---
name: reviewshield-eval
description: Ingest Amazon or Yelp review datasets and compute precision, recall, F1, ROC-AUC, and PR-AUC. Use when adding loaders, evaluation scripts, labeled fixtures, or analytics metrics.
---

# ReviewShield evaluation

## Canonical schema

`review_id`, `reviewer_id`, `product_id`, `rating`, `review_text`, `review_timestamp`, optional `review_label`.

## Loaders

- Amazon: `reviewerID`, `asin`, `overall`, `reviewText`, `unixReviewTime`, `label` (`CG`/`OR` or `__label1__`/`__label2__`)
- Yelp: `user_id`, `business_id`, `stars`, `text`, `date`, `label` (`fake`/`filtered` vs `genuine`/`recommended`)

Use `load_dataset(path, kind=...)`. Fixtures: `data/sample/amazon_reviews.csv`, `data/sample/yelp_reviews.jsonl`.

## Metrics

`ml/evaluation/metrics.py` computes binary fake-vs-genuine precision, recall, F1, accuracy, ROC-AUC, PR-AUC from `fraud_probability`. Unlabeled rows are skipped. Missing class variety => AUC is `null`, not a made-up number.

```bash
python scripts/evaluate_public_dataset.py data/sample/amazon_reviews.csv
python scripts/evaluate_public_dataset.py data/sample/yelp_reviews.jsonl --kind yelp
```
