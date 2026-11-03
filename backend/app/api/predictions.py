from fastapi import APIRouter, HTTPException
from app.schemas.schemas import (
    DelayPredictionRequest, DelayPredictionResponse, MLModelInfoResponse
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/api/predictions", tags=["Delay Prediction ML"])

_pred_service_instance = None

def get_prediction_service() -> PredictionService:
    global _pred_service_instance
    if _pred_service_instance is None:
        _pred_service_instance = PredictionService()
    return _pred_service_instance

@router.post("/delay", response_model=DelayPredictionResponse)
def predict_train_delay(request: DelayPredictionRequest):
    """
    Predict expected operational arrival delay in minutes for an Indian Railways service.
    Uses pre-departure features only to prevent data leakage.
    """
    svc = get_prediction_service()
    result = svc.predict_delay(
        train_number=request.train_number,
        scheduled_dep_hour=request.scheduled_departure_hour,
        day_of_week=request.day_of_week,
        month=request.month,
        prev_segment_delay_min=request.prev_segment_delay_min or 0.0
    )

    return DelayPredictionResponse(
        train_number=result["train_number"],
        train_name=result["train_name"],
        train_type=result["train_type"],
        predicted_delay_min=result["predicted_delay_min"],
        delay_risk_level=result["delay_risk_level"],
        confidence_interval_min=result["confidence_interval_min"],
        model_version=result["model_version"],
        is_model_backed=result["is_model_backed"],
        scheduled_departure_hour=result.get("scheduled_departure_hour", request.scheduled_departure_hour)
    )

@router.get("/model-info", response_model=MLModelInfoResponse)
def get_ml_model_info():
    """Retrieve performance metrics, feature importances, and version info for the active ML model."""
    svc = get_prediction_service()
    info = svc.get_model_info()
    return MLModelInfoResponse(
        status=info["status"],
        model_name=info.get("model_name"),
        version=info.get("version"),
        algorithm=info.get("algorithm"),
        metrics=info.get("metrics"),
        training_samples=info.get("training_samples"),
        features_used=info.get("features_used"),
        corridor=info.get("corridor"),
        data_freshness=info.get("data_freshness"),
        db_registered=info.get("db_registered")
    )

