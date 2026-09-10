from dataclasses import dataclass, field


@dataclass
class ModalityScores:
    text_risk: float = 0.0
    behavior_risk: float = 0.0
    temporal_risk: float = 0.0
    similarity_risk: float = 0.0
    graph_risk: float = 0.0


@dataclass
class FeatureVector:
    features: dict[str, float] = field(default_factory=dict)
    modality_scores: ModalityScores = field(default_factory=ModalityScores)


@dataclass
class PredictionResult:
    fraud_probability: float
    classification: str
    model_version: str
    modality_scores: ModalityScores
    explanation: str
    top_features: list[dict[str, float]] = field(default_factory=list)
    weights_used: dict[str, float] = field(default_factory=dict)
    missing_modalities: list[str] = field(default_factory=list)
    history_available: bool = True
    similarity_backend: str = "tfidf"
