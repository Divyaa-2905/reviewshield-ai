#!/usr/bin/env python3
"""Evaluate model performance on demo data."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal, init_db
from app.models.prediction import Prediction
from app.models.review import Review


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        predictions = db.query(Prediction).all()
        reviews = {r.id: r for r in db.query(Review).all()}

        if not predictions:
            print("No predictions found. Run seed_demo_data.py first.")
            return

        correct = 0
        total = 0
        distribution = {"Genuine": 0, "Suspicious": 0, "Potentially Fake": 0}

        for pred in predictions:
            distribution[pred.classification] = distribution.get(pred.classification, 0) + 1
            review = reviews.get(pred.review_id)
            if review and review.review_label:
                total += 1
                expected = "Genuine" if review.review_label == "genuine" else "Potentially Fake"
                if pred.classification == expected or (
                    pred.classification == "Suspicious" and review.review_label == "fake"
                ):
                    correct += 1

        metrics = {
            "total_predictions": len(predictions),
            "classification_distribution": distribution,
            "labeled_reviews": total,
            "accuracy_on_labeled": correct / total if total else 0,
            "avg_fraud_probability": sum(p.fraud_probability for p in predictions) / len(predictions),
            "note": "DEMO DATA evaluation only. Not real-world metrics.",
        }

        output = ROOT / "data" / "processed" / "evaluation_metrics.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(metrics, f, indent=2)

        print(json.dumps(metrics, indent=2))
        print(f"\nMetrics saved to {output}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
