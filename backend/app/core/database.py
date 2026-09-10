from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")
is_memory = ":memory:" in settings.database_url
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs: dict = {"connect_args": connect_args, "pool_pre_ping": True}
if is_memory:
    engine_kwargs["poolclass"] = StaticPool
engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import (  # noqa: F401
        audit_log,
        behavior_profile,
        fraud_cluster,
        prediction,
        product,
        review,
        review_embedding,
        review_similarity,
        reviewer,
        user,
    )

    Base.metadata.create_all(bind=engine)
