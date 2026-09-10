import json
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "review_id",
    "reviewer_id",
    "product_id",
    "rating",
    "review_text",
    "review_timestamp",
]


def load_raw_dataset(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        try:
            return pd.read_json(path, lines=True)
        except ValueError:
            return pd.read_json(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported format: {suffix}")


def detect_dataset_kind(df: pd.DataFrame) -> str:
    columns = {str(col).strip().lower() for col in df.columns}
    if {"asin", "reviewtext"} & columns or "unixreviewtime" in columns or "overall" in columns:
        return "amazon"
    if {"business_id", "stars", "text"} <= columns or {"business_id", "user_id"} <= columns:
        return "yelp"
    return "canonical"


def load_dataset(path: str, kind: str | None = None) -> pd.DataFrame:
    df = load_raw_dataset(path)
    detected = kind or detect_dataset_kind(df)
    if detected == "amazon":
        from ml.data.loaders.amazon import normalize_amazon_reviews

        return normalize_amazon_reviews(df)
    if detected == "yelp":
        from ml.data.loaders.yelp import normalize_yelp_reviews

        return normalize_yelp_reviews(df)
    return df


def validate_dataset(df: pd.DataFrame) -> dict:
    report = {
        "records": len(df),
        "missing_values": {},
        "duplicate_records": 0,
        "columns_present": list(df.columns),
        "required_missing": [],
    }

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            report["required_missing"].append(col)
        else:
            report["missing_values"][col] = int(df[col].isna().sum())

    if "review_id" in df.columns:
        report["duplicate_records"] = int(df["review_id"].duplicated().sum())

    if "reviewer_id" in df.columns:
        report["reviewers"] = int(df["reviewer_id"].nunique())
    if "product_id" in df.columns:
        report["products"] = int(df["product_id"].nunique())

    if "review_timestamp" in df.columns and "review_timestamp" in df.columns:
        ts = pd.to_datetime(df["review_timestamp"], errors="coerce")
        report["timestamp_range"] = {
            "min": str(ts.min()) if not ts.isna().all() else None,
            "max": str(ts.max()) if not ts.isna().all() else None,
        }

    if "review_text" in df.columns:
        lengths = df["review_text"].astype(str).str.len()
        report["review_length_stats"] = {
            "min": int(lengths.min()),
            "max": int(lengths.max()),
            "mean": float(lengths.mean()),
        }

    if "review_label" in df.columns:
        report["label_distribution"] = df["review_label"].value_counts().to_dict()

    return report


def save_report(report: dict, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
