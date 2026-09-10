from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

POSITIVE_LABELS = {
    "fake",
    "spam",
    "deceptive",
    "computer_generated",
    "cg",
    "1",
    "true",
    "yes",
    "positive",
    "filtered",
    "__label1__",
}
NEGATIVE_LABELS = {
    "genuine",
    "real",
    "organic",
    "human",
    "original",
    "or",
    "og",
    "0",
    "false",
    "no",
    "negative",
    "recommended",
    "__label2__",
}


def to_binary_label(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        if np.isnan(value):
            return None
        return 1 if float(value) >= 0.5 else 0
    text = str(value).strip().lower()
    if not text or text in {"nan", "none", "null", "unknown", "unlabeled"}:
        return None
    if text in POSITIVE_LABELS:
        return 1
    if text in NEGATIVE_LABELS:
        return 0
    if "fake" in text or "spam" in text or "deceptive" in text:
        return 1
    if "genuine" in text or "real" in text:
        return 0
    return None


def classification_to_score(classification: str, probability: float) -> float:
    if classification == "Potentially Fake":
        return max(probability, 0.7)
    if classification == "Suspicious":
        return max(min(probability, 0.69), 0.4)
    return min(probability, 0.39)


def evaluate_binary_scores(
    y_true: list[int],
    y_score: list[float],
    threshold: float = 0.5,
) -> dict:
    if not y_true or len(y_true) != len(y_score):
        return {
            "labeled_reviews": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "accuracy": 0.0,
            "roc_auc": None,
            "pr_auc": None,
            "threshold": threshold,
        }

    y_true_arr = np.asarray(y_true, dtype=int)
    y_score_arr = np.clip(np.asarray(y_score, dtype=float), 0.0, 1.0)
    y_pred = (y_score_arr >= threshold).astype(int)

    metrics: dict = {
        "labeled_reviews": len(y_true_arr),
        "positive_labels": int(y_true_arr.sum()),
        "negative_labels": int((1 - y_true_arr).sum()),
        "threshold": threshold,
        "precision": float(precision_score(y_true_arr, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true_arr, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true_arr, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true_arr, y_pred)),
        "roc_auc": None,
        "pr_auc": None,
    }

    if len(np.unique(y_true_arr)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true_arr, y_score_arr))
        metrics["pr_auc"] = float(average_precision_score(y_true_arr, y_score_arr))
        fpr, tpr, _ = roc_curve(y_true_arr, y_score_arr)
        precisions, recalls, _ = precision_recall_curve(y_true_arr, y_score_arr)
        metrics["roc_curve"] = {
            "fpr": [float(v) for v in fpr],
            "tpr": [float(v) for v in tpr],
        }
        metrics["pr_curve"] = {
            "precision": [float(v) for v in precisions],
            "recall": [float(v) for v in recalls],
        }

    return metrics
