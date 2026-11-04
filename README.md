# 🚌 Public Transport Route Helper for India

> **GenAI + Machine Learning + Graph-Based Multimodal Journey Planner**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-route--helper.vercel.app-brightgreen?style=for-the-badge)](https://route-helper.vercel.app/)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-emerald.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-orange.svg)](https://scikit-learn.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.3%2B-red.svg)](https://networkx.org/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-Codestral-purple.svg)](https://mistral.ai/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg)]()

---

## 🌐 Live Demo

**Try it out:** [https://route-helper.vercel.app/](https://route-helper.vercel.app/)

A production-grade, delay-aware multimodal public transportation journey planner for India. The system unites:
- 🗺️ **NetworkX Graph Algorithms** — timetable-aware multimodal pathfinding
- 🤖 **Scikit-learn ML Regressor** — predicting Indian Railways arrival delays
- 💬 **Mistral AI** (`codestral-latest`) — natural language travel understanding & grounded route reasoning

---

## 📋 Table of Contents

1. [System Architecture](#-system-architecture)
2. [Features](#-features)
3. [Corridor Coverage](#-verified-active-corridor-coverage)
4. [Machine Learning Pipeline](#-machine-learning-train-delay-prediction)
5. [Quickstart Guide](#-quickstart-guide)
6. [Test Suite](#-automated-test-suite)
7. [Demo Scenarios](#-demonstration-scenarios)
8. [Directory Structure](#-directory-structure)
9. [Limitations & Roadmap](#-known-limitations--future-roadmap)

---

## 🏗️ System Architecture

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
    │     ├── India Bounding Box Coordinate Validation (6°–38°N, 68°–98°E)
    │     └── Audit Log & Provenance Separation (Verified vs Demo)
    │
    └── PostgreSQL / PostGIS Database (with SQLite fallback)
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗣️ **Natural Language Search** | Ask in plain English — AI extracts origin, destination, and preferences |
| 🛤️ **Multimodal Routing** | Combines trains, metro, and buses in a single journey |
| ⏱️ **Delay Prediction** | ML model predicts arrival delays with uncertainty intervals |
| 🗺️ **Interactive Map** | Leaflet-powered map showing full route visualization |
| 💰 **Fare Optimization** | Find cheapest or fastest routes based on preference |
| 🔄 **Alternative Routes** | Diversified route suggestions with trade-off explanations |
| 📴 **Offline Fallback** | Works without an API key using deterministic regex parser |

---

## 🗺️ Verified Active Corridor Coverage

The system begins with the high-density **Chennai ↔ Bengaluru Multimodal Corridor (2026)**:

- **Indian Railways**: Vande Bharat Express (20607/20608), Shatabdi Express (12007/12008), Brindavan Superfast (12639/12640), Lalbagh Superfast (12607/12608), Chennai Mail (12657/12658), Kaveri Express (16021)
- **Intercity Buses**: KSRTC Airavat Multi-Axle AC, SETC Ultra Deluxe Semi-Sleeper
- **Urban Rapid Transit**: Chennai Metro (CMRL Blue & Green Lines), Bengaluru Namma Metro (BMRCL Purple & Green Lines), Feeder Buses (BMTC Vajra AC, MTC Express)
- **Major Interchanges**: MGR Central (MAS), Chennai Egmore (MS), Tambaram, Katpadi Junction, Jolarpettai, KSR Bengaluru City (SBC), Yesvantpur, Kempegowda Majestic, Koyambedu CMBT, Chennai Airport, and more

---

## 🤖 Machine Learning: Train Delay Prediction

| Metric | Value |
|---|---|
| **Model** | `RandomForestRegressor` |
| **Baseline MAE** | 14.43 min |
| **Trained Model MAE** | 6.25 min (**↓ 56.7% error reduction**) |
| **RMSE (Holdout Test)** | 8.06 min |
| **R² Variance Explained** | 0.7914 |

**Features Used**: Priority tier, route distance, scheduled duration, cyclical time of day (`sin_hour`, `cos_hour`), day of week, seasonal month proxy, previous segment delay.

**Leakage Prevention**: Strictly chronological 80/20 train/test split — pre-departure features only.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL *(optional — automatically falls back to SQLite)*

### Step 1: Clone & Configure Environment

```bash
git clone https://github.com/Gowtham7023/Public-transport-route-helper-
cd Public-transport-route-helper-

cp .env.example .env
cp .env.example backend/.env
```

Optionally add your Mistral API key to `.env`:
```ini
MISTRAL_API_KEY="your_mistral_api_key_here"
MISTRAL_MODEL="codestral-latest"
```
> If left empty, the app runs in **offline deterministic fallback mode** — no crashes.

---

### Step 2: Backend Setup & ML Training

```bash
pip install -r backend/requirements.txt

# Train the ML delay prediction model
python backend/ml/train.py

# Run the test suite
python -m pytest backend/tests -v
```

---

### Step 3: Frontend Setup

```bash
cd frontend
npm install
npm run build
cd ..
```

---

### Step 4: Launch the Application

**Option A — Development Servers (Recommended)**
```bash
# Terminal 1: FastAPI Backend
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload

# Terminal 2: React Frontend
cd frontend && npm run dev
```
Open: [http://localhost:5173](http://localhost:5173)
Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

**Option B — Docker Compose**
```bash
docker compose up --build
```
Open: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Automated Test Suite

```bash
python -m pytest backend/tests -v
```

**23/23 Tests Passed ✅**

| Test File | Coverage |
|---|---|
| `test_graph.py` | Direct routes, alternative paths, fare vs time ranking, unreachable destinations |
| `test_timetable.py` | Time conversions, departure windows, multimodal transfer sequencing |
| `test_ml.py` | Model artifact verification, delay regression, uncertainty intervals, fallback |
| `test_gemini.py` | NL query extraction, missing destination clarification, route explanation |
| `test_api.py` | `/api/health`, `/api/stations/search`, `/api/routes/search`, `/api/predictions/delay` |

---

## 🎬 Demonstration Scenarios

### 💰 Scenario 1: Cheapest Journey
> *"Find the cheapest journey from Chennai to Bengaluru"*

**Result**: Brindavan Superfast / Lalbagh Express — Second Sitting (2S) at **₹145.00** (verified IRCTC fare)

---

### ⚡ Scenario 2: Fastest Journey
> *"Find the fastest route from Chennai to Bengaluru"*

**Result**: Vande Bharat Express (20607) in **4h 20m** — or Shatabdi Express (12007) in 4h 45m

---

### 🕐 Scenario 3: Delay-Aware Journey
> *"Find the best journey accounting for train delays"*

**Result**: ML model evaluates scheduled duration + predicted delay (e.g. +4.4 min for Vande Bharat at LOW risk vs +24 min for nocturnal express) and penalizes risky transfer windows

---

### 🚇 Scenario 4: Multimodal Journey
> *"Find a journey using metro, train and bus"*

**Result**: Chennai Airport Metro → Central Railway Station → Brindavan Express → K.R. Puram → Namma Metro Purple Line to Whitefield

---

### ❌ Scenario 5: No Route / Clarification
> *"Find a route to NowhereStation"*

**Result**: Clear diagnostic explanation — the system never invents fictional connections

---

## 📁 Directory Structure

```
Public-transport-route-helper/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Endpoints (health, stations, routes, ai, predictions, data)
│   │   ├── core/            # Config & environment settings
│   │   ├── database/        # SQLAlchemy engine & session management
│   │   ├── models/          # 12 SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Graph Engine, Prediction, Mistral, Data services
│   │   └── main.py          # FastAPI application factory
│   ├── ml/
│   │   ├── artifacts/       # Trained joblib model artifacts
│   │   ├── data_generator.py
│   │   ├── preprocess.py    # Cyclical & categorical feature engineering
│   │   └── train.py         # Model training & evaluation pipeline
│   ├── tests/               # 23 automated pytest tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   ├── processed/           # Verified corridor GTFS/CSV datasets (2026)
│   │   └── chennai_bengaluru/
│   ├── gazetteer/           # India places JSON
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
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚠️ Known Limitations & Future Roadmap

1. **Nationwide Coverage** — Current verified dataset covers Chennai ↔ Bengaluru corridor. The modular adapter architecture supports adding new corridors via GTFS upload.
2. **Real-time Live GPS** — Delay predictions use trained ML models on pre-departure features. Live NTES GPS telemetry requires authorized institutional railway access.
3. **Mistral Fallback** — Without `MISTRAL_API_KEY`, conversational queries fall back to an offline regex/synonym parser and deterministic route explainer.

---

<div align="center">
  <strong>Built with ❤️ for Indian commuters</strong><br/>
  <a href="https://route-helper.vercel.app/">🌐 Live Demo</a> •
  <a href="docs/architecture.md">📐 Architecture</a> •
  <a href="docs/api-documentation.md">📖 API Docs</a> •
  <a href="docs/data-sources.md">🗃️ Data Sources</a>
</div>
