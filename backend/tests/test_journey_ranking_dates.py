import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.route_engine import GraphRouteEngine
from app.database.connection import SessionLocal

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def route_engine():
    db = SessionLocal()
    engine = GraphRouteEngine(db)
    yield engine
    db.close()

def test_same_day_journey_dates_api(client):
    """Test 1: Same-day journey has matching departure and arrival dates via API."""
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
    
    same_day_journeys = [j for j in data["journeys"] if not j.get("is_overnight")]
    assert len(same_day_journeys) > 0, "Expected same-day journeys between Chennai and Madurai"
    for j in same_day_journeys:
        assert j["departure_date_formatted"] == "Wednesday, 04 November 2026"
        assert j["arrival_date_formatted"] == "Wednesday, 04 November 2026"
        assert j["departure_datetime"].startswith("2026-11-04")
        assert j["arrival_datetime"].startswith("2026-11-04")
        assert j["scheduled_duration_min"] > 0
        dep_dt = datetime.fromisoformat(j["departure_datetime"])
        arr_dt = datetime.fromisoformat(j["arrival_datetime"])
        computed_min = int((arr_dt - dep_dt).total_seconds() / 60)
        assert j["scheduled_duration_min"] == computed_min

def test_overnight_journey_dates_api(client):
    """Test 2: Overnight journey crossing midnight correctly advances arrival date by 1 day."""
    payload = {
        "origin": "Hyderabad",
        "destination": "Tirupati",
        "travel_date": "2026-11-04",
        "departure_after": "17:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    
    overnight = [j for j in data["journeys"] if j.get("is_overnight")]
    assert len(overnight) > 0, "Expected overnight journeys between Hyderabad and Tirupati"
    for j in overnight:
        assert j["departure_date_formatted"] == "Wednesday, 04 November 2026"
        assert j["arrival_date_formatted"] == "Thursday, 05 November 2026"
        assert j["departure_datetime"].startswith("2026-11-04")
        assert j["arrival_datetime"].startswith("2026-11-05")
        assert "(+1 day" in j["scheduled_duration_formatted"]

def test_every_leg_has_dates_and_times_api(client):
    """Test 3: Every segment/leg contains valid formatted dates and times."""
    payload = {
        "origin": "Chennai",
        "destination": "Bengaluru",
        "travel_date": "2026-11-04",
        "departure_after": "06:00",
        "preferred_modes": ["train", "bus", "metro"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    for j in data["journeys"]:
        for leg in j["legs"]:
            assert "departure_date_formatted" in leg and leg["departure_date_formatted"]
            assert "arrival_date_formatted" in leg and leg["arrival_date_formatted"]
            assert "departure_datetime" in leg and leg["departure_datetime"]
            assert "arrival_datetime" in leg and leg["arrival_datetime"]
            assert "scheduled_departure" in leg and ":" in leg["scheduled_departure"]
            assert "scheduled_arrival" in leg and ":" in leg["scheduled_arrival"]
            assert leg["duration_min"] > 0

def test_monotonic_total_duration_api(client):
    """Test 4: Total duration equals sum of leg durations plus transfer waiting times."""
    payload = {
        "origin": "Chennai",
        "destination": "Madurai",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    for j in data["journeys"]:
        dep_dt = datetime.fromisoformat(j["departure_datetime"])
        arr_dt = datetime.fromisoformat(j["arrival_datetime"])
        expected_total_min = int((arr_dt - dep_dt).total_seconds() / 60)
        assert j["scheduled_duration_min"] == expected_total_min
        
        sum_legs = sum(l["duration_min"] for l in j["legs"])
        sum_waits = sum(l.get("transfer_wait_min", 0) for l in j["legs"])
        assert j["scheduled_duration_min"] == sum_legs + sum_waits

def test_fastest_route_ranking_api(client):
    """Test 5: Fastest ranking puts strictly lowest scheduled duration first."""
    payload = {
        "origin": "Chennai",
        "destination": "Madurai",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    journeys = response.json()["journeys"]
    assert len(journeys) >= 2
    for i in range(len(journeys) - 1):
        assert journeys[i]["scheduled_duration_min"] <= journeys[i + 1]["scheduled_duration_min"]
    
    assert "Fastest" in journeys[0]["tags"]
    min_dur = journeys[0]["scheduled_duration_min"]
    for j in journeys:
        if "Fastest" in j["tags"]:
            assert abs(j["scheduled_duration_min"] - min_dur) <= 1

def test_cheapest_route_ranking_api(client):
    """Test 6: Cheapest ranking puts lowest verified fare first."""
    payload = {
        "origin": "Chennai",
        "destination": "Madurai",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "cheapest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    journeys = response.json()["journeys"]
    assert len(journeys) >= 2
    verified = [j for j in journeys if j.get("is_fare_verified", True) and j["total_fare_inr"] > 0]
    if len(verified) >= 2:
        for i in range(len(verified) - 1):
            assert verified[i]["total_fare_inr"] <= verified[i + 1]["total_fare_inr"]
        assert "Cheapest" in verified[0]["tags"]

def test_fewest_transfers_ranking_api(client):
    """Test 7: Fewest transfers ranking puts 0-transfer journeys first."""
    payload = {
        "origin": "Chennai",
        "destination": "Bengaluru",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fewest_transfers"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    journeys = response.json()["journeys"]
    assert len(journeys) >= 2
    for i in range(len(journeys) - 1):
        assert journeys[i]["transfer_count"] <= journeys[i + 1]["transfer_count"]
    if journeys[0]["transfer_count"] == 0:
        assert "Direct" in journeys[0]["tags"]

def test_delay_aware_ranking_api(client):
    """Test 8: Delay-aware ranking ranks by estimated duration + penalty."""
    payload = {
        "origin": "Chennai",
        "destination": "Madurai",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "delay_aware"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    journeys = response.json()["journeys"]
    assert len(journeys) >= 1
    for j in journeys:
        assert j["estimated_duration_min"] >= j["scheduled_duration_min"]
        assert "delay_risk_level" in j

def test_multimodal_journey_structure_api(client):
    """Test 9: Multimodal journeys have correct modes and transfer waits."""
    payload = {
        "origin": "Chennai",
        "destination": "Bengaluru",
        "travel_date": "2026-11-04",
        "departure_after": "00:00",
        "preferred_modes": ["train", "bus", "metro"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    multimodal = [j for j in response.json()["journeys"] if j.get("is_multimodal")]
    if multimodal:
        m = multimodal[0]
        assert len(m["modes"]) > 1
        assert "Multimodal" in m["tags"]
        assert m["transfer_count"] >= 1

def test_direct_engine_search_with_station_ids(route_engine):
    """Test 10: Direct engine call with station codes MAS and MDU works properly."""
    results = route_engine.search_routes(
        origin_id="MAS",
        dest_id="MDU",
        dep_after="05:00",
        travel_date="2026-11-04"
    )
    assert len(results) > 0
    first = results[0]
    assert first["origin_code"] == "MAS"
    assert first["destination_code"] == "MDU"
    assert first["departure_date_formatted"] == "Wednesday, 04 November 2026"
    assert "departure_datetime" in first
