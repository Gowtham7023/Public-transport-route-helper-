import React, { useState } from 'react';
import { X, Sparkles, Send, ArrowRight, CornerDownLeft, ShieldCheck, HelpCircle } from 'lucide-react';
import { api } from '../services/api';
import { SearchFilters, Journey } from '../types';

interface AiAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyFilters: (filters: SearchFilters) => void;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  parsedParams?: any;
  journeys?: Journey[];
}

const PRESET_QUERIES = [
  "Find the cheapest journey from Chennai to Bengaluru",
  "Direct bus or train from Bengaluru to Mysuru",
  "Fastest route from Chennai to Madurai",
  "Train or bus from Hyderabad to Vijayawada",
  "Fastest journey from Mumbai to Pune",
  "Delay-aware route from Delhi to Jaipur"
];

export const AiAssistantModal: React.FC<AiAssistantModalProps> = ({
  isOpen,
  onClose,
  onApplyFilters,
}) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Namaste! I am your AI Indian Public Transport Assistant powered by Mistral AI and verified timetable datasets. Ask me to find journeys, prioritize speed or low fares, check train delays, or find multimodal connections.",
    },
  ]);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.queryAI(textToSend);
      const assistantMsg: Message = {
        role: 'assistant',
        content: response.assistant_reply || `Found ${response.routes_found} route options for your journey.`,
        parsedParams: response.parsed_parameters,
        journeys: response.recommended_journeys,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error while searching: ${err.message || 'Please try again.'}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApply = (params: any) => {
    onApplyFilters({
      origin: params.origin_station_id || params.origin_name || 'MAS',
      destination: params.destination_station_id || params.destination_name || 'SBC',
      travel_date: params.travel_date || new Date().toISOString().split('T')[0],
      departure_after: params.departure_after || '05:00',
      arrival_before: params.arrival_before || undefined,
      preferred_modes: params.preferred_modes || ['train', 'bus', 'metro'],
      optimisation: params.optimisation || 'fastest',
      max_transfers: params.max_transfers,
      max_budget: params.max_budget,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-2xl h-[640px] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-emerald-50/40">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">AI Travel Assistant</h2>
              <p className="text-xs text-slate-500">Natural Language Multimodal Search</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Thread */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === 'user'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-800 border border-slate-200/60'
                }`}
              >
                <p className="leading-relaxed whitespace-pre-line">{msg.content}</p>

                {/* Extracted Parameters Card */}
                {msg.parsedParams && (
                  <div className="mt-3 pt-3 border-t border-slate-200 text-xs text-slate-600 space-y-1 bg-white/70 p-3 rounded-xl">
                    <div className="font-semibold text-slate-800 flex items-center space-x-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Extracted Parameters:</span>
                    </div>
                    <div>
                      &bull; Route: <span className="font-semibold text-slate-900">{msg.parsedParams.origin_station_id || msg.parsedParams.origin_name} &rarr; {msg.parsedParams.destination_station_id || msg.parsedParams.destination_name}</span>
                    </div>
                    <div>
                      &bull; Optimization: <span className="font-semibold capitalize text-slate-900">{msg.parsedParams.optimisation}</span>
                    </div>
                    {msg.parsedParams.arrival_before && (
                      <div>&bull; Arrive Before: <span className="font-semibold">{msg.parsedParams.arrival_before}</span></div>
                    )}
                    <button
                      onClick={() => handleApply(msg.parsedParams)}
                      className="mt-2 w-full py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs flex items-center justify-center space-x-1 transition shadow-xs"
                    >
                      <span>Apply to Search Form &amp; View All Journeys</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-500 flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing travel request and calculating routes...</span>
              </div>
            </div>
          )}
        </div>

        {/* Suggestion Chips */}
        <div className="px-6 py-2 border-t border-slate-100 bg-slate-50 flex items-center space-x-2 overflow-x-auto text-xs">
          <span className="text-slate-400 font-medium whitespace-nowrap">Try asking:</span>
          {PRESET_QUERIES.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(preset)}
              className="px-2.5 py-1 rounded-full bg-white hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 border border-slate-200 whitespace-nowrap transition text-[11px]"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-200 bg-white">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything (e.g. 'Find the fastest train to Bangalore before 11 AM')..."
              className="flex-1 px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl disabled:opacity-40 transition shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

