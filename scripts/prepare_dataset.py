#!/usr/bin/env python3
"""Prepare and normalize a review dataset."""
import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.data.loaders.dataset_loader import load_dataset, save_report, validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare review dataset")
    parser.add_argument("dataset", help="Input dataset path")
    parser.add_argument("--kind", choices=["auto", "amazon", "yelp", "canonical"], default="auto")
    parser.add_argument("--output", default="data/processed/prepared_reviews.parquet")
    args = parser.parse_args()

    kind = None if args.kind == "auto" else args.kind
    df = load_dataset(args.dataset, kind=kind)
    if "review_timestamp" in df.columns:
        df["review_timestamp"] = pd.to_datetime(df["review_timestamp"], errors="coerce")
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").clip(1, 5)
    if "review_text" in df.columns:
        df["review_text"] = df["review_text"].astype(str).str.strip()

    df = df.drop_duplicates(subset=["review_id"], keep="first")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)

    report = validate_dataset(df)
    save_report(report, "data/processed/prepare_report.json")
    print(f"Prepared {len(df)} records -> {args.output}")


if __name__ == "__main__":
    main()
