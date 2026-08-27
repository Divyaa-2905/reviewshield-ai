#!/usr/bin/env python3
"""Validate a review dataset and output a quality report."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.data.loaders.dataset_loader import load_dataset, save_report, validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate review dataset")
    parser.add_argument("dataset", help="Path to CSV, JSON, or Parquet file")
    parser.add_argument("--output", default="data/processed/quality_report.json")
    args = parser.parse_args()

    df = load_dataset(args.dataset)
    report = validate_dataset(df)
    save_report(report, args.output)
    print(f"Validation complete. Report saved to {args.output}")
    print(f"Records: {report['records']}, Duplicates: {report.get('duplicate_records', 0)}")


if __name__ == "__main__":
    main()
