import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.route_engine import GraphRouteEngine

@pytest.fixture(scope="module")
def engine():
    return GraphRouteEngine()

def test_graph_has_nodes_and_edges(engine):
    assert engine.graph.number_of_nodes() >= 20
    assert engine.graph.number_of_edges() >= 50

def test_direct_route_search(engine):
    journeys = engine.search_routes("MAS", "SBC", dep_after="05:00", optimisation="fastest")
    assert len(journeys) > 0
    first = journeys[0]
    assert first["origin_id"] == "MAS"
    assert first["destination_id"] == "SBC"
    assert first["scheduled_duration_min"] > 0
    assert first["total_fare_inr"] > 0

def test_multiple_alternative_routes(engine):
    journeys = engine.search_routes("MAS", "SBC", dep_after="05:00")
    assert len(journeys) >= 3  # Shatabdi, Brindavan, Mail, etc.

def test_cheapest_vs_fastest_ranking(engine):
    fastest = engine.search_routes("MAS", "SBC", optimisation="fastest")
    cheapest = engine.search_routes("MAS", "SBC", optimisation="cheapest")
    assert len(fastest) > 0
    assert len(cheapest) > 0
    assert cheapest[0]["total_fare_inr"] <= fastest[0]["total_fare_inr"]

def test_unreachable_destination(engine):
    # Non-existent node
    journeys = engine.search_routes("MAS", "NON_EXISTENT_STATION")
    assert journeys == []

def test_non_negative_edge_weights(engine):
    for u, v, k, data in engine.graph.edges(keys=True, data=True):
        assert data.get("duration_min", 0) >= 0
        assert data.get("fare_inr", 0) >= 0
        assert data.get("distance_km", 0) >= 0

