from ml.schemas.features import ModalityScores, PredictionResult


def classify_probability(probability: float) -> str:
    if probability < 0.4:
        return "Genuine"
    if probability < 0.7:
        return "Suspicious"
    return "Potentially Fake"


def fuse_modalities(
    text_risk: float,
    behavior_risk: float,
    temporal_risk: float,
    similarity_risk: float,
    graph_risk: float,
    model_version: str = "demo-v0.1.0",
) -> PredictionResult:
    weights = {
        "text": 0.2,
        "behavior": 0.25,
        "temporal": 0.2,
        "similarity": 0.2,
        "graph": 0.15,
    }
    fraud_probability = (
        text_risk * weights["text"]
        + behavior_risk * weights["behavior"]
        + temporal_risk * weights["temporal"]
        + similarity_risk * weights["similarity"]
        + graph_risk * weights["graph"]
    )
    fraud_probability = min(max(fraud_probability, 0.0), 1.0)
    classification = classify_probability(fraud_probability)

    modality_scores = ModalityScores(
        text_risk=text_risk,
        behavior_risk=behavior_risk,
        temporal_risk=temporal_risk,
        similarity_risk=similarity_risk,
        graph_risk=graph_risk,
    )

    top_features = sorted(
        [
            {"feature": "text_risk", "contribution": text_risk * weights["text"]},
            {"feature": "behavior_risk", "contribution": behavior_risk * weights["behavior"]},
            {"feature": "temporal_risk", "contribution": temporal_risk * weights["temporal"]},
            {"feature": "similarity_risk", "contribution": similarity_risk * weights["similarity"]},
            {"feature": "graph_risk", "contribution": graph_risk * weights["graph"]},
        ],
        key=lambda x: x["contribution"],
        reverse=True,
    )

    return PredictionResult(
        fraud_probability=fraud_probability,
        classification=classification,
        model_version=model_version,
        modality_scores=modality_scores,
        explanation="",
        top_features=top_features,
    )
