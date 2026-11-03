import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { DelayPredictorTab } from './components/DelayPredictorTab';
import { DataStatusTab } from './components/DataStatusTab';
import { Train } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'planner' | 'ml-explorer' | 'data-status'>('planner');
  const [isAIOpen, setIsAIOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col selection:bg-emerald-500 selection:text-white">
      {/* Global Clean Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAI={() => setIsAIOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        {activeTab === 'planner' && (
          <HomePage isAIOpen={isAIOpen} setIsAIOpen={setIsAIOpen} />
        )}

        {activeTab === 'ml-explorer' && (
          <DelayPredictorTab />
        )}

        {activeTab === 'data-status' && (
          <DataStatusTab />
        )}
      </main>

      {/* Application Footer with Utility Navigation */}
      <footer className="bg-white border-t border-slate-200/80 py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-lg bg-emerald-600 flex items-center justify-center text-white">
              <Train className="w-3.5 h-3.5" />
            </div>
            <span className="font-bold text-slate-800">Public Transport Route Helper for India</span>
            <span>&bull;</span>
            <span>Multimodal GenAI &amp; ML Optimization</span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px]">
            <button 
              type="button"
              onClick={() => setActiveTab('planner')}
              className={`hover:underline transition ${activeTab === 'planner' ? 'font-bold text-emerald-700' : 'text-slate-600'}`}
            >
              Journey Planner
            </button>
            <span>&bull;</span>
            <button 
              type="button"
              onClick={() => setActiveTab('ml-explorer')}
              className={`hover:underline transition ${activeTab === 'ml-explorer' ? 'font-bold text-emerald-700' : 'text-slate-600'}`}
            >
              Delay Predictor ML
            </button>
            <span>&bull;</span>
            <button 
              type="button"
              onClick={() => setActiveTab('data-status')}
              className={`hover:underline transition ${activeTab === 'data-status' ? 'font-bold text-emerald-700' : 'text-slate-600'}`}
            >
              Transit Data Coverage
            </button>
            <span>&bull;</span>
            <span className="text-slate-400">Mistral AI (Codestral) Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
