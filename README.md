# Data Analyst + ML Agent

[![CI](https://github.com/sarathdunna/AI-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/sarathdunna/AI-Agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![React + TypeScript](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-61dafb)

A full-stack M.Tech major project: an AI-assisted data analysis and machine
learning platform. Upload a dataset, profile and clean it, explore it (EDA,
charts, natural-language Q&A, SQL), train and compare ML models, get
explainability, make predictions, and generate PDF reports — all backed by a
FastAPI + Pandas/DuckDB/scikit-learn backend and a React + TypeScript +
Tailwind frontend. An optional Anthropic Claude integration adds natural-
language explanations on top of deterministic, code-computed results; every
core feature works without any LLM key.

## Tech stack

- **Backend**: Python, FastAPI, Pydantic, Uvicorn, Pandas, NumPy, DuckDB,
  openpyxl, scikit-learn, joblib, ChromaDB-free TF-IDF RAG, SQLite, reportlab.
- **Frontend**: React, Vite, TypeScript, Tailwind CSS, Recharts, Lucide icons.
- **LLM**: Anthropic Claude via a modular provider abstraction
  (`backend/app/services/llm_provider.py`) — optional.

## Prerequisites

- Python 3.11+ (tested with 3.12)
- Node.js 18+ and npm
- (Optional) An Anthropic API key for AI-generated explanations

## Local setup

### 1. Clone the project

```bash
git clone https://github.com/sarathdunna/AI-Agent.git
cd AI-Agent
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and optionally set ANTHROPIC_API_KEY=sk-ant-...
```

`.env` lives at the project root and is read by the backend. Key settings:

```
ANTHROPIC_API_KEY=          # leave blank to run without AI explanations
LLM_PROVIDER=anthropic
LLM_MODEL=claude-opus-5-5    # Claude model used for explanations and NL->SQL
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
MAX_UPLOAD_MB=25
```

### 3. Backend setup

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now live at http://localhost:8000 (docs at `/docs`).

### 4. Frontend setup

In a new terminal:

**Windows / macOS / Linux (same commands):**
```bash
cd frontend
cp .env.example .env   # sets VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### 5. Generate sample datasets (optional, already included)

```bash
cd sample_data
python generate_samples.py
```

This produces `customer_churn_sample.csv` (classification demo) and
`sales_sample.csv` (regression demo).

### 6. Run backend tests

```bash
cd backend
# with the virtual environment activated (see step 3):
python -m pytest
```

The same tests, plus a frontend production build, run on every push and pull
request via GitHub Actions (`.github/workflows/ci.yml`).

## Docker Compose (alternative to manual setup)

```bash
cp .env.example .env
docker compose up --build
```

Backend: http://localhost:8000, Frontend: http://localhost:5173.

## Project structure

```
backend/app/
  core/        settings
  api/         FastAPI routers
  agents/      profiling, cleaning, EDA, visualization, query, SQL, pandas, insight agents
  ml/          problem identification, algorithm selection, preprocessing, training,
               evaluation, tuning, explainability, prediction
  analytics/   BI dashboard KPIs
  rag/         local TF-IDF knowledge base + markdown docs
  services/    dataset I/O, LLM provider abstraction, PDF report generator
  database/    SQLite metadata store
  utils/       security (safe filenames, SQL allowlist)
frontend/src/
  pages/       one file per route/page
  components/  shared UI (skeletons, empty states)
  charts/      Recharts chart renderer
  services/    typed fetch API client
  hooks/       dataset + toast context providers
  types/       shared TypeScript types
sample_data/   synthetic demo CSVs + generator script
docs/          project docs for the M.Tech report and demo
```

## Known limitations

- The RAG knowledge agent uses TF-IDF (scikit-learn) rather than a heavy
  embedding model, to keep the project dependency-light and runnable without
  a GPU — this is called out explicitly in the code.
- AI explanations (visualization interpretation, NL->SQL, chat narrative)
  gracefully degrade to deterministic templates when `ANTHROPIC_API_KEY` is
  unset; only the wording is affected, never the computed numbers.
- Hyperparameter search spaces are intentionally small (suited to an academic
  demo / limited compute), not exhaustive.

## License

Released under the [MIT License](LICENSE).
