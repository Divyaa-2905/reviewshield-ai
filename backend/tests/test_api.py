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
