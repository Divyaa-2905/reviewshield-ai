# ReviewShield AI — Project Status

Last updated: 2026-11-17
Phase: **CHUNK 3 — final features implemented**
Scope: product-level trust analysis, analyst feedback and export, downloadable PDF reports, and related API/UI integration.

This document replaces the earlier “all phases done” checklist. The application is a working investigation demo. Several declared capabilities (trained models, SHAP, migrations, frontend tests) are dependencies or docs only.

## Verdict

ReviewShield can authenticate users, seed labeled demo reviews, score a review in memory across five heuristic modalities, and render product investigations, analyst feedback, and downloadable reports alongside the dashboard. Product scores and campaign signals remain heuristics, not proof of fraud. Do not treat fusion weights, XGBoost, or SHAP as a trained fraud model.

Risk scores are estimates. `POST /api/v1/predictions/analyze` must stay read-only.

## What exists

| Layer | Location | What works |
|-------|----------|------------|
| Frontend | `frontend/` | React 19, Vite, Tailwind 4, React Router 7. Product trust investigation and analyst feedback pages behind JWT. API client in `frontend/src/services/api.ts`. Cytoscape graph with click, pan, and zoom. Recharts for analytics and product ratings. |
| Backend | `backend/app/` | FastAPI app, CORS, `/health`, `/docs`. JWT login, `/auth/me`, admin user create/list. Repository + service layout. RBAC: viewer reads, analyst analyzes and submits feedback, admin manages users. |
| Database | `backend/app/models/` | SQLAlchemy 2 models created with `Base.metadata.create_all`, including one feedback record per stored prediction. SQLite for local dev. Optional Postgres + pgvector persistence in `VectorStore` (Docker only). |
| ML | `ml/` | Heuristic NLP, behavior, temporal, TF-IDF similarity, NetworkX graph, weighted fusion with missing-history reweight, template explanations, labeled precision/recall/F1/ROC-AUC/PR-AUC. |
| Scripts | `scripts/` | Deterministic demo seed (`is_demo=True`), Amazon/Yelp loaders and eval entry points, feature/dataset helpers. |
| Fixtures | `data/sample/` | Small labeled Amazon CSV and Yelp JSONL. |
| Ops | root | `docker-compose.yml` (pgvector Postgres, API, nginx frontend), GitHub Actions (Ruff, pytest, frontend lint + build), `Makefile`, `.env.example`. |
| Docs | `docs/`, `AGENTS.md` | Architecture, API, methodology, security, data and ML pipeline, model card. Agent contract matches the code. |

### API surface (all under `/api/v1` except health)

| Method | Path | Auth | Persistence |
|--------|------|------|-------------|
| GET | `/health` | public | none |
| POST | `/auth/login` | public | none |
| GET | `/auth/me` | any role | none |
| POST/GET | `/auth/users` | admin | users only |
| GET | `/reviews`, `/reviews/{id}` | viewer+ | read |
| GET | `/reviewers`, `/reviewers/{id}` | viewer+ | read |
| GET | `/products`, `/products/{id}` | viewer+ | read |
| GET | `/products/{id}/trust`, `/products/{id}/report.pdf` | viewer+ | computed from stored reviews/predictions/campaigns |
| GET | `/predictions`, `/predictions/review/{db_id}` | viewer+ | read |
| GET/PUT | `/predictions/{id}/feedback` | analyst+ | read/update analyst decision and timestamps |
| GET | `/feedback`, `/feedback/export` | analyst+ | filter/paginate and export reviewed decisions |
| POST | `/predictions/analyze` | analyst+ | **in memory only** (`persisted=false`) |
| GET | `/similarity/review/{db_id}` | viewer+ | seeded pairs |
| GET | `/clusters`, `/clusters/{id}` | viewer+ | seeded clusters |
| GET | `/analytics/dashboard`, `/analytics/model` | viewer+ | computed from stored rows |
| GET | `/graph` | viewer+ | rebuilt from all reviews |
| GET | `/models/info` | viewer+ | runtime config |

Demo logins (seeded, not production secrets): `admin/admin123`, `analyst/analyst123`, `viewer/viewer123`.

### Database models (11 tables)

`User`, `Reviewer`, `Product`, `Review`, `Prediction`, `PredictionFeedback`, `BehaviorProfile`, `FraudCluster`, `ReviewSimilarity`, `ReviewEmbedding`, `AuditLog`.

`Review.review_label` and `Review.is_demo` support honest evaluation and demo labeling. Embeddings are stored as JSON floats so SQLite stays valid. pgvector writes go through raw SQL in `backend/app/services/vector_store.py`.

### ML behavior that is real

- Fusion weights in `ml/fusion/model.py`: text 0.20, behavior 0.25, temporal 0.20, similarity 0.20, graph 0.15. Missing reviewer history zeros behavior and temporal and redistributes that mass.
- Classes: Genuine `< 0.4`, Suspicious `< 0.7`, Potentially Fake otherwise.
- Similarity: `SIMILARITY_BACKEND=auto` prefers Sentence-Transformers + FAISS when installed (`backend/requirements-ml.txt`); otherwise TF-IDF + numpy. CI forces `tfidf`.
- Metrics in `ml/evaluation/metrics.py` return null AUC when labels are missing or single-class. Analytics passes stored labels through `evaluate_predictions`.
- Tests present: 5 backend (`test_health.py` + `test_api.py`), 13 ML (`test_ml.py`, `test_evaluation.py`, `test_datasets.py`). Analyze-route test asserts no `Review` or `Prediction` insert.

### Dependencies actually imported

Core: FastAPI, Uvicorn, Pydantic, SQLAlchemy, python-jose, bcrypt, pandas, numpy, scikit-learn (TF-IDF + metrics), NetworkX, ReportLab (product reports).

Frontend: React, react-router-dom, cytoscape, recharts, lucide-react, Tailwind via Vite.

Declared but unused in application code: **Alembic** (no `alembic/` tree), **XGBoost**, **SHAP**. Explainability is string templates in `ml/explainability/explainer.py`.

## What is missing or thin

These are gaps relative to a production fraud system and relative to packages listed in `backend/requirements.txt`. They are not blockers for the current demo.

1. **No trained model.** Fusion is a fixed weighted sum of hand rules. `ML_MODEL_VERSION=demo-v0.1.0` is a label, not a checkpoint. XGBoost is never fit or loaded.
2. **Rating is accepted and ignored on the scored review.** `MLService.analyze_review` takes `rating` and does not pass it into `analyze_text` or fusion. Behavior uses ratings only from stored history.
3. **Graph risk is corpus-wide.** `analyze_graph` returns one `graph_risk` for the whole network. Every live analysis receives that same score. Similarity edges are optional in `build_review_graph` and the `/graph` route does not pass them.
4. **Live analyze rebuilds the corpus index every call** (`VectorStore.rebuild_runtime_index` / `build_similarity_index`) and does not write clusters, similarities, or embeddings.
5. **`AuditLog` is never written.** The table is created; no route or service inserts rows.
6. **`BehaviorProfile` is seed-only.** No read API. The dashboard uses reviewer aggregates and live heuristics instead.
7. **No schema migrations.** `init_db()` calls `create_all`. Alembic is a dependency without versions, so later column changes will not upgrade existing SQLite or Postgres databases.
8. **No frontend tests.** Vitest and Testing Library are in `package.json`. `make test` does not run them. CI typechecks and builds only. API responses are typed as `any` on several pages.
9. **No admin UI.** User create/list exists on the API only. Settings shows health and model info.
10. **List endpoints have page size only.** No text search, label filter, date range, or risk sort beyond repository defaults.
11. **Makefile is Unix-only.** Targets use `python3`, `source` (`.`), and `rm`. This workspace is Windows PowerShell; `make install` will not run as written without Git Bash or WSL.
12. **Security is demo-grade.** Default `SECRET_KEY` / `JWT_SECRET_KEY` in `.env.example` and Compose. No refresh tokens, rate limits, or audit of analyze calls. Access token expiry is 30 minutes.
13. **Evaluation fixtures are tiny.** `data/sample/` is enough to exercise loaders and metrics. It is not a benchmark of real Amazon or Yelp scale. Seeded dashboard metrics describe demo labels.
14. **Frontend role is login-only.** A viewer who knows the analyzer URL still calls the API; the API returns 403. The UI does not hide analyst actions by role.

## Chunk 3 — delivered

- **Product trust analysis:** `ProductTrustService` combines the latest stored prediction per review, the exact rating distribution, and product reviews included in detected campaign candidates. The 0–100 risk score uses weighted indicators (50% suspicious share, 25% exact five-star concentration, 25% campaign involvement). If no stored predictions exist, that unavailable weight is redistributed. Coverage and clear indicator explanations accompany the risk and trust scores.
- **Analyst feedback:** analysts/admins can mark a stored prediction correct, incorrect, or needing correction, add an optional note, and update that decision later. One `PredictionFeedback` row per prediction preserves creation/update timestamps and analyst identity. Analysts can filter, paginate, and export feedback as CSV. Live analyze remains read-only and cannot be annotated.
- **PDF reports:** ReportLab creates downloadable product investigation reports from the same trust analysis, including product metadata, review/prediction statistics, indicator evidence, and a rating-distribution chart.
- **UI/API:** product cards open an evidence-rich trust investigation; review detail can submit analyst feedback; Verified Feedback is displayed for analysts/admins.
- **Persistence note:** `PredictionFeedback` is an additive table created by the existing `create_all` initialization. This does not resolve the project's broader lack of migrations for future schema changes.
- Risk and trust scores remain heuristic estimates and are not proof of fraud.

## What to reuse (do not rewrite)

- `POST /predictions/analyze` contract: `AnalyzeResponse`, `persisted=false`, no inserts. Tests in `backend/tests/test_api.py`.
- `fuse_modalities(..., history_available=False)` and `resolve_modality_weights`.
- `ml/similarity/engine.py` public API and the TF-IDF fallback. Keep `SIMILARITY_BACKEND=tfidf` in tests and CI.
- `ml/evaluation/metrics.py` and `scripts/evaluate_public_dataset.py`. Never invent AUC.
- SQLAlchemy models and JSON embeddings. Keep pgvector behind `VectorStore` and the Postgres URL check.
- Repository classes and `AnalyticsService.get_model_metrics` (null metrics when unlabeled).
- Frontend shell: `App.tsx` routes, `DashboardLayout`, `ui.tsx`, `api.ts`, Cytoscape `GraphPage`.
- Seed path: `scripts/seed_demo_data.py` + `scripts/_seed_impl.py`, with `is_demo=True`.
- Loaders: `ml/data/loaders/amazon.py`, `yelp.py`.
- Docs and `AGENTS.md` as the contract. Update them only when a public contract changes.

## Implementation plan

Work in this order. Each step keeps the hard rules in `AGENTS.md`. Do not start step N+1 by weakening analyze-route read-only behavior, fusion reweighting, or SQLite compatibility.

### Step 1 — Confirm the baseline on this machine

- Create a Windows venv, install `backend/requirements.txt` and `backend/requirements-dev.txt`, set `DATABASE_URL=sqlite:///:memory:` and `SIMILARITY_BACKEND=tfidf`, run `pytest` for `backend/tests` and `ml/tests`.
- `npm ci`, `npm run lint`, and `npm run build` in `frontend/`.
- Seed SQLite and hit `/health`, login, dashboard, and one analyze call. Record real pass/fail in this file’s “Verification log” section.
- Add a short PowerShell (or cross-platform) dev script only if `make` cannot run. Leave Makefile targets for CI and Unix.

### Step 2 — Make scoring use inputs it already accepts

- Feed the current review’s `rating` into behavior or a small rating feature when history exists, and document the rule when history does not.
- Compute graph risk for the reviewer/product neighborhood of the review under analysis, instead of assigning the global component score to every call.
- Pass stored or freshly computed similarity pairs into `build_review_graph` on `/graph` when pairs exist.
- Add ML tests for the new weight path. Add an API test that analyze still inserts zero rows.

### Step 3 — Optional explicit persistence (separate from analyze)

- Add a dedicated store endpoint or seed/job flag that calls the existing `MLService.analyze_and_store`. Analyze stays read-only.
- When storing, write `ReviewSimilarity` rows from `find_similar_reviews` and refresh `FraudCluster` from `analyze_graph` clusters.
- Write `AuditLog` rows for login, analyze, and store. Expose a viewer-safe recent-activity read if the dashboard should show it.
- Expose `GET` for a reviewer’s `BehaviorProfile` or stop writing the table at seed time. Prefer reading it if the seed already fills it.

### Step 4 — Schema changes go through migrations

- Initialize Alembic against the current models and generate a baseline revision matching `create_all`.
- Keep models free of the `vector` column type. Continue optional pgvector DDL inside `VectorStore`.
- CI stays on SQLite memory.

### Step 5 — Investigation UX on top of existing pages

- Add query params for review label, classification, and reviewer/product id on the list repositories and `api.ts`.
- Type the API client (`DashboardStats`, `AnalyzeResponse`, graph nodes) and remove `any` on analytics, settings, and analyzer.
- Hide analyze actions unless `user.role` is `admin` or `analyst`.
- Add Vitest coverage for auth redirect and analyzer “not saved” state. Wire `npm run test` into `make test` and CI.
- Verify Overview, Analyzer, Review detail, and Graph in the browser (click, pan, zoom) after UI edits.

### Step 6 — Evaluation honesty

- Keep analytics metrics null when `review_label` is absent.
- Document that sample-file AUC is fixture-scale. Run `scripts/evaluate_public_dataset.py` on `data/sample/` and paste the command output into docs only when the numbers come from that run.
- If a learned ranker is added later, train it offline in `ml/`, serialize an artifact outside git if large, and call it from fusion behind the same `PredictionResult` shape. Until that artifact exists, leave XGBoost and SHAP out of runtime imports. Remove them from `requirements.txt` or start using them in this step — do not leave a false dependency.

### Step 7 — Hardening (after the demo path is stable)

- Require non-default JWT secrets outside `APP_ENV=development`.
- Rate-limit `/auth/login` and `/predictions/analyze`.
- Avoid loading the full review table on every graph request once data grows (limit, or a cached graph payload written at seed/store time).
- Production Compose should not ship `reviewshield/reviewshield` database passwords.

## Suggested next development work

The Step 2 scoring gaps above remain candidates for future work; they are independent of the completed Chunk 3 features.

## Verification log

Updated after Chunk 3 implementation. Backend tests include the existing analyze read-only assertion.

| Check | Result | Notes |
|-------|--------|-------|
| Backend pytest | passed — 12 tests | `DATABASE_URL=sqlite:///:memory:`; includes trust, PDF, feedback RBAC/update/export, and analyze read-only coverage |
| ML pytest | passed as part of the 26-test combined run | `SIMILARITY_BACKEND=tfidf` |
| Frontend lint + build | passed | Oxlint reports two pre-existing `AuthContext.tsx` warnings; Vite warns Node 20.15.0 is below its 20.19+ requirement but production build completed |
| Seed + login + analyze | passed | Backend tests seed demo data; analyze response asserts `persisted=false` |
| Product trust/feedback UI | passed | Browser verified trust evidence, PDF endpoint response, feedback update/filter, and CSV export |
| Browser graph pan/zoom | not run | Graph UI was not changed in Chunk 3 |
