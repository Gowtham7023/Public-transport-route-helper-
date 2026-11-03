# REST API Documentation
## Public Transport Route Helper for India

Interactive OpenAPI Swagger UI is available at:
`http://localhost:8000/docs`

Interactive ReDoc documentation is available at:
`http://localhost:8000/redoc`

---

### 1. Health API

#### `GET /api/health`
Returns system status, active database connection, ML model status, and Gemini AI integration state.

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "timestamp": "2026-11-03T15:11:52.114520",
  "version": "1.0.0",
  "database": "HEALTHY",
  "ml_model": "ACTIVE",
  "gemini_ai": "OFFLINE_FALLBACK (no key provided)",
  "environment": "development"
}
```

---

### 2. Station APIs

#### `GET /api/stations/search?q={query}&city={city}&mode={mode}`
Database-backed station autocomplete. Matches station name, code, or city with synonym expansion (e.g. `bangalore` &harr; `bengaluru`, `madras` &harr; `chennai`).

**Response (200 OK):**
```json
[
  {
    "id": "MAS",
    "name": "Puratchi Thalaivar Dr. M.G. Ramachandran Central Railway Station",
    "code": "MAS",
    "city": "Chennai",
    "state": "Tamil Nadu",
    "latitude": 13.0827,
    "longitude": 80.2755,
    "transport_types": ["train", "metro", "bus"],
    "is_hub": true,
    "wheelchair_accessible": true
  }
]
```

#### `GET /api/stations/{station_id}`
Retrieves specific station details by Station ID or Station Code.

#### `GET /api/stations/nearby?lat={lat}&lon={lon}&radius_km={radius}`
Finds stations proximate to specified GPS coordinates using haversine geographic calculation.

---

### 3. Route Search & Comparison APIs

#### `POST /api/routes/search`
Executes timetable-aware multimodal route search with ML delay estimation.

**Request Body:**
```json
{
  "origin": "MAS",
  "destination": "SBC",
  "travel_date": "2026-11-04",
  "departure_after": "05:00",
  "arrival_before": "12:00",
  "preferred_modes": ["train", "bus", "metro"],
  "optimisation": "fastest",
  "max_transfers": 3,
  "max_budget": 1000.0
}
```

**Response (200 OK):**
```json
{
  "origin": "MAS",
  "destination": "SBC",
  "travel_date": "2026-11-04",
  "optimisation": "fastest",
  "total_results": 4,
  "journeys": [
    {
      "journey_id": "JRN_TRIP_SHATABDI_12007_TRIP_SHATABDI_12007_0600",
      "origin_id": "MAS",
      "origin_name": "Puratchi Thalaivar Dr. M.G. Ramachandran Central Railway Station",
      "destination_id": "SBC",
      "destination_name": "KSR Bengaluru City Junction",
      "scheduled_departure": "06:00",
      "scheduled_arrival": "10:45",
      "scheduled_duration_min": 285,
      "scheduled_duration_formatted": "4h 45m",
      "predicted_delay_min": 2.7,
      "delay_risk_level": "LOW",
      "estimated_arrival": "10:47",
      "estimated_duration_min": 287,
      "estimated_duration_formatted": "4h 47m",
      "total_fare_inr": 145.0,
      "total_distance_km": 358.5,
      "transfer_count": 0,
      "modes": ["train"],
      "is_multimodal": false,
      "legs": [ ... ],
      "data_source": "Verified Corridor Schedules 2026",
      "data_freshness": "VERIFIED_OFFICIAL",
      "is_verified": true,
      "tags": ["Fastest", "Cheapest", "Direct", "High Punctuality"]
    }
  ],
  "applied_filters": { ... }
}
```

#### `POST /api/routes/compare`
Side-by-side trade-off comparison between 2 or 3 candidate journeys.

---

### 4. AI APIs

#### `POST /api/ai/query`
Natural language query understanding, structured entity extraction, and instant graph search.

**Request Body:**
```json
{
  "prompt": "Find the cheapest journey from Chennai to Bengaluru tomorrow before 9 AM"
}
```

#### `POST /api/ai/explain-route`
Data-grounded route explanation highlighting speed, cost, and ML delay trade-offs.

---

### 5. Machine Learning Prediction APIs

#### `POST /api/predictions/delay`
Predicts expected arrival delay in minutes for an Indian Railways service.

**Request Body:**
```json
{
  "train_number": "20607",
  "scheduled_departure_hour": 6
}
```

**Response (200 OK):**
```json
{
  "train_number": "20607",
  "train_name": "Vande Bharat Express (MAS->SBC)",
  "train_type": "VANDE_BHARAT",
  "predicted_delay_min": 2.6,
  "delay_risk_level": "LOW",
  "confidence_interval_min": [0.0, 12.3],
  "model_version": "1.0.0",
  "is_model_backed": true,
  "scheduled_departure_hour": 6
}
```

#### `GET /api/predictions/model-info`
Retrieves registered ML model metrics (MAE, RMSE, R², sample count, features used).

---

### 6. Data Ingestion APIs

#### `GET /api/data/status`
Returns status of loaded transit datasets, record counts, and verification levels.

#### `POST /api/data/import`
Uploads and validates a GTFS ZIP archive or CSV dataset.

