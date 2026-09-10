# ReviewShield AI — Agent Guide

This file is the starter contract for every coding agent working in this repository. Read it before editing. Prefer the project skills in `.cursor/skills/` for deeper workflows.

## What this project is

ReviewShield AI is a multi-modal review-fraud investigation system:

- `frontend/` — React 19 + Vite dashboard
- `backend/` — FastAPI + SQLAlchemy + JWT
- `ml/` — NLP, behavior, temporal, similarity, graph, fusion, evaluation
- `scripts/` — seeding, dataset prep, evaluation
- `data/sample/` — checked-in Amazon/Yelp fixtures for eval

Risk scores are estimates, not proof of fraud. Never invent live metrics or pretend unlabeled data is labeled.

## Quick commands

```bash
make install
make seed
make dev-backend    # terminal 1
make dev-frontend   # terminal 2
make test
make lint
```

Optional similarity stack (Sentence-Transformers + FAISS):

```bash
pip install -r backend/requirements-ml.txt
# SIMILARITY_BACKEND=sentence-transformers
```

Public-dataset eval:

```bash
python scripts/prepare_public_datasets.py data/sample/amazon_reviews.csv --kind amazon
python scripts/evaluate_public_dataset.py data/sample/amazon_reviews.csv
python scripts/evaluate_public_dataset.py data/sample/yelp_reviews.jsonl --kind yelp
```

Login: `admin/admin123`, `analyst/analyst123`, `viewer/viewer123`.

## Hard rules

1. **`POST /api/v1/predictions/analyze` is read-only.** Score in memory. Do not insert `Review` or `Prediction` rows. Persistence belongs to seed jobs or an explicit store endpoint.
2. **Missing reviewer history must reweight fusion.** Do not let zero behavior/temporal scores silently dilute text, similarity, and graph evidence. Use `fuse_modalities(..., history_available=False)`.
3. **Do not fake evaluation.** Precision, recall, F1, ROC-AUC, and PR-AUC require labels. If labels are missing, return `null` metrics and say so.
4. **Similarity backends must degrade.** Prefer Sentence-Transformers + FAISS when installed; fall back to TF-IDF + numpy. Tests and CI set `SIMILARITY_BACKEND=tfidf`.
5. **SQLite must keep working.** pgvector is optional Postgres persistence. SQLAlchemy models cannot depend on the `vector` type.
6. **No secrets in git.** Use `.env.example`. Do not commit `.env`, credentials, or downloaded raw datasets.
7. **UI changes need verification.** Exercise the changed page, not just a screenshot. Graph explorer must remain interactive (click, pan, zoom).
8. **Keep demo data labeled as demo.** `is_demo=True` on seeded rows. Public Amazon/Yelp fixtures live under `data/sample/`.

## Where to change what

| Task | Start here |
|------|------------|
| Fusion weights | `ml/fusion/model.py` |
| Embeddings / FAISS | `ml/similarity/` |
| pgvector persistence | `backend/app/services/vector_store.py` |
| Analyze API | `backend/app/api/routes.py` |
| Graph UI | `frontend/src/pages/GraphPage.tsx` |
| Amazon/Yelp ingest | `ml/data/loaders/amazon.py`, `yelp.py` |
| Precision/recall/AUC | `ml/evaluation/metrics.py` |

## Testing expectations

- Backend API tests: `backend/tests/`
- ML tests: `ml/tests/` (fusion, similarity, loaders, eval)
- Frontend: `npm run lint` and `npm run build` after UI changes
- New behavior needs a test. Analyze-route changes must assert no DB insert.

## Agent skills

- [reviewshield-dev](.cursor/skills/reviewshield-dev/SKILL.md) — repo workflow, commands, PR hygiene
- [reviewshield-ml](.cursor/skills/reviewshield-ml/SKILL.md) — modalities, fusion, similarity backends
- [reviewshield-eval](.cursor/skills/reviewshield-eval/SKILL.md) — Amazon/Yelp ingest and metrics
- [reviewshield-frontend](.cursor/skills/reviewshield-frontend/SKILL.md) — dashboard and Cytoscape graph

## Done means

- Tests covering the change pass
- Lint is clean on touched Python/TS
- Docs updated if a public contract changed (`docs/`, README limitations, this file)
- Frontend behavior verified when UI changed
