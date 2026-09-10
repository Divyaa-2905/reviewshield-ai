# Data Pipeline

## Supported Formats

CSV, JSON, Parquet

## Scripts

```bash
python scripts/validate_dataset.py data/sample/amazon_reviews.csv
python scripts/prepare_public_datasets.py data/sample/amazon_reviews.csv --kind amazon
python scripts/evaluate_public_dataset.py data/sample/yelp_reviews.jsonl --kind yelp
python scripts/seed_demo_data.py
```

Amazon and Yelp column mappings live in `ml/data/loaders/`. Fixtures in `data/sample/` are labeled for precision/recall/AUC tests. Large raw dumps belong in `data/raw/` (gitignored).

## Canonical Schema

- review_id, reviewer_id, product_id, rating, review_text, review_timestamp
- Optional: review_label, verified_purchase, account_created_at

Missing fields are marked unavailable, never invented.
