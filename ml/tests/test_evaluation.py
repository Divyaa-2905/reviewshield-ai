from ml.evaluation.evaluate import evaluate_predictions
from ml.evaluation.metrics import evaluate_binary_scores, to_binary_label


def test_label_normalization() -> None:
    assert to_binary_label("fake") == 1
    assert to_binary_label("genuine") == 0
    assert to_binary_label("CG") == 1
    assert to_binary_label("OR") == 0
    assert to_binary_label("__label1__") == 1
    assert to_binary_label("recommended") is None or to_binary_label("recommended") == 0


def test_precision_recall_auc() -> None:
    y_true = [1, 1, 0, 0, 1, 0]
    y_score = [0.92, 0.81, 0.12, 0.30, 0.77, 0.18]
    metrics = evaluate_binary_scores(y_true, y_score, threshold=0.5)
    assert metrics["precision"] > 0.9
    assert metrics["recall"] > 0.9
    assert metrics["roc_auc"] is not None and metrics["roc_auc"] > 0.9
    assert metrics["pr_auc"] is not None and metrics["pr_auc"] > 0.9


def test_evaluate_predictions_skips_unlabeled() -> None:
    predictions = [
        {"review_pk": 1, "classification": "Potentially Fake", "fraud_probability": 0.9},
        {"review_pk": 2, "classification": "Genuine", "fraud_probability": 0.1},
        {"review_pk": 3, "classification": "Suspicious", "fraud_probability": 0.5},
    ]
    reviews = {
        1: {"review_label": "fake"},
        2: {"review_label": "genuine"},
        3: {"review_label": None},
    }
    metrics = evaluate_predictions(predictions, reviews)
    assert metrics["labeled_reviews"] == 2
    assert metrics["roc_auc"] == 1.0
