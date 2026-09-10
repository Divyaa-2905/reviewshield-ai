from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from ml.data.loaders.dataset_loader import REQUIRED_COLUMNS

AMAZON_COLUMN_MAP = {
    "reviewerid": "reviewer_id",
    "reviewer_id": "reviewer_id",
    "userid": "reviewer_id",
    "user_id": "reviewer_id",
    "asin": "product_id",
    "productid": "product_id",
    "product_id": "product_id",
    "overall": "rating",
    "rating": "rating",
    "stars": "rating",
    "reviewtext": "review_text",
    "review_text": "review_text",
    "text": "review_text",
    "review": "review_text",
    "unixreviewtime": "review_timestamp",
    "unix_review_time": "review_timestamp",
    "reviewtime": "review_timestamp",
    "review_timestamp": "review_timestamp",
    "timestamp": "review_timestamp",
    "reviewid": "review_id",
    "review_id": "review_id",
    "label": "review_label",
    "review_label": "review_label",
    "fake": "review_label",
    "verified": "verified_purchase",
    "verified_purchase": "verified_purchase",
    "summary": "summary",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for column in df.columns:
        key = str(column).strip().lower().replace(" ", "_")
        if key in AMAZON_COLUMN_MAP:
            renamed[column] = AMAZON_COLUMN_MAP[key]
    return df.rename(columns=renamed)


def _parse_timestamp(value: object) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        unix = float(value)
        if unix > 1e12:
            unix /= 1000
        return datetime.fromtimestamp(unix, tz=UTC)
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def normalize_amazon_reviews(df: pd.DataFrame) -> pd.DataFrame:
    frame = _normalize_columns(df.copy())
    if "review_id" not in frame.columns:
        frame["review_id"] = [f"amz-{i+1:06d}" for i in range(len(frame))]
    if "review_timestamp" in frame.columns:
        frame["review_timestamp"] = frame["review_timestamp"].map(_parse_timestamp)
    if "rating" in frame.columns:
        frame["rating"] = pd.to_numeric(frame["rating"], errors="coerce").clip(1, 5)
    if "review_label" in frame.columns:
        frame["review_label"] = frame["review_label"].map(_normalize_amazon_label)
    keep = [col for col in [*REQUIRED_COLUMNS, "review_label", "verified_purchase", "summary"] if col in frame.columns]
    return frame[keep]


def _normalize_amazon_label(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    # CG/OR dumps: computer-generated vs original. __label1__ is commonly fake.
    if text in {"__label1__", "fake", "spam", "deceptive", "cg", "computer_generated", "1"}:
        return "fake"
    if text in {"__label2__", "genuine", "real", "original", "or", "og", "0"}:
        return "genuine"
    return text or None
