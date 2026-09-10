from ml.schemas.features import PredictionResult


def build_explanation(
    result: PredictionResult,
    text_observations: list[str],
    behavior_observations: list[str],
    temporal_observations: list[str],
    similarity_matches: list[dict],
    graph_observations: list[str],
) -> str:
    lines = [
        f"Fraud probability: {result.fraud_probability:.2f}",
        f"Classification: {result.classification}",
        "Evidence:",
    ]

    all_observations = (
        text_observations[:2]
        + behavior_observations[:2]
        + temporal_observations[:2]
        + graph_observations[:2]
    )
    for obs in all_observations:
        lines.append(f"- {obs}")

    if similarity_matches:
        lines.append(
            f"- Review has high semantic similarity with {len(similarity_matches)} other review(s)."
        )

    if not all_observations and not similarity_matches:
        lines.append("- No strong fraud indicators detected across available modalities.")

    if result.missing_modalities:
        lines.append(
            "- Missing modalities: "
            + ", ".join(result.missing_modalities)
            + ". Their weights were redistributed."
        )

    lines.append(f"Model version: {result.model_version}")
    return "\n".join(lines)


def explain_prediction(
    result: PredictionResult,
    observations: dict,
    similarity_matches: list[dict] | None = None,
) -> PredictionResult:
    explanation = build_explanation(
        result=result,
        text_observations=observations.get("text", []),
        behavior_observations=observations.get("behavior", []),
        temporal_observations=observations.get("temporal", []),
        similarity_matches=similarity_matches or [],
        graph_observations=observations.get("graph", []),
    )
    result.explanation = explanation
    return result
