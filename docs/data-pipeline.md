# Data Pipeline

## Supported Formats

CSV, JSON, Parquet

## Scripts

```bash
python scripts/validate_dataset.py data/sample/reviews.csv
python scripts/prepare_dataset.py data/sample/reviews.csv
python scripts/generate_features.py data/processed/prepared_reviews.parquet
python scripts/seed_demo_data.py
```

## Canonical Schema

- review_id, reviewer_id, product_id, rating, review_text, review_timestamp
- Optional: review_label, verified_purchase, account_created_at

Missing fields are marked unavailable, never invented.
