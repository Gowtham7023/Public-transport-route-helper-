from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.schemas.schemas import HealthResponse
from app.services.prediction_service import PredictionService
from app.services.mistral_service import MistralService

router = APIRouter(prefix="/api", tags=["System Health"])

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Backend service health check."""
    # Check DB
    db_status = "HEALTHY"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"UNHEALTHY ({e})"

    # Check ML model
    pred_svc = PredictionService()
    ml_status = "ACTIVE" if pred_svc.model_data else "DEGRADED (artifact missing)"

    # Check Mistral AI
    mistral_svc = MistralService()
    if mistral_svc.is_configured:
        mistral_status = f"CONFIGURED ({mistral_svc.model_name})"
    else:
        mistral_status = "OFFLINE_FALLBACK (no key provided)"

    overall = "HEALTHY" if db_status == "HEALTHY" else "DEGRADED"

    return HealthResponse(
        status=overall,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        database=db_status,
        ml_model=ml_status,
        mistral_ai=mistral_status,
        gemini_ai=mistral_status,
        environment="development"
    )
