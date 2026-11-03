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

def test_india_places_autocomplete(client):
    """Verify autocomplete returns categorized items (city, railway, bus, metro) with state labels."""
    response = client.get("/api/places/search?q=mad&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    categories = [item["category"] for item in data]
    assert "city" in categories or "railway" in categories

    first = data[0]
    assert "display_label" in first
    assert "category_label" in first
    assert "state" in first

def test_bengaluru_autocomplete_categories(client):
    """Verify Bengaluru search returns city and terminal stations."""
    response = client.get("/api/places/search?q=bengaluru&limit=10")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 2
    cats = {item["category"] for item in items}
    assert "city" in cats

def test_bus_journey_search(client):
    """Verify bus journeys are found with positive count and valid fares and stops."""
    payload = {
        "origin": "CMBT_BUS",
        "destination": "KBS_BUS",
        "travel_date": "2026-11-04",
        "departure_after": "06:00",
        "preferred_modes": ["bus"],
        "optimisation": "cheapest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    for j in data["journeys"]:
        assert "bus" in j["modes"]
        assert j["total_fare_inr"] > 0
        assert len(j["legs"]) > 0

def test_bengaluru_mysuru_corridor(client):
    """Verify Bengaluru <-> Mysuru corridor returns train and bus journeys."""
    payload = {
        "origin": "place_bengaluru_ka",
        "destination": "place_mysuru_ka",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0

def test_chennai_madurai_corridor(client):
    """Verify Chennai <-> Madurai corridor returns journeys."""
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

def test_hyderabad_vijayawada_corridor(client):
    """Verify Hyderabad <-> Vijayawada corridor returns journeys."""
    payload = {
        "origin": "Hyderabad",
        "destination": "Vijayawada",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0

def test_mumbai_pune_corridor(client):
    """Verify Mumbai <-> Pune corridor returns journeys."""
    payload = {
        "origin": "Mumbai",
        "destination": "Pune",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0

def test_delhi_jaipur_corridor(client):
    """Verify Delhi <-> Jaipur corridor returns journeys."""
    payload = {
        "origin": "Delhi",
        "destination": "Jaipur",
        "travel_date": "2026-11-04",
        "departure_after": "05:00",
        "preferred_modes": ["train", "bus"],
        "optimisation": "fastest"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0

def test_unserviced_gazetteer_place_diagnostic(client):
    """
    Verify searching for a place in the gazetteer without active transit schedules
    returns an informative diagnostic message rather than a generic crash.
    """
    payload = {
        "origin": "Shillong",
        "destination": "Bengaluru",
        "travel_date": "2026-11-04",
        "departure_after": "05:00"
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Gazetteer" in detail or "verified" in detail or "active" in detail

def test_transport_agencies_api(client):
    """Verify GET /api/data/providers returns authorized transit agencies."""
    response = client.get("/api/data/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert data["total_providers"] >= 10
    agency_ids = [p["id"] for p in data["providers"]]
    assert "IR" in agency_ids
    assert "KSRTC" in agency_ids
    assert "SETC" in agency_ids

def test_all_expanded_corridors(client):
    """Verify expanded national corridors return viable journeys."""
    test_corridors = [
        ("Chennai", "Pudukkottai"),
        ("Hyderabad", "Karimnagar"),
        ("Kochi", "Thiruvananthapuram"),
        ("Kolkata", "Bhubaneswar"),
        ("Ahmedabad", "Surat"),
        ("Lucknow", "Varanasi"),
        ("Coimbatore", "Salem")
    ]
    for orig, dest in test_corridors:
        res = client.post("/api/routes/search", json={"origin": orig, "destination": dest})
        assert res.status_code == 200, f"Failed for {orig} -> {dest}"
        body = res.json()
        assert body["total_results"] > 0, f"No journeys for {orig} -> {dest}"

def test_journey_timing_accuracy(client):
    """
    Verify journey duration consistency:
    Total journey duration must equal (final arrival - initial departure) taking into account overnight (+1 day).
    """
    res = client.post("/api/routes/search", json={"origin": "Chennai", "destination": "Madurai"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["journeys"]) > 0
    for j in data["journeys"]:
        dep_parts = list(map(int, j["scheduled_departure"].split(":")))
        arr_parts = list(map(int, j["scheduled_arrival"].split(":")))
        dep_min = dep_parts[0] * 60 + dep_parts[1]
        arr_min = arr_parts[0] * 60 + arr_parts[1]
        if j.get("is_overnight"):
            arr_min += 24 * 60
        expected_duration = arr_min - dep_min
        assert j["scheduled_duration_min"] == expected_duration
        assert "transfer_waiting_time_min" in j
        assert "in_vehicle_duration_min" in j

def test_dynamic_nine_user_test_corridors(client):
    """
    Validate that the application dynamically plans journeys across all 9 user test corridors:
    Hyderabad -> Tirupati, Madurai -> Bengaluru, Coimbatore -> Hyderabad,
    Pudukkottai -> Chennai, Vijayawada -> Mumbai, Delhi -> Kochi,
    Jaipur -> Ahmedabad, Lucknow -> Varanasi, Mysuru -> Pune.
    """
    nine_corridors = [
        ("Hyderabad", "Tirupati"),
        ("Madurai", "Bengaluru"),
        ("Coimbatore", "Hyderabad"),
        ("Pudukkottai", "Chennai"),
        ("Vijayawada", "Mumbai"),
        ("Delhi", "Kochi"),
        ("Jaipur", "Ahmedabad"),
        ("Lucknow", "Varanasi"),
        ("Mysuru", "Pune"),
    ]
    for orig, dest in nine_corridors:
        res = client.post("/api/routes/search", json={"origin": orig, "destination": dest})
        assert res.status_code == 200, f"Search failed for {orig} -> {dest}: {res.text}"
        data = res.json()
        assert data["total_results"] > 0, f"0 results for {orig} -> {dest}"
        assert len(data["journeys"]) > 0
        assert (data.get("train_count", 0) + data.get("bus_count", 0)) > 0
        assert len(data.get("origin_resolved_stations", [])) >= 1
        assert len(data.get("destination_resolved_stations", [])) >= 1

def test_multi_station_city_candidate_resolution(client):
    """
    Verify city-level multi-station resolution:
    Resolving e.g. 'Hyderabad' retrieves all relevant stations and bus terminals (SC, HYB, KCG, MGBS_BUS).
    """
    res = client.post("/api/routes/search", json={"origin": "Hyderabad", "destination": "Tirupati"})
    assert res.status_code == 200
    data = res.json()
    resolved_orig = data.get("origin_resolved_stations", [])
    resolved_dest = data.get("destination_resolved_stations", [])
    
    # Must contain both train stations and bus terminals
    assert any(st in resolved_orig for st in ["SC", "HYB", "KCG"])
    assert "MGBS_BUS" in resolved_orig
    assert any(st in resolved_dest for st in ["TPTY", "RU"])
    assert "TPTY_BUS" in resolved_dest


