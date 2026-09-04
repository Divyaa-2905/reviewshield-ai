#!/usr/bin/env python3
"""Generate comprehensive ReviewShield AI project documentation PDF."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
    from fpdf import FPDF


OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "ReviewShield_AI_Complete_Documentation.pdf"


class DocPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "ReviewShield AI - Complete Project Documentation", align="R")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def cover(self) -> None:
        self.add_page()
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(15, 23, 42)
        self.ln(40)
        self.cell(0, 14, "ReviewShield AI", ln=True, align="C")
        self.set_font("Helvetica", "", 14)
        self.set_text_color(56, 189, 248)
        self.cell(0, 10, "Complete Project Documentation", ln=True, align="C")
        self.ln(8)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(80, 80, 80)
        self.multi_cell(
            0,
            7,
            "Multi-Modal AI System for Online Review Fraud and\n"
            "Coordinated Manipulation Detection",
            align="C",
        )
        self.ln(20)
        self.set_font("Helvetica", "", 10)
        items = [
            "Architecture & Technology Stack",
            "Installation & Deployment (Local + Docker)",
            "Complete API Reference (20+ endpoints)",
            "ML Pipeline (5 modalities + fusion + explainability)",
            "Database Schema (9 entities)",
            "Frontend Dashboard (9 pages)",
            "Authentication & Security (JWT + RBAC)",
            "Demo Data & Data Pipeline Scripts",
            "Testing, CI/CD & Makefile Commands",
            "Limitations & Demo Walkthrough",
        ]
        for item in items:
            self.set_x(self.l_margin)
            w = self.w - self.l_margin - self.r_margin
            self.multi_cell(w, 7, f"  -  {item}", align="C")
        self.ln(30)
        self.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y')}", align="C")
        self.ln(6)
        self.cell(0, 8, "GitHub: github.com/shivanshehehe/reviewshield-ai", align="C")
        self.ln(6)
        self.cell(0, 8, "Author: Shivanshi Sharma (shivanshehehe)", align="C")

    def h1(self, text: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, text, ln=True)
        self.set_draw_color(56, 189, 248)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def h2(self, text: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 58, 95)
        self.cell(0, 8, text, ln=True)
        self.ln(1)

    def h3(self, text: str) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(51, 65, 85)
        self.cell(0, 7, text, ln=True)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        w = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin)
        self.multi_cell(w, 5, text)
        self.ln(2)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        w = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin)
        self.multi_cell(w, 5, f"  * {text}")
        self.ln(1)

    def code(self, text: str) -> None:
        self.set_font("Courier", "", 8)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        for line in text.split("\n"):
            self.cell(0, 5, f"  {line}", ln=True, fill=True)
        self.ln(2)

    def table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None) -> None:
        if col_widths is None:
            w = 190 // len(headers)
            col_widths = [w] * len(headers)
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h[:30], border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 7)
        self.set_text_color(30, 30, 30)
        fill = False
        for row in rows:
            if self.get_y() > 270:
                self.add_page()
            if fill:
                self.set_fill_color(248, 250, 252)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, str(cell)[:40], border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(2)


def build_pdf() -> Path:
    pdf = DocPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.cover()

    # 1. Overview
    pdf.add_page()
    pdf.h1("1. Project Overview")
    pdf.body(
        "ReviewShield AI is an end-to-end AI fraud-intelligence platform that detects suspicious "
        "online reviews by combining five evidence modalities: NLP text analysis, reviewer "
        "behaviour profiling, temporal pattern detection, semantic similarity analysis, and "
        "graph-based network intelligence.\n\n"
        "The system produces a fraud probability score (0.0 to 1.0), a classification "
        "(Genuine / Suspicious / Potentially Fake), modality-level risk scores, and a "
        "human-readable explanation. It is designed as an evidence-based risk assessment tool "
        "for academic demonstration, portfolio projects, and investigation support - NOT as "
        "definitive proof of fraud."
    )
    pdf.h2("1.1 Key Capabilities")
    for cap in [
        "Review classification with multi-modal evidence fusion",
        "NLP-based linguistic feature extraction",
        "Reviewer behaviour profiling and anomaly detection",
        "Temporal burst and synchronized activity detection",
        "Semantic similarity (duplicate/paraphrase detection via TF-IDF)",
        "Reviewer-product graph analysis (NetworkX)",
        "Explainable AI with human-readable evidence",
        "Investigation dashboard with 9 pages",
        "JWT authentication with role-based access control",
        "Deterministic demo data for reproducible demonstrations",
    ]:
        pdf.bullet(cap)

    pdf.h2("1.2 Repository")
    pdf.body(
        "GitHub: https://github.com/shivanshehehe/reviewshield-ai\n"
        "License: MIT\n"
        "Model Version: demo-v0.1.0"
    )

    # 2. Architecture
    pdf.add_page()
    pdf.h1("2. System Architecture")
    pdf.h2("2.1 Data Flow")
    pdf.code(
        "Review Input\n"
        "  -> NLP Analysis (linguistic features)\n"
        "  -> Behaviour Profiling (reviewer metrics)\n"
        "  -> Temporal Analysis (burst detection)\n"
        "  -> Semantic Similarity (TF-IDF cosine)\n"
        "  -> Graph Intelligence (NetworkX)\n"
        "  -> Feature Fusion (weighted combination)\n"
        "  -> Risk Score (0.0 - 1.0)\n"
        "  -> Explainability (evidence generation)\n"
        "  -> Dashboard (React frontend)"
    )
    pdf.h2("2.2 Technology Stack")
    pdf.table(
        ["Layer", "Technologies"],
        [
            ["Frontend", "React 19, TypeScript, Vite, Tailwind CSS, Recharts"],
            ["Backend", "Python, FastAPI, SQLAlchemy, Pydantic, JWT"],
            ["ML", "scikit-learn, NetworkX, pandas, numpy"],
            ["Database", "SQLite (dev) / PostgreSQL 15 (Docker)"],
            ["DevOps", "Docker Compose, GitHub Actions, Makefile"],
            ["Testing", "pytest, Vitest, Ruff, oxlint"],
        ],
        [40, 150],
    )
    pdf.h2("2.3 Project Structure")
    pdf.code(
        "reviewshield-ai/\n"
        "  frontend/          React dashboard (9 pages)\n"
        "  backend/app/       FastAPI (api, core, models, repos, services)\n"
        "  ml/                NLP, behavior, temporal, similarity, graph, fusion\n"
        "  scripts/           Data pipeline + demo seeding\n"
        "  docs/              Architecture, API, methodology docs\n"
        "  .github/workflows/ CI pipeline\n"
        "  docker-compose.yml PostgreSQL + backend + frontend"
    )

    # 3. Installation
    pdf.add_page()
    pdf.h1("3. Installation & Setup")
    pdf.h2("3.1 Prerequisites")
    pdf.bullet("Python 3.11 or higher")
    pdf.bullet("Node.js 20 or higher")
    pdf.bullet("Git")
    pdf.bullet("Optional: Docker for containerized deployment")

    pdf.h2("3.2 Local Setup")
    pdf.code(
        "git clone https://github.com/shivanshehehe/reviewshield-ai.git\n"
        "cd reviewshield-ai\n"
        "cp .env.example .env\n"
        "make install\n"
        "make seed"
    )
    pdf.h2("3.3 Run Locally")
    pdf.code(
        "# Terminal 1 - Backend\n"
        "make dev-backend\n\n"
        "# Terminal 2 - Frontend\n"
        "make dev-frontend"
    )
    pdf.table(
        ["Service", "URL"],
        [
            ["Frontend Dashboard", "http://localhost:5173"],
            ["Backend API", "http://localhost:8000"],
            ["Swagger API Docs", "http://localhost:8000/docs"],
            ["ReDoc", "http://localhost:8000/redoc"],
            ["Health Check", "http://localhost:8000/health"],
        ],
        [60, 130],
    )

    pdf.h2("3.4 Docker Deployment")
    pdf.code("docker compose up --build")
    pdf.table(
        ["Service", "URL", "Details"],
        [
            ["Frontend", "http://localhost:3000", "Nginx serves React build"],
            ["Backend", "http://localhost:8000", "FastAPI + Uvicorn"],
            ["PostgreSQL", "localhost:5432", "User/Pass: reviewshield"],
        ],
        [35, 55, 100],
    )

    # 4. Environment Variables
    pdf.add_page()
    pdf.h1("4. Environment Variables")
    pdf.table(
        ["Variable", "Default", "Description"],
        [
            ["DATABASE_URL", "sqlite:///./reviewshield.db", "Database connection string"],
            ["SECRET_KEY", "change-me-in-production", "Application secret key"],
            ["JWT_SECRET_KEY", "change-me-in-production", "JWT token signing key"],
            ["JWT_ALGORITHM", "HS256", "JWT signing algorithm"],
            ["ACCESS_TOKEN_EXPIRE_MINUTES", "30", "Token expiry in minutes"],
            ["CORS_ORIGINS", "localhost:5173,3000", "Allowed frontend origins"],
            ["ML_MODEL_VERSION", "demo-v0.1.0", "Active model version tag"],
            ["ML_DEVICE", "cpu", "ML compute device label"],
            ["VITE_API_BASE_URL", "http://localhost:8000", "Frontend API base URL"],
        ],
        [55, 55, 80],
    )

    # 5. Authentication
    pdf.add_page()
    pdf.h1("5. Authentication & Security")
    pdf.body(
        "ReviewShield AI uses JWT (JSON Web Token) authentication with bcrypt password hashing. "
        "All protected API endpoints require a Bearer token in the Authorization header."
    )
    pdf.h2("5.1 Demo Credentials")
    pdf.table(
        ["Role", "Username", "Password", "Permissions"],
        [
            ["Admin", "admin", "admin123", "Full access + user management"],
            ["Analyst", "analyst", "analyst123", "Analyze reviews + investigate"],
            ["Viewer", "viewer", "viewer123", "Read-only dashboard access"],
        ],
        [25, 30, 35, 100],
    )
    pdf.h2("5.2 Login Example")
    pdf.code(
        'curl -X POST http://localhost:8000/api/v1/auth/login \\\n'
        '  -H "Content-Type: application/x-www-form-urlencoded" \\\n'
        '  -d "username=admin&password=admin123"\n\n'
        "# Response:\n"
        '# {"access_token": "eyJ...", "token_type": "bearer"}\n\n'
        'curl http://localhost:8000/api/v1/analytics/dashboard \\\n'
        '  -H "Authorization: Bearer <token>"'
    )
    pdf.h2("5.3 Role-Based Access Control (RBAC)")
    pdf.table(
        ["Role", "Can Access"],
        [
            ["admin", "All endpoints including user CRUD"],
            ["analyst", "All read endpoints + POST /predictions/analyze"],
            ["viewer", "All read/list/get endpoints only"],
        ],
        [30, 160],
    )

    # 6. Complete API Reference
    pdf.add_page()
    pdf.h1("6. Complete API Reference")
    pdf.body("Base URL: http://localhost:8000 | Prefix: /api/v1 | Auth: Bearer JWT")

    pdf.h2("6.1 System Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [["GET", "/health", "None", "Service health check"]],
        [20, 55, 25, 90],
    )

    pdf.h2("6.2 Authentication Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["POST", "/api/v1/auth/login", "None", "Login, returns JWT token"],
            ["GET", "/api/v1/auth/me", "Any", "Current user profile"],
            ["POST", "/api/v1/auth/users", "Admin", "Create new user"],
            ["GET", "/api/v1/auth/users", "Admin", "List all users"],
        ],
        [18, 55, 22, 95],
    )

    pdf.h2("6.3 Review Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/reviews", "Viewer+", "List reviews (paginated)"],
            ["GET", "/api/v1/reviews/{review_id}", "Viewer+", "Get review by external ID"],
        ],
        [18, 60, 22, 90],
    )

    pdf.h2("6.4 Reviewer Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/reviewers", "Viewer+", "List reviewers (paginated)"],
            ["GET", "/api/v1/reviewers/{reviewer_id}", "Viewer+", "Get reviewer details"],
        ],
        [18, 60, 22, 90],
    )

    pdf.h2("6.5 Product Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/products", "Viewer+", "List products (paginated)"],
            ["GET", "/api/v1/products/{product_id}", "Viewer+", "Get product details"],
        ],
        [18, 60, 22, 90],
    )

    pdf.add_page()
    pdf.h2("6.6 Prediction Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/predictions", "Viewer+", "List all predictions"],
            ["GET", "/api/v1/predictions/review/{id}", "Viewer+", "Prediction for a review"],
            ["POST", "/api/v1/predictions/analyze", "Analyst+", "Analyze review text live"],
        ],
        [18, 65, 22, 85],
    )
    pdf.h3("Analyze Request Body (JSON):")
    pdf.code(
        '{\n'
        '  "review_text": "Amazing product! Best ever!",\n'
        '  "rating": 5,\n'
        '  "reviewer_id": "rev-suspicious-01",\n'
        '  "review_timestamp": "2025-01-15T10:00:00Z"\n'
        '}'
    )
    pdf.h3("Prediction Response Fields:")
    pdf.table(
        ["Field", "Type", "Description"],
        [
            ["fraud_probability", "float 0-1", "Overall fraud risk score"],
            ["classification", "string", "Genuine / Suspicious / Potentially Fake"],
            ["model_version", "string", "Model version used"],
            ["text_risk", "float", "NLP modality risk"],
            ["behavior_risk", "float", "Behaviour modality risk"],
            ["temporal_risk", "float", "Temporal modality risk"],
            ["similarity_risk", "float", "Similarity modality risk"],
            ["graph_risk", "float", "Graph modality risk"],
            ["explanation", "string", "Human-readable evidence"],
        ],
        [45, 30, 115],
    )

    pdf.h2("6.7 Similarity Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [["GET", "/api/v1/similarity/review/{id}", "Viewer+", "Similar reviews for a review"]],
        [18, 65, 22, 85],
    )

    pdf.h2("6.8 Cluster Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/clusters", "Viewer+", "List fraud clusters"],
            ["GET", "/api/v1/clusters/{cluster_id}", "Viewer+", "Get cluster details"],
        ],
        [18, 60, 22, 90],
    )

    pdf.h2("6.9 Analytics Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/analytics/dashboard", "Viewer+", "Dashboard statistics"],
            ["GET", "/api/v1/analytics/model", "Viewer+", "Model performance metrics"],
        ],
        [18, 65, 22, 85],
    )

    pdf.h2("6.10 Graph & Model Endpoints")
    pdf.table(
        ["Method", "Path", "Auth", "Description"],
        [
            ["GET", "/api/v1/graph", "Viewer+", "Reviewer-product graph data"],
            ["GET", "/api/v1/models/info", "Viewer+", "Model version and status"],
        ],
        [18, 55, 22, 95],
    )

    pdf.h2("6.11 Pagination")
    pdf.body(
        "All list endpoints support query parameters: page (default 1, min 1) and "
        "page_size (default 20, max 100). Response includes: items, total, page, page_size, pages."
    )

    # 7. Database Schema
    pdf.add_page()
    pdf.h1("7. Database Schema (9 Entities)")
    pdf.h2("7.1 users")
    pdf.body("id, username (unique), email (unique), hashed_password (bcrypt), role (admin/analyst/viewer), is_active, created_at, updated_at")
    pdf.h2("7.2 reviewers")
    pdf.body("id, reviewer_id (unique), account_created_at, total_reviews, average_rating, rating_variance, five_star_percentage, product_count, review_frequency, suspicious_score, is_demo, created_at, updated_at")
    pdf.h2("7.3 products")
    pdf.body("id, product_id (unique), name, category, seller, is_demo, created_at, updated_at")
    pdf.h2("7.4 reviews")
    pdf.body("id, review_id (unique), reviewer_id (FK), product_id (FK), rating (1-5), review_text, review_timestamp, verified_purchase, review_label (genuine/fake), is_demo, created_at")
    pdf.h2("7.5 predictions")
    pdf.body("id, review_id (FK), fraud_probability, classification, model_version, text_risk, behavior_risk, temporal_risk, similarity_risk, graph_risk, explanation, created_at")
    pdf.h2("7.6 review_similarities")
    pdf.body("id, review_a_id (FK), review_b_id (FK), similarity_score, similarity_type (exact/semantic), same_product, same_reviewer, time_difference_hours, created_at")
    pdf.h2("7.7 behavior_profiles")
    pdf.body("id, reviewer_id (FK unique), behavioural_metrics (JSON), temporal_metrics (JSON), rating_metrics (JSON), anomaly_metrics (JSON), observations, created_at, updated_at")
    pdf.h2("7.8 fraud_clusters")
    pdf.body("id, cluster_id (unique), risk_score, reviewer_count, product_count, review_count, reviewers (JSON), products (JSON), temporal_evidence (JSON), similarity_evidence (JSON), graph_metrics (JSON), explanation, created_at")
    pdf.h2("7.9 audit_logs")
    pdf.body("id, user_id (FK), action, metadata (JSON), created_at")

    # 8. ML Pipeline
    pdf.add_page()
    pdf.h1("8. Machine Learning Pipeline")
    pdf.h2("8.1 Inference Flow (MLService)")
    pdf.code(
        "1. Retrieve review + reviewer/product context\n"
        "2. Extract NLP features (linguistic analysis)\n"
        "3. Profile reviewer behaviour\n"
        "4. Analyze temporal patterns\n"
        "5. Find semantic similarities (TF-IDF)\n"
        "6. Build and analyze reviewer-product graph\n"
        "7. Fuse modality scores (weighted combination)\n"
        "8. Classify: Genuine / Suspicious / Potentially Fake\n"
        "9. Generate human-readable explanation\n"
        "10. Store prediction with model version"
    )

    pdf.h2("8.2 NLP Module (ml/nlp/linguistic_features.py)")
    pdf.body("Functions: analyze_text(), text_risk_score()")
    pdf.bullet("Features: text_length, word_count, sentence_count, lexical_diversity")
    pdf.bullet("Features: avg_word_length, caps_ratio, exclamation_count")
    pdf.bullet("Features: promotional_language, repeated_phrase_ratio, sentiment_proxy")
    pdf.bullet("Risk signals: high promotional language, low diversity, excessive caps")

    pdf.h2("8.3 Behaviour Module (ml/behavior/profiler.py)")
    pdf.body("Function: analyze_reviewer_behavior(reviews, account_created_at)")
    pdf.bullet("Metrics: total_reviews, average_rating, rating_variance, five_star_percentage")
    pdf.bullet("Metrics: product_diversity, reviews_per_day, median/min interval hours")
    pdf.bullet("Detects: unusually high five-star ratio, high volume, short intervals")

    pdf.h2("8.4 Temporal Module (ml/temporal/analyzer.py)")
    pdf.body("Functions: analyze_temporal_patterns(), detect_synchronized_activity()")
    pdf.bullet("Detects: review bursts within configurable time windows (default 24h)")
    pdf.bullet("Detects: rapid succession posting, sustained high-frequency patterns")
    pdf.bullet("Detects: synchronized activity across reviewer groups")

    pdf.h2("8.5 Similarity Module (ml/similarity/engine.py)")
    pdf.body("Uses TF-IDF vectorization (max 5000 features, 1-2 gram) + cosine similarity")
    pdf.bullet("build_similarity_index() - builds global corpus index")
    pdf.bullet("find_similar_reviews() - nearest neighbour search")
    pdf.bullet("pairwise_similarity_risk() - risk from max similarity + match count")
    pdf.bullet("compute_all_pairs_efficient() - batch pair detection above threshold")
    pdf.bullet("Types: exact (>0.95 score) or semantic (>0.5 score)")

    pdf.h2("8.6 Graph Module (ml/graph/intelligence.py)")
    pdf.body("Uses NetworkX for reviewer-product bipartite graph analysis")
    pdf.bullet("build_review_graph() - nodes: reviewers + products, edges: reviews")
    pdf.bullet("analyze_graph() - connected components, degree analysis, cluster extraction")
    pdf.bullet("graph_to_frontend() - converts to nodes/edges for dashboard visualization")
    pdf.bullet("Detects: high connectivity reviewers, suspicious connected components")

    pdf.add_page()
    pdf.h2("8.7 Fusion Module (ml/fusion/model.py)")
    pdf.body("Functions: fuse_modalities(), classify_probability()")
    pdf.table(
        ["Modality", "Weight"],
        [
            ["Text (NLP)", "20%"],
            ["Behaviour", "25%"],
            ["Temporal", "20%"],
            ["Similarity", "20%"],
            ["Graph", "15%"],
        ],
        [80, 110],
    )
    pdf.table(
        ["Probability Range", "Classification"],
        [
            ["< 0.40", "Genuine"],
            ["0.40 - 0.70", "Suspicious"],
            [">= 0.70", "Potentially Fake"],
        ],
        [80, 110],
    )

    pdf.h2("8.8 Explainability (ml/explainability/explainer.py)")
    pdf.body(
        "Functions: build_explanation(), explain_prediction()\n"
        "Generates evidence from actual modality observations and similarity matches. "
        "Never invents explanations. Includes fraud probability, classification, top evidence "
        "items, and model version."
    )
    pdf.h3("Example Explanation Output:")
    pdf.code(
        "Fraud probability: 0.72\n"
        "Classification: Potentially Fake\n"
        "Evidence:\n"
        "- Reviewer has an unusually high five-star ratio.\n"
        "- High review concentration detected within a short time window.\n"
        "- Review has high semantic similarity with 3 other review(s).\n"
        "Model version: demo-v0.1.0"
    )

    # 9. Frontend Dashboard
    pdf.add_page()
    pdf.h1("9. Frontend Dashboard (9 Pages)")
    pdf.body("Stack: React 19, TypeScript, Vite, Tailwind CSS, Recharts, React Router, Lucide Icons")
    pdf.table(
        ["Route", "Page", "Functionality"],
        [
            ["/login", "Login", "JWT authentication form"],
            ["/", "Overview", "Stats cards + classification bar chart"],
            ["/analyzer", "Analyzer", "Submit review text for live fraud analysis"],
            ["/reviews", "Investigation", "Browse reviews with risk badges"],
            ["/reviews/:id", "Review Detail", "Full prediction, modalities, similar reviews"],
            ["/reviewers", "Reviewers", "Risk intelligence table"],
            ["/products", "Products", "Product intelligence cards"],
            ["/clusters", "Clusters", "Fraud cluster cards with evidence"],
            ["/graph", "Graph Explorer", "Reviewer-product network visualization"],
            ["/analytics", "Analytics", "Model metrics and modality averages"],
            ["/settings", "Settings", "API health + model info + demo credentials"],
        ],
        [30, 35, 125],
    )

    # 10. Demo Data
    pdf.add_page()
    pdf.h1("10. Demo Data")
    pdf.body("Command: make seed | Seed: 42 (deterministic) | All records: is_demo=True")
    pdf.h2("10.1 Demo Products (5)")
    pdf.table(
        ["ID", "Name", "Category"],
        [
            ["prod-001", "Wireless Earbuds Pro", "electronics"],
            ["prod-002", "Organic Face Cream", "beauty"],
            ["prod-003", "Smart Fitness Band", "electronics"],
            ["prod-004", "Kitchen Blender XL", "home"],
            ["prod-005", "LED Desk Lamp", "home"],
        ],
        [30, 80, 80],
    )
    pdf.h2("10.2 Demo Reviewers (8)")
    pdf.table(
        ["ID", "Profile", "Suspicious Score"],
        [
            ["rev-normal-01", "Normal reviewer", "0.10"],
            ["rev-normal-02", "Normal reviewer", "0.05"],
            ["rev-active-01", "Active reviewer", "0.30"],
            ["rev-suspicious-01", "Promotional text", "0.85"],
            ["rev-suspicious-02", "Promotional text", "0.90"],
            ["rev-coord-01", "Coordinated burst", "0.80"],
            ["rev-coord-02", "Coordinated burst", "0.82"],
            ["rev-coord-03", "Coordinated burst", "0.78"],
        ],
        [40, 80, 70],
    )
    pdf.h2("10.3 Demo Reviews (24 total)")
    pdf.table(
        ["Category", "Count", "Label", "Pattern"],
        [
            ["Genuine", "8", "genuine", "Normal review templates"],
            ["Suspicious", "6", "fake", "Promotional language"],
            ["Paraphrase pairs", "4", "fake", "Near-duplicate reviews"],
            ["Coordinated burst", "6", "fake", "Same-day burst on prod-005"],
        ],
        [40, 20, 30, 100],
    )
    pdf.body("Also generates: similarity pairs, fraud clusters, predictions, behavior profiles.")

    # 11. Scripts & Makefile
    pdf.add_page()
    pdf.h1("11. Scripts & Makefile Commands")
    pdf.h2("11.1 Makefile Commands")
    pdf.table(
        ["Command", "Description"],
        [
            ["make install", "Install backend + frontend dependencies"],
            ["make seed", "Seed deterministic demo data"],
            ["make dev-backend", "Start FastAPI on port 8000"],
            ["make dev-frontend", "Start Vite on port 5173"],
            ["make test", "Run backend + ML tests"],
            ["make lint", "Run Ruff + oxlint"],
            ["make build", "Production frontend build"],
            ["make docker-up", "Start Docker Compose stack"],
            ["make docker-down", "Stop Docker Compose"],
            ["make clean", "Remove venv, caches, node_modules, db"],
        ],
        [50, 140],
    )
    pdf.h2("11.2 Data Pipeline Scripts")
    pdf.table(
        ["Script", "Purpose"],
        [
            ["scripts/seed_demo_data.py", "Seed all demo data"],
            ["scripts/validate_dataset.py", "Validate CSV/JSON/Parquet dataset"],
            ["scripts/prepare_dataset.py", "Normalize dataset to Parquet"],
            ["scripts/generate_features.py", "Extract NLP features from dataset"],
            ["ml/evaluation/evaluate.py", "Evaluate model on demo predictions"],
            ["scripts/push-to-github.sh", "Create and push GitHub repo"],
        ],
        [70, 120],
    )
    pdf.h2("11.3 Required Dataset Columns")
    pdf.body("review_id, reviewer_id, product_id, rating, review_text, review_timestamp")
    pdf.body("Optional: review_label, verified_purchase, account_created_at")

    # 12. Testing & CI
    pdf.add_page()
    pdf.h1("12. Testing & CI/CD")
    pdf.h2("12.1 Backend Tests (4 tests)")
    pdf.bullet("test_health_endpoint_returns_ok - GET /health returns ok")
    pdf.bullet("test_login_and_dashboard - seed, login, dashboard stats > 0")
    pdf.bullet("test_analyze_review_requires_auth - analyze without token returns 401")
    pdf.h2("12.2 ML Tests (5 tests)")
    pdf.bullet("test_nlp_features - promotional text yields risk > 0")
    pdf.bullet("test_behavior_profiling - high volume reviewer yields risk > 0")
    pdf.bullet("test_temporal_analysis - rapid posting pattern detection")
    pdf.bullet("test_fusion_model - weighted fusion output in valid range")
    pdf.bullet("test_classify_probability - threshold boundary checks")
    pdf.h2("12.3 CI Pipeline (GitHub Actions)")
    pdf.body("Triggers: push/PR to main branch")
    pdf.bullet("Backend job: Python 3.11, Ruff lint, pytest (in-memory SQLite)")
    pdf.bullet("Frontend job: Node 20, oxlint, TypeScript build")

    # 13. Docker
    pdf.h1("13. Docker Architecture")
    pdf.table(
        ["Service", "Image", "Port", "Health Check"],
        [
            ["db", "postgres:15-alpine", "5432", "pg_isready"],
            ["backend", "Python 3.11-slim build", "8000", "GET /health"],
            ["frontend", "Node 20 build + nginx", "3000", "wget localhost"],
        ],
        [30, 55, 25, 80],
    )
    pdf.body("Frontend nginx proxies /api/ requests to backend:8000")

    # 14. Limitations
    pdf.add_page()
    pdf.h1("14. Limitations & Assumptions")
    for lim in [
        "All data is DEMO DATA (synthetic, seed=42) - not real-world statistics",
        "Risk scores are estimates, NOT proof of fraud",
        "TF-IDF similarity used instead of transformer embeddings (CPU-friendly)",
        "No real-time streaming ingestion",
        "Not validated on production-scale datasets",
        "XGBoost/SHAP listed in dependencies but not active in demo pipeline",
        "Single suspicious signal does NOT confirm fraud",
        "System must not be used for legal evidence or automated conviction",
    ]:
        pdf.bullet(lim)

    # 15. Demo Walkthrough
    pdf.h1("15. Demo Walkthrough (Viva / Interview)")
    steps = [
        "Start: make dev-backend + make dev-frontend",
        "Open http://localhost:5173 and login as admin / admin123",
        "Overview: view classification distribution and risk statistics",
        "Analyzer: paste suspicious review text, click Analyze, view risk gauge",
        "Investigation: browse reviews with fraud classifications",
        "Reviewers: inspect high-risk reviewers and suspicious scores",
        "Clusters: view coordinated fraud cluster evidence",
        "Graph: explore reviewer-product network connections",
        "Analytics: view model performance and modality averages",
        "Settings: confirm API status and model version demo-v0.1.0",
        "API: demonstrate /docs Swagger UI and /health endpoint",
    ]
    for i, step in enumerate(steps, 1):
        pdf.bullet(f"Step {i}: {step}")

    pdf.ln(10)
    pdf.h1("16. Quick Reference")
    pdf.table(
        ["Item", "Value"],
        [
            ["GitHub", "github.com/shivanshehehe/reviewshield-ai"],
            ["Frontend (local)", "http://localhost:5173"],
            ["Backend (local)", "http://localhost:8000"],
            ["API Docs", "http://localhost:8000/docs"],
            ["Login", "admin / admin123"],
            ["Model Version", "demo-v0.1.0"],
            ["Demo Reviews", "24 (synthetic)"],
            ["Modalities", "NLP, Behaviour, Temporal, Similarity, Graph"],
            ["License", "MIT"],
        ],
        [50, 140],
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF generated: {path}")
    print(f"Size: {path.stat().st_size / 1024:.1f} KB")
