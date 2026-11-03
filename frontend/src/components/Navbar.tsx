import React from 'react';
import { Train, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'planner' | 'ml-explorer' | 'data-status';
  setActiveTab: (tab: 'planner' | 'ml-explorer' | 'data-status') => void;
  onOpenAI: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onOpenAI }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Left: Logo & RouteHelper Branding */}
          <div 
            className="flex items-center space-x-3 cursor-pointer shrink-0" 
            onClick={() => setActiveTab('planner')}
            title="RouteHelper India - Multimodal Public Transport"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-sm shadow-emerald-200">
              <Train className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg text-slate-900 tracking-tight">RouteHelper</span>
                <span className="text-[11px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                  India
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">Public Transport Route Helper</p>
            </div>
          </div>

          {/* Center-Left: Main Journey Planner Navigation */}
          <nav className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setActiveTab('planner')}
              className={`px-3.5 py-1.5 rounded-xl text-sm font-semibold transition flex items-center space-x-1.5 ${
                activeTab === 'planner'
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <span>Journey Planner</span>
            </button>
          </nav>

          {/* Right Action: Ask AI Assistant Button */}
          <div className="flex items-center">
            <button
              type="button"
              onClick={onOpenAI}
              className="flex items-center space-x-2 px-3.5 sm:px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold text-xs sm:text-sm shadow-sm hover:from-emerald-700 hover:to-teal-700 active:scale-98 transition shrink-0"
              title="Ask AI Assistant about Indian trains, buses, and routes"
            >
              <Sparkles className="w-4 h-4 text-emerald-200" />
              <span>Ask AI Assistant</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

