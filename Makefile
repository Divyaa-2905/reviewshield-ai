.PHONY: help install install-backend install-frontend install-ml dev dev-backend dev-frontend seed test test-backend test-frontend test-ml lint lint-backend lint-frontend build build-frontend eval-amazon eval-yelp clean docker-up docker-down

help:
	@echo "ReviewShield AI - Development Commands"
	@echo ""
	@echo "  make install          Install all dependencies"
	@echo "  make install-ml       Optional Sentence-Transformers + FAISS"
	@echo "  make seed             Seed demo data (SQLite)"
	@echo "  make eval-amazon      Precision/recall/AUC on Amazon sample"
	@echo "  make eval-yelp        Precision/recall/AUC on Yelp sample"
	@echo "  make dev-backend      Run FastAPI backend"
	@echo "  make dev-frontend     Run Vite frontend"
	@echo "  make test             Run all tests"
	@echo "  make docker-up        Start with Docker Compose"
	@echo "  make clean            Remove build artifacts"

install: install-backend install-frontend

install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

install-ml:
	cd backend && . .venv/bin/activate && pip install -r requirements-ml.txt

seed:
	DATABASE_URL=sqlite:///./reviewshield.db PYTHONPATH=backend:. python scripts/seed_demo_data.py

dev-backend:
	cd backend && DATABASE_URL=sqlite:///../reviewshield.db PYTHONPATH=.. . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-ml

test-backend:
	cd backend && DATABASE_URL=sqlite:///:memory: . .venv/bin/activate && PYTHONPATH=..:. pytest -v

test-ml:
	cd backend && . .venv/bin/activate && PYTHONPATH=..:. SIMILARITY_BACKEND=tfidf pytest ../ml/tests -v

eval-amazon:
	SIMILARITY_BACKEND=tfidf PYTHONPATH=backend:. python3 scripts/evaluate_public_dataset.py data/sample/amazon_reviews.csv

eval-yelp:
	SIMILARITY_BACKEND=tfidf PYTHONPATH=backend:. python3 scripts/evaluate_public_dataset.py data/sample/yelp_reviews.jsonl --kind yelp

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

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	rm -rf backend/.venv backend/.pytest_cache backend/.ruff_cache reviewshield.db
	rm -rf frontend/node_modules frontend/dist
