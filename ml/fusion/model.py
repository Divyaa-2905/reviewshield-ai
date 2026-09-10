from ml.schemas.features import ModalityScores, PredictionResult

DEFAULT_WEIGHTS: dict[str, float] = {
    "text": 0.20,
    "behavior": 0.25,
    "temporal": 0.20,
    "similarity": 0.20,
    "graph": 0.15,
}


def classify_probability(probability: float) -> str:
    if probability < 0.4:
        return "Genuine"
    if probability < 0.7:
        return "Suspicious"
    return "Potentially Fake"


def resolve_modality_weights(
    *,
    history_available: bool = True,
    available_modalities: dict[str, bool] | None = None,
    base_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Redistribute fusion weights when a modality has no evidence.

    Missing reviewer history zeros behavior/temporal instead of letting those
    zeros silently dilute text, similarity, and graph evidence.
    """
    weights = dict(base_weights or DEFAULT_WEIGHTS)
    available = {
        "text": True,
        "behavior": history_available,
        "temporal": history_available,
        "similarity": True,
        "graph": True,
    }
    if available_modalities:
        available.update(available_modalities)

    dropped = 0.0
    for name, is_available in available.items():
        if name in weights and not is_available:
            dropped += weights[name]
            weights[name] = 0.0

    remaining = [name for name, value in weights.items() if value > 0]
    remaining_sum = sum(weights[name] for name in remaining)
    if dropped and remaining_sum > 0:
        for name in remaining:
            weights[name] += dropped * (weights[name] / remaining_sum)

    total = sum(weights.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {name: value / total for name, value in weights.items()}


def fuse_modalities(
    text_risk: float,
    behavior_risk: float,
    temporal_risk: float,
    similarity_risk: float,
    graph_risk: float,
    model_version: str = "demo-v0.1.0",
    *,
    history_available: bool = True,
    available_modalities: dict[str, bool] | None = None,
) -> PredictionResult:
    weights = resolve_modality_weights(
        history_available=history_available,
        available_modalities=available_modalities,
    )
    scores = {
        "text": text_risk,
        "behavior": 0.0 if weights["behavior"] == 0 else behavior_risk,
        "temporal": 0.0 if weights["temporal"] == 0 else temporal_risk,
        "similarity": similarity_risk,
        "graph": graph_risk,
    }
    fraud_probability = sum(scores[name] * weights[name] for name in weights)
    fraud_probability = min(max(fraud_probability, 0.0), 1.0)
    classification = classify_probability(fraud_probability)

    modality_scores = ModalityScores(
        text_risk=text_risk,
        behavior_risk=scores["behavior"],
        temporal_risk=scores["temporal"],
        similarity_risk=similarity_risk,
        graph_risk=graph_risk,
    )

    top_features = sorted(
        [
            {"feature": f"{name}_risk", "contribution": scores[name] * weights[name]}
            for name in weights
        ],
        key=lambda item: item["contribution"],
        reverse=True,
    )

    missing = [name for name, value in weights.items() if value == 0]
    return PredictionResult(
        fraud_probability=fraud_probability,
        classification=classification,
        model_version=model_version,
        modality_scores=modality_scores,
        explanation="",
        top_features=top_features,
        weights_used=weights,
        missing_modalities=missing,
        history_available=history_available,
    )
