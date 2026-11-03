import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.mistral_service import MistralService

@pytest.fixture(scope="module")
def ai_svc():
    return MistralService()

def test_offline_nlp_extraction(ai_svc):
    prompt = "Cheapest train from Chennai Central to Bangalore tomorrow before 10 AM"
    parsed = ai_svc._offline_nlp_parse(prompt)
    assert parsed["origin_station_id"] == "MAS"
    assert parsed["destination_station_id"] == "SBC"
    assert parsed["optimisation"] == "cheapest"
    assert "train" in parsed["preferred_modes"]

def test_missing_destination_clarification(ai_svc):
    prompt = "I want to start from Chennai"
    parsed = ai_svc._offline_nlp_parse(prompt)
    assert parsed["origin_station_id"] == "MAS"
    assert parsed["clarification_question"] is not None

def test_explain_route_generation(ai_svc):
    sample_journey = {
        "scheduled_duration_formatted": "4h 45m",
        "total_fare_inr": 145.0,
        "transfer_count": 0,
        "delay_risk_level": "LOW",
        "predicted_delay_min": 5.0,
        "total_distance_km": 358.5,
        "modes": ["train"]
    }
    exp = ai_svc.explain_route(sample_journey, "fastest")
    assert "explanation" in exp
    assert len(exp["explanation"]) > 30

def test_mistral_configured(ai_svc):
    assert ai_svc.is_configured is True
    assert ai_svc.model_name == "codestral-latest"
