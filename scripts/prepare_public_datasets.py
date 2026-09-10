#!/usr/bin/env python3
"""Normalize Amazon/Yelp review files into the canonical ReviewShield schema."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.data.loaders.dataset_loader import load_dataset, save_report, validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Amazon or Yelp reviews")
    parser.add_argument("dataset", help="Input CSV/JSON/JSONL/Parquet path")
    parser.add_argument("--kind", choices=["auto", "amazon", "yelp", "canonical"], default="auto")
    parser.add_argument("--output", default="data/processed/prepared_reviews.parquet")
    args = parser.parse_args()

    kind = None if args.kind == "auto" else args.kind
    df = load_dataset(args.dataset, kind=kind)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.output.endswith(".csv"):
        df.to_csv(args.output, index=False)
    else:
        df.to_parquet(args.output, index=False)

    report = validate_dataset(df)
    report["source_kind"] = kind or "auto"
    save_report(report, "data/processed/prepare_report.json")
    print(f"Prepared {len(df)} records -> {args.output}")
    if report.get("required_missing"):
        print(f"Missing required columns: {report['required_missing']}")


if __name__ == "__main__":
    main()
