# Running the Social Product Intelligence Module

This guide details how to configure, boot, and run the **Social Product Intelligence** project end-to-end. The recommended approach uses **Docker Compose** to run all services together. You can also run individual pipeline scripts or launch the web services manually for development.

> **Last updated:** June 2026 — Reflects Docker-based backend, multi-company workspace switching, auto report generation, and all bug fixes applied.

---

## Table of Contents
1. [Prerequisites & Environment Configuration](#1-prerequisites--environment-configuration)
2. [Infrastructure Setup (Docker Compose)](#2-infrastructure-setup-docker-compose)
3. [Database Migrations (Alembic)](#3-database-migrations-alembic)
4. [Running the Frontend Dashboard (React + Vite)](#4-running-the-frontend-dashboard-react--vite)
5. [Running the Web Backend (FastAPI - Local Dev)](#5-running-the-web-backend-fastapi---local-dev)
6. [Onboarding a New Company (Setup Wizard)](#6-onboarding-a-new-company-setup-wizard)
7. [Running the Pipelines File-by-File](#7-running-the-pipelines-file-by-file)
8. [Reports — Generating & Viewing](#8-reports--generating--viewing)
9. [Running the Full Orchestrator](#9-running-the-full-orchestrator)
10. [Inspecting & Querying the Database](#10-inspecting--querying-the-database)
11. [Service URLs & Ports Reference](#11-service-urls--ports-reference)
12. [Known Issues & Applied Fixes](#12-known-issues--applied-fixes)

---

## 1. Prerequisites & Environment Configuration

Ensure you have the following installed:
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **Docker Desktop** (with Docker Compose v2+)

### A. Environment File (`.env`)
Copy the example env file and fill in your credentials:
```powershell
cp .env.example .env
```

Minimum required values:
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=social_intelligence
POSTGRES_HOST=db          # Use 'db' inside Docker containers, 'localhost' on host
POSTGRES_PORT=5432

# API Server
BACKEND_PORT=8000
FASTAPI_ENV=development

# AI & Data APIs (required for full pipeline)
GEMINI_API_KEY=your_gemini_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=social-intelligence-bot
```

> ⚠️ `GEMINI_API_KEY` is required for AI-powered insight generation (`analytics/insight_generator.py`) and the `ai_summarizer.py`. Without it, insights will be skipped gracefully but no executive summaries will be generated.

### B. Python Virtual Environment (for running pipeline scripts locally)
Only needed if running pipeline scripts **outside** Docker:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r backend/requirements.txt
pip install -r pipeline/requirements.txt
```

---

## 2. Infrastructure Setup (Docker Compose)

All backend services (API, database, Elasticsearch, Airflow) run inside Docker. Start them with:

```powershell
# From the project root directory
docker compose up -d
```

### Running Services & Container Names

| Container Name              | Service         | Host Port | Notes                        |
|-----------------------------|-----------------|-----------|------------------------------|
| `social_intel_backend`      | FastAPI backend | `8000`    | Primary API — use this       |
| `social_intel_db`           | PostgreSQL 15   | `5432`    | Main database                |
| `social_intel_es`           | Elasticsearch   | `9200`    | Full-text search index       |
| `social-intelligence-copy-airflow-webserver-1` | Airflow UI | `8080` | DAG scheduler UI |
| `social-intelligence-copy-airflow-scheduler-1` | Airflow scheduler | — | Background job runner |

> **Note:** There may be a second set of containers (`si_backend` on port `8001`, `si_postgres` on port `5433`) from a parallel project instance. The **active production backend is `social_intel_backend` on port `8000`**.

### Verify Services Are Running
```powershell
docker ps
```

Check individual services:
```powershell
# Backend API health
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workspace"

# Elasticsearch cluster check
Invoke-RestMethod -Uri "http://localhost:9200"
```

### Restart a Specific Container
```powershell
docker restart social_intel_backend
docker restart social_intel_db
```

---

## 3. Database Migrations (Alembic)

Run migrations to create all tables before first use. Migrations run **inside** the backend container:

```powershell
docker exec social_intel_backend alembic upgrade head
```

Or if running locally on host:
```powershell
cd backend
alembic upgrade head
cd ..
```

Tables created:
- `raw_mentions` — raw collected text from all sources
- `processed_mentions` — cleaned & sentiment-labelled records
- `aspect_results` — ABSA aspect breakdown per mention
- `topic_results` — BERTopic cluster assignments
- `executive_insights` — AI-generated brand insight summaries
- `generated_reports` — PDF report metadata & file paths
- `alert_log` — triggered alerts for sentiment spikes

---

## 4. Running the Frontend Dashboard (React + Vite)

```powershell
# Navigate to the frontend folder
cd frontend

# Install dependencies (first run only)
npm install

# Start the development server
npm run dev
```

Open **http://localhost:5173** in your browser.

> If the browser shows `chrome-error://chromewebdata/`, the Vite server has stopped. Re-run `npm run dev` from the `frontend/` directory.

### Dashboard Pages
| Route | Description |
|-------|-------------|
| `/setup` | Onboard a new company & run the pipeline |
| `/` or `/overview` | Brand health overview & KPIs |
| `/brand/:id` | Deep-dive brand detail with charts |
| `/executive` | AI executive intelligence summary |
| `/reports` | Generated intelligence reports list |
| `/alerts` | Sentiment spike & keyword alerts |

---

## 5. Running the Web Backend (FastAPI - Local Dev)

If you prefer **not** to run the backend API inside Docker, you can run the FastAPI server directly on your host machine in hot-reload mode:

```powershell
# Navigate to the backend folder
cd backend

# Activate your virtual environment (if not already active)
..\.venv\Scripts\Activate.ps1

# Start the uvicorn API server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **API Documentation UI:** Go to `http://127.0.0.1:8000/docs` to see all interactive endpoints.
- **Health Verification:** Go to `http://127.0.0.1:8000/api/v1/health`.

> **Note:** If running locally, make sure your `.env` file has `POSTGRES_HOST=localhost` so it can connect to the database container correctly.

---

## 6. Onboarding a New Company (Setup Wizard)

The setup wizard (`/setup` page) is the **primary entry point**. It:
1. Creates company & workspace config JSON files
2. Writes competitor configs
3. Kicks off the full background pipeline (all 8 phases)
4. Auto-generates a PDF intelligence report on completion

### Via the UI
1. Go to `http://localhost:5173/setup`
2. Fill in Company Name, Industry, Play Store ID, Keywords, and Competitors
3. Click **"Start Analysis"**
4. Watch the progress bar complete through all pipeline phases
5. Navigate to the dashboard when done

### Via API (PowerShell)
```powershell
$body = @{
  company_id   = "zomato"
  display_name = "Zomato"
  industry     = "food_delivery"
  playstore_id = "com.application.zomato"
  keywords     = @("zomato", "food delivery", "zomato app")
  competitors  = @(
    @{ id = "swiggy"; display_name = "Swiggy"; playstore_id = "bundl.technologies.swiggy" },
    @{ id = "blinkit"; display_name = "Blinkit"; playstore_id = "com.blinkit.android" }
  )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/setup" -Body $body -ContentType "application/json"
```

### Check Pipeline Progress
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/setup/status/zomato_workspace"
```
Returns:
```json
{ "step": "Analysis Complete!", "progress": 100, "done": true, "error": null }
```

### Pipeline Phases (background thread)
| # | Step | Progress |
|---|------|----------|
| 1 | Initializing | 2% |
| 2 | Collecting Google News | 15% |
| 3 | Collecting Reddit | 30% |
| 4 | Collecting Play Store reviews | 45% |
| 5 | Cleaning & Normalising Text | 55% |
| 6 | Sentiment Analysis (RoBERTa) | 70% |
| 7 | Aspect Analysis (ABSA) | 80% |
| 8 | Generating AI Insights | 90% |
| 9 | Indexing to Elasticsearch | 95% |
| 10 | Generating Report | 98% |
| 11 | Analysis Complete! | 100% |

---

## 7. Running the Pipelines File-by-File

If you need to run pipeline stages individually (e.g. for debugging), execute them with the virtual environment active from the **project root**:

### Phase 1: Ingest Data (Collectors)
```powershell
python pipeline/collectors/google_news_collector.py
python pipeline/collectors/reddit_collector.py
python pipeline/collectors/playstore_collector.py
```

> **Note:** `google_news_collector.py` uses `feedparser` (no API key needed). `reddit_collector.py` requires `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET` in `.env`.

### Phase 2: Clean & Validate Text
```powershell
python pipeline/nlp/cleaner.py
```

### Phase 3: Sentiment Classification (RoBERTa)
```powershell
python pipeline/nlp/sentiment.py
```
Downloads `cardiffnlp/twitter-roberta-base-sentiment` from HuggingFace on first run (~500 MB).

### Phase 4: Aspect-Based Sentiment Analysis
```powershell
python pipeline/nlp/absa.py
```

### Phase 5: Insight Generation (Gemini AI)
```powershell
python pipeline/analytics/insight_generator.py
```
Requires `GEMINI_API_KEY` in `.env`. Uses `google-genai` package.

### Phase 6: Search Indexing (Elasticsearch)
```powershell
python pipeline/indexer/indexer.py
```

### Phase 7: Alert Engine
```powershell
python pipeline/alert_engine.py
```

### Phase 8: AI Summarizer
```powershell
python pipeline/analytics/ai_summarizer.py
```

---

## 8. Reports — Generating & Viewing

### View Reports in the Dashboard
Navigate to `http://localhost:5173/reports`.

- A report is **auto-generated** at the end of every pipeline run.
- Click **"Generate Report"** to create a fresh report on demand.
- Click **"View Report"** to open the full interactive report drawer.
- Click **"Export as PDF"** inside the drawer to print/save as PDF.

### Generate a Report via API
```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/reports/generate"
```

### List All Reports
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/reports" | ConvertTo-Json -Depth 4
```

### Report Contents
Each report includes:
1. KPI Scorecard (score, mentions, rating, net sentiment)
2. Executive Summary (AI-generated)
3. Sentiment Distribution (Positive / Neutral / Negative %)
4. Aspect Satisfaction Analysis (delivery, quality, price, UX, returns)
5. Top Complaint Themes
6. Risks & Opportunities
7. Recent Reviews Sample (top 5–6 mentions)
8. Recommended Actions

> **PDF files** are saved to `generated_pdfs/` at the project root (mounted via Docker volume).

---

## 9. Running the Full Orchestrator

For automated or scheduled runs, execute the unified orchestrator which runs all pipeline phases in sequence:

```powershell
# Activate venv first
.venv\Scripts\Activate.ps1

# Run all 8 stages sequentially
python pipeline/orchestrator.py
```

### Automated Scheduling (APScheduler)
```powershell
# Runs orchestrator every 6 hours, generates PDF reports weekly
python pipeline/scheduler.py
```

### Airflow DAG Scheduler (Docker)
Airflow is available at `http://localhost:8080`. DAGs are defined in the `dags/` folder and can be triggered from the Airflow UI.

---

## 10. Inspecting & Querying the Database

### Method A: CLI Inspector Script
```powershell
.venv\Scripts\Activate.ps1
python inspect_db.py
```

### Method B: psql inside Docker
```powershell
# Enter the Postgres container
docker exec -it social_intel_db psql -U postgres -d social_intelligence

# Useful queries:
\dt                                                                    # List all tables
SELECT COUNT(*) FROM raw_mentions;
SELECT COUNT(*) FROM processed_mentions;
SELECT brand, COUNT(*) FROM processed_mentions GROUP BY brand;
SELECT brand, sentiment_label, COUNT(*) FROM processed_mentions GROUP BY brand, sentiment_label ORDER BY brand;
SELECT * FROM generated_reports ORDER BY generated_at DESC LIMIT 5;
SELECT * FROM executive_insights ORDER BY generated_at DESC LIMIT 5;
\q                                                                     # Exit
```

### Method C: GUI Client (DBeaver / PGAdmin / TablePlus)
| Field    | Value               |
|----------|---------------------|
| Engine   | PostgreSQL          |
| Host     | `localhost`         |
| Port     | `5432`              |
| Database | `social_intelligence` |
| User     | `postgres`          |
| Password | `postgres`          |

---

## 11. Service URLs & Ports Reference

| Service | URL | Notes |
|---------|-----|-------|
| **Frontend Dashboard** | http://localhost:5173 | Vite dev server — run `npm run dev` |
| **Backend API** | http://localhost:8000 | FastAPI in Docker |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive endpoint explorer |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | Machine-readable spec |
| **Elasticsearch** | http://localhost:9200 | Full-text search |
| **Airflow UI** | http://localhost:8080 | DAG scheduler dashboard |
| **PostgreSQL** | localhost:5432 | Direct DB connection |

### Key API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/setup` | Onboard a company, start pipeline |
| `GET`  | `/api/v1/setup/status/{workspace_id}` | Poll pipeline progress |
| `GET`  | `/api/v1/workspace` | Get active workspace context |
| `GET`  | `/api/v1/brands` | List all brand IDs |
| `GET`  | `/api/v1/brands/{id}` | Brand KPIs & sentiment |
| `GET`  | `/api/v1/feed?brand={id}` | Paginated mention feed |
| `GET`  | `/api/v1/insights?brand={id}` | AI executive insights |
| `GET`  | `/api/v1/aspects?brand={id}` | ABSA aspect scores |
| `GET`  | `/api/v1/topics?brand={id}` | Top complaint topics |
| `GET`  | `/api/v1/alerts` | Recent triggered alerts |
| `GET`  | `/api/v1/reports` | List all generated reports |
| `POST` | `/api/v1/reports/generate` | Generate a new report now |
| `GET`  | `/api/v1/rankings` | Competitive brand rankings |
| `GET`  | `/api/v1/competitor-analysis` | Side-by-side brand comparison |

---

## 12. Known Issues & Applied Fixes

### Fix 1 — `No module named 'google'` in Docker container
**Symptom:** Pipeline thread fails immediately after setup with `No module named 'google'`.  
**Cause:** `google-genai` package was missing from the Docker container (installed in virtual env but not in Docker image).  
**Fix Applied:** `google-genai>=0.1.1` added to `backend/requirements.txt`. Rebuild the Docker image to apply:
```powershell
docker compose build backend
docker compose up -d backend
```
Or install directly into running container:
```powershell
docker exec social_intel_backend pip install google-genai
```

---

### Fix 2 — PDF Report crashes on HTML in news article titles
**Symptom:** Auto-report generation fails with `paraparser: syntax error: invalid attribute name _blank"`.  
**Cause:** Google News RSS feed returns article titles containing raw HTML anchor tags (e.g. `<a href=" target="_blank">`). ReportLab's paragraph parser rejects these.  
**Fix Applied:** `_strip_html()` sanitizer added to `backend/app/utils/pdf_generator.py`. All text fields (news body, executive summary, risk/opportunity) are stripped of HTML and have `&`, `<`, `>` properly XML-escaped before being passed to ReportLab.

---

### Fix 3 — Reports page showed "No reports generated yet" always
**Symptom:** The `/reports` page was always empty even after a successful pipeline run.  
**Cause:** Reports were only created when sending alert emails (via `/alerts/send`). No reports were created automatically by the pipeline.  
**Fix Applied:**  
- `POST /api/v1/reports/generate` endpoint added — generates a report on demand.  
- Pipeline background thread now auto-generates a report as the final step (progress 98%).  
- The Reports page now shows a **"Generate Report"** button and a call-to-action in the empty state.

---

### Fix 4 — Frontend shows `chrome-error` page
**Symptom:** Browser shows `chrome-error://chromewebdata/` on localhost:5173.  
**Cause:** The Vite development server is not running.  
**Fix:** Restart the frontend server:
```powershell
cd frontend
npm run dev
```

---

*Generated by SocialIntel AI Platform · Social Product Intelligence Module*
