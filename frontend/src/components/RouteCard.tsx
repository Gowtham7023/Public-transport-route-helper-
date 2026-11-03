import React, { useState } from 'react';
import { 
  Train, Bus, Zap, Footprints, Clock, AlertTriangle, 
  ChevronDown, ChevronUp, Sparkles, ShieldCheck, CheckCircle2, 
  ArrowRight, Calendar, AlertCircle
} from 'lucide-react';
import { Journey, Leg } from '../types';
import { api } from '../services/api';

interface RouteCardProps {
  journey: Journey;
  isSelected: boolean;
  onSelect: () => void;
  isCompared: boolean;
  onToggleCompare: () => void;
}

const formatDateText = (dateFormatted?: string, isoDateTime?: string, fallback: string = ''): string => {
  if (dateFormatted) return dateFormatted;
  if (isoDateTime) {
    try {
      const dt = new Date(isoDateTime);
      if (!isNaN(dt.getTime())) {
        return dt.toLocaleDateString('en-IN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
      }
    } catch {}
  }
  return fallback;
};

export const RouteCard: React.FC<RouteCardProps> = ({
  journey,
  isSelected,
  onSelect,
  isCompared,
  onToggleCompare,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);

  const handleExplainAI = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (aiExplanation) {
      setAiExplanation(null);
      return;
    }
    setIsExplaining(true);
    try {
      const res = await api.explainRoute(journey);
      setAiExplanation(res.explanation);
    } catch (err) {
      setAiExplanation('Could not generate AI explanation. Please check backend connection.');
    } finally {
      setIsExplaining(false);
    }
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'train':
        return <Train className="w-4 h-4 text-emerald-600" />;
      case 'bus':
        return <Bus className="w-4 h-4 text-amber-600" />;
      case 'metro':
        return <Zap className="w-4 h-4 text-indigo-600" />;
      default:
        return <Footprints className="w-4 h-4 text-slate-500" />;
    }
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MODERATE':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'HIGH':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const depDate = formatDateText(journey.departure_date_formatted, journey.departure_datetime, 'Departure Date');
  const arrDate = formatDateText(journey.arrival_date_formatted, journey.arrival_datetime, depDate);

  return (
    <div
      onClick={onSelect}
      className={`bg-white rounded-2xl border transition-all cursor-pointer p-5 mb-4 ${
        isSelected
          ? 'border-emerald-500 ring-2 ring-emerald-500/20 shadow-md'
          : 'border-slate-200 hover:border-slate-300 hover:shadow-sm'
      }`}
    >
      {/* Top Header: Dynamic Badges & Compare Checkbox */}
      <div className="flex items-center justify-between gap-2 mb-4">
        <div className="flex flex-wrap items-center gap-1.5">
          {journey.tags.map((tag) => (
            <span
              key={tag}
              className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                tag === 'Fastest'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                  : tag === 'Cheapest'
                  ? 'bg-blue-100 text-blue-800 border border-blue-200'
                  : tag === 'High Punctuality'
                  ? 'bg-teal-100 text-teal-800 border border-teal-200'
                  : tag === 'Direct'
                  ? 'bg-indigo-100 text-indigo-800 border border-indigo-200'
                  : 'bg-slate-100 text-slate-700 border border-slate-200'
              }`}
            >
              {tag}
            </span>
          ))}
          {journey.is_multimodal && (
            <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 border border-purple-200">
              Multimodal ({journey.modes.join(' + ')})
            </span>
          )}
        </div>

        {/* Compare Checkbox */}
        <div className="flex items-center space-x-2" onClick={(e) => e.stopPropagation()}>
          <label className="flex items-center space-x-1.5 text-xs text-slate-500 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={isCompared}
              onChange={onToggleCompare}
              className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4 cursor-pointer"
            />
            <span className="font-medium">Compare</span>
          </label>
        </div>
      </div>

      {/* Main Timing & Price Layout with Clear Date Hierarchies */}
      <div className="grid grid-cols-12 gap-3 items-center">
        {/* Origin Departure Block */}
        <div className="col-span-4 sm:col-span-4">
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {journey.scheduled_departure}
          </div>
          {/* Departure Date Display */}
          <div className="text-[11px] sm:text-xs font-semibold text-emerald-700 mt-1 flex items-center space-x-1">
            <Calendar className="w-3 h-3 text-emerald-600 shrink-0" />
            <span className="truncate">{depDate}</span>
          </div>
          <div className="text-xs font-bold text-slate-700 uppercase mt-1 tracking-wide truncate" title={journey.origin_name}>
            {journey.origin_name} {journey.origin_code ? `(${journey.origin_code})` : ''}
          </div>
        </div>

        {/* Center Route Track & Duration */}
        <div className="col-span-4 sm:col-span-4 text-center px-1">
          <div className="text-xs font-semibold text-slate-700 mb-1 flex items-center justify-center space-x-1">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>{journey.scheduled_duration_formatted}</span>
          </div>
          <div className="relative flex items-center justify-center my-1.5">
            <div className="w-full h-0.5 bg-slate-200"></div>
            <div className="absolute flex space-x-1 bg-white px-1">
              {journey.legs
                .filter((l) => !l.is_transfer)
                .map((leg, idx) => (
                  <span key={idx} className="p-1 rounded-full bg-slate-100 shadow-2xs" title={`${leg.mode}: ${leg.route_name}`}>
                    {getModeIcon(leg.mode)}
                  </span>
                ))}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 font-medium">
            {journey.transfer_count === 0 ? (
              <span className="text-emerald-700 font-semibold">Direct</span>
            ) : (
              <span>
                {journey.transfer_count} transfer{journey.transfer_count > 1 ? 's' : ''}
                {journey.transfer_waiting_time_min && journey.transfer_waiting_time_min > 0 ? (
                  <span className="text-slate-600 font-semibold ml-1">
                    ({journey.transfer_waiting_time_min}m wait)
                  </span>
                ) : null}
              </span>
            )}
          </div>
        </div>

        {/* Destination Arrival Block & Fare */}
        <div className="col-span-4 sm:col-span-4 text-right">
          <div className="flex items-baseline justify-end space-x-1.5">
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {journey.scheduled_arrival}
            </span>
            {journey.is_overnight && (
              <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-1.5 py-0.5 rounded border border-amber-300" title="Overnight arrival on following day (+1 day)">
                +1 day
              </span>
            )}
          </div>
          {/* Arrival Date Display */}
          <div className="text-[11px] sm:text-xs font-semibold text-emerald-700 mt-1 flex items-center justify-end space-x-1">
            <Calendar className="w-3 h-3 text-emerald-600 shrink-0" />
            <span className="truncate">{arrDate}</span>
          </div>
          <div className="text-xs font-bold text-slate-700 uppercase mt-1 tracking-wide truncate" title={journey.destination_name}>
            {journey.destination_name} {journey.destination_code ? `(${journey.destination_code})` : ''}
          </div>
        </div>
      </div>

      {/* Fare and Verification Row */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-slate-500 font-medium">Total Fare:</span>
          <span className="text-lg font-extrabold text-slate-900">
            ₹{journey.total_fare_inr.toFixed(0)}
          </span>
          {journey.is_fare_verified !== false ? (
            <span className="text-[11px] text-emerald-700 font-semibold flex items-center space-x-0.5 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              <span>Verified Fare</span>
            </span>
          ) : (
            <span className="text-[11px] text-amber-700 font-semibold flex items-center space-x-0.5 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              <AlertCircle className="w-3 h-3 text-amber-600" />
              <span>Fare Incomplete / Estimate</span>
            </span>
          )}
        </div>

        <div className="text-[11px] text-slate-500">
          Distance: <strong className="text-slate-700">{journey.total_distance_km} km</strong>
        </div>
      </div>

      {/* Delay-Aware Status Banner */}
      <div className="mt-3 p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-wrap items-center justify-between text-xs gap-2">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-700">ML Train Delay Estimate:</span>
          {journey.predicted_delay_min > 0 ? (
            <span className={`px-2 py-0.5 rounded-md font-semibold border ${getRiskBadgeColor(journey.delay_risk_level)}`}>
              +{journey.predicted_delay_min} min ({journey.delay_risk_level} Risk)
            </span>
          ) : (
            <span className="text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              On Schedule (&lt;3m delay)
            </span>
          )}
        </div>
        <div className="text-slate-600">
          Estimated Arrival:{' '}
          <span className="font-bold text-slate-900">{journey.estimated_arrival}</span>{' '}
          {journey.estimated_arrival_date_formatted && journey.estimated_arrival_date_formatted !== depDate && (
            <span className="text-emerald-700 font-medium">({journey.estimated_arrival_date_formatted})</span>
          )}{' '}
          <span className="text-slate-500">({journey.estimated_duration_formatted})</span>
        </div>
      </div>

      {/* AI Explanation Box (if toggled) */}
      {aiExplanation && (
        <div className="mt-3 p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl text-xs text-slate-700 relative">
          <div className="flex items-center space-x-1.5 text-emerald-800 font-semibold mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Mistral AI Route Reasoning</span>
          </div>
          <p className="leading-relaxed whitespace-pre-line">{aiExplanation}</p>
        </div>
      )}

      {/* Action Footer: Expand Leg Details & AI Explainer */}
      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <button
          type="button"
          onClick={handleExplainAI}
          disabled={isExplaining}
          className="flex items-center space-x-1 text-emerald-600 hover:text-emerald-700 font-semibold transition"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{isExplaining ? 'Analyzing...' : aiExplanation ? 'Hide AI Explanation' : 'Explain with Mistral AI'}</span>
        </button>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setExpanded(!expanded);
          }}
          className="flex items-center space-x-1 text-slate-600 hover:text-slate-900 font-medium transition"
        >
          <span>{expanded ? 'Hide Journey Steps' : `View ${journey.legs.length} Step(s)`}</span>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expanded Step-by-Step Leg Breakdown with Explicit Dates */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-slate-200/80 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center justify-between">
            <span>Detailed Timetable &amp; Segment Breakdown</span>
            <span className="text-[11px] text-slate-400 font-normal">All times in IST (UTC+05:30)</span>
          </div>

          {journey.legs.map((leg, idx) => {
            const legDepDate = formatDateText(leg.departure_date_formatted, leg.departure_datetime, depDate);
            const legArrDate = formatDateText(leg.arrival_date_formatted, leg.arrival_datetime, legDepDate);

            return (
              <div key={idx} className="space-y-2">
                <div className="flex items-start space-x-3 text-xs bg-slate-50 p-3.5 rounded-xl border border-slate-200/70">
                  <div className="p-2 rounded-lg bg-white border border-slate-200 shadow-2xs mt-0.5 shrink-0">
                    {getModeIcon(leg.mode)}
                  </div>
                  <div className="flex-1 min-w-0 space-y-2">
                    {/* Leg Service Header & Fare */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-slate-900 text-sm">
                          {leg.mode === 'walk' ? 'Station Transfer Walkway' : leg.route_name}
                        </span>
                        <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                          {leg.mode}
                        </span>
                      </div>
                      <span className="font-bold text-slate-800">
                        {leg.fare_inr > 0 ? `₹${leg.fare_inr.toFixed(0)}` : 'Free Transfer'}
                      </span>
                    </div>

                    {/* Leg Boarding & Destination with Explicit Dates */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-700 bg-white p-2.5 rounded-lg border border-slate-100">
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Boarding</div>
                        <div className="font-bold text-slate-900">
                          {leg.from_station_name} {leg.from_station_code ? `(${leg.from_station_code})` : ''}
                        </div>
                        <div className="text-xs font-semibold text-slate-800">
                          Time: <span className="text-emerald-700 font-bold">{leg.scheduled_departure}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 flex items-center space-x-1 mt-0.5">
                          <Calendar className="w-3 h-3 text-slate-400 shrink-0" />
                          <span>{legDepDate}</span>
                        </div>
                      </div>

                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Arrival</div>
                        <div className="font-bold text-slate-900">
                          {leg.to_station_name} {leg.to_station_code ? `(${leg.to_station_code})` : ''}
                        </div>
                        <div className="text-xs font-semibold text-slate-800">
                          Time: <span className="text-emerald-700 font-bold">{leg.scheduled_arrival}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 flex items-center space-x-1 mt-0.5">
                          <Calendar className="w-3 h-3 text-slate-400 shrink-0" />
                          <span>{legArrDate}</span>
                        </div>
                      </div>
                    </div>

                    {/* Leg Metrics & Delay Info */}
                    <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500 pt-0.5">
                      <span>Duration: <strong className="text-slate-700">{leg.duration_min} min</strong></span>
                      <span>Distance: <strong className="text-slate-700">{leg.distance_km} km</strong></span>
                      {leg.predicted_delay_min > 0 && (
                        <span className="text-amber-700 font-medium bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                          Est. Delay: +{leg.predicted_delay_min}m ({leg.delay_risk_level} Risk)
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Transfer Wait Callout Between Connecting Legs */}
                {leg.transfer_wait_min && leg.transfer_wait_min > 0 ? (
                  <div className="flex items-center space-x-2 px-4 py-2 bg-indigo-50/80 border border-indigo-200/70 rounded-xl text-xs text-indigo-900 font-medium">
                    <ArrowRight className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    <span>
                      Transfer at <strong>{leg.to_station_name}</strong>: Wait <strong>{leg.transfer_wait_min} min</strong> for connection
                    </span>
                  </div>
                ) : null}
              </div>
            );
          })}

          {/* Verified Data Source Attribution */}
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
            <span>Schedule Data: <strong className="text-slate-600">{journey.data_source || 'Official National Timetables'}</strong></span>
            <span className="flex items-center space-x-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              <span>{journey.data_freshness || 'Verified 2026'}</span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
