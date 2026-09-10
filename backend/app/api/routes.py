from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.core.deps import AnalystUser, DbSession, ViewerUser
from app.repositories.analysis_repository import ClusterRepository, SimilarityRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.domain import (
    AnalyzeResponse,
    AnalyzeReviewRequest,
    DashboardStats,
    FraudClusterResponse,
    GraphResponse,
    ModelInfoResponse,
    PaginatedResponse,
    PredictionResponse,
    ProductResponse,
    ReviewerResponse,
    ReviewResponse,
    SimilarityResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.ml_service import MLService

router = APIRouter(tags=["Reviews"])


def _paginate(items: list, total: int, page: int, page_size: int) -> PaginatedResponse:
    pages = max((total + page_size - 1) // page_size, 1)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/reviews", response_model=PaginatedResponse, summary="List reviews")
def list_reviews(
    db: DbSession,
    _: ViewerUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    items, total = ReviewRepository(db).list_paginated(page, page_size)
    return _paginate([ReviewResponse.model_validate(i) for i in items], total, page, page_size)


@router.get("/reviews/{review_id}", response_model=ReviewResponse, summary="Get review by ID")
def get_review(review_id: str, db: DbSession, _: ViewerUser) -> ReviewResponse:
    review = ReviewRepository(db).get_by_review_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewResponse.model_validate(review)


@router.get("/reviewers", response_model=PaginatedResponse, summary="List reviewers")
def list_reviewers(
    db: DbSession,
    _: ViewerUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    items, total = ReviewerRepository(db).list_paginated(page, page_size)
    return _paginate([ReviewerResponse.model_validate(i) for i in items], total, page, page_size)


@router.get("/reviewers/{reviewer_id}", response_model=ReviewerResponse, summary="Get reviewer")
def get_reviewer(reviewer_id: str, db: DbSession, _: ViewerUser) -> ReviewerResponse:
    reviewer = ReviewerRepository(db).get_by_reviewer_id(reviewer_id)
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")
    return ReviewerResponse.model_validate(reviewer)


@router.get("/products", response_model=PaginatedResponse, summary="List products")
def list_products(
    db: DbSession,
    _: ViewerUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    items, total = ProductRepository(db).list_paginated(page, page_size)
    return _paginate([ProductResponse.model_validate(i) for i in items], total, page, page_size)


@router.get("/products/{product_id}", response_model=ProductResponse, summary="Get product")
def get_product(product_id: str, db: DbSession, _: ViewerUser) -> ProductResponse:
    product = ProductRepository(db).get_by_product_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/predictions", response_model=PaginatedResponse, summary="List predictions")
def list_predictions(
    db: DbSession,
    _: ViewerUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    items, total = PredictionRepository(db).list_paginated(page, page_size)
    return _paginate([PredictionResponse.model_validate(i) for i in items], total, page, page_size)


@router.get("/predictions/review/{review_db_id}", response_model=PredictionResponse, summary="Get prediction for review")
def get_prediction(review_db_id: int, db: DbSession, _: ViewerUser) -> PredictionResponse:
    prediction = PredictionRepository(db).get_latest_for_review(review_db_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return PredictionResponse.model_validate(prediction)


@router.post("/predictions/analyze", response_model=AnalyzeResponse, summary="Analyze a review")
def analyze_review(data: AnalyzeReviewRequest, db: DbSession, _: AnalystUser) -> AnalyzeResponse:
    """Score a review in-memory. Does not insert reviews or predictions."""
    reviewer_db_id = None
    if data.reviewer_id:
        reviewer = ReviewerRepository(db).get_by_reviewer_id(data.reviewer_id)
        reviewer_db_id = reviewer.id if reviewer else None

    result = MLService(db).analyze_review(
        review_text=data.review_text,
        rating=data.rating,
        reviewer_db_id=reviewer_db_id,
        review_timestamp=data.review_timestamp or datetime.now(UTC),
    )
    scores = result.modality_scores
    return AnalyzeResponse(
        persisted=False,
        review_id=None,
        fraud_probability=result.fraud_probability,
        classification=result.classification,
        model_version=result.model_version,
        text_risk=scores.text_risk,
        behavior_risk=scores.behavior_risk,
        temporal_risk=scores.temporal_risk,
        similarity_risk=scores.similarity_risk,
        graph_risk=scores.graph_risk,
        explanation=result.explanation,
        weights_used=result.weights_used,
        missing_modalities=result.missing_modalities,
        history_available=result.history_available,
        similarity_backend=result.similarity_backend,
        created_at=datetime.now(UTC),
    )


@router.get("/similarity/review/{review_db_id}", response_model=list[SimilarityResponse], summary="Get similar reviews")
def get_similarities(review_db_id: int, db: DbSession, _: ViewerUser) -> list[SimilarityResponse]:
    items = SimilarityRepository(db).list_for_review(review_db_id)
    return [SimilarityResponse.model_validate(i) for i in items]


@router.get("/clusters", response_model=PaginatedResponse, summary="List fraud clusters")
def list_clusters(
    db: DbSession,
    _: ViewerUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    items, total = ClusterRepository(db).list_paginated(page, page_size)
    return _paginate([FraudClusterResponse.model_validate(i) for i in items], total, page, page_size)


@router.get("/clusters/{cluster_id}", response_model=FraudClusterResponse, summary="Get fraud cluster")
def get_cluster(cluster_id: str, db: DbSession, _: ViewerUser) -> FraudClusterResponse:
    cluster = ClusterRepository(db).get_by_cluster_id(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return FraudClusterResponse.model_validate(cluster)


@router.get("/analytics/dashboard", response_model=DashboardStats, summary="Dashboard statistics")
def dashboard_stats(db: DbSession, _: ViewerUser) -> DashboardStats:
    settings = get_settings()
    return AnalyticsService(db).get_dashboard_stats(settings.ml_model_version)


@router.get("/analytics/model", summary="Model performance metrics")
def model_metrics(db: DbSession, _: ViewerUser) -> dict:
    return AnalyticsService(db).get_model_metrics()


@router.get("/graph", response_model=GraphResponse, summary="Reviewer-product graph data")
def get_graph(db: DbSession, _: ViewerUser) -> GraphResponse:
    reviews = ReviewRepository(db).list_all()
    review_data = [
        {
            "review_id": r.review_id,
            "reviewer_id": r.reviewer.reviewer_id if r.reviewer else str(r.reviewer_id),
            "product_id": r.product.product_id if r.product else str(r.product_id),
            "rating": r.rating,
            "review_text": r.review_text,
            "review_timestamp": r.review_timestamp,
        }
        for r in reviews
    ]
    from ml.graph.intelligence import build_review_graph, graph_to_frontend

    graph = build_review_graph(review_data)
    data = graph_to_frontend(graph)
    return GraphResponse(**data)


@router.get("/models/info", response_model=ModelInfoResponse, summary="Model system information")
def model_info(_: ViewerUser) -> ModelInfoResponse:
    from ml.similarity.engine import similarity_runtime

    settings = get_settings()
    runtime = similarity_runtime()
    return ModelInfoResponse(
        model_version=settings.ml_model_version,
        device=settings.ml_device,
        modalities=["nlp", "behavior", "temporal", "similarity", "graph"],
        status="ready",
        similarity_backend=runtime.get("embedding_backend", settings.similarity_backend),
        vector_index=runtime.get("vector_index", "numpy"),
    )
