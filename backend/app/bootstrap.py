import sys
from pathlib import Path

# Add project root so `ml` package is importable when running from backend/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def bootstrap_demo_users() -> None:
    from scripts._seed_impl import seed_users

    from app.core.database import SessionLocal, init_db

    init_db()
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap_demo_users()
    print("Default demo users are ready.")
