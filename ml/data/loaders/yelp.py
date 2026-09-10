from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from ml.data.loaders.dataset_loader import REQUIRED_COLUMNS

YELP_COLUMN_MAP = {
    "user_id": "reviewer_id",
    "userid": "reviewer_id",
    "reviewer_id": "reviewer_id",
    "business_id": "product_id",
    "businessid": "product_id",
    "product_id": "product_id",
    "stars": "rating",
    "rating": "rating",
    "text": "review_text",
    "review_text": "review_text",
    "review": "review_text",
    "date": "review_timestamp",
    "review_timestamp": "review_timestamp",
    "review_id": "review_id",
    "reviewid": "review_id",
    "label": "review_label",
    "review_label": "review_label",
    "fake": "review_label",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for column in df.columns:
        key = str(column).strip().lower().replace(" ", "_")
        if key in YELP_COLUMN_MAP:
            renamed[column] = YELP_COLUMN_MAP[key]
    return df.rename(columns=renamed)


def normalize_yelp_reviews(df: pd.DataFrame) -> pd.DataFrame:
    frame = _normalize_columns(df.copy())
    if "review_id" not in frame.columns:
        frame["review_id"] = [f"yelp-{i+1:06d}" for i in range(len(frame))]
    if "review_timestamp" in frame.columns:
        parsed = pd.to_datetime(frame["review_timestamp"], errors="coerce", utc=True)
        frame["review_timestamp"] = parsed.map(
            lambda value: value.to_pydatetime() if not pd.isna(value) else datetime.now(UTC)
        )
    if "rating" in frame.columns:
        frame["rating"] = pd.to_numeric(frame["rating"], errors="coerce").clip(1, 5)
    if "review_label" in frame.columns:
        frame["review_label"] = frame["review_label"].map(_normalize_yelp_label)
    keep = [col for col in [*REQUIRED_COLUMNS, "review_label"] if col in frame.columns]
    return frame[keep]


def _normalize_yelp_label(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    if text in {"fake", "spam", "filtered", "deceptive", "y", "1", "true"}:
        return "fake"
    if text in {"genuine", "real", "recommended", "n", "0", "false"}:
        return "genuine"
    return text or None
