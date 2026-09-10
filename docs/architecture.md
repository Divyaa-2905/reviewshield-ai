# ReviewShield AI Architecture

## Overview

ReviewShield AI is a multi-modal fraud intelligence platform with a React frontend, FastAPI backend, PostgreSQL/SQLite database, and Python ML pipeline.

## Components

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI with JWT auth, repository pattern, service layer
- **Database**: SQLAlchemy ORM (SQLite for dev, PostgreSQL + pgvector for Docker)
- **ML Pipeline**: NLP, behavior, temporal, similarity, graph, fusion, explainability

## Data Flow

```
Review → Feature Extraction (5 modalities) → Fusion Model → Risk Score → Explanation → Dashboard
```

## API Structure

All authenticated endpoints under `/api/v1/` with role-based access control.
