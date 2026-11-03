import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeftRight, Calendar, Search, SlidersHorizontal, Train, 
  Bus, Zap, Clock, ShieldAlert, DollarSign, RotateCcw, Check,
  MapPin, Building2, X, Loader2, AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { AutocompleteItem, SearchFilters } from '../types';

interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
  initialFilters?: Partial<SearchFilters>;
  onReset?: () => void;
}

const STATE_CODE_MAP: Record<string, string> = {
  ts: 'Telangana',
  tn: 'Tamil Nadu',
  ka: 'Karnataka',
  ap: 'Andhra Pradesh',
  kl: 'Kerala',
  mh: 'Maharashtra',
  dl: 'Delhi',
  rj: 'Rajasthan',
  wb: 'West Bengal',
  gj: 'Gujarat',
  up: 'Uttar Pradesh',
  or: 'Odisha',
  od: 'Odisha',
  pb: 'Punjab',
  hr: 'Haryana',
  mp: 'Madhya Pradesh',
  br: 'Bihar',
  as: 'Assam',
  jh: 'Jharkhand',
  ct: 'Chhattisgarh',
  uk: 'Uttarakhand',
  hp: 'Himachal Pradesh',
  jk: 'Jammu & Kashmir',
  ga: 'Goa',
  ml: 'Meghalaya',
  tr: 'Tripura',
  mn: 'Manipur',
  nl: 'Nagaland',
  mz: 'Mizoram',
  ar: 'Arunachal Pradesh',
  sk: 'Sikkim',
  ch: 'Chandigarh',
  py: 'Puducherry'
};

function formatPlaceLabel(rawIdOrName?: string, explicitDisplay?: string): string {
  if (explicitDisplay && !explicitDisplay.startsWith('place_')) {
    return explicitDisplay;
  }
  if (!rawIdOrName) return '';
  if (rawIdOrName.startsWith('place_')) {
    const parts = rawIdOrName.replace('place_', '').split('_');
    const stateCode = parts.pop() || '';
    const cityName = parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
    const stateName = STATE_CODE_MAP[stateCode.toLowerCase()] || stateCode.toUpperCase();
    return stateName ? `${cityName}, ${stateName}` : cityName;
  }
  return rawIdOrName;
}

export const SearchForm: React.FC<SearchFormProps> = ({ 
  onSearch, 
  isLoading, 
  initialFilters,
  onReset
}) => {
  const [originText, setOriginText] = useState(() => 
    formatPlaceLabel(initialFilters?.origin || '', initialFilters?.origin_display)
  );
  const [destText, setDestText] = useState(() => 
    formatPlaceLabel(initialFilters?.destination || '', initialFilters?.destination_display)
  );
  const [originItem, setOriginItem] = useState<AutocompleteItem | null>(null);
  const [destItem, setDestItem] = useState<AutocompleteItem | null>(null);

  // Initial travel date starts empty (unselected)
  const [travelDate, setTravelDate] = useState(initialFilters?.travel_date || '');
  const [departureAfter, setDepartureAfter] = useState(initialFilters?.departure_after || '00:00');
  const [arrivalBefore, setArrivalBefore] = useState(initialFilters?.arrival_before || '');
  const [selectedModes, setSelectedModes] = useState<string[]>(initialFilters?.preferred_modes || ['train', 'bus', 'metro']);
  const [optimisation, setOptimisation] = useState<SearchFilters['optimisation']>(initialFilters?.optimisation || 'fastest');
  const [maxTransfers, setMaxTransfers] = useState<number | undefined>(initialFilters?.max_transfers ?? 3);
  const [maxBudget, setMaxBudget] = useState<number | undefined>(initialFilters?.max_budget);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Autocomplete state
  const [originSuggestions, setOriginSuggestions] = useState<AutocompleteItem[]>([]);
  const [destSuggestions, setDestSuggestions] = useState<AutocompleteItem[]>([]);
  const [showOriginDrop, setShowOriginDrop] = useState(false);
  const [showDestDrop, setShowDestDrop] = useState(false);
  const [isOriginLoading, setIsOriginLoading] = useState(false);
  const [isDestLoading, setIsDestLoading] = useState(false);
  const [originActiveIdx, setOriginActiveIdx] = useState(-1);
  const [destActiveIdx, setDestActiveIdx] = useState(-1);

  const originRef = useRef<HTMLDivElement>(null);
  const destRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (originRef.current && !originRef.current.contains(e.target as Node)) {
        setShowOriginDrop(false);
      }
      if (destRef.current && !destRef.current.contains(e.target as Node)) {
        setShowDestDrop(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Sync initial filters when updated from parent shortcuts or resets
  useEffect(() => {
    if (initialFilters?.origin !== undefined) {
      setOriginText(formatPlaceLabel(initialFilters.origin, initialFilters.origin_display));
      if (!initialFilters.origin) setOriginItem(null);
    }
    if (initialFilters?.destination !== undefined) {
      setDestText(formatPlaceLabel(initialFilters.destination, initialFilters.destination_display));
      if (!initialFilters.destination) setDestItem(null);
    }
    if (initialFilters?.optimisation) setOptimisation(initialFilters.optimisation);
    if (initialFilters?.travel_date !== undefined) setTravelDate(initialFilters.travel_date);
    if (initialFilters?.departure_after) setDepartureAfter(initialFilters.departure_after);
    if (initialFilters?.preferred_modes) setSelectedModes(initialFilters.preferred_modes);
  }, [initialFilters]);

  // Debounced search for Origin (300 ms debounce)
  useEffect(() => {
    if (!originText || originText.trim().length < 2) {
      setOriginSuggestions([]);
      setIsOriginLoading(false);
      return;
    }
    setIsOriginLoading(true);
    const timer = setTimeout(() => {
      api.searchPlaces(originText.trim(), 12)
        .then((items) => {
          setOriginSuggestions(items);
          setOriginActiveIdx(-1);
        })
        .catch(() => setOriginSuggestions([]))
        .finally(() => setIsOriginLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [originText]);

  // Debounced search for Destination (300 ms debounce)
  useEffect(() => {
    if (!destText || destText.trim().length < 2) {
      setDestSuggestions([]);
      setIsDestLoading(false);
      return;
    }
    setIsDestLoading(true);
    const timer = setTimeout(() => {
      api.searchPlaces(destText.trim(), 12)
        .then((items) => {
          setDestSuggestions(items);
          setDestActiveIdx(-1);
        })
        .catch(() => setDestSuggestions([]))
        .finally(() => setIsDestLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [destText]);

  const handleSwap = () => {
    setValidationError(null);
    const tempText = originText;
    const tempItem = originItem;

    setOriginText(destText);
    setOriginItem(destItem);

    setDestText(tempText);
    setDestItem(tempItem);
  };

  const handleModeToggle = (mode: string) => {
    if (mode === 'all') {
      setSelectedModes(['train', 'bus', 'metro']);
      return;
    }
    if (selectedModes.includes(mode)) {
      if (selectedModes.length > 1) {
        setSelectedModes(selectedModes.filter((m) => m !== mode));
      }
    } else {
      setSelectedModes([...selectedModes, mode]);
    }
  };

  const handleResetFilters = () => {
    setOriginText('');
    setDestText('');
    setOriginItem(null);
    setDestItem(null);
    setTravelDate('');
    setDepartureAfter('00:00');
    setArrivalBefore('');
    setSelectedModes(['train', 'bus', 'metro']);
    setOptimisation('fastest');
    setMaxTransfers(3);
    setMaxBudget(undefined);
    setShowAdvanced(false);
    setValidationError(null);
    setOriginSuggestions([]);
    setDestSuggestions([]);
    setShowOriginDrop(false);
    setShowDestDrop(false);
    if (onReset) onReset();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const origQuery = originItem ? originItem.id : originText.trim();
    const destQuery = destItem ? destItem.id : destText.trim();
    const origDisplay = originItem ? (originItem.display_label || originItem.name) : originText.trim();
    const destDisplay = destItem ? (destItem.display_label || destItem.name) : destText.trim();

    // Required Field Validations
    if (!origQuery) {
      setValidationError('Please enter or select a starting location (Origin).');
      return;
    }

    if (!destQuery) {
      setValidationError('Please enter or select a destination.');
      return;
    }

    if (!travelDate) {
      setValidationError('Please select a travel date before searching.');
      return;
    }

    if (origQuery.toLowerCase() === destQuery.toLowerCase()) {
      setValidationError('Starting location and destination cannot be identical. Please select different points.');
      return;
    }

    onSearch({
      origin: origQuery,
      destination: destQuery,
      origin_display: origDisplay,
      destination_display: destDisplay,
      travel_date: travelDate,
      departure_after: departureAfter,
      arrival_before: arrivalBefore || undefined,
      preferred_modes: selectedModes,
      optimisation,
      max_transfers: maxTransfers,
      max_budget: maxBudget,
    });
  };

  const renderCategoryIcon = (category?: string) => {
    switch (category) {
      case 'city':
        return <Building2 className="w-3.5 h-3.5 text-sky-600" />;
      case 'railway':
        return <Train className="w-3.5 h-3.5 text-emerald-600" />;
      case 'bus_terminal':
      case 'bus_stop':
        return <Bus className="w-3.5 h-3.5 text-amber-600" />;
      case 'metro':
        return <Zap className="w-3.5 h-3.5 text-indigo-600" />;
      default:
        return <MapPin className="w-3.5 h-3.5 text-slate-500" />;
    }
  };

  const getCategoryBadgeClass = (category?: string) => {
    switch (category) {
      case 'city':
        return 'bg-sky-50 text-sky-700 border-sky-200';
      case 'railway':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'bus_terminal':
      case 'bus_stop':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'metro':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 p-5 md:p-6 mb-8">
      {/* Validation Alert */}
      {validationError && (
        <div className="mb-4 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center justify-between animate-in fade-in duration-100">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span className="font-semibold">{validationError}</span>
          </div>
          <button
            type="button"
            onClick={() => setValidationError(null)}
            className="text-amber-500 hover:text-amber-800 p-0.5 rounded"
            title="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Main Origin, Destination & Date Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Origin Input with India-wide Autocomplete */}
          <div className="relative md:col-span-4" ref={originRef}>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center justify-between">
              <span>From (Starting Location)</span>
              {originItem && (
                <span className="text-[10px] text-emerald-600 font-normal truncate max-w-[180px]">
                  ✓ {originItem.name}
                </span>
              )}
            </label>
            <div className="relative">
              <input
                type="text"
                value={originText}
                onChange={(e) => {
                  setOriginText(e.target.value);
                  setOriginItem(null);
                  setShowOriginDrop(true);
                  if (validationError) setValidationError(null);
                }}
                onFocus={() => setShowOriginDrop(true)}
                onKeyDown={(e) => {
                  if (!showOriginDrop || originSuggestions.length === 0) return;
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setOriginActiveIdx((prev) => (prev < originSuggestions.length - 1 ? prev + 1 : 0));
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setOriginActiveIdx((prev) => (prev > 0 ? prev - 1 : originSuggestions.length - 1));
                  } else if (e.key === 'Enter' && originActiveIdx >= 0) {
                    e.preventDefault();
                    const sel = originSuggestions[originActiveIdx];
                    setOriginItem(sel);
                    setOriginText(sel.display_label || sel.name);
                    setShowOriginDrop(false);
                  } else if (e.key === 'Escape') {
                    setShowOriginDrop(false);
                  }
                }}
                placeholder="Enter city, station, or bus terminal..."
                className="w-full pl-4 pr-9 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />

              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-1">
                {isOriginLoading && (
                  <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
                )}
                {originText && !isOriginLoading && (
                  <button
                    type="button"
                    onClick={() => {
                      setOriginText('');
                      setOriginItem(null);
                      setOriginSuggestions([]);
                    }}
                    className="text-slate-400 hover:text-slate-600 p-0.5 rounded-full"
                    title="Clear origin"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Categorised Autocomplete dropdown */}
              {showOriginDrop && originText.trim().length >= 2 && (
                <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-72 overflow-y-auto divide-y divide-slate-100 animate-in fade-in duration-100">
                  {isOriginLoading ? (
                    <div className="p-4 text-center text-xs text-slate-500 flex items-center justify-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
                      <span>Searching Indian places &amp; stations...</span>
                    </div>
                  ) : originSuggestions.length > 0 ? (
                    originSuggestions.map((item, idx) => (
                      <div
                        key={item.id}
                        onClick={() => {
                          setOriginItem(item);
                          setOriginText(item.display_label || item.name);
                          setShowOriginDrop(false);
                        }}
                        className={`px-4 py-2.5 cursor-pointer text-sm flex items-center justify-between transition ${
                          idx === originActiveIdx ? 'bg-emerald-50/80' : 'hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-start space-x-2.5 min-w-0 pr-2">
                          <div className="mt-0.5 flex-shrink-0">
                            {renderCategoryIcon(item.category)}
                          </div>
                          <div className="min-w-0">
                            <div className="font-medium text-slate-900 truncate">
                              {item.display_label || item.name}
                            </div>
                            <div className="text-xs text-slate-500 truncate">
                              {item.sub_label || item.subtitle}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1.5 flex-shrink-0">
                          {item.code && (
                            <span className="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                              {item.code}
                            </span>
                          )}
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getCategoryBadgeClass(item.category)}`}>
                            {item.category_label || item.type}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-xs text-slate-500">
                      No Indian places or transit stations found matching "{originText.trim()}"
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center md:col-span-1 my-[-6px] md:my-0">
            <button
              type="button"
              onClick={handleSwap}
              className="p-2.5 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition border border-slate-200 mt-0 md:mt-5"
              title="Swap Origin and Destination"
            >
              <ArrowLeftRight className="w-4 h-4" />
            </button>
          </div>

          {/* Destination Input with India-wide Autocomplete */}
          <div className="relative md:col-span-4" ref={destRef}>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center justify-between">
              <span>To (Destination)</span>
              {destItem && (
                <span className="text-[10px] text-emerald-600 font-normal truncate max-w-[180px]">
                  ✓ {destItem.name}
                </span>
              )}
            </label>
            <div className="relative">
              <input
                type="text"
                value={destText}
                onChange={(e) => {
                  setDestText(e.target.value);
                  setDestItem(null);
                  setShowDestDrop(true);
                  if (validationError) setValidationError(null);
                }}
                onFocus={() => setShowDestDrop(true)}
                onKeyDown={(e) => {
                  if (!showDestDrop || destSuggestions.length === 0) return;
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setDestActiveIdx((prev) => (prev < destSuggestions.length - 1 ? prev + 1 : 0));
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setDestActiveIdx((prev) => (prev > 0 ? prev - 1 : destSuggestions.length - 1));
                  } else if (e.key === 'Enter' && destActiveIdx >= 0) {
                    e.preventDefault();
                    const sel = destSuggestions[destActiveIdx];
                    setDestItem(sel);
                    setDestText(sel.display_label || sel.name);
                    setShowDestDrop(false);
                  } else if (e.key === 'Escape') {
                    setShowDestDrop(false);
                  }
                }}
                placeholder="Enter city, station, or bus terminal..."
                className="w-full pl-4 pr-9 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />

              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-1">
                {isDestLoading && (
                  <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
                )}
                {destText && !isDestLoading && (
                  <button
                    type="button"
                    onClick={() => {
                      setDestText('');
                      setDestItem(null);
                      setDestSuggestions([]);
                    }}
                    className="text-slate-400 hover:text-slate-600 p-0.5 rounded-full"
                    title="Clear destination"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Categorised Autocomplete dropdown */}
              {showDestDrop && destText.trim().length >= 2 && (
                <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-72 overflow-y-auto divide-y divide-slate-100 animate-in fade-in duration-100">
                  {isDestLoading ? (
                    <div className="p-4 text-center text-xs text-slate-500 flex items-center justify-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
                      <span>Searching Indian places &amp; stations...</span>
                    </div>
                  ) : destSuggestions.length > 0 ? (
                    destSuggestions.map((item, idx) => (
                      <div
                        key={item.id}
                        onClick={() => {
                          setDestItem(item);
                          setDestText(item.display_label || item.name);
                          setShowDestDrop(false);
                        }}
                        className={`px-4 py-2.5 cursor-pointer text-sm flex items-center justify-between transition ${
                          idx === destActiveIdx ? 'bg-emerald-50/80' : 'hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-start space-x-2.5 min-w-0 pr-2">
                          <div className="mt-0.5 flex-shrink-0">
                            {renderCategoryIcon(item.category)}
                          </div>
                          <div className="min-w-0">
                            <div className="font-medium text-slate-900 truncate">
                              {item.display_label || item.name}
                            </div>
                            <div className="text-xs text-slate-500 truncate">
                              {item.sub_label || item.subtitle}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1.5 flex-shrink-0">
                          {item.code && (
                            <span className="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                              {item.code}
                            </span>
                          )}
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getCategoryBadgeClass(item.category)}`}>
                            {item.category_label || item.type}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-xs text-slate-500">
                      No Indian places or transit stations found matching "{destText.trim()}"
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Travel Date */}
          <div className="md:col-span-3">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
              Travel Date
            </label>
            <div className="relative">
              <input
                type="date"
                value={travelDate}
                onChange={(e) => {
                  setTravelDate(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
            </div>
          </div>
        </div>

        {/* Mode Selector & Optimisation Row */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4">
          {/* Transport Modes */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Modes:</span>
            <button
              type="button"
              onClick={() => handleModeToggle('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedModes.length === 3
                  ? 'bg-slate-900 text-white font-semibold'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              All Modes
            </button>
            <button
              type="button"
              onClick={() => handleModeToggle('train')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1 ${
                selectedModes.includes('train')
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 font-semibold'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Train className="w-3.5 h-3.5" />
              <span>Train</span>
            </button>
            <button
              type="button"
              onClick={() => handleModeToggle('bus')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1 ${
                selectedModes.includes('bus')
                  ? 'bg-amber-100 text-amber-800 border border-amber-300 font-semibold'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Bus className="w-3.5 h-3.5" />
              <span>Bus</span>
            </button>
            <button
              type="button"
              onClick={() => handleModeToggle('metro')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1 ${
                selectedModes.includes('metro')
                  ? 'bg-indigo-100 text-indigo-800 border border-indigo-300 font-semibold'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Metro</span>
            </button>
          </div>

          {/* Optimisation Criteria */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Optimize:</span>
            {(['fastest', 'cheapest', 'fewest_transfers', 'delay_aware'] as const).map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setOptimisation(opt)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition flex items-center space-x-1 ${
                  optimisation === opt
                    ? 'bg-emerald-600 text-white shadow-sm font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {opt === 'delay_aware' ? (
                  <>
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Delay-Aware ML</span>
                  </>
                ) : (
                  <span>{opt.replace('_', ' ')}</span>
                )}
              </button>
            ))}
          </div>

          {/* Advanced toggle & Submit button */}
          <div className="flex items-center space-x-2 ml-auto">
            <button
              type="button"
              onClick={handleResetFilters}
              className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center space-x-1 px-2.5 py-2 rounded-lg hover:bg-slate-100 transition"
              title="Reset all inputs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs font-medium text-slate-600 hover:text-slate-900 flex items-center space-x-1 px-2.5 py-2 rounded-lg hover:bg-slate-100 transition"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{showAdvanced ? 'Hide Filters' : 'More Filters'}</span>
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm shadow-sm transition flex items-center space-x-2 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Search Routes</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Collapsible Advanced Filters */}
        {showAdvanced && (
          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-4 gap-4 bg-slate-50/70 p-4 rounded-xl animate-in fade-in duration-150">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Departure After</label>
              <input
                type="time"
                value={departureAfter}
                onChange={(e) => setDepartureAfter(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Arrival Before (Optional)</label>
              <input
                type="time"
                value={arrivalBefore}
                onChange={(e) => setArrivalBefore(e.target.value)}
                placeholder="--:--"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Max Transfers</label>
              <select
                value={maxTransfers ?? ''}
                onChange={(e) => setMaxTransfers(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm"
              >
                <option value="">Any Transfers</option>
                <option value="0">Direct Only (0 transfers)</option>
                <option value="1">Max 1 Transfer</option>
                <option value="2">Max 2 Transfers</option>
                <option value="3">Max 3 Transfers</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Max Budget (₹ INR)</label>
              <input
                type="number"
                value={maxBudget ?? ''}
                onChange={(e) => setMaxBudget(e.target.value ? Number(e.target.value) : undefined)}
                placeholder="e.g. 500"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm"
              />
            </div>
          </div>
        )}
      </form>
    </div>
  );
};
