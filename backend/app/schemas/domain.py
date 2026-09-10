from datetime import datetime

from pydantic import BaseModel, Field


class ReviewerResponse(BaseModel):
    id: int
    reviewer_id: str
    account_created_at: datetime | None
    total_reviews: int
    average_rating: float
    rating_variance: float
    five_star_percentage: float
    product_count: int
    review_frequency: float
    suspicious_score: float
    is_demo: bool

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    product_id: str
    name: str
    category: str
    seller: str | None
    is_demo: bool

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    id: int
    review_id: str
    reviewer_id: int
    product_id: int
    rating: float
    review_text: str
    review_timestamp: datetime
    verified_purchase: bool | None
    review_label: str | None
    is_demo: bool

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    review_id: str
    reviewer_id: str
    product_id: str
    rating: float = Field(..., ge=1, le=5)
    review_text: str = Field(..., min_length=1)
    review_timestamp: datetime
    verified_purchase: bool | None = None


class PredictionResponse(BaseModel):
    id: int
    review_id: int
    fraud_probability: float
    classification: str
    model_version: str
    text_risk: float
    behavior_risk: float
    temporal_risk: float
    similarity_risk: float
    graph_risk: float
    explanation: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeReviewRequest(BaseModel):
    review_text: str = Field(..., min_length=1)
    reviewer_id: str | None = None
    product_id: str | None = None
    rating: float = Field(..., ge=1, le=5)
    review_timestamp: datetime | None = None


class AnalyzeResponse(BaseModel):
    persisted: bool = False
    review_id: str | None = None
    fraud_probability: float
    classification: str
    model_version: str
    text_risk: float
    behavior_risk: float
    temporal_risk: float
    similarity_risk: float
    graph_risk: float
    explanation: str | None = None
    weights_used: dict[str, float] = Field(default_factory=dict)
    missing_modalities: list[str] = Field(default_factory=list)
    history_available: bool = True
    similarity_backend: str = "tfidf"
    created_at: datetime


class SimilarityResponse(BaseModel):
    id: int
    review_a_id: int
    review_b_id: int
    similarity_score: float
    similarity_type: str
    same_product: bool
    same_reviewer: bool
    time_difference_hours: float | None

    model_config = {"from_attributes": True}


class BehaviorProfileResponse(BaseModel):
    id: int
    reviewer_id: int
    behavioural_metrics: dict
    temporal_metrics: dict
    rating_metrics: dict
    anomaly_metrics: dict
    observations: str | None

    model_config = {"from_attributes": True}


class FraudClusterResponse(BaseModel):
    id: int
    cluster_id: str
    risk_score: float
    reviewer_count: int
    product_count: int
    review_count: int
    reviewers: list
    products: list
    temporal_evidence: dict
    similarity_evidence: dict
    graph_metrics: dict
    explanation: str | None

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int


class DashboardStats(BaseModel):
    total_reviews: int
    suspicious_reviews: int
    potentially_fake_reviews: int
    genuine_reviews: int
    high_risk_reviewers: int
    suspicious_clusters: int
    model_version: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    risk_score: float = 0.0


class GraphEdge(BaseModel):
    source: str
    target: str
    rating: float | None = None
    review_id: str | None = None


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ModelInfoResponse(BaseModel):
    model_version: str
    device: str
    modalities: list[str]
    status: str
    similarity_backend: str = "tfidf"
    vector_index: str = "numpy"
