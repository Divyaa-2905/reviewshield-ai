from datetime import datetime

from pydantic import BaseModel, Field

MAX_BATCH_ROWS = 500


class BatchValidationRow(BaseModel):
    row_number: int = Field(..., ge=2)
    review_text: str
    rating: float | None = None
    reviewer_id: str | None = None
    review_id: str | None = None
    review_timestamp: datetime | None = None
    errors: list[str] = Field(default_factory=list)


class BatchValidationResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    rows: list[BatchValidationRow]


class BatchAnalyzeRequest(BaseModel):
    rows: list[BatchValidationRow] = Field(..., min_length=1, max_length=MAX_BATCH_ROWS)


class BatchAnalysisResult(BaseModel):
    row_number: int = Field(..., ge=2)
    review_id: str | None
    reviewer_id: str | None
    review_text: str
    rating: float = Field(..., ge=1, le=5)
    fraud_probability: float
    classification: str
    model_version: str
    text_risk: float
    behavior_risk: float
    temporal_risk: float
    similarity_risk: float
    graph_risk: float
    explanation: str | None = None


class BatchStatistics(BaseModel):
    average_fraud_probability: float
    high_risk_count: int
    classification_counts: dict[str, int]


class BatchAnalysisResponse(BaseModel):
    total_rows: int
    statistics: BatchStatistics
    results: list[BatchAnalysisResult]


class BatchExportRequest(BaseModel):
    results: list[BatchAnalysisResult] = Field(..., min_length=1, max_length=MAX_BATCH_ROWS)
