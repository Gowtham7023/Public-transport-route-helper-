import React, { useState } from 'react';
import { 
  Sparkles, SlidersHorizontal, Train, Bus, Zap, 
  Layers, ArrowUpDown, ShieldCheck, AlertCircle, RefreshCw, Compass 
} from 'lucide-react';
import { SearchForm } from '../components/SearchForm';
import { RouteCard } from '../components/RouteCard';
import { InteractiveMap } from '../components/InteractiveMap';
import { AiAssistantModal } from '../components/AiAssistantModal';
import { RouteCompareModal } from '../components/RouteCompareModal';
import { api } from '../services/api';
import { Journey, SearchFilters, Station } from '../types';

interface HomePageProps {
  isAIOpen: boolean;
  setIsAIOpen: (open: boolean) => void;
}

const POPULAR_CORRIDORS = [
  { label: 'Chennai ↔ Madurai', orig: 'Chennai', dest: 'Madurai', orig_disp: 'Chennai, Tamil Nadu', dest_disp: 'Madurai, Tamil Nadu', desc: 'Tejas, Pandian Express, SETC Ultra Deluxe' },
  { label: 'Bengaluru ↔ Mysuru', orig: 'Bengaluru', dest: 'Mysuru', orig_disp: 'Bengaluru, Karnataka', dest_disp: 'Mysuru, Karnataka', desc: 'Vande Bharat, Tipu Express, KSRTC Airavat' },
  { label: 'Chennai ↔ Bengaluru', orig: 'Chennai', dest: 'Bengaluru', orig_disp: 'Chennai, Tamil Nadu', dest_disp: 'Bengaluru, Karnataka', desc: 'Shatabdi, Vande Bharat, KSRTC, SETC, Metro' },
  { label: 'Chennai ↔ Coimbatore', orig: 'Chennai', dest: 'Coimbatore', orig_disp: 'Chennai, Tamil Nadu', dest_disp: 'Coimbatore, Tamil Nadu', desc: 'Vande Bharat, Cheran Express, TNSTC' },
  { label: 'Chennai ↔ Pudukkottai', orig: 'Chennai', dest: 'Pudukkottai', orig_disp: 'Chennai, Tamil Nadu', dest_disp: 'Pudukkottai, Tamil Nadu', desc: 'Silambu Express, Pallavan Express, SETC' },
  { label: 'Hyderabad ↔ Warangal', orig: 'Hyderabad', dest: 'Warangal', orig_disp: 'Hyderabad, Telangana', dest_disp: 'Warangal, Telangana', desc: 'Satavahana Express, TSRTC Express' },
  { label: 'Hyderabad ↔ Karimnagar', orig: 'Hyderabad', dest: 'Karimnagar', orig_disp: 'Hyderabad, Telangana', dest_disp: 'Karimnagar, Telangana', desc: 'Karimnagar Express, TSRTC Super Luxury' },
  { label: 'Hyderabad ↔ Vijayawada', orig: 'Hyderabad', dest: 'Vijayawada', orig_disp: 'Hyderabad, Telangana', dest_disp: 'Vijayawada, Andhra Pradesh', desc: 'Vande Bharat, Satavahana, APSRTC Amaravati' },
  { label: 'Mumbai ↔ Pune', orig: 'Mumbai', dest: 'Pune', orig_disp: 'Mumbai, Maharashtra', dest_disp: 'Pune, Maharashtra', desc: 'Deccan Queen, Pragati, MSRTC Shivneri' },
  { label: 'Delhi ↔ Jaipur', orig: 'Delhi', dest: 'Jaipur', orig_disp: 'Delhi, Delhi', dest_disp: 'Jaipur, Rajasthan', desc: 'Vande Bharat, Double Decker, RSRTC Goldline' },
  { label: 'Kochi ↔ Thiruvananthapuram', orig: 'Kochi', dest: 'Thiruvananthapuram', orig_disp: 'Kochi, Kerala', dest_disp: 'Thiruvananthapuram, Kerala', desc: 'Vande Bharat, Jan Shatabdi, Kerala RTC' },
  { label: 'Ahmedabad ↔ Surat', orig: 'Ahmedabad', dest: 'Surat', orig_disp: 'Ahmedabad, Gujarat', dest_disp: 'Surat, Gujarat', desc: 'Vande Bharat, Tejas Express, GSRTC Sleeper' },
  { label: 'Lucknow ↔ Varanasi', orig: 'Lucknow', dest: 'Varanasi', orig_disp: 'Lucknow, Uttar Pradesh', dest_disp: 'Varanasi, Uttar Pradesh', desc: 'Vande Bharat, UPSRTC Janrath' },
];

export const HomePage: React.FC<HomePageProps> = ({ isAIOpen, setIsAIOpen }) => {
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [selectedJourney, setSelectedJourney] = useState<Journey | null>(null);
  const [comparedJourneyIds, setComparedJourneyIds] = useState<string[]>([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'all' | 'train' | 'bus' | 'metro' | 'multimodal'>('all');
  const [activeSort, setActiveSort] = useState<'fastest' | 'cheapest' | 'fewest_transfers' | 'delay_aware'>('fastest');
  
  // Initial search filters start completely empty (no hardcoded cities or pre-selected dates)
  const [currentFilters, setCurrentFilters] = useState<SearchFilters>({
    origin: '',
    destination: '',
    origin_display: '',
    destination_display: '',
    travel_date: '',
    departure_after: '00:00',
    preferred_modes: ['train', 'bus', 'metro'],
    optimisation: 'fastest',
    max_transfers: 3,
  });

  const sortJourneys = (list: Journey[], sortKey: 'fastest' | 'cheapest' | 'fewest_transfers' | 'delay_aware'): Journey[] => {
    const sorted = [...list];
    if (sortKey === 'cheapest') {
      return sorted.sort((a, b) => {
        const aVerified = a.is_fare_verified !== false && a.total_fare_inr > 0;
        const bVerified = b.is_fare_verified !== false && b.total_fare_inr > 0;
        if (aVerified && !bVerified) return -1;
        if (!aVerified && bVerified) return 1;
        if (a.total_fare_inr !== b.total_fare_inr) {
          return a.total_fare_inr - b.total_fare_inr;
        }
        return a.scheduled_duration_min - b.scheduled_duration_min;
      });
    } else if (sortKey === 'fewest_transfers') {
      return sorted.sort((a, b) => {
        if (a.transfer_count !== b.transfer_count) {
          return a.transfer_count - b.transfer_count;
        }
        return a.scheduled_duration_min - b.scheduled_duration_min;
      });
    } else if (sortKey === 'delay_aware') {
      const getScore = (j: Journey) => {
        const riskPen = j.delay_risk_level === 'HIGH' ? 30 : j.delay_risk_level === 'MODERATE' ? 12 : 0;
        return j.estimated_duration_min + riskPen + (j.transfer_count * 10);
      };
      return sorted.sort((a, b) => getScore(a) - getScore(b));
    } else {
      // fastest
      return sorted.sort((a, b) => {
        if (a.scheduled_duration_min !== b.scheduled_duration_min) {
          return a.scheduled_duration_min - b.scheduled_duration_min;
        }
        return a.total_fare_inr - b.total_fare_inr;
      });
    }
  };

  const handleSearch = async (filters: SearchFilters) => {
    if (!filters.origin || !filters.destination || !filters.travel_date) {
      setErrorMsg('Please enter a starting location, destination, and select a travel date.');
      return;
    }
    setHasSearched(true);
    setIsLoading(true);
    setErrorMsg(null);
    setJourneys([]);
    setSelectedJourney(null);
    setCurrentFilters(filters);
    const effectiveSort = filters.optimisation || activeSort;
    setActiveSort(effectiveSort);
    try {
      const res = await api.searchRoutes(filters);
      const rankedJourneys = sortJourneys(res.journeys, effectiveSort);
      setJourneys(rankedJourneys);
      if (rankedJourneys.length > 0) {
        setSelectedJourney(rankedJourneys[0]);
      } else {
        setSelectedJourney(null);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'No feasible journeys found with current criteria.');
      setJourneys([]);
      setSelectedJourney(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setJourneys([]);
    setSelectedJourney(null);
    setComparedJourneyIds([]);
    setErrorMsg(null);
    setHasSearched(false);
    setActiveFilter('all');
    setCurrentFilters({
      origin: '',
      destination: '',
      origin_display: '',
      destination_display: '',
      travel_date: '',
      departure_after: '00:00',
      preferred_modes: ['train', 'bus', 'metro'],
      optimisation: 'fastest',
      max_transfers: 3,
    });
  };

  const handleSortChange = (newSort: 'fastest' | 'cheapest' | 'fewest_transfers' | 'delay_aware') => {
    setActiveSort(newSort);
    setCurrentFilters((prev) => ({ ...prev, optimisation: newSort }));
    const sorted = sortJourneys(journeys, newSort);
    setJourneys(sorted);
    if (sorted.length > 0) {
      setSelectedJourney(sorted[0]);
    }
  };

  const handleToggleCompare = (id: string) => {
    if (comparedJourneyIds.includes(id)) {
      setComparedJourneyIds(comparedJourneyIds.filter((item) => item !== id));
    } else {
      if (comparedJourneyIds.length >= 3) {
        alert('You can compare up to 3 journeys side-by-side.');
        return;
      }
      setComparedJourneyIds([...comparedJourneyIds, id]);
    }
  };

  // Optional shortcut helper: populates input fields for user convenience WITHOUT triggering auto-search
  const handleQuickCorridor = (orig: string, dest: string, orig_disp?: string, dest_disp?: string) => {
    const today = new Date().toISOString().split('T')[0];
    const newFilters: SearchFilters = {
      origin: orig,
      destination: dest,
      origin_display: orig_disp || orig,
      destination_display: dest_disp || dest,
      travel_date: currentFilters.travel_date || today,
      departure_after: currentFilters.departure_after || '00:00',
      preferred_modes: currentFilters.preferred_modes || ['train', 'bus', 'metro'],
      optimisation: activeSort,
      max_transfers: 3,
    };
    setCurrentFilters(newFilters);
    setErrorMsg(null);
  };

  // Dynamic counts calculated from current journeys
  const totalCount = journeys.length;
  const trainCount = journeys.filter((j) => j.modes.includes('train')).length;
  const busCount = journeys.filter((j) => j.modes.includes('bus')).length;
  const metroCount = journeys.filter((j) => j.modes.includes('metro')).length;
  const multimodalCount = journeys.filter((j) => j.is_multimodal).length;

  // Filter journeys by mode
  const filteredJourneys = journeys.filter((j) => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'multimodal') return j.is_multimodal;
    return j.modes.includes(activeFilter);
  });

  const comparedJourneys = journeys.filter((j) => comparedJourneyIds.includes(j.journey_id));

  return (
    <div className="space-y-6">
      {/* Hero Welcome & AI Quick Prompt */}
      <div className="bg-gradient-to-r from-emerald-800 via-teal-900 to-slate-900 rounded-3xl p-6 md:p-8 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>GenAI + Machine Learning Transit Optimization</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white mb-2">
            Intelligent Public Transport Journey Planner for India
          </h1>
          <p className="text-xs md:text-sm text-slate-300 font-normal leading-relaxed mb-4">
            Search and compare verified Indian Railways trains, intercity government &amp; private buses (KSRTC, SETC, TNSTC, APSRTC, MSRTC, RSRTC), and metro rail networks. 
            Features graph-based multimodal routing, Scikit-learn train delay regression, and Mistral AI reasoning.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setIsAIOpen(true)}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-xs shadow-sm transition flex items-center space-x-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ask Mistral AI in Natural Language</span>
            </button>
            <div className="text-xs text-slate-300 hidden sm:inline ml-2">
              National gazetteer: <strong className="text-white">119 cities</strong> &middot; <strong className="text-white">20 verified corridors (16 National &amp; State Authorities)</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Verified Corridors Bar: Optional user shortcuts that populate fields without auto-searching */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-2xs space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1">
              <Compass className="w-3.5 h-3.5 text-emerald-600 mr-1" />
              <span>Suggested Corridor Shortcuts:</span>
            </span>
          </div>
          <span className="text-[11px] text-slate-400 hidden sm:inline">Click to populate origin &amp; destination</span>
        </div>
        <div className="flex flex-wrap items-center gap-2 pt-1">
          {POPULAR_CORRIDORS.map((c) => {
            const isActive = 
              Boolean(currentFilters.origin) &&
              Boolean(currentFilters.destination) &&
              ((currentFilters.origin.toLowerCase().includes(c.orig.toLowerCase()) && currentFilters.destination.toLowerCase().includes(c.dest.toLowerCase())) ||
               (currentFilters.origin.toLowerCase().includes(c.dest.toLowerCase()) && currentFilters.destination.toLowerCase().includes(c.orig.toLowerCase())));

            return (
              <button
                key={c.label}
                type="button"
                onClick={() => handleQuickCorridor(c.orig, c.dest, c.orig_disp, c.dest_disp)}
                title={c.desc}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center space-x-1.5 border ${
                  isActive
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs font-semibold'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300'
                }`}
              >
                <span>{c.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Search Component */}
      <SearchForm
        onSearch={handleSearch}
        isLoading={isLoading}
        initialFilters={currentFilters}
        onReset={handleReset}
      />

      {/* Error Notice */}
      {errorMsg && (
        <div className="p-5 rounded-2xl bg-amber-50/90 border border-amber-200 text-amber-900 text-xs space-y-3">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-sm block text-amber-950">Notice: Route Search Unsuccessful</span>
              <p className="text-amber-900 leading-relaxed">{errorMsg}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Controls Bar: Dynamic Filter Pills & Active Sort Selector (Only shown after search returns results) */}
      {hasSearched && journeys.length > 0 && (
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-2xs space-y-3 animate-in fade-in duration-150">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Mode Filter Pills with Dynamic Counts */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mr-1">Filter:</span>
              <button
                onClick={() => setActiveFilter('all')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  activeFilter === 'all'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                All Journeys ({totalCount})
              </button>
              <button
                onClick={() => setActiveFilter('train')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1 ${
                  activeFilter === 'train'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Train className="w-3.5 h-3.5" />
                <span>Train ({trainCount})</span>
              </button>
              <button
                onClick={() => setActiveFilter('bus')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1 ${
                  activeFilter === 'bus'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Bus className="w-3.5 h-3.5" />
                <span>Bus ({busCount})</span>
              </button>
              <button
                onClick={() => setActiveFilter('metro')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1 ${
                  activeFilter === 'metro'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Metro ({metroCount})</span>
              </button>
              <button
                onClick={() => setActiveFilter('multimodal')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  activeFilter === 'multimodal'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Multimodal Only ({multimodalCount})
              </button>
            </div>

            {/* Floating Compare Action */}
            {comparedJourneyIds.length > 0 && (
              <button
                onClick={() => setIsCompareModalOpen(true)}
                className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 text-white font-semibold text-xs shadow-sm hover:bg-slate-800 transition shrink-0"
              >
                <span>Compare ({comparedJourneyIds.length}) Selected</span>
              </button>
            )}
          </div>

          {/* Intuitive Sort Controls Bar */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
            <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-500 uppercase tracking-wider mr-1">
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
              <span>Sort By:</span>
            </div>
            <button
              type="button"
              onClick={() => handleSortChange('fastest')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 border ${
                activeSort === 'fastest'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300 shadow-2xs font-bold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>⚡ Fastest First</span>
            </button>
            <button
              type="button"
              onClick={() => handleSortChange('cheapest')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 border ${
                activeSort === 'cheapest'
                  ? 'bg-blue-50 text-blue-800 border-blue-300 shadow-2xs font-bold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>💰 Cheapest First</span>
            </button>
            <button
              type="button"
              onClick={() => handleSortChange('fewest_transfers')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 border ${
                activeSort === 'fewest_transfers'
                  ? 'bg-indigo-50 text-indigo-800 border-indigo-300 shadow-2xs font-bold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>🔄 Fewest Transfers</span>
            </button>
            <button
              type="button"
              onClick={() => handleSortChange('delay_aware')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 border ${
                activeSort === 'delay_aware'
                  ? 'bg-teal-50 text-teal-800 border-teal-300 shadow-2xs font-bold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>🛡️ Delay-Aware (ML)</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Split Layout: Left Route Cards / Empty State, Right Interactive Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Journey Cards List or Clean Empty State */}
        <div className="lg:col-span-7 space-y-4">
          {isLoading ? (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-sm font-semibold text-slate-800">
                Evaluating Multimodal Paths &amp; Predicting Delays...
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Running timetable-expanded graph search &amp; Scikit-learn inference
              </p>
            </div>
          ) : !hasSearched ? (
            /* Helpful Initial Empty State */
            <div className="bg-white rounded-2xl p-10 md:p-14 border border-slate-200/90 text-center space-y-4 shadow-2xs">
              <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-100 shadow-2xs">
                <Compass className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto space-y-2">
                <h3 className="text-lg font-bold text-slate-900">
                  Plan your journey by entering your starting location and destination.
                </h3>
                <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
                  Enter your origin, destination, and travel date above, then click <strong className="text-slate-700">Search Routes</strong> to discover verified Indian Railways trains, intercity government &amp; private buses, and metro connections.
                </p>
              </div>
            </div>
          ) : filteredJourneys.length > 0 ? (
            filteredJourneys.map((j) => (
              <RouteCard
                key={j.journey_id}
                journey={j}
                isSelected={selectedJourney?.journey_id === j.journey_id}
                onSelect={() => setSelectedJourney(j)}
                isCompared={comparedJourneyIds.includes(j.journey_id)}
                onToggleCompare={() => handleToggleCompare(j.journey_id)}
              />
            ))
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
                <SlidersHorizontal className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">No Journeys Match Current Filters</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                No direct or connecting services were found for the selected transport modes. Try enabling all modes or adjusting your travel date.
              </p>
            </div>
          )}
        </div>

        {/* Right: Sticky Interactive Map */}
        <div className="lg:col-span-5 sticky top-20">
          <InteractiveMap journey={selectedJourney} />
        </div>
      </div>

      {/* AI Assistant Modal */}
      <AiAssistantModal
        isOpen={isAIOpen}
        onClose={() => setIsAIOpen(false)}
        onApplyFilters={(filters) => handleSearch(filters)}
      />

      {/* Route Compare Modal */}
      <RouteCompareModal
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        journeys={comparedJourneys}
      />
    </div>
  );
};
