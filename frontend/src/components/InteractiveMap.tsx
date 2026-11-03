import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Journey, Station } from '../types';

/**
 * Configurable Tile Provider Abstraction
 * Uses OpenStreetMap standard raster tiles (No CARTO API key required).
 * Adheres strictly to OSM tile usage policy (interactive user viewing only).
 */
export const MAP_TILE_CONFIG = {
  url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
  maxZoom: 19,
  minZoom: 5,
};

// Custom marker pins with high-contrast badge styling
const createCustomIcon = (color: string, label: string) => {
  return L.divIcon({
    className: 'custom-map-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 11px;
        font-family: system-ui, -apple-system, sans-serif;
      ">
        ${label}
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -14],
  });
};

interface InteractiveMapProps {
  journey: Journey | null;
  allStations?: Station[];
}

// Auto-adjust map bounds when selected journey changes, or reset to all-India overview
const MapBoundsFitter: React.FC<{ coords: [number, number][] }> = ({ coords }) => {
  const map = useMap();
  useEffect(() => {
    if (coords && coords.length > 1) {
      try {
        const bounds = L.latLngBounds(coords.map((c) => L.latLng(c[0], c[1])));
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
      } catch (e) {
        console.warn('Map bounds fit error:', e);
      }
    } else {
      map.setView([20.5937, 78.9629], 5);
    }
  }, [coords, map]);
  return null;
};

export const InteractiveMap: React.FC<InteractiveMapProps> = ({ journey, allStations = [] }) => {
  const [tileError, setTileError] = useState(false);

  // Fallback coordinate lookup if backend leg coordinates are ever missing
  const stationCoords: Record<string, [number, number]> = useMemo(() => {
    const map: Record<string, [number, number]> = {
      // Chennai
      MAS: [13.0827, 80.2755],
      MS: [13.0782, 80.2608],
      TBM: [12.9250, 80.1170],
      CMRL_CENTRAL: [13.0820, 80.2745],
      CMRL_EGMORE: [13.0785, 80.2612],
      CMRL_GUINDY: [13.0092, 80.2131],
      CMRL_AIRPORT: [12.9815, 80.1636],
      CMBT_BUS: [13.0694, 80.1948],
      KCBT_BUS: [12.8711, 80.0823],
      TNAGAR_BUS: [13.0405, 80.2337],
      AJJ: [13.0836, 79.6687],
      KPD: [12.9723, 79.1352],
      JTJ: [12.5714, 78.5772],
      BWT: [12.9972, 78.1994],
      // Bengaluru
      KJM: [13.0012, 77.6789],
      BNC: [12.9934, 77.5983],
      SBC: [12.9781, 77.5695],
      YPR: [13.0238, 77.5503],
      SMVB: [13.0084, 77.6534],
      BMRCL_MAJESTIC: [12.9757, 77.5728],
      BMRCL_MGROAD: [12.9756, 77.6066],
      BMRCL_INDIRANAGAR: [12.9783, 77.6387],
      BMRCL_BYPL: [12.9912, 77.6521],
      BMRCL_WHITEFIELD: [12.9961, 77.7610],
      KBS_BUS: [12.9768, 77.5713],
      SHANTINAGAR_BUS: [12.9542, 77.5925],
      SILKBOARD_BUS: [12.9172, 77.6228],
      ECITY_BUS: [12.8452, 77.6602],
      // Mysuru
      MYS: [12.3164, 76.6433],
      MYS_BUS: [12.3106, 76.6558],
      MANDYA: [12.5244, 76.8958],
      // Madurai
      MDU: [9.9178, 78.1121],
      MDU_BUS: [9.9430, 78.1582],
      DG: [10.3673, 77.9803],
      TPJ: [10.7942, 78.6854],
      // Coimbatore
      CBE: [11.0016, 76.9628],
      CBE_BUS: [11.0183, 76.9686],
      SA: [11.6643, 78.1460],
      ED: [11.3410, 77.7172],
      TUP: [11.1085, 77.3411],
      // Hyderabad
      SC: [17.4334, 78.5045],
      HYB: [17.3920, 78.4697],
      KCG: [17.3878, 78.5003],
      MGBS_BUS: [17.3789, 78.4815],
      WL: [17.9784, 79.5941],
      KMT: [17.2473, 80.1514],
      // Vijayawada
      BZA: [16.5186, 80.6200],
      PNBS_BUS: [16.5097, 80.6133],
      // Mumbai
      CSMT: [18.9402, 72.8356],
      DR: [19.0182, 72.8431],
      LTT: [19.0699, 72.8911],
      TNA: [19.1860, 72.9759],
      DADAR_ASIAD_BUS: [19.0191, 72.8443],
      LNL: [18.7557, 73.4091],
      // Pune
      PUNE: [18.5284, 73.8744],
      SHIVAJINAGAR_BUS: [18.5312, 73.8505],
      SWARGATE_BUS: [18.4988, 73.8584],
      // Delhi NCR
      NDLS: [28.6431, 77.2197],
      DLI: [28.6619, 77.2309],
      NZM: [28.5888, 77.2534],
      ANVT: [28.6508, 77.3153],
      KASHMERE_GATE_BUS: [28.6672, 77.2325],
      GGN: [28.4682, 77.0192],
      RE: [28.1990, 76.6180],
      // Jaipur
      JP: [26.9196, 75.7878],
      GADJ: [26.8837, 75.8012],
      SINDHI_CAMP_BUS: [26.9242, 75.8016],
      AWR: [27.5645, 76.6253],
      BKI: [27.0483, 76.5746],
      DO: [26.8924, 76.3374],
    };
    allStations.forEach((s) => {
      map[s.id] = [s.latitude, s.longitude];
    });
    return map;
  }, [allStations]);

  // Extract legs coordinates and polyline segments from FastAPI route response
  const { pathSegments, allCoords, markers } = useMemo(() => {
    if (!journey || !journey.legs || journey.legs.length === 0) {
      // Overview mode when no route is active - no fake or stale markers
      return {
        pathSegments: [],
        allCoords: [[20.5937, 78.9629]] as [number, number][],
        markers: [],
      };
    }

    const segments: Array<{ coords: [number, number][]; mode: string; leg: any }> = [];
    const coordsList: [number, number][] = [];
    const markerList: Array<{ pos: [number, number]; title: string; type: string; stopSeq: number; code?: string; time?: string }> = [];

    journey.legs.forEach((leg, i) => {
      // Use exact coordinates returned by FastAPI leg response, fallback if missing
      const fromCoord: [number, number] = (leg.from_latitude && leg.from_longitude)
        ? [leg.from_latitude, leg.from_longitude]
        : (stationCoords[leg.from_station_id] || [13.0827, 80.2755]);

      const toCoord: [number, number] = (leg.to_latitude && leg.to_longitude)
        ? [leg.to_latitude, leg.to_longitude]
        : (stationCoords[leg.to_station_id] || [12.9781, 77.5695]);

      // Build path segments with intermediate railway/transit stops
      const segCoords: [number, number][] = [fromCoord];
      if (leg.intermediate_stops && leg.intermediate_stops.length > 0) {
        leg.intermediate_stops.forEach((stop) => {
          if (stop.latitude && stop.longitude) {
            const stopPos: [number, number] = [stop.latitude, stop.longitude];
            segCoords.push(stopPos);
            coordsList.push(stopPos);
            markerList.push({
              pos: stopPos,
              title: `Stop: ${stop.station_name}`,
              code: stop.station_code || stop.station_id,
              time: stop.arrival_time ? `Arr: ${stop.arrival_time}` : undefined,
              type: 'inter',
              stopSeq: stop.stop_sequence ?? (markerList.length + 1),
            });
          }
        });
      }
      segCoords.push(toCoord);

      segments.push({
        coords: segCoords,
        mode: leg.mode,
        leg,
      });

      coordsList.push(fromCoord);
      coordsList.push(toCoord);

      // Add Origin marker for first leg
      if (i === 0) {
        markerList.push({
          pos: fromCoord,
          title: `Origin: ${leg.from_station_name}`,
          code: leg.from_station_code || leg.from_station_id,
          time: leg.scheduled_departure,
          type: 'origin',
          stopSeq: 1,
        });
      }

      // Add Stop / Destination marker
      const isLast = i === journey.legs.length - 1;
      markerList.push({
        pos: toCoord,
        title: isLast ? `Destination: ${leg.to_station_name}` : `Transfer Stop: ${leg.to_station_name}`,
        code: leg.to_station_code || leg.to_station_id,
        time: leg.scheduled_arrival,
        type: isLast ? 'dest' : 'inter',
        stopSeq: i + 2,
      });
    });

    return { pathSegments: segments, allCoords: coordsList, markers: markerList };
  }, [journey, stationCoords]);

  // Distinct styling by transport mode
  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'train':
        return '#059669'; // Emerald
      case 'bus':
        return '#D97706'; // Amber
      case 'metro':
        return '#4F46E5'; // Indigo
      default:
        return '#64748B'; // Slate dashed
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-3 shadow-sm h-[520px] relative overflow-hidden flex flex-col">
      {/* Top Legend Bar */}
      <div className="flex items-center justify-between mb-2 px-2 text-xs">
        <span className="font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
          <span>Route &amp; Network Map</span>
          {journey && (
            <span className="text-[11px] font-normal text-slate-500">
              ({journey.legs.length} segments)
            </span>
          )}
        </span>
        <div className="flex items-center space-x-3 text-[11px]">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
            <span>Train</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
            <span>Bus</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
            <span>Metro</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span>
            <span>Walk</span>
          </span>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="flex-1 w-full rounded-xl overflow-hidden relative border border-slate-100">
        {tileError && (
          <div className="absolute top-2 left-2 right-2 z-20 bg-amber-50 text-amber-900 border border-amber-200 p-2 rounded-lg text-xs">
            OpenStreetMap tiles are currently loading. Offline markers &amp; geometry remain visible.
          </div>
        )}

        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          {/* Standard OpenStreetMap Raster Tiles (No CARTO API key needed) */}
          <TileLayer
            attribution={MAP_TILE_CONFIG.attribution}
            url={MAP_TILE_CONFIG.url}
            maxZoom={MAP_TILE_CONFIG.maxZoom}
            minZoom={MAP_TILE_CONFIG.minZoom}
            eventHandlers={{
              tileerror: () => setTileError(true),
              load: () => setTileError(false),
            }}
          />

          <MapBoundsFitter coords={allCoords} />

          {/* Polyline Route Segments */}
          {pathSegments.map((seg, idx) => (
            <Polyline
              key={idx}
              positions={seg.coords}
              pathOptions={{
                color: getModeColor(seg.mode),
                weight: seg.mode === 'walk' ? 3 : 5,
                opacity: 0.9,
                dashArray: seg.mode === 'walk' ? '6, 8' : undefined,
              }}
            >
              <Popup>
                <div className="text-xs p-1 space-y-1">
                  <div className="font-bold text-slate-900 capitalize text-sm">
                    {seg.leg.mode === 'walk' ? 'Transfer Walkway' : seg.leg.route_name}
                  </div>
                  <div className="text-slate-600">
                    {seg.leg.from_station_name} &rarr; {seg.leg.to_station_name}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Dep: <strong>{seg.leg.scheduled_departure}</strong> | Arr: <strong>{seg.leg.scheduled_arrival}</strong>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Distance: {seg.leg.distance_km} km | Duration: {seg.leg.duration_min} min
                  </div>
                </div>
              </Popup>
            </Polyline>
          ))}

          {/* Station Markers */}
          {markers.map((m, idx) => {
            const iconColor =
              m.type === 'origin' ? '#059669' : m.type === 'dest' ? '#DC2626' : '#4F46E5';
            const label = m.type === 'origin' ? 'A' : m.type === 'dest' ? 'B' : String(m.stopSeq);
            return (
              <Marker key={idx} position={m.pos} icon={createCustomIcon(iconColor, label)}>
                <Popup>
                  <div className="text-xs p-1.5 space-y-0.5">
                    <p className="font-bold text-slate-900 text-sm">{m.title}</p>
                    {m.code && (
                      <p className="text-[11px] font-mono text-slate-600 font-semibold">
                        Code: {m.code}
                      </p>
                    )}
                    {m.time && (
                      <p className="text-[11px] text-slate-700">
                        Scheduled Time: <strong>{m.time}</strong>
                      </p>
                    )}
                    <p className="text-[10px] text-slate-400">
                      GPS: {m.pos[0].toFixed(4)}, {m.pos[1].toFixed(4)}
                    </p>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
};
