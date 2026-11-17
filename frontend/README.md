# ReviewShield AI 🛡️

ReviewShield AI is a full-stack, enterprise-grade **Review Fraud Intelligence & Analytics Platform** designed to detect, analyze, and mitigate fraudulent reviews, bot networks, and coordinated scam campaigns on e-commerce platforms. 

Built as a college major project, this application combines a **FastAPI backend**, an **advanced machine learning & network analysis pipeline (Scikit-learn, NetworkX)**, and a **modern React + Tailwind CSS frontend**.

---

## 🚀 Key Features

1. **Bulk Review Fraud Scanner:** Upload CSV files of product reviews for batch risk-scoring, data preview, validation, and filtered CSV exports.
2. **Explainable Fraud Detection:** Multi-signal risk assessment breaking down NLP, behavioral, temporal, similarity, and graph metrics without relying on a single signal.
3. **Coordinated Campaign Detection:** Identifies synchronized groups of suspicious reviewers and products using temporal patterns and graph network relationships.
4. **Model Performance Dashboard:** Evaluates true chronological holdout performance metrics (Accuracy, Precision, Recall, F1-Score, and Confusion Matrix).
5. **Product Trust Score:** Computes transparent product-level trust scores combining rating distributions, suspicious review ratios, and campaign involvement.
6. **Human Feedback & Correction System:** Allows authorized analysts to review, correct, and comment on stored predictions with role-based access control.
7. **PDF Investigation Reports:** Generates professional, downloadable investigation reports using ReportLab, complete with review statistics and visual charts.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy, SQLite, ReportLab, Scikit-learn, NetworkX
* **Frontend:** React 19, Vite, Tailwind CSS, TypeScript, Recharts, Lucide Icons, Cytoscape (Graph Visualizer)
* **Testing & Tools:** Pytest, Ruff, Git, GitHub

---

## 📂 Project Structure

```text
reviewshield-ai/
├── backend/
│   ├── app/
│   │   ├── routers/       # API endpoints (Scanner, Analytics, Campaigns, Feedback)
│   │   ├── services/      # Business logic & ML integration services
│   │   └── models/        # SQLAlchemy database models
│   └── tests/             # Backend & ML test suites
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI widgets and layout templates
│   │   └── pages/         # Dashboard pages (Overview, Analyzer, Batch CSV, Products, Verified Feedback, Campaigns, Analytics)
├── ml/                    # Machine learning pipelines & feature extractors
├── docs/                  # API documentation and project specifications
└── PROJECT_STATUS.md      # Development milestones and architecture logs 
