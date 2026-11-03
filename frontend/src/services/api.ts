import { Station, Journey, SearchFilters, SystemHealth, MLModelInfo, DatasetStatus, DataCoverage, AutocompleteItem, PlaceDetail, TransportAgency, RouteSearchResponse } from '../types';

// Connect directly to FastAPI on port 8000 when running in development browser
const isLocal = typeof window !== 'undefined' && 
  (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost');

const PRIMARY_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || (isLocal ? 'http://127.0.0.1:8000/api' : '/api');
const FALLBACK_BASE_URL = '/api';

async function fetchWithFallback(endpoint: string, options: RequestInit = {}): Promise<Response> {
  try {
    const res = await fetch(`${PRIMARY_BASE_URL}${endpoint}`, options);
    return res;
  } catch (err) {
    if (PRIMARY_BASE_URL !== FALLBACK_BASE_URL) {
      console.warn(`Primary API call to ${PRIMARY_BASE_URL}${endpoint} failed, trying fallback ${FALLBACK_BASE_URL}${endpoint}...`);
      return fetch(`${FALLBACK_BASE_URL}${endpoint}`, options);
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: async (): Promise<SystemHealth> => {
    const res = await fetchWithFallback('/health');
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  // Stations
  searchStations: async (q: string): Promise<Station[]> => {
    const res = await fetchWithFallback(`/stations/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) throw new Error('Failed to search stations');
    return res.json();
  },

  // India-Wide Places & Unified Autocomplete
  searchPlaces: async (q: string, limit: number = 10): Promise<AutocompleteItem[]> => {
    if (!q || !q.trim()) return [];
    const res = await fetchWithFallback(`/places/search?q=${encodeURIComponent(q)}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to search places');
    return res.json();
  },

  getPlaceDetails: async (placeId: string): Promise<PlaceDetail> => {
    const res = await fetchWithFallback(`/places/${encodeURIComponent(placeId)}`);
    if (!res.ok) throw new Error('Failed to get place details');
    return res.json();
  },

  getDataProviders: async (): Promise<{ providers: TransportAgency[]; total_providers: number }> => {
    const res = await fetchWithFallback('/data/providers');
    if (!res.ok) throw new Error('Failed to fetch data providers');
    return res.json();
  },

  // Routes
  searchRoutes: async (filters: SearchFilters): Promise<RouteSearchResponse> => {
    const res = await fetchWithFallback('/routes/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Route search failed with status ${res.status}`);
    }
    return res.json();
  },

  compareRoutes: async (origin: string, destination: string, journey_ids: string[]) => {
    const res = await fetchWithFallback('/routes/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination, journey_ids }),
    });
    if (!res.ok) throw new Error('Failed to compare routes');
    return res.json();
  },

  // AI Assistant
  queryAI: async (prompt: string) => {
    const res = await fetchWithFallback('/ai/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'AI query failed');
    }
    return res.json();
  },

  explainRoute: async (journey: Journey, user_preference: string = 'fastest') => {
    const res = await fetchWithFallback('/ai/explain-route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ journey, user_preference }),
    });
    if (!res.ok) throw new Error('Failed to generate route explanation');
    return res.json();
  },

  // Machine Learning
  predictDelay: async (train_number: string, scheduled_departure_hour: number = 7) => {
    const res = await fetchWithFallback('/predictions/delay', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ train_number, scheduled_departure_hour }),
    });
    if (!res.ok) throw new Error('Failed to predict train delay');
    return res.json();
  },

  getMLModelInfo: async (): Promise<MLModelInfo> => {
    const res = await fetchWithFallback('/predictions/model-info');
    if (!res.ok) throw new Error('Failed to fetch ML model metrics');
    return res.json();
  },

  // Data & Dataset Status
  getDataStatus: async (): Promise<DatasetStatus> => {
    const res = await fetchWithFallback('/data/status');
    if (!res.ok) throw new Error('Failed to fetch dataset status');
    return res.json();
  },

  getDataCoverage: async (): Promise<DataCoverage> => {
    const res = await fetchWithFallback('/data/coverage');
    if (!res.ok) throw new Error('Failed to fetch data coverage');
    return res.json();
  },

  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetchWithFallback('/data/import', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload transit dataset');
    }
    return res.json();
  }
};
