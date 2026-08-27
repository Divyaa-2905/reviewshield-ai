import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.fusion.model import classify_probability, fuse_modalities
from ml.nlp.linguistic_features import analyze_text, text_risk_score
from ml.temporal.analyzer import analyze_temporal_patterns
from datetime import UTC, datetime, timedelta


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


def test_classify_probability() -> None:
    assert classify_probability(0.2) == "Genuine"
    assert classify_probability(0.5) == "Suspicious"
    assert classify_probability(0.9) == "Potentially Fake"
