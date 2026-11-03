# Architecture Specification
## Public Transport Route Helper for India

### 1. High-Level Architecture Overview

The system is architected as an intelligent, delay-aware multimodal transit optimizer designed for Indian public transit networks (Indian Railways, Urban Metro systems, and State Road Transport Corporations).

```
+-------------------------------------------------------------------+
|                        React 18 Frontend                          |
|  - Leaflet Map Visualizer (CartoDB / OSM tiles)                   |
|  - Real-time Station Autocomplete (DB Backed)                     |
|  - Multi-Criteria Filters (Fastest, Cheapest, Delay-Aware)        |
|  - AI Travel Assistant Chat Modal (Gemini 2.5)                    |
|  - Delay Predictor ML Dashboard                                   |
+---------------------------------+---------------------------------+
                                  | HTTP / JSON REST APIs
                                  v
+-------------------------------------------------------------------+
|                         FastAPI Backend                           |
|                                                                   |
|  +---------------------+   +-------------------+   +------------+ |
|  |   Mistral Service   |   | ML Delay Service  |   | Data Svc   | |
|  | - Structured JSON   |   | - HistGradient    |   | - GTFS     | |
|  | - Grounded Reasoner |   | - RandomForest    |   | - CSV      | |
|  | - Offline Fallback  |   | - Zero-Leakage    |   | - Adapters | |
|  +----------+----------+   +---------+---------+   +-----+------+ |
|             |                        |                   |        |
|             +------------+-----------+-------------------+        |
|                          |                                        |
|                          v                                        |
|             +----------------------------+                        |
|             |  Graph Route Engine (Nx)   |                        |
|             |  - Timetable Expansion     |                        |
|             |  - Transfer Constraints    |                        |
|             |  - Delay Generalized Cost  |                        |
|             +-------------+--------------+                        |
|                           |                                       |
+---------------------------+---------------------------------------+
                            | SQLAlchemy 2.0 ORM
                            v
+-------------------------------------------------------------------+
|             PostgreSQL / PostGIS (or Local SQLite)                |
|  - stations (28)        - routes (15)        - trips (31)         |
|  - connections (265)    - transfers (14)     - fares (30)         |
|  - ml_model_versions    - dataset_imports    - data_sources       |
+-------------------------------------------------------------------+
```

---

### 2. Core Subsystems

#### A. NetworkX MultiDiGraph Transit Engine
- **Nodes**: Physical stations, metro interchanges, railway terminals, and bus stands with precise geographic coordinates.
- **Edges**: 
  - Directed transit connections (`train`, `bus`, `metro`) with scheduled departure, scheduled arrival, duration, distance, and verified fares.
  - Transfer walking edges with minimal interchange duration buffers and distance in meters.
- **Timetable-Aware Routing**:
  - Validates chronological sequence: $t_{\text{dep}}^{(i+1)} \ge t_{\text{arr}}^{(i)} + \Delta t_{\text{transfer}}$.
  - Detects missed connections when transfer buffer is violated.
  - Evaluates high-frequency urban transit lines (Metro & Feeder buses) using dynamic headway dispatching.

#### B. Delay-Aware Generalized Optimization
The journey optimizer evaluates candidate routes via the multi-objective cost function:
$$\text{Cost}(J) = T_{\text{sched}}(J) + \sum_{l \in \text{legs}} d_{\text{pred}}(l) + \lambda_{\text{risk}} \cdot \mathbb{I}(\text{Risk} = \text{HIGH}) + \gamma \cdot N_{\text{transfers}}$$
Where:
- $T_{\text{sched}}(J)$ is the scheduled trip duration.
- $d_{\text{pred}}(l)$ is the ML-predicted delay for train leg $l$.
- $\lambda_{\text{risk}} = 45\text{ min}$ penalty if transfer buffer is compromised by predicted delay.
- $\gamma = 12\text{ min}$ per transfer interchange.

#### C. Machine Learning Delay Prediction Pipeline
- **Dataset**: Chronological historical operational records on the high-density Chennai Central &harr; KSR Bengaluru corridor.
- **Zero Future Leakage**: Training/Test split executed temporally (80% past / 20% future).
- **Models Evaluated**:
  1. `RandomForestRegressor` (Champion model, MAE: 6.25 min, RMSE: 8.06 min, $R^2$: 0.7914).
  2. `HistGradientBoostingRegressor` (MAE: 6.27 min, RMSE: 8.18 min, $R^2$: 0.7852).
- **Features**: Priority tier, distance, scheduled duration, cyclical sine/cosine time of day, day of week, seasonal month proxy, previous segment delay.

#### D. Mistral AI Generative Integration
- Backend-only execution using Mistral AI's official API (`https://api.mistral.ai/v1/chat/completions`) with `codestral-latest` / `ministral-8b-latest`.
- Translates conversational requests into validated `QueryExtraction` parameters.
- Route Explanation: Synthesizes data-grounded trade-offs between speed, cost, and ML delay risk without fabricating unverified schedules.
- Seamless fallback to offline deterministic natural language parser when `MISTRAL_API_KEY` is not provided.

