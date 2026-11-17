import csv
import io

from app.models.prediction_feedback import PredictionFeedback


def export_feedback_csv(feedback: list[PredictionFeedback]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "review_id",
            "product_id",
            "product_name",
            "prediction_classification",
            "decision",
            "comment",
            "analyst",
            "created_at",
            "updated_at",
        ]
    )
    for item in feedback:
        review = item.prediction.review
        writer.writerow(
            [
                _spreadsheet_safe(review.review_id),
                _spreadsheet_safe(review.product.product_id if review.product else ""),
                _spreadsheet_safe(review.product.name if review.product else ""),
                _spreadsheet_safe(item.prediction.classification),
                item.decision,
                _spreadsheet_safe(item.comment or ""),
                _spreadsheet_safe(item.analyst.username),
                item.created_at.isoformat(),
                item.updated_at.isoformat(),
            ]
        )
    return output.getvalue()


def _spreadsheet_safe(value: str) -> str:
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value
