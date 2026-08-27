.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend test test-backend test-frontend lint lint-backend lint-frontend build build-frontend clean

help:
	@echo "ReviewShield AI - Development Commands"
	@echo ""
	@echo "  make install          Install all dependencies"
	@echo "  make dev              Run backend and frontend (separate terminals)"
	@echo "  make dev-backend      Run FastAPI backend"
	@echo "  make dev-frontend     Run Vite frontend"
	@echo "  make test             Run all tests"
	@echo "  make lint             Run all linters"
	@echo "  make build            Build frontend for production"
	@echo "  make clean            Remove build artifacts"

install: install-backend install-frontend

install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && . .venv/bin/activate && pytest -v

test-frontend:
	cd frontend && npm run test -- --run

lint: lint-backend lint-frontend

lint-backend:
	cd backend && . .venv/bin/activate && ruff check app tests

lint-frontend:
	cd frontend && npm run lint

build: build-frontend

build-frontend:
	cd frontend && npm run build

clean:
	rm -rf backend/.venv backend/.pytest_cache backend/.ruff_cache
	rm -rf frontend/node_modules frontend/dist
