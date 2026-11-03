import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "version" in data

def test_station_search(client):
    res = client.get("/api/stations/search?q=bangalore")
    assert res.status_code == 200
    stations = res.json()
    assert len(stations) > 0
    assert any("SBC" in s["id"] or "Bengaluru" in s["name"] or "Bangalore" in s["name"] for s in stations)

def test_route_search_api(client):
    payload = {
        "origin": "MAS",
        "destination": "SBC",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "optimisation": "fastest"
    }
    res = client.post("/api/routes/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] > 0
    assert len(data["journeys"]) > 0

def test_route_search_invalid_station(client):
    payload = {
        "origin": "INVALID_ABCXYZ",
        "destination": "SBC"
    }
    res = client.post("/api/routes/search", json=payload)
    assert res.status_code == 400

def test_predictions_api(client):
    res = client.post("/api/predictions/delay", json={
        "train_number": "12007",
        "scheduled_departure_hour": 6
    })
    assert res.status_code == 200
    data = res.json()
    assert data["train_number"] == "12007"
    assert "predicted_delay_min" in data

def test_data_status_api(client):
    res = client.get("/api/data/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["counts"]["stations"] >= 20

