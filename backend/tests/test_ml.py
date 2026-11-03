import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.prediction_service import PredictionService

@pytest.fixture(scope="module")
def ml_service():
    return PredictionService()

def test_ml_model_loaded(ml_service):
    info = ml_service.get_model_info()
    assert info["status"] == "ACTIVE"
    assert "metrics" in info
    assert info["metrics"]["mean_absolute_error_minutes"] < 10.0

def test_predict_delay_vande_bharat(ml_service):
    pred = ml_service.predict_delay("20607", scheduled_dep_hour=6)
    assert pred["train_type"] == "VANDE_BHARAT"
    assert pred["predicted_delay_min"] >= 0.0
    assert pred["delay_risk_level"] in ["LOW", "MODERATE", "HIGH"]
    assert len(pred["confidence_interval_min"]) == 2
    assert pred["confidence_interval_min"][0] <= pred["confidence_interval_min"][1]

def test_predict_delay_mail_express(ml_service):
    pred = ml_service.predict_delay("12657", scheduled_dep_hour=22)
    assert pred["train_type"] == "MAIL_EXPRESS"
    assert pred["predicted_delay_min"] >= 0.0

def test_predict_delay_unknown_train_fallback(ml_service):
    pred = ml_service.predict_delay("99999", scheduled_dep_hour=10)
    assert pred["predicted_delay_min"] >= 0.0

