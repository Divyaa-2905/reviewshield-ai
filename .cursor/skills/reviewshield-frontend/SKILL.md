---
name: reviewshield-frontend
description: Change the ReviewShield React dashboard, especially GraphPage Cytoscape rendering, analyzer live results, and analytics metrics. Use when editing frontend pages, API client types, or graph visualization.
---

# ReviewShield frontend

## Graph

`frontend/src/pages/GraphPage.tsx` renders `/api/v1/graph` with Cytoscape.js. Keep click-to-inspect, pan, zoom, reviewer vs product styling, and a details pane. Do not replace it with a static list.

## Analyzer

`POST /predictions/analyze` returns a non-persisted payload. Show `persisted === false` and missing-history weight notes. Field names stay `text_risk`, `behavior_risk`, and so on.

## Analytics

Display precision, recall, ROC-AUC, and PR-AUC from `/api/v1/analytics/model`. Use `n/a` when a metric is null.

## Verification

After UI changes, open the affected route, exercise the control, and check a related page that reads the same API.
