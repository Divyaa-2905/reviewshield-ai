from datetime import datetime, timedelta
from statistics import mean


def analyze_temporal_patterns(reviews: list[dict], window_hours: int = 24) -> dict:
    if len(reviews) < 2:
        return {"temporal_risk": 0.0, "metrics": {}, "observations": []}

    timestamps = sorted(r["review_timestamp"] for r in reviews)
    observations = []
    risk = 0.0

    bursts = 0
    for i in range(len(timestamps)):
        window_end = timestamps[i] + timedelta(hours=window_hours)
        count = sum(1 for t in timestamps if timestamps[i] <= t <= window_end)
        if count >= 5:
            bursts += 1

    intervals = [
        (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600
        for i in range(1, len(timestamps))
    ]
    avg_interval = mean(intervals) if intervals else 0.0

    metrics = {
        "burst_windows": float(bursts),
        "avg_interval_hours": avg_interval,
        "review_count": float(len(reviews)),
    }

    if bursts > 0:
        risk += 0.35
        observations.append("High review concentration detected within a short time window.")
    if avg_interval < 2 and len(reviews) >= 4:
        risk += 0.25
        observations.append("Reviews appear in rapid succession.")
    if len(reviews) >= 10 and avg_interval < 6:
        risk += 0.15
        observations.append("Sustained high-frequency posting pattern detected.")

    return {
        "temporal_risk": min(risk, 1.0),
        "metrics": metrics,
        "observations": observations,
    }


def detect_synchronized_activity(review_groups: list[list[datetime]], tolerance_hours: float = 2.0) -> int:
    sync_count = 0
    for group in review_groups:
        if len(group) < 2:
            continue
        sorted_ts = sorted(group)
        for i in range(len(sorted_ts) - 1):
            diff = (sorted_ts[i + 1] - sorted_ts[i]).total_seconds() / 3600
            if diff <= tolerance_hours:
                sync_count += 1
    return sync_count
