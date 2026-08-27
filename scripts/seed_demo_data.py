#!/usr/bin/env python3
"""Seed deterministic demo data for ReviewShield AI."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal, init_db  # noqa: E402

# Import after path setup
from scripts._seed_impl import seed_demo_data  # noqa: E402


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        print("Demo data seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
