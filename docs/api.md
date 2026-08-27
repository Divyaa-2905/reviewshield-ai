# API Documentation

See interactive docs at `http://localhost:8000/docs` when the backend is running.

## Authentication

`POST /api/v1/auth/login` — OAuth2 password flow, returns JWT

## Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/v1/analytics/dashboard` | GET | Viewer+ | Dashboard stats |
| `/api/v1/predictions/analyze` | POST | Analyst+ | Analyze review text |
| `/api/v1/reviews` | GET | Viewer+ | List reviews |
| `/api/v1/clusters` | GET | Viewer+ | Fraud clusters |
| `/api/v1/graph` | GET | Viewer+ | Graph data |

## Demo Credentials

- admin / admin123 (full access)
- analyst / analyst123 (analyze + investigate)
- viewer / viewer123 (read-only)
