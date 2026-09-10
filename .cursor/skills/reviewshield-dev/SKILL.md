---
name: reviewshield-dev
description: Develop, test, and change ReviewShield AI across frontend, backend, and ML. Use when editing this repo, adding features, fixing bugs, running tests, or following project conventions.
---

# ReviewShield development

Read [AGENTS.md](../../../AGENTS.md) first.

## Workflow

1. Identify the layer: `frontend/`, `backend/`, `ml/`, or `scripts/`.
2. Match existing patterns (repository + service on the backend, page + `api.ts` on the frontend).
3. Add or update tests in the same layer.
4. Run `make test` and the relevant linter.
5. If UI changed, verify the page in the browser.

## Commands

```bash
make install
make seed
make test
make lint
```

## Do not

- Insert rows from `POST /predictions/analyze`
- Commit `.env`, databases, or `data/raw/` dumps
- Report precision/AUC without labels
- Skip SQLite compatibility for Postgres-only types
