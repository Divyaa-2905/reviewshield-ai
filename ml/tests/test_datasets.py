from pathlib import Path

import pandas as pd

from ml.data.loaders.amazon import normalize_amazon_reviews
from ml.data.loaders.dataset_loader import (
    detect_dataset_kind,
    load_dataset,
    validate_dataset,
)
from ml.data.loaders.yelp import normalize_yelp_reviews

ROOT = Path(__file__).resolve().parents[2]


def test_amazon_loader_maps_public_schema() -> None:
    raw = pd.DataFrame(
        [
            {
                "reviewerID": "A1",
                "asin": "B00TEST",
                "overall": 5,
                "reviewText": "Amazing product!",
                "unixReviewTime": 1609459200,
                "label": "CG",
            }
        ]
    )
    assert detect_dataset_kind(raw) == "amazon"
    df = normalize_amazon_reviews(raw)
    assert {
        "review_id",
        "reviewer_id",
        "product_id",
        "rating",
        "review_text",
        "review_timestamp",
    }.issubset(df.columns)
    assert df.iloc[0]["review_label"] == "fake"
    assert df.iloc[0]["rating"] == 5


def test_yelp_loader_maps_public_schema() -> None:
    raw = pd.DataFrame(
        [
            {
                "user_id": "u1",
                "business_id": "b1",
                "stars": 2,
                "text": "Food arrived cold.",
                "date": "2021-03-01",
                "label": "recommended",
            }
        ]
    )
    assert detect_dataset_kind(raw) == "yelp"
    df = normalize_yelp_reviews(raw)
    assert df.iloc[0]["reviewer_id"] == "u1"
    assert df.iloc[0]["review_label"] == "genuine"


def test_sample_amazon_and_yelp_files_validate() -> None:
    amazon = load_dataset(str(ROOT / "data/sample/amazon_reviews.csv"))
    yelp = load_dataset(str(ROOT / "data/sample/yelp_reviews.jsonl"))
    amazon_report = validate_dataset(amazon)
    yelp_report = validate_dataset(yelp)
    assert amazon_report["records"] >= 10
    assert yelp_report["records"] >= 10
    assert not amazon_report["required_missing"]
    assert not yelp_report["required_missing"]
    assert "fake" in amazon_report["label_distribution"]
    assert "genuine" in yelp_report["label_distribution"]
