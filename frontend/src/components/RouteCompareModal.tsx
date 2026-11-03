import React from 'react';
import { X, Check, Clock, ShieldAlert, Award, DollarSign } from 'lucide-react';
import { Journey } from '../types';

interface RouteCompareModalProps {
  isOpen: boolean;
  onClose: () => void;
  journeys: Journey[];
}

export const RouteCompareModal: React.FC<RouteCompareModalProps> = ({
  isOpen,
  onClose,
  journeys,
}) => {
  if (!isOpen || journeys.length === 0) return null;

  const minFare = Math.min(...journeys.map((j) => j.total_fare_inr));
  const minTime = Math.min(...journeys.map((j) => j.scheduled_duration_min));
  const minDelay = Math.min(...journeys.map((j) => j.predicted_delay_min));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Compare Route Alternatives</h2>
            <p className="text-xs text-slate-500">Side-by-side trade-off matrix: Cost, Duration &amp; ML Delay Risk</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Comparison Table */}
        <div className="flex-1 overflow-x-auto p-6">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="py-3 px-4 font-bold text-slate-400 uppercase tracking-wider w-1/4">
                  Feature / Metric
                </th>
                {journeys.map((j, idx) => (
                  <th key={idx} className="py-3 px-4 font-bold text-slate-900 text-sm">
                    Option {idx + 1}
                    <div className="text-xs font-normal text-slate-500">
                      {j.legs[0]?.route_name || j.journey_id.slice(0, 16)}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {/* Departure & Arrival */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Departure &rarr; Arrival</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4 font-bold text-slate-900">
                    {j.scheduled_departure} &rarr; {j.scheduled_arrival}
                  </td>
                ))}
              </tr>

              {/* Scheduled Duration */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Scheduled Duration</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4">
                    <span className="font-semibold text-slate-900">{j.scheduled_duration_formatted}</span>
                    {j.scheduled_duration_min === minTime && (
                      <span className="ml-2 px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                        Fastest
                      </span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Total Fare */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Total Fare (INR)</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4 font-bold text-slate-900 text-sm">
                    ₹{j.total_fare_inr.toFixed(0)}
                    {j.total_fare_inr === minFare && (
                      <span className="ml-2 px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold text-[10px]">
                        Cheapest
                      </span>
                    )}
                  </td>
                ))}
              </tr>

              {/* ML Predicted Delay */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">ML Predicted Delay</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4">
                    <span className="font-semibold text-slate-900">+{j.predicted_delay_min} min</span>
                    {j.predicted_delay_min === minDelay && (
                      <span className="ml-2 px-2 py-0.5 rounded bg-teal-100 text-teal-800 font-bold text-[10px]">
                        Lowest Delay
                      </span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Delay-Aware Estimated Arrival */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Estimated Arrival (Delay-Aware)</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4 font-bold text-emerald-700">
                    {j.estimated_arrival} ({j.estimated_duration_formatted})
                  </td>
                ))}
              </tr>

              {/* Delay Risk Level */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Delay Risk Level</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded font-bold text-[11px] ${
                        j.delay_risk_level === 'LOW'
                          ? 'bg-emerald-100 text-emerald-800'
                          : j.delay_risk_level === 'MODERATE'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {j.delay_risk_level}
                    </span>
                  </td>
                ))}
              </tr>

              {/* Transfers */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Transfers</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4 font-medium text-slate-800">
                    {j.transfer_count === 0 ? 'Direct (0 transfers)' : `${j.transfer_count} transfer(s)`}
                  </td>
                ))}
              </tr>

              {/* Modes Involved */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Transport Modes</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4 capitalize font-medium text-slate-700">
                    {j.modes.join(', ')}
                  </td>
                ))}
              </tr>

              {/* Tags */}
              <tr>
                <td className="py-3 px-4 font-semibold text-slate-600">Key Advantages</td>
                {journeys.map((j, idx) => (
                  <td key={idx} className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {j.tags.map((t) => (
                        <span key={t} className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px]">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 text-right">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 text-white font-semibold text-xs hover:bg-slate-800 transition"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
};

