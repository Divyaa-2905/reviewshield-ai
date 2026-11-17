from datetime import UTC, datetime

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile

from app.core.config import get_settings
from app.core.deps import AnalystUser, DbSession, ViewerUser
from app.models.prediction_feedback import PredictionFeedback
from app.repositories.analysis_repository import ClusterRepository, SimilarityRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.csv_batch import (
    BatchAnalysisResponse,
    BatchAnalyzeRequest,
    BatchExportRequest,
    BatchValidationResponse,
)
from app.schemas.domain import (
    AnalyzeResponse,
    AnalyzeReviewRequest,
    CampaignsResponse,
    DashboardStats,
    FraudClusterResponse,
    GraphResponse,
    ModelInfoResponse,
    PaginatedResponse,
    PredictionFeedbackRequest,
    PredictionFeedbackResponse,
    PredictionResponse,
    ProductResponse,
    ProductTrustResponse,
    ReviewerResponse,
    ReviewResponse,
    SimilarityResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.campaign_service import CampaignService
from app.services.csv_batch_service import (
    analyze_batch,
    export_batch_csv,
    read_csv_upload,
    validate_csv_content,
    validate_csv_rows,
)
from app.services.feedback_export_service import export_feedback_csv
from app.services.ml_service import MLService
from app.services.product_report_service import create_product_report
from app.services.product_trust_service import ProductTrustService

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


@router.get(
    "/products/{product_id}/trust",
    response_model=ProductTrustResponse,
    summary="Analyze product review trust signals",
)
def get_product_trust(product_id: str, db: DbSession, _: ViewerUser) -> ProductTrustResponse:
    product = ProductRepository(db).get_by_product_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductTrustResponse.model_validate(ProductTrustService(db).analyze(product))


@router.get(
    "/products/{product_id}/report.pdf",
    summary="Download a product investigation report",
    response_class=Response,
)
def download_product_report(product_id: str, db: DbSession, _: ViewerUser) -> Response:
    product = ProductRepository(db).get_by_product_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    analysis = ProductTrustService(db).analyze(product)
    report = create_product_report(
        {
            "product_id": product.product_id,
            "name": product.name,
            "category": product.category,
            "seller": product.seller,
        },
        analysis,
    )
    filename = "".join(
        char if char.isascii() and (char.isalnum() or char in "._-") else "-"
        for char in product.product_id
    )
    filename = filename.strip(".-") or "product"
    return Response(
        content=report,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="product-investigation-{filename}.pdf"'},
    )


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


def _feedback_response(feedback: PredictionFeedback) -> PredictionFeedbackResponse:
    review = feedback.prediction.review
    product = review.product
    return PredictionFeedbackResponse(
        id=feedback.id,
        prediction_id=feedback.prediction_id,
        review_db_id=review.id,
        review_id=review.review_id,
        product_id=product.product_id if product else str(review.product_id),
        product_name=product.name if product else "Unknown product",
        prediction_classification=feedback.prediction.classification,
        decision=feedback.decision,
        comment=feedback.comment,
        analyst_username=feedback.analyst.username,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )


@router.get(
    "/predictions/{prediction_id}/feedback",
    response_model=PredictionFeedbackResponse | None,
    summary="Get analyst feedback for a prediction",
)
def get_prediction_feedback(
    prediction_id: int,
    db: DbSession,
    _: AnalystUser,
) -> PredictionFeedbackResponse | None:
    feedback = FeedbackRepository(db).get_by_prediction_id(prediction_id)
    return _feedback_response(feedback) if feedback else None


@router.put(
    "/predictions/{prediction_id}/feedback",
    response_model=PredictionFeedbackResponse,
    summary="Record or update analyst feedback",
)
def upsert_prediction_feedback(
    prediction_id: int,
    data: PredictionFeedbackRequest,
    db: DbSession,
    analyst: AnalystUser,
) -> PredictionFeedbackResponse:
    prediction = PredictionRepository(db).get_by_id(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    repository = FeedbackRepository(db)
    feedback = repository.get_by_prediction_id(prediction_id)
    if feedback is None:
        feedback = PredictionFeedback(
            prediction_id=prediction_id,
            analyst_id=analyst.id,
            decision=data.decision,
            comment=data.comment,
        )
        db.add(feedback)
    else:
        feedback.analyst_id = analyst.id
        feedback.decision = data.decision
        feedback.comment = data.comment
        feedback.updated_at = datetime.now(UTC)
    db.commit()
    feedback = repository.get_by_prediction_id(prediction_id)
    if feedback is None:
        raise HTTPException(status_code=500, detail="Feedback could not be loaded after saving")
    return _feedback_response(feedback)


@router.get(
    "/feedback",
    summary="List verified prediction feedback",
)
def list_feedback(
    db: DbSession,
    _: AnalystUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    decision: str | None = Query(None, pattern="^(correct|incorrect|needs_correction)$"),
) -> PaginatedResponse:
    items, total = FeedbackRepository(db).list_paginated(page, page_size, decision)
    return _paginate([_feedback_response(item) for item in items], total, page, page_size)


@router.get(
    "/feedback/export",
    summary="Export verified prediction feedback as CSV",
    response_class=Response,
)
def download_feedback(
    db: DbSession,
    _: AnalystUser,
    decision: str | None = Query(None, pattern="^(correct|incorrect|needs_correction)$"),
) -> Response:
    content = export_feedback_csv(FeedbackRepository(db).list_all(decision))
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="verified-feedback.csv"'},
    )


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


@router.post(
    "/predictions/batch/validate",
    response_model=BatchValidationResponse,
    summary="Validate an uploaded review CSV",
)
async def validate_review_csv(
    _: AnalystUser,
    file: UploadFile = File(...),
) -> BatchValidationResponse:
    content = await read_csv_upload(file)
    rows = validate_csv_content(content)
    return BatchValidationResponse(**validate_csv_rows(rows))


@router.post(
    "/predictions/batch/analyze",
    response_model=BatchAnalysisResponse,
    summary="Analyze validated review rows",
)
def analyze_review_batch(
    data: BatchAnalyzeRequest,
    db: DbSession,
    _: AnalystUser,
) -> BatchAnalysisResponse:
    invalid_rows = [
        row.row_number
        for row in data.rows
        if row.errors or row.rating is None or not row.review_text.strip()
    ]
    if invalid_rows:
        raise HTTPException(
            status_code=422,
            detail=f"Batch contains invalid CSV row(s): {', '.join(map(str, invalid_rows))}.",
        )
    return BatchAnalysisResponse(**analyze_batch(data.rows, db))


@router.post(
    "/predictions/batch/export",
    summary="Export batch analysis results as CSV",
    response_class=Response,
)
def export_review_batch(data: BatchExportRequest, _: AnalystUser) -> Response:
    content = export_batch_csv(data.results)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="review-analysis-results.csv"'},
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


@router.get("/campaigns", response_model=CampaignsResponse, summary="Detect coordinated review campaigns")
def get_campaigns(db: DbSession, _: ViewerUser) -> CampaignsResponse:
    return CampaignsResponse(**CampaignService(db).get_campaigns())


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
