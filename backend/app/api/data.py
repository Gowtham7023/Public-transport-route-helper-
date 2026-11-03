from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.transport_data_service import TransportDataService
from app.schemas.schemas import DataCoverageResponse

router = APIRouter(prefix="/api/data", tags=["Data Management"])

@router.get("/status")
def get_data_status(db: Session = Depends(get_db)):
    """Audit status of transport datasets, verification levels, and record counts."""
    svc = TransportDataService(db=db)
    return svc.get_system_status()

@router.get("/coverage", response_model=DataCoverageResponse)
def get_data_coverage(db: Session = Depends(get_db)):
    """Dynamic data coverage returning supported cities, corridors, modes, and verification state."""
    svc = TransportDataService(db=db)
    return svc.get_data_coverage()

@router.get("/providers")
def get_data_providers(db: Session = Depends(get_db)):
    """Return all verified transport agencies and dataset providers."""
    svc = TransportDataService(db=db)
    providers = svc.get_providers()
    return {
        "providers": providers,
        "total_providers": len(providers)
    }

@router.post("/reload")
def reload_transit_graph():
    """Trigger reload of the in-memory multimodal routing graph."""
    from app.api.routes import reload_engine
    reload_engine()
    return {"success": True, "message": "Multimodal routing graph reloaded successfully."}

@router.post("/import")
async def import_dataset(
    file: UploadFile = File(..., description="GTFS ZIP archive or CSV dataset"),
    db: Session = Depends(get_db)
):
    """
    Import transit datasets (GTFS ZIP or CSV).
    Validates station coordinates within India bounds and logs audit trail.
    """
    if not file.filename.endswith((".zip", ".csv")):
        raise HTTPException(status_code=400, detail="Only .zip (GTFS archive) or .csv files are supported.")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 50MB maximum limit.")

    svc = TransportDataService(db=db)
    result = svc.import_gtfs_or_csv(content, file.filename)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Import failed."))

    from app.api.routes import reload_engine
    reload_engine()

    return result

