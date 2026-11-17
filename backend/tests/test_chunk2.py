from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient
from scripts._seed_impl import seed_demo_data

from app.core.database import SessionLocal, init_db
from app.main import app
from app.services.analytics_service import AnalyticsService

client = TestClient(app)


def test_chronological_split_never_places_cutoff_ties_in_reference_data() -> None:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    reviews = [
        SimpleNamespace(id=index, review_timestamp=start + timedelta(days=day))
        for index, day in enumerate((0, 1, 2, 2, 2, 3), start=1)
    ]

    training, test = AnalyticsService._chronological_split(reviews)

    assert {review.id for review in training} == {1, 2}
    assert {review.id for review in test} == {3, 4, 5, 6}
    assert max(review.review_timestamp for review in training) < min(
        review.review_timestamp for review in test
    )


def _seed_and_login() -> dict[str, str]:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_campaign_detection_includes_connected_entities_and_signals() -> None:
    headers = _seed_and_login()
    response = client.get("/api/v1/campaigns", headers=headers)
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == len(payload["campaigns"])
    assert payload["data_source"] == "demo/sample"
    assert payload["campaigns"]
    campaign = payload["campaigns"][0]
    assert campaign["risk_score"] > 0
    assert campaign["reviewer_count"] >= 2
    assert campaign["connected_entities"]["reviewers"]
    assert campaign["connected_entities"]["products"]
    assert campaign["connected_entities"]["reviews"]
    assert campaign["temporal_evidence"]["synchronized_pairs"] > 0 or campaign[
        "temporal_evidence"
    ]["risk_score"] > 0
    assert campaign["similarity_evidence"]["pair_count"] > 0
    assert campaign["graph_evidence"]["edge_count"] > 0


def test_model_metrics_only_evaluate_chronological_holdout() -> None:
    headers = _seed_and_login()
    response = client.get("/api/v1/analytics/model", headers=headers)
    assert response.status_code == 200
    metrics = response.json()

    assert metrics["training_reviews"] + metrics["test_reviews"] == metrics["total_reviews"]
    assert metrics["test_reviews"] > 0
    assert metrics["total_predictions"] == metrics["test_reviews"]
    assert metrics["labeled_reviews"] <= metrics["test_reviews"]
    assert metrics["data_source"] == "demo/sample"
    assert "Chronological holdout" in metrics["evaluation_protocol"]
    assert "excluded from feature context" in metrics["evaluation_note"]
    matrix = metrics["confusion_matrix"]
    if metrics["labeled_reviews"]:
        assert sum(matrix.values()) == metrics["labeled_reviews"]
        assert 0 <= metrics["accuracy"] <= 1
