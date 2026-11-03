import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

class DataSource(Base):
    """Tracks origin of transit data (GTFS, CSV, Official API, Demo)."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(100), nullable=False)
    dataset_type = Column(String(50), nullable=False)  # GTFS, CSV, API, DEMO
    coverage_area = Column(String(150), nullable=False)  # e.g., "India Multi-Corridor", "Chennai Urban"
    license = Column(String(100), default="Open Transit Data / CC-BY")
    is_verified = Column(Boolean, default=True)  # True = Verified official source, False = Demo test dataset
    last_synced_at = Column(DateTime, default=datetime.datetime.utcnow)

    routes = relationship("Route", back_populates="data_source")
    imports = relationship("DatasetImport", back_populates="data_source")

class Place(Base):
    """Geographical cities, towns, and district headquarters across India."""
    __tablename__ = "places"

    id = Column(String(100), primary_key=True)  # e.g. "place_madurai_tn", "place_bengaluru_ka"
    name = Column(String(150), nullable=False, index=True)
    alternate_names = Column(String(255), nullable=True, index=True)  # e.g. "Bangalore, Bengalooru"
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    place_type = Column(String(50), default="city")  # metropolis, city, town, district_hq
    population_tier = Column(Integer, default=2)  # 1 = Tier 1, 2 = Tier 2, 3 = Town
    has_transit_coverage = Column(Boolean, default=False)
    associated_station_ids = Column(Text, nullable=True)  # Comma-separated station IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    stations = relationship("Station", back_populates="place")

    __table_args__ = (
        Index("idx_place_name_state", "name", "state"),
        Index("idx_place_lat_lon", "latitude", "longitude"),
    )

class TransportAgency(Base):
    """Transport authority or operating corporation."""
    __tablename__ = "transport_agencies"

    id = Column(String(50), primary_key=True)  # IR, KSRTC, SETC, TNSTC, CMRL, BMRCL, APSRTC, TSRTC, MSRTC
    name = Column(String(150), nullable=False)
    short_name = Column(String(50), nullable=False)
    agency_type = Column(String(50), nullable=False)  # railway, intercity_bus, city_bus, metro
    state = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

class DatasetImport(Base):
    """Audit log for imported GTFS or CSV files."""
    __tablename__ = "dataset_imports"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    file_name = Column(String(200), nullable=False)
    file_type = Column(String(50), nullable=False)  # GTFS_ZIP, CSV, GEOJSON
    records_imported = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, PARTIAL
    error_log = Column(Text, nullable=True)
    imported_at = Column(DateTime, default=datetime.datetime.utcnow)

    data_source = relationship("DataSource", back_populates="imports")

class TransportMode(Base):
    """Metadata and operational defaults for transport modes."""
    __tablename__ = "transport_modes"

    id = Column(Integer, primary_key=True, index=True)
    mode_key = Column(String(50), unique=True, nullable=False)  # train, bus, metro
    display_name = Column(String(100), nullable=False)
    average_speed_kmh = Column(Float, default=45.0)
    carbon_per_km = Column(Float, default=35.0)  # g CO2 per passenger-km
    color_hex = Column(String(20), default="#3B82F6")
    is_active = Column(Boolean, default=True)

    routes = relationship("Route", back_populates="transport_mode")

class Station(Base):
    """Physical or logical transport stops/stations/terminals."""
    __tablename__ = "stations"

    id = Column(String(50), primary_key=True)  # e.g. "MAS", "SBC", "CMRL_CENTRAL", "KBS_BUS"
    name = Column(String(150), nullable=False, index=True)
    code = Column(String(20), index=True, nullable=True)  # e.g. "MAS", "SBC"
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), default="Tamil Nadu")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    transport_types = Column(String(150), nullable=False)  # comma-separated: train,metro,bus
    station_type = Column(String(50), default="railway")  # railway, bus_terminal, bus_stop, metro, airport
    place_id = Column(String(100), ForeignKey("places.id"), nullable=True)
    is_hub = Column(Boolean, default=False)
    wheelchair_accessible = Column(Boolean, default=True)

    place = relationship("Place", back_populates="stations")
    stop_times = relationship("StopTime", back_populates="station")

    __table_args__ = (
        Index("idx_station_city_name", "city", "name"),
        Index("idx_station_lat_lon", "latitude", "longitude"),
        Index("idx_station_type", "station_type"),
    )

class Route(Base):
    """A distinct transit line or service (e.g. Vande Bharat Express, CMRL Blue Line)."""
    __tablename__ = "routes"

    id = Column(String(50), primary_key=True)  # e.g. "IR_20607", "CMRL_L1"
    route_short_name = Column(String(100), nullable=False)
    route_long_name = Column(String(200), nullable=False)
    transport_mode_id = Column(Integer, ForeignKey("transport_modes.id"), nullable=False)
    operator_name = Column(String(150), nullable=False)  # Southern Railway, CMRL, KSRTC, etc.
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    transport_mode = relationship("TransportMode", back_populates="routes")
    data_source = relationship("DataSource", back_populates="routes")
    trips = relationship("Trip", back_populates="route")

class Trip(Base):
    """A scheduled run of a route at a specific time."""
    __tablename__ = "trips"

    id = Column(String(50), primary_key=True)  # e.g. "TRIP_VB_20607_DAILY"
    route_id = Column(String(50), ForeignKey("routes.id"), nullable=False)
    service_id = Column(String(50), default="DAILY")
    trip_headsign = Column(String(150), nullable=False)
    direction_id = Column(Integer, default=0)
    scheduled_departure = Column(String(10), nullable=False)  # HH:MM
    scheduled_arrival = Column(String(10), nullable=False)  # HH:MM
    operating_days = Column(String(100), default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")  # Days of week

    route = relationship("Route", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip", cascade="all, delete-orphan")

class StopTime(Base):
    """Schedule stop on a trip."""
    __tablename__ = "stop_times"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(50), ForeignKey("trips.id"), nullable=False)
    station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    arrival_time = Column(String(10), nullable=False)  # HH:MM
    departure_time = Column(String(10), nullable=False)  # HH:MM
    distance_from_start_km = Column(Float, default=0.0)

    trip = relationship("Trip", back_populates="stop_times")
    station = relationship("Station", back_populates="stop_times")

    __table_args__ = (
        Index("idx_trip_sequence", "trip_id", "stop_sequence"),
        UniqueConstraint("trip_id", "stop_sequence", name="uq_trip_stop_seq"),
    )

class Connection(Base):
    """Pre-computed directed edge between stations for fast graph traversal."""
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    to_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    transport_mode = Column(String(50), nullable=False)  # train, bus, metro
    route_id = Column(String(50), ForeignKey("routes.id"), nullable=True)
    trip_id = Column(String(50), ForeignKey("trips.id"), nullable=True)
    distance_km = Column(Float, nullable=False)
    scheduled_duration_min = Column(Integer, nullable=False)
    departure_time = Column(String(10), nullable=False)  # HH:MM
    arrival_time = Column(String(10), nullable=False)  # HH:MM
    fare_inr = Column(Float, nullable=True)
    operating_days = Column(String(100), default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")

    __table_args__ = (
        Index("idx_conn_from_to", "from_station_id", "to_station_id"),
        Index("idx_conn_mode", "transport_mode"),
    )

class Transfer(Base):
    """Walking or internal interchange between proximate stations/platforms."""
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    to_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    transfer_type = Column(String(50), default="WALK")  # WALK, INTERCHANGE_SUBWAY, SHUTTLE
    min_transfer_time_min = Column(Integer, default=10)
    distance_meters = Column(Integer, default=200)
    walking_route_notes = Column(String(255), default="Follow concourse signs")

    __table_args__ = (
        Index("idx_transfer_stations", "from_station_id", "to_station_id"),
    )

class Fare(Base):
    """Fare chart entry between station pairs by service/class."""
    __tablename__ = "fares"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(50), ForeignKey("routes.id"), nullable=True)
    from_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    to_station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    fare_class = Column(String(50), default="STANDARD")  # 2S, CC, EC, SLEEPER, AC3, METRO_TOKEN
    amount_inr = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    data_freshness = Column(String(50), default="VERIFIED_2026")

    __table_args__ = (
        Index("idx_fare_route_stations", "from_station_id", "to_station_id"),
    )

class DelayPrediction(Base):
    """Historical or stored machine learning delay predictions."""
    __tablename__ = "delay_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    train_number = Column(String(50), nullable=False, index=True)
    station_id = Column(String(50), ForeignKey("stations.id"), nullable=False)
    scheduled_time = Column(String(10), nullable=False)
    predicted_delay_min = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    delay_risk_level = Column(String(20), default="LOW")  # LOW, MODERATE, HIGH
    model_version = Column(String(50), default="hist_gradient_boosting_v1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MLModelVersion(Base):
    """Registry of trained machine learning model artifacts."""
    __tablename__ = "ml_model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False, unique=True)
    algorithm = Column(String(100), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    training_records_count = Column(Integer, default=0)
    artifact_path = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

