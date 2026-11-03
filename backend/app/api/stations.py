import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.models.models import Station
from app.schemas.schemas import StationResponse, StationNearbyResponse

router = APIRouter(prefix="/api/stations", tags=["Stations"])

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@router.get("/search", response_model=List[StationResponse])
def search_stations(
    q: Optional[str] = Query("", description="Query string for station name, code, or city"),
    city: Optional[str] = Query(None, description="Optional city filter"),
    mode: Optional[str] = Query(None, description="Filter by transport type (train, metro, bus)"),
    db: Session = Depends(get_db)
):
    """Database-backed station autocomplete and search."""
    query = db.query(Station)

    if q and q.strip():
        term = q.strip().lower()
        search_terms = [f"%{term}%"]
        # Handle common city synonyms
        if "bangalore" in term:
            search_terms.append("%bengaluru%")
        elif "bengaluru" in term:
            search_terms.append("%bangalore%")
        if "madras" in term:
            search_terms.append("%chennai%")

        filters = []
        for t in search_terms:
            filters.extend([
                Station.name.ilike(t),
                Station.code.ilike(t),
                Station.city.ilike(t),
                Station.id.ilike(t)
            ])
        query = query.filter(or_(*filters))

    if city and city.strip():
        c_term = city.strip().lower()
        if "bangalore" in c_term or "bengaluru" in c_term:
            query = query.filter(or_(Station.city.ilike("%bengaluru%"), Station.city.ilike("%bangalore%")))
        else:
            query = query.filter(Station.city.ilike(f"%{c_term}%"))

    if mode and mode.strip():
        query = query.filter(Station.transport_types.ilike(f"%{mode.strip()}%"))

    stations = query.order_by(Station.is_hub.desc(), Station.name.asc()).limit(30).all()

    return [
        StationResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            city=s.city,
            state=s.state,
            latitude=s.latitude,
            longitude=s.longitude,
            transport_types=s.transport_types.split(","),
            is_hub=s.is_hub,
            wheelchair_accessible=s.wheelchair_accessible
        )
        for s in stations
    ]

@router.get("/nearby", response_model=List[StationNearbyResponse])
def get_nearby_stations(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(15.0, description="Radius in km", ge=0.5, le=100.0),
    db: Session = Depends(get_db)
):
    """Find stations proximate to given GPS coordinates."""
    all_stations = db.query(Station).all()
    results = []

    for s in all_stations:
        dist = haversine_distance_km(lat, lon, s.latitude, s.longitude)
        if dist <= radius_km:
            results.append(
                StationNearbyResponse(
                    station=StationResponse(
                        id=s.id,
                        name=s.name,
                        code=s.code,
                        city=s.city,
                        state=s.state,
                        latitude=s.latitude,
                        longitude=s.longitude,
                        transport_types=s.transport_types.split(","),
                        is_hub=s.is_hub,
                        wheelchair_accessible=s.wheelchair_accessible
                    ),
                    distance_km=dist
                )
            )

    return sorted(results, key=lambda x: x.distance_km)

@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific station by ID or Code."""
    st = db.query(Station).filter(
        or_(Station.id == station_id, Station.code == station_id)
    ).first()
    if not st:
        raise HTTPException(status_code=404, detail=f"Station with ID or Code '{station_id}' not found.")

    return StationResponse(
        id=st.id,
        name=st.name,
        code=st.code,
        city=st.city,
        state=st.state,
        latitude=st.latitude,
        longitude=st.longitude,
        transport_types=st.transport_types.split(","),
        is_hub=st.is_hub,
        wheelchair_accessible=st.wheelchair_accessible
    )
