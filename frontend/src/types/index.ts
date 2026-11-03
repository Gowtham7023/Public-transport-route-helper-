export interface Station {
  id: string;
  name: string;
  code?: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
  transport_types: string[];
  station_type?: string;
  place_id?: string;
  is_hub: boolean;
  wheelchair_accessible: boolean;
}

export interface AutocompleteItem {
  id: string;
  name: string;
  display_name: string;
  display_label: string;
  sub_label?: string;
  subtitle?: string;
  category?: 'city' | 'railway' | 'bus_terminal' | 'bus_stop' | 'metro';
  category_label?: string;
  type?: string;
  city?: string;
  state: string;
  code?: string;
  latitude: number;
  longitude: number;
  is_hub?: boolean;
  has_transit_coverage?: boolean;
}

export interface PlaceDetail {
  id: string;
  name: string;
  state: string;
  district?: string;
  latitude: number;
  longitude: number;
  place_type: string;
  population_tier: number;
  has_transit_coverage: boolean;
  stations: Array<{
    id: string;
    name: string;
    code?: string;
    station_type: string;
    is_hub: boolean;
  }>;
}

export interface TransportAgency {
  id: string;
  name: string;
  short_name: string;
  agency_type: string;
  state?: string;
  website?: string;
}

export interface IntermediateStop {
  station_id: string;
  station_name: string;
  station_code?: string;
  latitude: number;
  longitude: number;
  arrival_time?: string;
  departure_time?: string;
  stop_sequence?: number;
}

export interface Leg {
  from_station_id: string;
  from_station_name: string;
  from_station_code?: string;
  from_latitude?: number;
  from_longitude?: number;
  to_station_id: string;
  to_station_name: string;
  to_station_code?: string;
  to_latitude?: number;
  to_longitude?: number;
  mode: 'train' | 'bus' | 'metro' | 'walk';
  route_id: string;
  route_name: string;
  trip_id: string;
  distance_km: number;
  scheduled_departure: string;
  scheduled_arrival: string;
  departure_datetime?: string;
  arrival_datetime?: string;
  departure_date_formatted?: string;
  arrival_date_formatted?: string;
  departure_time_formatted?: string;
  arrival_time_formatted?: string;
  duration_min: number;
  transfer_wait_min?: number;
  fare_inr: number;
  is_transfer: boolean;
  predicted_delay_min: number;
  delay_risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  estimated_arrival: string;
  intermediate_stops?: IntermediateStop[];
}

export interface Journey {
  journey_id: string;
  origin_id: string;
  origin_name: string;
  origin_code?: string;
  destination_id: string;
  destination_name: string;
  destination_code?: string;
  scheduled_departure: string;
  scheduled_arrival: string;
  departure_datetime?: string;
  arrival_datetime?: string;
  departure_date_formatted?: string;
  arrival_date_formatted?: string;
  departure_time_formatted?: string;
  arrival_time_formatted?: string;
  scheduled_duration_min: number;
  scheduled_duration_formatted: string;
  predicted_delay_min: number;
  delay_risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  estimated_arrival: string;
  estimated_arrival_datetime?: string;
  estimated_arrival_date_formatted?: string;
  estimated_duration_min: number;
  estimated_duration_formatted: string;
  total_fare_inr: number;
  is_fare_verified?: boolean;
  total_distance_km: number;
  transfer_count: number;
  transfer_waiting_time_min?: number;
  in_vehicle_duration_min?: number;
  is_overnight?: boolean;
  modes: string[];
  is_multimodal: boolean;
  legs: Leg[];
  data_source: string;
  data_freshness: string;
  is_verified: boolean;
  tags: string[];
}

export interface SearchFilters {
  origin: string;
  destination: string;
  origin_display?: string;
  destination_display?: string;
  travel_date: string;
  departure_after: string;
  arrival_before?: string;
  preferred_modes: string[];
  optimisation: 'fastest' | 'cheapest' | 'fewest_transfers' | 'delay_aware';
  max_transfers?: number;
  max_budget?: number;
}

export interface SystemHealth {
  status: string;
  timestamp: string;
  version: string;
  database: string;
  ml_model: string;
  mistral_ai?: string;
  gemini_ai?: string;
  environment: string;
}

export interface MLModelInfo {
  status: string;
  model_name?: string;
  version?: string;
  algorithm?: string;
  metrics?: {
    mean_absolute_error_minutes: number;
    root_mean_squared_error_minutes: number;
    r2_score: number;
  };
  training_samples?: number;
  features_used?: string[];
  corridor?: string;
  data_freshness?: string;
  db_registered?: boolean;
}

export interface DataCoverage {
  supported_cities: string[];
  supported_stations_count: number;
  available_transport_modes: string[];
  available_corridors: Array<{
    name: string;
    cities: string[];
    operators: string[];
    verification_status: string;
    is_active: boolean;
  }>;
  dataset_source: string;
  last_updated: string;
  data_verification_status: string;
  is_demo_mode: boolean;
}

export interface RouteSearchResponse {
  origin: string;
  destination: string;
  travel_date: string;
  optimisation: string;
  total_results: number;
  train_count?: number;
  bus_count?: number;
  metro_count?: number;
  multimodal_count?: number;
  origin_resolved_stations?: string[];
  destination_resolved_stations?: string[];
  journeys: Journey[];
  applied_filters?: Record<string, any>;
}

export interface DatasetStatus {
  status: string;
  counts: {
    stations: number;
    routes: number;
    trips: number;
    connections: number;
    transfers: number;
    fares: number;
    places?: number;
    agencies?: number;
    railway_stations?: number;
    bus_terminals?: number;
    metro_stations?: number;
  };
  data_sources: Array<{
    id: number;
    name: string;
    provider: string;
    dataset_type: string;
    coverage_area: string;
    is_verified: boolean;
    last_synced?: string;
  }>;
  recent_imports: Array<{
    id: number;
    file_name: string;
    records_imported: number;
    status: string;
    imported_at?: string;
  }>;
  corridor: string;
  is_production_ready: boolean;
}

