import os

os.environ.setdefault("SIMILARITY_BACKEND", "tfidf")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
