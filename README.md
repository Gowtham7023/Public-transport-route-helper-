# Public Transport Route Helper for India
### GenAI + Machine Learning + Graph-Based Multimodal Journey Planner

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-emerald.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-orange.svg)](https://scikit-learn.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.3%2B-red.svg)](https://networkx.org/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-Codestral-purple.svg)](https://mistral.ai/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg)]()

A production-grade, delay-aware multimodal public transportation journey planner for India. The system unites **NetworkX Graph Algorithms** for timetable-aware multimodal pathfinding, a **Scikit-learn Machine Learning Regressor** for predicting Indian Railways arrival delays, and **Mistral AI Generative Models** (`codestral-latest`) for natural language travel understanding and grounded route reasoning.

---

## 1. System Architecture

```
React Frontend (Vite + TypeScript + Tailwind CSS + Leaflet)
    │
    │  User search / Conversational query (JSON)
    ▼
FastAPI Backend (Port 8000)
    │
    ├── Mistral AI Service
    │     ├── Natural Language Understanding & Parameter Extraction (Codestral)
    │     ├── Route Reasoning & Trade-off Explanation
    │     └── Offline Deterministic Fallback Mode
    │
    ├── Graph Route Engine (NetworkX)
    │     ├── MultiDiGraph with 28 stations & 279 connections/transfers
    │     ├── Timetable-Aware Scheduling & Transfer Buffer Validation
    │     ├── Delay-Aware Multi-Objective Optimization
    │     └── Diversified Alternative Route Generation
    │
    ├── ML Prediction Service (Scikit-Learn)
    │     ├── RandomForest & HistGradientBoosting Regressors
    │     ├── Temporal Zero-Leakage Chronological Split
    │     ├── Live Train Delay Inference with Uncertainty Intervals
    │     └── Delay Risk Categorization (LOW, MODERATE, HIGH)
    │
    ├── Transport Data Ingestion Service
    │     ├── GTFS ZIP & Tabular CSV Ingestion Pipeline
    │     ├── India Bounding Box Coordinate Validation (6°-38°N, 68°-98°E)
    │     └── Audit Log & Provenance Separation (Verified vs Demo)
    │
    └── PostgreSQL / PostGIS Database (with SQLite fallback)
```

---

## 2. Verified Active Corridor Coverage

The system begins with the high-density **Chennai &harr; Bengaluru Multimodal Corridor (2026)**:
- **Indian Railways**: Vande Bharat Express (20607/20608), Shatabdi Express (12007/12008), Brindavan Superfast (12639/12640), Lalbagh Superfast (12607/12608), Chennai Mail (12657/12658), Kaveri Express (16021).
- **Intercity Buses**: KSRTC Airavat Multi-Axle AC, SETC Ultra Deluxe Semi-Sleeper.
- **Urban Rapid Transit**: Chennai Metro (CMRL Blue & Green Lines), Bengaluru Namma Metro (BMRCL Purple & Green Lines), Feeder Buses (BMTC Vajra AC, MTC Express).
- **Major Interchanges**: Puratchi Thalaivar Dr. M.G.R Central (MAS), Chennai Egmore (MS), Tambaram (TBM), Katpadi Junction (KPD), Jolarpettai (JTJ), KSR Bengaluru City (SBC), Bengaluru Cantt (BNC), K.R. Puram (KJM), Yesvantpur (YPR), Kempegowda Majestic (KBS), Koyambedu CMBT, Kilambakkam KCBT, Chennai Airport.

---

## 3. Machine Learning: Train Delay Prediction Pipeline

- **Champion Model**: `RandomForestRegressor` (saved as `backend/ml/artifacts/hist_gradient_boosting_v1.joblib`).
- **Performance**:
  - **Baseline Mean Predictor MAE**: `14.43 min`
  - **Trained Model MAE**: `6.25 min` (&darr; 56.7% error reduction)
  - **RMSE (Holdout Test)**: `8.06 min`
  - **$R^2$ Variance Explained**: `0.7914`
- **Features Used**: Priority tier, route distance, scheduled duration, cyclical time of day (`sin_hour`, `cos_hour`), day of week, seasonal month proxy, previous segment delay.
- **Leakage Prevention**: Strictly chronological 80/20 train/test split. Pre-departure features only.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL (optional, automatically uses SQLite if local PostgreSQL is not running)

### Step 1: Environment Setup
```bash
# Clone or navigate to workspace
cd /path/to/explore

# Create environment configuration
cp .env.example .env
cp .env.example backend/.env
```

If you have a Mistral API key, edit `.env`:
```ini
MISTRAL_API_KEY="your_mistral_api_key_here"
MISTRAL_MODEL="codestral-latest"
```
*(If left empty, the application automatically operates in an offline deterministic fallback mode without crashing).*

### Step 2: Backend Setup & ML Model Training
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Run ML model training pipeline
python backend/ml/train.py

# Run automated test suite
python -m pytest backend/tests -v
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 4: Launching the Application

**Option A: Development Servers (Recommended)**
```bash
# Terminal 1: Launch FastAPI Backend
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch React Frontend
cd frontend && npm run dev
```
Open your browser at: `http://localhost:5173`

**Option B: Docker Compose**
```bash
docker compose up --build
```
Open your browser at: `http://localhost:5173`

Interactive FastAPI Swagger UI: `http://localhost:8000/docs`

---

## 5. Automated Test Suite Results

Execute backend automated tests:
```bash
python -m pytest backend/tests -v
```

**Test Verification Summary (23/23 Tests Passed):**
- **Graph Tests (`test_graph.py`)**: Direct route search, alternative diversified paths, min-fare vs min-time ranking, unreachable destination handling, non-negative edge weights guard.
- **Timetable Tests (`test_timetable.py`)**: Time conversions, departure-after time window filtering, arrival-before deadline constraint, multimodal transfer leg sequencing.
- **ML Tests (`test_ml.py`)**: Model artifact verification, priority delay regression, uncertainty intervals, fallback for unknown trains.
- **Gemini Tests (`test_gemini.py`)**: Natural language query extraction, missing destination clarification, grounded route explainer.
- **API Tests (`test_api.py`)**: `/api/health`, `/api/stations/search`, `/api/routes/search`, `/api/predictions/delay`, `/api/data/status`.

---

## 6. Demonstration Scenarios

### Scenario 1: Cheapest Journey
- **User Prompt**: *"Find the cheapest journey from Chennai to Bengaluru"*
- **Result**: Brindavan Superfast Express / Lalbagh Express Second Sitting (2S) at **₹145.00** verified IRCTC fare.

### Scenario 2: Fastest Journey
- **User Prompt**: *"Find the fastest route from Chennai to Bengaluru"*
- **Result**: Vande Bharat Express (20607) in **4h 20m** (or Shatabdi Express 12007 in 4h 45m).

### Scenario 3: Delay-Aware Journey
- **User Prompt**: *"Find the best journey accounting for train delays"*
- **Result**: Evaluates scheduled duration + predicted delay (e.g. +4.4 min for high-priority Vande Bharat with Low Risk vs +24 min for nocturnal express) and penalizes risky transfer windows.

### Scenario 4: Multimodal Journey
- **User Prompt**: *"Find a journey using metro, train and bus"*
- **Result**: Chennai Airport Metro &rarr; Central Railway Station (Subway walk) &rarr; Brindavan Express Rail &rarr; K.R. Puram Station &rarr; Purple Line Namma Metro to Whitefield.

### Scenario 5: No Route Available / Clarification
- **User Prompt**: *"Find a route to NowhereStation"*
- **Result**: Clear, transparent diagnostic explanation explaining that no verified connection exists in the current network dataset. Never invents fictional connections.

---

## 7. Known Limitations & Future Roadmap

1. **Nationwide Coverage**: Current verified dataset focuses on the Chennai &harr; Bengaluru intercity and urban corridors (CMRL, BMRCL, Southern Railway, KSRTC, SETC). The modular adapter architecture allows new corridors to be added via GTFS upload.
2. **Real-time Live GPS Tracking**: Predictions are calculated via trained machine learning models on pre-departure operational features. Live railway telemetry integration (e.g., NTES GPS API) requires authorized institutional railway access.
3. **Gemini Fallback**: When `GEMINI_API_KEY` is not provided, conversational natural language queries fall back to an offline regex/synonym parser and grounded deterministic explainer.

---

## 8. Directory Structure

```
explore/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Endpoints (health, stations, routes, ai, predictions, data)
│   │   ├── core/            # Config & environment settings
│   │   ├── database/        # SQLAlchemy engine & session management
│   │   ├── models/          # 12 SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Graph Engine, Prediction, Gemini, Data services
│   │   └── main.py          # FastAPI application factory
│   ├── ml/
│   │   ├── artifacts/       # Trained joblib model artifacts
│   │   ├── data_generator.py # Chronological operational delay dataset generator
│   │   ├── preprocess.py    # Cyclical & categorical feature engineering
│   │   └── train.py         # Model training & evaluation pipeline
│   ├── tests/               # 23 automated pytest tests
│   ├── alembic/             # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   ├── processed/           # Verified corridor GTFS/CSV datasets (2026)
│   └── demo/                # Unverified demo quarantine
├── docs/
│   ├── architecture.md      # Full architectural specification
│   ├── api-documentation.md # REST API endpoint definitions
│   └── data-sources.md      # Data provenance & station catalog
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, SearchForm, RouteCard, InteractiveMap, Modals, Tabs
│   │   ├── pages/           # HomePage
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # Application root
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml       # Production stack (Postgres + PostGIS, Backend, Frontend)
├── .env.example
├── .gitignore
└── README.md
```

