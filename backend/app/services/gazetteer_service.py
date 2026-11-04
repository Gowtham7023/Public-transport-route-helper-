import os
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database.connection import SessionLocal
from app.models.models import Place, Station

logger = logging.getLogger(__name__)

def get_gazetteer_path() -> str:
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "gazetteer", "india_places.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "gazetteer", "india_places.json"),
        "data/gazetteer/india_places.json",
        "../data/gazetteer/india_places.json",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

GAZETTEER_PATH = get_gazetteer_path()

class GazetteerService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def close(self):
        if self.db:
            self.db.close()

    def seed_places_if_empty(self) -> int:
        """Seed places table from india_places.json if empty."""
        count = self.db.query(Place).count()
        if count > 0:
            logger.info(f"Gazetteer already contains {count} Indian places.")
            self.refresh_transit_coverage_flags()
            return count

        if not os.path.exists(GAZETTEER_PATH):
            logger.warning(f"Gazetteer file not found at: {GAZETTEER_PATH}")
            return 0

        logger.info(f"Seeding Indian places gazetteer from: {GAZETTEER_PATH}")
        try:
            with open(GAZETTEER_PATH, "r", encoding="utf-8") as f:
                places_data = json.load(f)

            places = []
            for p in places_data:
                place = Place(
                    id=p["id"],
                    name=p["name"],
                    alternate_names=p.get("alternate_names", ""),
                    state=p["state"],
                    district=p.get("district", ""),
                    latitude=float(p["latitude"]),
                    longitude=float(p["longitude"]),
                    place_type=p.get("place_type", "city"),
                    population_tier=int(p.get("population_tier", 2)),
                    has_transit_coverage=False,
                    associated_station_ids=""
                )
                places.append(place)

            self.db.bulk_save_objects(places)
            self.db.commit()
            logger.info(f"Successfully seeded {len(places)} places across India.")
            self.refresh_transit_coverage_flags()
            return len(places)
        except Exception as e:
            logger.error(f"Error seeding gazetteer: {e}", exc_info=True)
            self.db.rollback()
            return 0

    def refresh_transit_coverage_flags(self):
        """Map active stations to places and update has_transit_coverage."""
        try:
            stations = self.db.query(Station).all()
            places = self.db.query(Place).all()
            place_dict = {p.name.lower(): p for p in places}

            place_stations_map: Dict[str, List[str]] = {}

            for st in stations:
                st_city = st.city.lower() if st.city else ""
                matched_place = place_dict.get(st_city)
                if not matched_place:
                    # Try partial match
                    for p_name, p_obj in place_dict.items():
                        if p_name in st_city or st_city in p_name:
                            matched_place = p_obj
                            break

                if matched_place:
                    if matched_place.id not in place_stations_map:
                        place_stations_map[matched_place.id] = []
                    place_stations_map[matched_place.id].append(st.id)
                    st.place_id = matched_place.id

            for p in places:
                st_ids = place_stations_map.get(p.id, [])
                if st_ids:
                    p.has_transit_coverage = True
                    p.associated_station_ids = ",".join(st_ids)

            self.db.commit()
            logger.info(f"Updated transit coverage for {len(place_stations_map)} places with active stations.")
        except Exception as e:
            logger.warning(f"Notice while refreshing transit flags: {e}")
            self.db.rollback()

    def search_places(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Intelligently search places with prefix matching, substring,
        alternate names, and ranking based on population tier and transit coverage.
        """
        if not query or len(query.strip()) < 1:
            return []

        q = query.strip()
        q_lower = q.lower()

        # Query candidates
        filter_cond = or_(
            Place.name.ilike(f"%{q}%"),
            Place.alternate_names.ilike(f"%{q}%"),
            Place.state.ilike(f"%{q}%"),
            Place.district.ilike(f"%{q}%"),
            Place.id.ilike(f"%{q}%")
        )

        candidates = self.db.query(Place).filter(filter_cond).all()

        # Score & rank candidates
        scored = []
        for p in candidates:
            score = 0
            name_lower = p.name.lower()
            alt_lower = (p.alternate_names or "").lower()

            # Exact name match gets highest score
            if name_lower == q_lower:
                score += 100
            elif name_lower.startswith(q_lower):
                score += 80
            elif alt_lower and any(alt.strip().startswith(q_lower) for alt in alt_lower.split(",")):
                score += 70
            elif q_lower in name_lower:
                score += 50
            elif q_lower in alt_lower:
                score += 40
            else:
                score += 20

            # Boost cities with verified transit coverage
            if p.has_transit_coverage:
                score += 30

            # Boost population tier (Tier 1 > Tier 2 > Tier 3)
            tier_bonus = {1: 25, 2: 15, 3: 5}.get(p.population_tier, 5)
            score += tier_bonus

            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for _, p in scored[:limit]:
            st_count = len(p.associated_station_ids.split(",")) if p.associated_station_ids else 0
            results.append({
                "id": p.id,
                "name": p.name,
                "alternate_names": p.alternate_names,
                "state": p.state,
                "district": p.district,
                "type": "city",
                "place_type": p.place_type,
                "population_tier": p.population_tier,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "has_transit_coverage": p.has_transit_coverage,
                "stations_count": st_count,
                "display_label": f"{p.name}, {p.state}"
            })

        return results

    def get_place_by_id(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve place details and linked stations."""
        p = self.db.query(Place).filter(Place.id == place_id).first()
        if not p:
            return None

        station_records = []
        if p.associated_station_ids:
            st_ids = [s.strip() for s in p.associated_station_ids.split(",") if s.strip()]
            stations = self.db.query(Station).filter(Station.id.in_(st_ids)).all()
            for st in stations:
                station_records.append({
                    "id": st.id,
                    "name": st.name,
                    "code": st.code,
                    "station_type": st.station_type or "railway",
                    "transport_types": st.transport_types.split(","),
                    "latitude": st.latitude,
                    "longitude": st.longitude,
                    "is_hub": st.is_hub
                })

        return {
            "id": p.id,
            "name": p.name,
            "alternate_names": p.alternate_names,
            "state": p.state,
            "district": p.district,
            "place_type": p.place_type,
            "population_tier": p.population_tier,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "has_transit_coverage": p.has_transit_coverage,
            "stations": station_records
        }
