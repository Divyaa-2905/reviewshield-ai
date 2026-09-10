"""Evaluate model performance with precision, recall, F1, and AUC."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from ml.evaluation.metrics import evaluate_binary_scores, to_binary_label


def evaluate_predictions(predictions: list[dict], reviews: dict[object, dict]) -> dict:
    y_true: list[int] = []
    y_score: list[float] = []
    distribution = {"Genuine": 0, "Suspicious": 0, "Potentially Fake": 0}

    for pred in predictions:
        classification = pred.get("classification") or "Genuine"
        distribution[classification] = distribution.get(classification, 0) + 1
        review = reviews.get(pred.get("review_pk")) or reviews.get(pred.get("review_id"))
        if not review:
            continue
        label = to_binary_label(review.get("review_label"))
        if label is None:
            continue
        y_true.append(label)
        y_score.append(float(pred.get("fraud_probability") or 0.0))

    metrics = evaluate_binary_scores(y_true, y_score, threshold=0.4)
    metrics.update(
        {
            "total_predictions": len(predictions),
            "classification_distribution": distribution,
            "avg_fraud_probability": (
                sum(float(p.get("fraud_probability") or 0.0) for p in predictions) / len(predictions)
                if predictions
                else 0.0
            ),
            "note": "Binary fake-vs-genuine metrics. Suspicious scores stay continuous for AUC.",
        }
    )
    return metrics


def evaluate_from_database() -> dict:
    from app.core.database import SessionLocal, init_db
    from app.models.prediction import Prediction
    from app.models.review import Review

    init_db()
    db = SessionLocal()
    try:
        predictions = db.query(Prediction).all()
        reviews = {
            review.id: {
                "review_id": review.review_id,
                "review_label": review.review_label,
            }
            for review in db.query(Review).all()
        }
        payload = [
            {
                "review_pk": pred.review_id,
                "classification": pred.classification,
                "fraud_probability": pred.fraud_probability,
            }
            for pred in predictions
        ]
        return evaluate_predictions(payload, reviews)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ReviewShield predictions")
    parser.add_argument("--from-db", action="store_true", help="Read labeled predictions from the database")
    parser.add_argument("--output", default="data/processed/evaluation_metrics.json")
    args = parser.parse_args()

    if not args.from_db:
        print("No input specified. Use --from-db after seeding, or call evaluate_predictions() from a dataset job.")
        metrics = {"error": "missing_input"}
    else:
        metrics = evaluate_from_database()
        if metrics.get("total_predictions") == 0:
            print("No predictions found. Run seed_demo_data.py or an Amazon/Yelp eval job first.")

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k not in {"roc_curve", "pr_curve"}}, indent=2))
    print(f"\nMetrics saved to {output}")


if __name__ == "__main__":
    main()
