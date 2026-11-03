from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Place & Autocomplete Schemas
class PlaceResponse(BaseModel):
    id: str
    name: str
    alternate_names: Optional[str] = None
    state: str
    district: Optional[str] = None
    type: str = "city"
    place_type: Optional[str] = "city"
    population_tier: Optional[int] = 2
    latitude: float
    longitude: float
    has_transit_coverage: bool = False
    stations_count: int = 0
    display_label: str

class AutocompleteItem(BaseModel):
    id: str
    name: str
    display_name: str
    state: str
    type: str  # "city", "railway", "bus_terminal", "bus_stop", "metro"
    latitude: float
    longitude: float
    code: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None  # alias for type
    category_label: Optional[str] = None  # "City", "Railway Station", "Bus Terminal", "Metro"
    display_label: str
    subtitle: Optional[str] = None
    sub_label: Optional[str] = None  # alias for subtitle
    is_hub: Optional[bool] = False
    has_transit_coverage: bool = True

class PlaceDetailResponse(BaseModel):
    id: str
    name: str
    alternate_names: Optional[str] = None
    state: str
    district: Optional[str] = None
    place_type: str
    population_tier: int
    latitude: float
    longitude: float
    has_transit_coverage: bool
    stations: List[Dict[str, Any]] = Field(default_factory=list)

# Station Schemas
class StationResponse(BaseModel):
    id: str
    name: str
    code: Optional[str] = None
    city: str
    state: str
    latitude: float
    longitude: float
    transport_types: List[str]
    station_type: Optional[str] = "railway"
    place_id: Optional[str] = None
    is_hub: bool
    wheelchair_accessible: bool

class StationNearbyResponse(BaseModel):
    station: StationResponse
    distance_km: float

# Route Search Schemas
class RouteSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin station ID or name (e.g., 'MAS', 'Chennai Central')")
    destination: str = Field(..., description="Destination station ID or name (e.g., 'SBC', 'Bengaluru')")
    origin_display: Optional[str] = Field(None, description="Human-readable origin display label")
    destination_display: Optional[str] = Field(None, description="Human-readable destination display label")
    travel_date: Optional[str] = Field("2026-11-04", description="Journey date YYYY-MM-DD")
    departure_after: Optional[str] = Field("00:00", description="Earliest departure HH:MM")
    arrival_before: Optional[str] = Field(None, description="Latest arrival HH:MM")
    preferred_modes: Optional[List[str]] = Field(default_factory=lambda: ["train", "bus", "metro"])
    optimisation: Optional[str] = Field("fastest", description="fastest, cheapest, fewest_transfers, delay_aware")
    max_transfers: Optional[int] = Field(3, description="Maximum number of intermediate transfers")
    max_budget: Optional[float] = Field(None, description="Max fare limit in INR")

class LegResponse(BaseModel):
    from_station_id: str
    from_station_name: str
    from_station_code: Optional[str] = None
    from_latitude: Optional[float] = None
    from_longitude: Optional[float] = None
    to_station_id: str
    to_station_name: str
    to_station_code: Optional[str] = None
    to_latitude: Optional[float] = None
    to_longitude: Optional[float] = None
    mode: str
    route_id: str
    route_name: str
    trip_id: str
    distance_km: float
    scheduled_departure: str
    scheduled_arrival: str
    departure_datetime: Optional[str] = None
    arrival_datetime: Optional[str] = None
    departure_date_formatted: Optional[str] = None
    arrival_date_formatted: Optional[str] = None
    departure_time_formatted: Optional[str] = None
    arrival_time_formatted: Optional[str] = None
    duration_min: int
    transfer_wait_min: Optional[int] = 0
    fare_inr: float
    is_transfer: bool
    predicted_delay_min: float
    delay_risk_level: str
    estimated_arrival: str
    intermediate_stops: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class JourneyResponse(BaseModel):
    journey_id: str
    origin_id: str
    origin_name: str
    origin_code: Optional[str] = None
    destination_id: str
    destination_name: str
    destination_code: Optional[str] = None
    scheduled_departure: str
    scheduled_arrival: str
    departure_datetime: Optional[str] = None
    arrival_datetime: Optional[str] = None
    departure_date_formatted: Optional[str] = None
    arrival_date_formatted: Optional[str] = None
    departure_time_formatted: Optional[str] = None
    arrival_time_formatted: Optional[str] = None
    scheduled_duration_min: int
    scheduled_duration_formatted: str
    predicted_delay_min: float
    delay_risk_level: str
    estimated_arrival: str
    estimated_arrival_datetime: Optional[str] = None
    estimated_arrival_date_formatted: Optional[str] = None
    estimated_duration_min: int
    estimated_duration_formatted: str
    total_fare_inr: float
    is_fare_verified: Optional[bool] = True
    total_distance_km: float
    transfer_count: int
    transfer_waiting_time_min: Optional[int] = 0
    in_vehicle_duration_min: Optional[int] = None
    is_overnight: Optional[bool] = False
    modes: List[str]
    is_multimodal: bool
    legs: List[LegResponse]
    data_source: str
    data_freshness: str
    is_verified: bool
    tags: List[str]

class RouteSearchResponse(BaseModel):
    origin: str
    destination: str
    travel_date: str
    optimisation: str
    total_results: int
    journeys: List[JourneyResponse]
    applied_filters: Dict[str, Any]
    train_count: Optional[int] = 0
    bus_count: Optional[int] = 0
    metro_count: Optional[int] = 0
    multimodal_count: Optional[int] = 0
    origin_resolved_stations: Optional[List[str]] = None
    destination_resolved_stations: Optional[List[str]] = None

class RouteCompareRequest(BaseModel):
    origin: str
    destination: str
    journey_ids: List[str] = Field(default_factory=list)

# AI Assistant Schemas
class AIQueryRequest(BaseModel):
    prompt: str = Field(..., description="User query (e.g., 'Find the cheapest route from Chennai to Bengaluru before 9 AM')")

class AIQueryResponse(BaseModel):
    prompt: str
    parsed_parameters: Dict[str, Any]
    clarification_question: Optional[str] = None
    assistant_reply: str
    routes_found: int
    recommended_journeys: List[JourneyResponse]
    is_ai_backed: bool = True
    is_gemini_backed: Optional[bool] = None
    model_name: Optional[str] = None
    notice: Optional[str] = None

class AIExplainRequest(BaseModel):
    journey: Dict[str, Any]
    user_preference: Optional[str] = "fastest"

class AIExplainResponse(BaseModel):
    explanation: str
    is_ai_backed: bool = True
    is_gemini_backed: Optional[bool] = None
    model_name: Optional[str] = None
    notice: Optional[str] = None

# Machine Learning Delay Schemas
class DelayPredictionRequest(BaseModel):
    train_number: str = Field(..., description="Indian Railways train number (e.g. '20607', '12007', '12639')")
    scheduled_departure_hour: int = Field(7, ge=0, le=23)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    month: Optional[int] = Field(None, ge=1, le=12)
    prev_segment_delay_min: Optional[float] = Field(0.0, ge=0.0)

class DelayPredictionResponse(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    predicted_delay_min: float
    delay_risk_level: str
    confidence_interval_min: List[float]
    model_version: str
    is_model_backed: bool
    scheduled_departure_hour: int

class MLModelInfoResponse(BaseModel):
    status: str
    model_name: Optional[str] = None
    version: Optional[str] = None
    algorithm: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    training_samples: Optional[int] = None
    features_used: Optional[List[str]] = None
    corridor: Optional[str] = None
    data_freshness: Optional[str] = None
    db_registered: Optional[bool] = None

# Health & Status Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database: str
    ml_model: str
    mistral_ai: str
    gemini_ai: Optional[str] = None
    environment: str

class CorridorInfo(BaseModel):
    name: str
    cities: List[str]
    operators: List[str]
    verification_status: str
    is_active: bool

class DataCoverageResponse(BaseModel):
    supported_cities: List[str]
    supported_stations_count: int
    available_transport_modes: List[str]
    available_corridors: List[CorridorInfo]
    dataset_source: str
    last_updated: str
    data_verification_status: str
    is_demo_mode: bool
    cities_count: Optional[int] = None
    towns_count: Optional[int] = None
    railway_stations_count: Optional[int] = None
    bus_terminals_count: Optional[int] = None
    metro_stations_count: Optional[int] = None
    train_services_count: Optional[int] = None
    bus_services_count: Optional[int] = None
    metro_services_count: Optional[int] = None
    scheduled_trips_count: Optional[int] = None
    connected_components_count: Optional[int] = None
    mode_coverage: Optional[Dict[str, Any]] = None

