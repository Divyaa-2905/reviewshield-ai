# API Documentation

See interactive docs at `http://localhost:8000/docs` when the backend is running.

## Authentication

`POST /api/v1/auth/login` — OAuth2 password flow, returns JWT

## Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/v1/analytics/dashboard` | GET | Viewer+ | Dashboard stats |
| `/api/v1/analytics/model` | GET | Viewer+ | Metrics from a chronological labeled holdout |
| `/api/v1/campaigns` | GET | Viewer+ | Detect reviewer-product campaigns and return evidence |
| `/api/v1/products/{product_id}/trust` | GET | Viewer+ | Product trust/risk indicators and rating evidence |
| `/api/v1/products/{product_id}/report.pdf` | GET | Viewer+ | Download a PDF product investigation report |
| `/api/v1/predictions/analyze` | POST | Analyst+ | Analyze review text (not persisted) |
| `/api/v1/predictions/{prediction_id}/feedback` | GET/PUT | Analyst+ | Read or record analyst feedback on a stored prediction |
| `/api/v1/feedback` | GET | Analyst+ | Filter and page through verified feedback |
| `/api/v1/feedback/export` | GET | Analyst+ | Export verified feedback as CSV |
| `/api/v1/predictions/batch/validate` | POST | Analyst+ | Upload and validate a review CSV |
| `/api/v1/predictions/batch/analyze` | POST | Analyst+ | Analyze validated CSV rows in memory |
| `/api/v1/predictions/batch/export` | POST | Analyst+ | Export batch results as CSV |
| `/api/v1/reviews` | GET | Viewer+ | List reviews |
| `/api/v1/clusters` | GET | Viewer+ | Fraud clusters |
| `/api/v1/graph` | GET | Viewer+ | Graph data |

`/api/v1/analytics/model` uses the earliest chronological review portion as
historical feature context and evaluates only reviews at or after the cutoff.
Unlabeled holdout reviews are excluded from accuracy, precision, recall, F1,
and confusion-matrix counts. Metrics identify demo/sample data in the response;
when there are no labeled holdout reviews, performance metrics are `null`.
The runtime uses fixed heuristics and does not fit a model.

`/api/v1/campaigns` returns candidate groups assembled from reviewer-product
graph connections and stored review-similarity pairs, with temporal, similarity,
and graph evidence. Campaign risk is a heuristic investigation signal, not proof
of fraud.

## Product Trust Analysis and PDF Reports

`GET /api/v1/products/{product_id}/trust` returns a 0–100 risk score and a
trust score (`100 - risk`) with indicator values, score weights, rating
distribution, campaign involvement, and stored-prediction coverage. The
weighted risk uses suspicious classifications (50%), five-star concentration
(25%), and campaign involvement (25%). When no stored predictions exist, the
suspicious-classification indicator is unavailable and its weight is
redistributed across the available indicators. The rating-concentration
heuristic begins above 60% five-star reviews. These indicators are estimates,
not proof of fraud; unscored reviews are not counted as genuine.

`GET /api/v1/products/{product_id}/report.pdf` generates a downloadable report
from the same product analysis, including product metadata, review and
prediction coverage, risk evidence, and a rating-distribution chart.

## Analyst Feedback

`PUT /api/v1/predictions/{prediction_id}/feedback` accepts a decision of
`correct`, `incorrect`, or `needs_correction`, plus an optional comment of up
to 2,000 characters. There is one editable feedback record per stored
prediction; updates record the analyst and update timestamp. Live
`/predictions/analyze` results are not persisted and therefore cannot be
annotated. Analysts can filter the paginated `/api/v1/feedback` view by
decision and export the same filter as CSV. These endpoints require the
analyst or admin role.

## Batch CSV Analysis

The upload endpoint accepts a UTF-8 `.csv` file of up to 5 MB and 500 data rows.
`review_text` and `rating` columns are required; `reviewer_id`, `review_id`, and
`review_timestamp` are optional. Ratings must be between 1 and 5, and timestamps
must use ISO 8601 format. Validation returns a per-row preview and errors; only
valid rows can be sent to the batch analysis endpoint. Analysis scores rows
through the existing ML pipeline but does not insert reviews or predictions.
The export endpoint accepts the returned analysis results and responds with a
downloadable CSV file.

## Demo Credentials

- admin / admin123 (full access)
- analyst / analyst123 (analyze + investigate)
- viewer / viewer123 (read-only)
