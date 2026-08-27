from datetime import datetime
from statistics import median


def analyze_reviewer_behavior(
    reviews: list[dict],
    account_created_at: datetime | None = None,
) -> dict:
    if not reviews:
        return {"behavior_risk": 0.0, "metrics": {}, "observations": []}

    ratings = [r["rating"] for r in reviews]
    timestamps = sorted(r["review_timestamp"] for r in reviews)
    products = [r["product_id"] for r in reviews]

    total = len(reviews)
    avg_rating = sum(ratings) / total
    variance = sum((r - avg_rating) ** 2 for r in ratings) / total
    five_star_pct = sum(1 for r in ratings if r == 5) / total
    one_star_pct = sum(1 for r in ratings if r == 1) / total
    product_diversity = len(set(products)) / total

    intervals = [
        (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600
        for i in range(1, len(timestamps))
    ]
    median_interval = median(intervals) if intervals else 0.0
    min_interval = min(intervals) if intervals else 0.0

    span_days = max((timestamps[-1] - timestamps[0]).total_seconds() / 86400, 1)
    reviews_per_day = total / span_days

    metrics = {
        "total_reviews": float(total),
        "average_rating": avg_rating,
        "rating_variance": variance,
        "five_star_percentage": five_star_pct,
        "one_star_percentage": one_star_pct,
        "product_diversity": product_diversity,
        "reviews_per_day": reviews_per_day,
        "median_interval_hours": median_interval,
        "min_interval_hours": min_interval,
    }

    observations = []
    risk = 0.0
    if five_star_pct > 0.85 and total >= 5:
        risk += 0.2
        observations.append("Reviewer has an unusually high five-star ratio.")
    if reviews_per_day > 3:
        risk += 0.2
        observations.append("Reviewer activity volume is unusually high.")
    if min_interval < 1 and total >= 3:
        risk += 0.2
        observations.append("Reviews posted with very short intervals detected.")
    if product_diversity < 0.2 and total >= 5:
        risk += 0.15
        observations.append("Reviewer concentrates activity on few products.")
    if variance < 0.1 and total >= 5:
        risk += 0.1
        observations.append("Rating pattern shows unusually low variance.")

    return {
        "behavior_risk": min(risk, 1.0),
        "metrics": metrics,
        "observations": observations,
    }
