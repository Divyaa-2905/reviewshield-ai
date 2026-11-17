import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal, init_db
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_login_and_dashboard() -> None:
    from scripts._seed_impl import seed_demo_data

    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dashboard = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_reviews"] > 0


def test_bootstrap_repairs_default_admin_password_hash() -> None:
    from app.models.user import User, UserRole

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is None:
            admin = User(
                username="admin",
                email="admin@reviewshield.demo",
                hashed_password="invalid-stale-hash",
                role=UserRole.ADMIN,
            )
            db.add(admin)
        else:
            admin.hashed_password = "invalid-stale-hash"
        db.commit()
    finally:
        db.close()

    from app.bootstrap import bootstrap_demo_users

    bootstrap_demo_users()
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_verify_password_rejects_malformed_hash() -> None:
    from app.core.security import verify_password

    assert not verify_password("admin123", "invalid-stale-hash")


def test_analyze_review_requires_auth() -> None:
    response = client.post(
        "/api/v1/predictions/analyze",
        json={
            "review_text": "Amazing product! Best ever!",
            "rating": 5,
            "review_timestamp": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 401


def test_analyze_review_does_not_insert_rows() -> None:
    from scripts._seed_impl import seed_demo_data

    from app.models.prediction import Prediction
    from app.models.review import Review

    db = SessionLocal()
    try:
        seed_demo_data(db)
        review_count = db.query(Review).count()
        prediction_count = db.query(Prediction).count()
    finally:
        db.close()


def test_csv_batch_validate_analyze_and_export_are_read_only() -> None:
    import csv
    import io

    from scripts._seed_impl import seed_demo_data

    from app.models.prediction import Prediction
    from app.models.review import Review

    db = SessionLocal()
    try:
        seed_demo_data(db)
        review_count = db.query(Review).count()
        prediction_count = db.query(Prediction).count()
    finally:
        db.close()

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst", "password": "analyst123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    validation = client.post(
        "/api/v1/predictions/batch/validate",
        headers=headers,
        files={
            "file": (
                "reviews.csv",
                "review_text,rating,reviewer_id\n"
                '"Great product, works well",5,\n'
                '"Missing rating",not-a-number,\n',
                "text/csv",
            )
        },
    )
    assert validation.status_code == 200
    validated = validation.json()
    assert validated["total_rows"] == 2
    assert validated["valid_rows"] == 1
    assert validated["invalid_rows"] == 1
    assert validated["rows"][1]["errors"]

    analysis = client.post(
        "/api/v1/predictions/batch/analyze",
        headers=headers,
        json={"rows": [validated["rows"][0]]},
    )
    assert analysis.status_code == 200
    results = analysis.json()
    assert results["total_rows"] == 1
    assert len(results["results"]) == 1
    assert 0 <= results["results"][0]["fraud_probability"] <= 1

    exported = client.post(
        "/api/v1/predictions/batch/export",
        headers=headers,
        json={"results": results["results"]},
    )
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    exported_rows = list(csv.DictReader(io.StringIO(exported.text)))
    assert len(exported_rows) == 1
    assert exported_rows[0]["review_text"] == "Great product, works well"

    formula_result = dict(results["results"][0], review_text="=1+1")
    safe_export = client.post(
        "/api/v1/predictions/batch/export",
        headers=headers,
        json={"results": [formula_result]},
    )
    assert safe_export.status_code == 200
    safe_rows = list(csv.DictReader(io.StringIO(safe_export.text)))
    assert safe_rows[0]["review_text"] == "'=1+1"

    db = SessionLocal()
    try:
        assert db.query(Review).count() == review_count
        assert db.query(Prediction).count() == prediction_count
    finally:
        db.close()

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst", "password": "analyst123"},
    )
    token = login.json()["access_token"]
    response = client.post(
        "/api/v1/predictions/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "review_text": "Amazing product! Best ever! Highly recommend!!!",
            "rating": 5,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["persisted"] is False
    assert payload["review_id"] is None
    assert "weights_used" in payload
    assert "behavior" in payload["missing_modalities"]

    db = SessionLocal()
    try:
        assert db.query(Review).count() == review_count
        assert db.query(Prediction).count() == prediction_count
    finally:
        db.close()
