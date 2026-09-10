import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("SIMILARITY_BACKEND", "tfidf")

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.fusion.model import (
    classify_probability,
    fuse_modalities,
    resolve_modality_weights,
)
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.similarity.engine import (
    build_similarity_index,
    find_similar_reviews,
    reset_similarity_state,
    similarity_runtime,
)
from ml.temporal.analyzer import analyze_temporal_patterns


def test_nlp_features() -> None:
    features = analyze_text("Amazing product! Best ever! Highly recommend!!!")
    assert features["word_count"] > 0
    assert text_risk_score(features) > 0


def test_behavior_profiling() -> None:
    now = datetime.now(UTC)
    reviews = [
        {"rating": 5, "product_id": "p1", "review_timestamp": now - timedelta(hours=i)}
        for i in range(10)
    ]
    result = analyze_reviewer_behavior(reviews)
    assert "behavior_risk" in result
    assert result["behavior_risk"] > 0


def test_temporal_analysis() -> None:
    now = datetime.now(UTC)
    reviews = [
        {"review_timestamp": now - timedelta(minutes=i * 10)} for i in range(6)
    ]
    result = analyze_temporal_patterns(reviews)
    assert result["temporal_risk"] >= 0


def test_fusion_model() -> None:
    result = fuse_modalities(0.8, 0.7, 0.6, 0.5, 0.4)
    assert 0 <= result.fraud_probability <= 1
    assert result.classification in {"Genuine", "Suspicious", "Potentially Fake"}
    assert abs(sum(result.weights_used.values()) - 1.0) < 1e-9


def test_fusion_redistributes_weights_without_history() -> None:
    with_history = fuse_modalities(0.9, 0.0, 0.0, 0.8, 0.7, history_available=True)
    without_history = fuse_modalities(0.9, 0.0, 0.0, 0.8, 0.7, history_available=False)
    weights = resolve_modality_weights(history_available=False)
    assert weights["behavior"] == 0.0
    assert weights["temporal"] == 0.0
    assert weights["text"] > 0.2
    assert without_history.fraud_probability > with_history.fraud_probability
    assert "behavior" in without_history.missing_modalities


def test_classify_probability() -> None:
    assert classify_probability(0.2) == "Genuine"
    assert classify_probability(0.5) == "Suspicious"
    assert classify_probability(0.9) == "Potentially Fake"


def test_similarity_index_finds_paraphrases() -> None:
    reset_similarity_state()
    reviews = [
        {"review_id": "r1", "review_text": "Excellent product and very fast delivery for this item."},
        {"review_id": "r2", "review_text": "Excellent product and very fast delivery for this package."},
        {"review_id": "r3", "review_text": "The lamp hue is slightly warm for late reading sessions."},
    ]
    build_similarity_index(reviews)
    runtime = similarity_runtime()
    assert runtime["embedding_backend"] == "tfidf"
    matches = find_similar_reviews("r1", reviews[0]["review_text"], threshold=0.1)
    assert matches
    assert matches[0]["review_id"] == "r2"
    assert matches[0]["similarity_score"] > 0.4
