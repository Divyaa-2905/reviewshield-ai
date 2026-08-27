# Security

## Authentication

- JWT tokens with configurable expiry
- bcrypt password hashing
- Role-based access: admin, analyst, viewer

## Configuration

All secrets via environment variables. Never commit `.env` files.

## CORS

Configured via `CORS_ORIGINS` environment variable.

## Authorization

Server-side role enforcement on all protected endpoints.
