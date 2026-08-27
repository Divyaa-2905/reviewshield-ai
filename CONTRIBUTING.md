# Contributing to ReviewShield AI

Thank you for your interest in contributing to ReviewShield AI.

## Branch Naming

- `feat/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `chore/<short-description>` — tooling, CI, dependencies
- `docs/<short-description>` — documentation only
- `test/<short-description>` — test additions or fixes

## Commit Conventions

Use clear, imperative commit messages:

- `feat: add reviewer behavior profiling`
- `fix: handle missing review timestamps`
- `chore: configure GitHub CI`
- `docs: update API documentation`
- `test: add health endpoint tests`

## Pull Requests

1. Fork the repository and create a feature branch from `main`.
2. Keep changes focused and reasonably sized.
3. Run tests and linters before opening a PR.
4. Describe what changed, why, and how to test it.
5. Link related issues when applicable.

## Testing

```bash
make test
```

Or run backend and frontend tests separately:

```bash
make test-backend
make test-frontend
```

## Code Review Expectations

- Follow existing project structure and naming conventions.
- Add tests for important logic.
- Do not commit secrets or `.env` files.
- Mark incomplete functionality as TODO rather than faking results.
- Prefer small, reviewable commits over large uncontrolled changes.

## Development Setup

See [README.md](README.md) for installation and local development instructions.
