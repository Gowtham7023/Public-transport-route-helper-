from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.models.models import Route, Station, Place
from app.schemas.schemas import (
    RouteSearchRequest, RouteSearchResponse, JourneyResponse,
    RouteCompareRequest
)
from app.services.route_engine import GraphRouteEngine

router = APIRouter(prefix="/api/routes", tags=["Routes"])

# Shared engine instance
_engine_instance = None

def get_route_engine(db: Session = Depends(get_db)) -> GraphRouteEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = GraphRouteEngine(db=db)
    return _engine_instance

def reload_engine():
    """Reload in-memory route engine graph with latest database connections."""
    global _engine_instance
    if _engine_instance is not None:
        _engine_instance.reload()

def _select_station_by_mode(stations: List[Station], preferred_modes: Optional[List[str]] = None) -> str:
    """Select canonical station among candidates based on user's preferred transit modes."""
    if not stations:
        return None

    # If bus is requested exclusively
    if preferred_modes and "bus" in preferred_modes and "train" not in preferred_modes:
        bus_sts = [s for s in stations if getattr(s, "station_type", "") in ("bus_terminal", "bus_stop") or "bus" in (s.transport_types or "")]
        if bus_sts:
            hub = next((s for s in bus_sts if s.is_hub), bus_sts[0])
            return hub.id

    # If metro is requested exclusively
    if preferred_modes and "metro" in preferred_modes and "train" not in preferred_modes and "bus" not in preferred_modes:
        metro_sts = [s for s in stations if getattr(s, "station_type", "") == "metro" or "metro" in (s.transport_types or "")]
        if metro_sts:
            hub = next((s for s in metro_sts if s.is_hub), metro_sts[0])
            return hub.id

    # Intercity train priority (backbone of national transit)
    train_sts = [s for s in stations if getattr(s, "station_type", "") == "railway" or "train" in (s.transport_types or "")]
    if train_sts:
        hub = next((s for s in train_sts if s.is_hub), train_sts[0])
        return hub.id

    # Fallback to any hub or first candidate
    hub = next((s for s in stations if s.is_hub), stations[0])
    return hub.id

from typing import List, Dict, Any, Optional, Tuple

def resolve_station_candidates(
    term: str,
    db: Session,
    preferred_modes: Optional[List[str]] = None
) -> Tuple[List[str], str]:
    """
    Intelligently resolve station code, compound label ('MAS - Name'),
    Place ID ('place_bengaluru_ka'), city name ('Madurai'),
    or transit stop name to a tuple of (List[candidate_station_ids], display_name).
    
    If the term is a city or place, retrieves ALL relevant stations/terminals
    associated with that location (railway, bus, metro) so multi-station search
    can discover all transport options across the entire network.
    """
    if not term or not str(term).strip():
        return [], ""

    term_clean = str(term).strip()
    term_lower = term_clean.lower()

    # 1. Handle Place ID directly: "place_..."
    if term_clean.startswith("place_"):
        place = db.query(Place).filter(Place.id == term_clean).first()
        if place:
            display_name = f"{place.name}, {place.state}"
            stations = db.query(Station).filter(Station.place_id == place.id).all()
            if place.associated_station_ids:
                st_ids = [s.strip() for s in place.associated_station_ids.split(",") if s.strip()]
                extra_sts = db.query(Station).filter(Station.id.in_(st_ids)).all()
                for s in extra_sts:
                    if s.id not in [x.id for x in stations]:
                        stations.append(s)
            
            # City name fallback lookup
            city_sts = db.query(Station).filter(Station.city.ilike(place.name)).all()
            for s in city_sts:
                if s.id not in [x.id for x in stations]:
                    stations.append(s)

            if not stations:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"'{place.name} ({place.state})' is verified in the India Gazetteer, but active transit service "
                        f"schedules are not yet imported into the routing graph. "
                        "Supported regions include Tamil Nadu, Karnataka, Telangana, Andhra Pradesh, Maharashtra, Delhi NCR, Rajasthan, Gujarat, Uttar Pradesh, and Kerala."
                    )
                )

            # Sort hubs first
            stations.sort(key=lambda s: (not s.is_hub, s.name))
            return [s.id for s in stations], display_name

    # 2. Check exact Station ID or Code
    st_exact = db.query(Station).filter(
        or_(Station.id.ilike(term_clean), Station.code.ilike(term_clean))
    ).first()
    if st_exact:
        code_disp = f" ({st_exact.code})" if st_exact.code and st_exact.code != st_exact.id else ""
        display_name = f"{st_exact.name}{code_disp}, {st_exact.city}"
        # Include all stations in that city so user can access all city transit options
        city_sts = db.query(Station).filter(Station.city.ilike(st_exact.city)).all()
        cand_ids = [st_exact.id] + [s.id for s in city_sts if s.id != st_exact.id]
        return cand_ids, display_name

    # 3. Handle "CODE - Name" or "ID - Name" autocomplete compound strings
    if " - " in term_clean:
        parts = term_clean.split(" - ", 1)
        code_part = parts[0].strip()
        name_part = parts[1].strip()

        st_code = db.query(Station).filter(
            or_(Station.code.ilike(code_part), Station.id.ilike(code_part))
        ).first()
        if st_code:
            code_disp = f" ({st_code.code})" if st_code.code and st_code.code != st_code.id else ""
            display_name = f"{st_code.name}{code_disp}, {st_code.city}"
            city_sts = db.query(Station).filter(Station.city.ilike(st_code.city)).all()
            cand_ids = [st_code.id] + [s.id for s in city_sts if s.id != st_code.id]
            return cand_ids, display_name

        if code_part.startswith("place_"):
            return resolve_station_candidates(code_part, db, preferred_modes)

        st_name = db.query(Station).filter(Station.name.ilike(f"%{name_part}%")).first()
        if st_name:
            code_disp = f" ({st_name.code})" if st_name.code and st_name.code != st_name.id else ""
            display_name = f"{st_name.name}{code_disp}, {st_name.city}"
            city_sts = db.query(Station).filter(Station.city.ilike(st_name.city)).all()
            cand_ids = [st_name.id] + [s.id for s in city_sts if s.id != st_name.id]
            return cand_ids, display_name

    # 4. Handle "City, State" compound strings e.g. "Madurai, Tamil Nadu"
    if "," in term_clean:
        city_part = term_clean.split(",")[0].strip()
        state_part = term_clean.split(",")[1].strip() if len(term_clean.split(",")) > 1 else ""
        pl_query = db.query(Place).filter(Place.name.ilike(city_part))
        if state_part:
            pl_query = pl_query.filter(Place.state.ilike(f"%{state_part}%"))
        pl = pl_query.first()
        if pl:
            return resolve_station_candidates(pl.id, db, preferred_modes)
        
        # Check by city name directly
        city_sts = db.query(Station).filter(Station.city.ilike(city_part)).all()
        if city_sts:
            display_name = f"{city_sts[0].city}, {city_sts[0].state}"
            city_sts.sort(key=lambda s: (not s.is_hub, s.name))
            return [s.id for s in city_sts], display_name

    # 5. Check Place record by exact or partial city name
    pl = db.query(Place).filter(
        or_(Place.name.ilike(term_clean), Place.alternate_names.ilike(f"%{term_clean}%"))
    ).first()
    if pl:
        return resolve_station_candidates(pl.id, db, preferred_modes)

    # 6. Check Station by city name match
    city_stations = db.query(Station).filter(Station.city.ilike(f"%{term_clean}%")).all()
    if city_stations:
        display_name = f"{city_stations[0].city}, {city_stations[0].state}"
        city_stations.sort(key=lambda s: (not s.is_hub, s.name))
        return [s.id for s in city_stations], display_name

    # 7. Check Station by station name substring
    name_stations = db.query(Station).filter(Station.name.ilike(f"%{term_clean}%")).all()
    if name_stations:
        st = name_stations[0]
        code_disp = f" ({st.code})" if st.code and st.code != st.id else ""
        display_name = f"{st.name}{code_disp}, {st.city}"
        city_sts = db.query(Station).filter(Station.city.ilike(st.city)).all()
        cand_ids = [s.id for s in name_stations] + [s.id for s in city_sts if s.id not in [x.id for x in name_stations]]
        return cand_ids, display_name

    return [], term_clean

def resolve_station_id(term: str, db: Session, preferred_modes: Optional[List[str]] = None) -> Optional[str]:
    """Canonical single-station resolver for backwards compatibility."""
    cand_ids, _ = resolve_station_candidates(term, db, preferred_modes)
    if not cand_ids:
        return None
    stations = db.query(Station).filter(Station.id.in_(cand_ids)).all()
    return _select_station_by_mode(stations, preferred_modes)

@router.post("/search", response_model=RouteSearchResponse)
def search_routes(
    request: RouteSearchRequest,
    db: Session = Depends(get_db),
    engine: GraphRouteEngine = Depends(get_route_engine)
):
    """
    Search multimodal routes across any connected locations in India using NetworkX Graph Engine,
    Timetable validation, Multi-Station resolution, and ML Train Delay predictions.
    """
    orig_ids, orig_disp = resolve_station_candidates(request.origin, db, request.preferred_modes)
    if not orig_ids:
        supported_cities = [c[0] for c in db.query(Station.city).distinct().all()]
        raise HTTPException(
            status_code=400,
            detail=(
                f"Transport data for origin '{request.origin}' is not yet available in the active transit network. "
                f"Currently connected hubs include: {', '.join(sorted(supported_cities)[:15])} and more. "
                "Please select an origin within the verified network."
            )
        )

    dest_ids, dest_disp = resolve_station_candidates(request.destination, db, request.preferred_modes)
    if not dest_ids:
        supported_cities = [c[0] for c in db.query(Station.city).distinct().all()]
        raise HTTPException(
            status_code=400,
            detail=(
                f"Transport data for destination '{request.destination}' is not yet available in the active transit network. "
                f"Currently connected hubs include: {', '.join(sorted(supported_cities)[:15])} and more. "
                "Please select a destination within the verified network."
            )
        )

    if request.origin.strip().lower() == request.destination.strip().lower() or (set(orig_ids) == set(dest_ids) and len(orig_ids) == 1):
        raise HTTPException(
            status_code=400,
            detail="Origin and destination cannot be identical. Please select different departure and arrival points."
        )

    res = engine.search_multimodal_journeys(
        origin_stations=orig_ids,
        dest_stations=dest_ids,
        travel_date=request.travel_date or "2026-11-04",
        dep_after=request.departure_after or "00:00",
        arrival_before=request.arrival_before,
        preferred_modes=request.preferred_modes,
        optimisation=request.optimisation or "fastest",
        max_transfers=request.max_transfers,
        max_budget=request.max_budget
    )

    return RouteSearchResponse(
        origin=orig_disp or request.origin,
        destination=dest_disp or request.destination,
        travel_date=request.travel_date or "2026-11-04",
        optimisation=request.optimisation or "fastest",
        total_results=res["total_results"],
        train_count=res["train_count"],
        bus_count=res["bus_count"],
        metro_count=res["metro_count"],
        multimodal_count=res["multimodal_count"],
        origin_resolved_stations=orig_ids,
        destination_resolved_stations=dest_ids,
        journeys=res["journeys"],
        applied_filters={
            "resolved_origin_ids": orig_ids,
            "resolved_dest_ids": dest_ids,
            "origin_display": orig_disp,
            "destination_display": dest_disp,
            "preferred_modes": request.preferred_modes,
            "departure_after": request.departure_after,
            "arrival_before": request.arrival_before,
            "max_budget": request.max_budget,
            "max_transfers": request.max_transfers
        }
    )

@router.post("/compare")
def compare_routes(
    request: RouteCompareRequest,
    db: Session = Depends(get_db),
    engine: GraphRouteEngine = Depends(get_route_engine)
):
    """Compare multiple route alternatives on cost, time, and delay-resilience."""
    orig_id = resolve_station_id(request.origin, db)
    dest_id = resolve_station_id(request.destination, db)
    if not orig_id or not dest_id:
        raise HTTPException(status_code=400, detail="Invalid origin or destination station.")

    return engine.compare_routes(
        route_ids=request.journey_ids,
        origin_id=orig_id,
        dest_id=dest_id
    )

@router.get("/{route_id}")
def get_route_details(route_id: str, db: Session = Depends(get_db)):
    """Retrieve operational details for a specific transit route/line."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail=f"Route '{route_id}' not found.")

    return {
        "id": route.id,
        "route_short_name": route.route_short_name,
        "route_long_name": route.route_long_name,
        "operator": route.operator_name,
        "mode": route.transport_mode.display_name if route.transport_mode else "Transit",
        "is_active": route.is_active,
        "trips_count": len(route.trips)
    }
