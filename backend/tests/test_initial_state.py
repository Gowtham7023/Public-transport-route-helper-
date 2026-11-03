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

def test_missing_origin_rejected(client):
    """Verify route search endpoint rejects missing or empty origin."""
    payload = {
        "origin": "",
        "destination": "Madurai",
        "travel_date": "2026-11-04"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 400

def test_missing_destination_rejected(client):
    """Verify route search endpoint rejects missing or empty destination."""
    payload = {
        "origin": "Chennai",
        "destination": "",
        "travel_date": "2026-11-04"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 400

def test_identical_origin_destination_rejected(client):
    """Verify route search endpoint rejects identical station IDs."""
    payload = {
        "origin": "MAS",
        "destination": "MAS",
        "travel_date": "2026-11-04"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 400

def test_manual_valid_search_succeeds(client):
    """Verify manual search with valid inputs succeeds as expected."""
    payload = {
        "origin": "Chennai",
        "destination": "Madurai",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    assert len(data["journeys"]) > 0
