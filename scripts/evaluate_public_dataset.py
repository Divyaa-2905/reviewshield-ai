#!/usr/bin/env python3
"""Run precision/recall/AUC evaluation on a labeled Amazon or Yelp file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from ml.data.loaders.dataset_loader import load_dataset
from ml.evaluation.evaluate import evaluate_predictions
from ml.evaluation.metrics import to_binary_label
from ml.fusion.model import fuse_modalities
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.similarity.engine import build_similarity_index, pairwise_similarity_risk, reset_similarity_state


def score_dataframe(df) -> tuple[list[dict], dict]:
    reviews = []
    for row in df.to_dict(orient="records"):
        reviews.append(
            {
                "review_id": str(row.get("review_id")),
                "reviewer_id": str(row.get("reviewer_id")),
                "product_id": str(row.get("product_id")),
                "rating": float(row.get("rating") or 3),
                "review_text": str(row.get("review_text") or ""),
                "review_timestamp": row.get("review_timestamp"),
                "review_label": row.get("review_label"),
            }
        )
    reset_similarity_state()
    build_similarity_index(reviews)
    predictions = []
    labeled = {}
    for review in reviews:
        text_risk = text_risk_score(analyze_text(review["review_text"]))
        similarity_risk, _ = pairwise_similarity_risk(review["review_id"], review["review_text"])
        history_available = sum(1 for item in reviews if item["reviewer_id"] == review["reviewer_id"]) > 1
        result = fuse_modalities(
            text_risk=text_risk,
            behavior_risk=0.0,
            temporal_risk=0.0,
            similarity_risk=similarity_risk,
            graph_risk=0.0,
            history_available=history_available,
        )
        predictions.append(
            {
                "review_id": review["review_id"],
                "classification": result.classification,
                "fraud_probability": result.fraud_probability,
            }
        )
        labeled[review["review_id"]] = {"review_label": review["review_label"]}
    return predictions, labeled


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate labeled Amazon/Yelp reviews")
    parser.add_argument("dataset", nargs="?", default="data/sample/amazon_reviews.csv")
    parser.add_argument("--kind", default="auto")
    parser.add_argument("--output", default="data/processed/evaluation_metrics.json")
    args = parser.parse_args()

    kind = None if args.kind == "auto" else args.kind
    df = load_dataset(args.dataset, kind=kind)
    labeled_count = sum(1 for value in df.get("review_label", []) if to_binary_label(value) is not None)
    if labeled_count == 0:
        raise SystemExit("Dataset has no usable review_label values for precision/recall/AUC.")

    predictions, reviews = score_dataframe(df)
    metrics = evaluate_predictions(predictions, reviews)
    metrics["dataset"] = args.dataset
    metrics["records"] = len(df)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({k: v for k, v in metrics.items() if k not in {"roc_curve", "pr_curve"}}, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k not in {"roc_curve", "pr_curve"}}, indent=2))


if __name__ == "__main__":
    main()
