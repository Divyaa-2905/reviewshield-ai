#!/usr/bin/env python3
"""Generate ML features from prepared dataset."""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.nlp.linguistic_features import analyze_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate features from dataset")
    parser.add_argument("dataset", default="data/processed/prepared_reviews.parquet")
    parser.add_argument("--output", default="data/processed/features.json")
    args = parser.parse_args()

    df = pd.read_parquet(args.dataset)
    features = []
    for _, row in df.iterrows():
        text_features = analyze_text(str(row.get("review_text", "")))
        features.append({"review_id": row["review_id"], **text_features})

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(features, f, indent=2)
    print(f"Generated features for {len(features)} reviews -> {args.output}")


if __name__ == "__main__":
    main()
