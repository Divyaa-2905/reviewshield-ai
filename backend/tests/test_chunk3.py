from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.database import SessionLocal, init_db
from app.main import app

client = TestClient(app)


def _token(username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _seed() -> None:
    from scripts._seed_impl import seed_demo_data

    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


def test_product_trust_score_and_pdf_report() -> None:
    from app.models.product import Product

    init_db()
    _seed()
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.product_id == "prod-001").one()
        product_id = product.product_id
    finally:
        db.close()

    headers = _token("viewer", "viewer123")
    response = client.get(f"/api/v1/products/{product_id}/trust", headers=headers)
    assert response.status_code == 200
    analysis = response.json()
    assert analysis["review_count"] > 0
    assert analysis["predicted_review_count"] > 0
    assert analysis["risk_score"] == round(analysis["risk_score"], 1)
    assert 0 <= analysis["trust_score"] <= 100
    assert sum(analysis["rating_distribution"].values()) == analysis["review_count"]
    assert sum(indicator["weight"] for indicator in analysis["indicators"]) == 100
    assert "not proof" in analysis["score_explanation"]

    report = client.get(f"/api/v1/products/{product_id}/report.pdf", headers=headers)
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/pdf"
    assert report.content.startswith(b"%PDF-")


def test_product_trust_discloses_missing_prediction_coverage() -> None:
    from app.models.product import Product
    from app.models.review import Review
    from app.models.reviewer import Reviewer

    init_db()
    _seed()
    db = SessionLocal()
    product_id = "trust-unscored-product"
    try:
        reviewer = Reviewer(reviewer_id="trust-unscored-reviewer")
        product = Product(
            product_id=product_id,
            name="Unscored product",
            category="test",
            is_demo=False,
        )
        db.add_all([reviewer, product])
        db.flush()
        db.add(
            Review(
                review_id="trust-unscored-review",
                reviewer_id=reviewer.id,
                product_id=product.id,
                rating=5,
                review_text="A sample review without a stored prediction.",
                review_timestamp=datetime.now(UTC),
                is_demo=False,
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.get(
        f"/api/v1/products/{product_id}/trust",
        headers=_token("viewer", "viewer123"),
    )
    assert response.status_code == 200
    analysis = response.json()
    assert analysis["prediction_coverage"] == 0
    assert analysis["suspicious_percentage"] is None
    suspicious_indicator = next(
        indicator for indicator in analysis["indicators"] if indicator["key"] == "suspicious_reviews"
    )
    assert suspicious_indicator["weight"] == 0
    assert "unavailable" in suspicious_indicator["explanation"]
    assert sum(indicator["weight"] for indicator in analysis["indicators"]) == 100


def test_analyst_feedback_upsert_filter_export_and_rbac() -> None:
    from app.models.prediction import Prediction
    from app.models.prediction_feedback import PredictionFeedback

    init_db()
    _seed()
    db = SessionLocal()
    try:
        prediction_id = db.query(Prediction.id).order_by(Prediction.id).first()[0]
    finally:
        db.close()

    analyst_headers = _token("analyst", "analyst123")
    viewer_headers = _token("viewer", "viewer123")
    base = f"/api/v1/predictions/{prediction_id}/feedback"

    denied = client.put(
        base,
        headers=viewer_headers,
        json={"decision": "correct"},
    )
    assert denied.status_code == 403

    created = client.put(
        base,
        headers=analyst_headers,
        json={"decision": "correct", "comment": "Reviewed against source evidence."},
    )
    assert created.status_code == 200
    created_data = created.json()
    assert created_data["decision"] == "correct"
    assert created_data["analyst_username"] == "analyst"
    assert created_data["updated_at"] >= created_data["created_at"]

    updated = client.put(
        base,
        headers=analyst_headers,
        json={"decision": "needs_correction", "comment": " =1+1"},
    )
    assert updated.status_code == 200
    assert updated.json()["decision"] == "needs_correction"
    assert updated.json()["created_at"] == created_data["created_at"]
    assert updated.json()["updated_at"] >= created_data["updated_at"]

    listing = client.get(
        "/api/v1/feedback?decision=needs_correction",
        headers=analyst_headers,
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["prediction_id"] == prediction_id

    exported = client.get(
        "/api/v1/feedback/export?decision=needs_correction",
        headers=analyst_headers,
    )
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    assert "' =1+1" in exported.text

    viewer_list = client.get("/api/v1/feedback", headers=viewer_headers)
    assert viewer_list.status_code == 403

    db = SessionLocal()
    try:
        assert db.query(PredictionFeedback).filter_by(prediction_id=prediction_id).count() == 1
    finally:
        db.close()
