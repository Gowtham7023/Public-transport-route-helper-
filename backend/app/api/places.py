import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.models.models import Place, Station
from app.schemas.schemas import PlaceResponse, PlaceDetailResponse, AutocompleteItem
from app.services.gazetteer_service import GazetteerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/places", tags=["Places & Gazetteer"])

@router.get("/search", response_model=List[AutocompleteItem])
def search_places_and_stations(
    q: Optional[str] = Query("", description="Search term for city, town, station, or terminal"),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Unified intelligent autocomplete across Indian cities, towns,
    railway stations, bus terminals, and metro stations.
    """
    if not q or len(q.strip()) < 1:
        return []

    term = q.strip()
    term_lower = term.lower()

    items: List[AutocompleteItem] = []
    seen_ids = set()

    # 1. Search Gazetteer Places (Cities, Towns, Districts)
    gaz = GazetteerService(db=db)
    places = gaz.search_places(term, limit=limit)

    for p in places:
        sub = f"{p['state']} • {p['place_type'].replace('_', ' ').title()}" + (
            f" • {p['stations_count']} Transit Hubs" if p["has_transit_coverage"] else " • Gazetted Location"
        )
        item = AutocompleteItem(
            id=p["id"],
            name=p["name"],
            display_name=f"{p['name']}, {p['state']}, India",
            code=None,
            state=p["state"],
            city=p["name"],
            type=p["type"],  # "city"
            category=p["type"],
            category_label=p["place_type"].replace('_', ' ').title(),
            latitude=p["latitude"],
            longitude=p["longitude"],
            has_transit_coverage=p["has_transit_coverage"],
            display_label=f"{p['name']}, {p['state']}",
            subtitle=sub,
            sub_label=sub,
            is_hub=p["population_tier"] == 1
        )
        items.append(item)
        seen_ids.add(p["id"])

    # 2. Search Transit Stations (Railway, Bus Terminal, Metro)
    st_filter = or_(
        Station.name.ilike(f"%{term}%"),
        Station.code.ilike(f"%{term}%"),
        Station.city.ilike(f"%{term}%"),
        Station.id.ilike(f"%{term}%")
    )
    stations = db.query(Station).filter(st_filter).order_by(Station.is_hub.desc()).limit(limit).all()

    for st in stations:
        if st.id in seen_ids:
            continue

        st_type = st.station_type or "railway"
        type_label = {
            "railway": "Railway Station",
            "bus_terminal": "Bus Terminal",
            "bus_stop": "Bus Stop",
            "metro": "Metro Station",
            "airport": "Airport Hub"
        }.get(st_type, "Transit Stop")

        code_suffix = f" ({st.code})" if st.code and st.code != st.id else ""
        sub = f"{type_label} • {st.city}, {st.state}"
        item = AutocompleteItem(
            id=st.id,
            name=st.name,
            display_name=f"{st.name}{code_suffix}, {st.city}, {st.state}, India",
            code=st.code or st.id,
            state=st.state,
            city=st.city,
            type=st_type,
            category=st_type,
            category_label=type_label,
            latitude=st.latitude,
            longitude=st.longitude,
            has_transit_coverage=True,
            display_label=f"{st.name}{code_suffix}",
            subtitle=sub,
            sub_label=sub,
            is_hub=st.is_hub
        )
        items.append(item)
        seen_ids.add(st.id)

    # 3. Sort so exact or prefix matches come first
    def get_sort_key(it: AutocompleteItem):
        name_l = it.name.lower()
        code_l = (it.code or "").lower()
        if name_l == term_lower or code_l == term_lower:
            return 0
        if name_l.startswith(term_lower) or code_l.startswith(term_lower):
            return 1
        if it.type == "city" and it.has_transit_coverage:
            return 2
        if it.type in ["railway", "bus_terminal"]:
            return 3
        return 4

    items.sort(key=get_sort_key)
    return items[:limit]

@router.get("/{place_id}", response_model=PlaceDetailResponse)
def get_place_details(place_id: str, db: Session = Depends(get_db)):
    """Retrieve details and transit hubs for a given Place ID."""
    gaz = GazetteerService(db=db)
    details = gaz.get_place_by_id(place_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Place '{place_id}' not found in gazetteer.")
    return details
