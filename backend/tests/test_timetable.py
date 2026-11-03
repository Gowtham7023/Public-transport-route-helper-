import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.route_engine import GraphRouteEngine, time_to_minutes, minutes_to_time

@pytest.fixture(scope="module")
def engine():
    return GraphRouteEngine()

def test_time_conversion_utilities():
    assert time_to_minutes("00:00") == 0
    assert time_to_minutes("06:30") == 390
    assert time_to_minutes("23:59") == 1439
    assert minutes_to_time(390) == "06:30"
    assert minutes_to_time(0) == "00:00"

def test_departure_after_filter(engine):
    # Only trains after 15:00
    journeys = engine.search_routes("MAS", "SBC", dep_after="15:00")
    for j in journeys:
        dep_m = time_to_minutes(j["scheduled_departure"])
        assert dep_m >= time_to_minutes("15:00")

def test_arrival_before_filter(engine):
    # Journeys that arrive before 14:00
    journeys = engine.search_routes("MAS", "SBC", dep_after="05:00", arrival_before="14:00")
    for j in journeys:
        arr_m = time_to_minutes(j["scheduled_arrival"])
        assert arr_m <= time_to_minutes("14:00")

def test_multimodal_transfer_leg_ordering(engine):
    # CMRL_AIRPORT to SBC
    journeys = engine.search_routes("CMRL_AIRPORT", "SBC", dep_after="05:30")
    assert len(journeys) > 0
    for j in journeys:
        for i in range(len(j["legs"]) - 1):
            leg_a = j["legs"][i]
            leg_b = j["legs"][i + 1]
            # Leg B must start from Leg A destination
            assert leg_b["from_station_id"] == leg_a["to_station_id"]

