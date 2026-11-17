import csv
import io
from datetime import UTC, datetime

from fastapi import HTTPException, UploadFile, status

from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.csv_batch import (
    MAX_BATCH_ROWS,
    BatchAnalysisResult,
    BatchStatistics,
    BatchValidationRow,
)
from app.services.ml_service import MLService

MAX_CSV_BYTES = 5 * 1024 * 1024
REQUIRED_COLUMNS = {"review_text", "rating"}
OPTIONAL_COLUMNS = {"reviewer_id", "review_id", "review_timestamp"}
EXPORT_COLUMNS = (
    "row_number",
    "review_id",
    "reviewer_id",
    "rating",
    "fraud_probability",
    "classification",
    "text_risk",
    "behavior_risk",
    "temporal_risk",
    "similarity_risk",
    "graph_risk",
    "model_version",
    "review_text",
)


async def read_csv_upload(upload: UploadFile) -> bytes:
    if upload.filename is None or not upload.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload a .csv file.")

    content = await upload.read(MAX_CSV_BYTES + 1)
    if len(content) > MAX_CSV_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="CSV files must be 5 MB or smaller.")
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded CSV is empty.")
    return content


def validate_csv_content(content: bytes) -> list[BatchValidationRow]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must use UTF-8 encoding.",
        ) from exc

    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV must include a header row.")

    headers = [header.strip().lower() for header in reader.fieldnames if header is not None]
    if (
        len(headers) != len(reader.fieldnames)
        or any(not header for header in headers)
        or len(set(headers)) != len(headers)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV headers must be non-empty and unique.")
    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required CSV column(s): {', '.join(sorted(missing))}.",
        )
    unexpected = set(headers) - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
    if unexpected:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported CSV column(s): {', '.join(sorted(unexpected))}.",
        )

    reader.fieldnames = headers
    rows: list[BatchValidationRow] = []
    for row_number, raw_row in enumerate(reader, start=2):
        if row_number - 1 > MAX_BATCH_ROWS:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"CSV files may contain at most {MAX_BATCH_ROWS} data rows.",
            )
        values = {key: (value or "").strip() for key, value in raw_row.items() if key is not None}
        errors: list[str] = []
        if None in raw_row:
            errors.append("Row has more values than the header.")

        review_text = values.get("review_text", "")
        if not review_text:
            errors.append("review_text is required.")

        rating: float | None = None
        rating_value = values.get("rating", "")
        if not rating_value:
            errors.append("rating is required.")
        else:
            try:
                rating = float(rating_value)
                if not 1 <= rating <= 5:
                    errors.append("rating must be between 1 and 5.")
            except ValueError:
                errors.append("rating must be a number between 1 and 5.")

        review_timestamp: datetime | None = None
        timestamp_value = values.get("review_timestamp", "")
        if timestamp_value:
            try:
                review_timestamp = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
                if review_timestamp.tzinfo is None:
                    review_timestamp = review_timestamp.replace(tzinfo=UTC)
            except ValueError:
                errors.append("review_timestamp must be an ISO 8601 date/time.")

        rows.append(
            BatchValidationRow(
                row_number=row_number,
                review_text=review_text,
                rating=rating,
                reviewer_id=values.get("reviewer_id") or None,
                review_id=values.get("review_id") or None,
                review_timestamp=review_timestamp,
                errors=errors,
            )
        )

    if not rows:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="CSV contains no data rows.")
    return rows


def validate_csv_rows(rows: list[BatchValidationRow]) -> dict:
    return {
        "total_rows": len(rows),
        "valid_rows": sum(not row.errors for row in rows),
        "invalid_rows": sum(bool(row.errors) for row in rows),
        "rows": rows,
    }


def analyze_batch(rows: list[BatchValidationRow], db) -> dict:
    reviewer_repository = ReviewerRepository(db)
    ml_service = MLService(db)
    results: list[BatchAnalysisResult] = []

    for row in rows:
        reviewer = reviewer_repository.get_by_reviewer_id(row.reviewer_id) if row.reviewer_id else None
        result = ml_service.analyze_review(
            review_text=row.review_text,
            rating=row.rating,
            reviewer_db_id=reviewer.id if reviewer else None,
            review_id=row.review_id or f"batch-row-{row.row_number}",
            review_timestamp=row.review_timestamp or datetime.now(UTC),
        )
        scores = result.modality_scores
        results.append(
            BatchAnalysisResult(
                row_number=row.row_number,
                review_id=row.review_id,
                reviewer_id=row.reviewer_id,
                review_text=row.review_text,
                rating=row.rating,
                fraud_probability=result.fraud_probability,
                classification=result.classification,
                model_version=result.model_version,
                text_risk=scores.text_risk,
                behavior_risk=scores.behavior_risk,
                temporal_risk=scores.temporal_risk,
                similarity_risk=scores.similarity_risk,
                graph_risk=scores.graph_risk,
                explanation=result.explanation,
            )
        )

    classification_counts: dict[str, int] = {}
    for result in results:
        classification_counts[result.classification] = classification_counts.get(result.classification, 0) + 1

    statistics = BatchStatistics(
        average_fraud_probability=sum(row.fraud_probability for row in results) / len(results),
        high_risk_count=sum(row.fraud_probability >= 0.7 for row in results),
        classification_counts=classification_counts,
    )
    return {"total_rows": len(results), "statistics": statistics, "results": results}


def export_batch_csv(rows: list[BatchAnalysisResult]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        values = row.model_dump()
        for field in ("review_id", "reviewer_id", "review_text"):
            value = values[field]
            if isinstance(value, str) and value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
                values[field] = f"'{value}"
        writer.writerow(values)
    return output.getvalue()
