import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { Overview } from './pages/Overview';
import { Sentiment } from './pages/Sentiment';
import { RawFeed } from './pages/RawFeed';
import { Topics } from './pages/Topics';
import { Search } from './pages/Search';
import { ExecutiveIntelligence } from './pages/ExecutiveIntelligence';
import { Reports } from './pages/Reports';
import { Alerts } from './pages/Alerts';
import { BrandDetails } from './pages/BrandDetails';
import { CompetitorAnalysis } from './pages/CompetitorAnalysis';
import { Chatbot } from './components/Chatbot';
import './index.css';

const TopNavBar = () => {
  const location = useLocation();
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return 'Dashboard Overview';
      case '/sentiment': return 'Sentiment Tracker';
      case '/feed': return 'Reviews Feed';
      case '/topics': return 'Complaint Themes';
      case '/search': return 'Search Insights';
      case '/intelligence': return 'Executive Intelligence';
      default: return 'Dashboard';
    }
  };

  return (
    <header className="w-full h-16 sticky top-0 z-40 bg-surface/40 backdrop-blur-3xl border-b border-white/40 flex justify-between items-center px-6 mb-8 rounded-xl shadow-sm">
      <div className="flex items-center gap-4">
        <span className="font-headline-md text-[24px] font-bold text-on-surface">{getPageTitle()}</span>
        <div className="h-4 w-[1px] bg-outline-variant mx-2"></div>
        <span className="text-on-surface-variant font-body-md text-[16px]">Q4 Analytics Overview</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative group">
          <input className="bg-surface-container-lowest border-none rounded-full py-2 px-10 focus:ring-2 focus:ring-primary/20 w-64 font-body-md text-[16px] shadow-sm transition-all" placeholder="Search insights..." type="text"/>
          <span className="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant">search</span>
        </div>
        <button className="w-10 h-10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors text-on-surface">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold border-2 border-white shadow-sm cursor-pointer hover:opacity-90">
          A
        </div>
      </div>
    </header>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="text-on-surface flex min-h-screen">
        <div className="aurora-bg"></div>
        
        {/* SideNavBar */}
        <nav className="h-screen w-72 fixed left-0 top-0 z-50 bg-surface/30 backdrop-blur-3xl border-r border-white/40 flex flex-col py-8 px-4">
          <div className="mb-10 px-4">
            <h1 className="font-headline-md text-[24px] font-extrabold text-on-surface tracking-tight">SocialIntel</h1>
            <p className="font-label-md text-[14px] text-on-surface-variant opacity-70">Market Insights</p>
          </div>
          <div className="space-y-2 flex-grow">
            <NavLink to="/" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`} end>
              <span className="material-symbols-outlined">dashboard</span>
              <span className="font-label-md text-[14px]">Overview</span>
            </NavLink>
            <NavLink to="/brands/amazon" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">storefront</span>
              <span className="font-label-md text-[14px]">Amazon Intelligence</span>
            </NavLink>
            <NavLink to="/compare" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">stacked_bar_chart</span>
              <span className="font-label-md text-[14px]">Competitor Analysis</span>
            </NavLink>
            <NavLink to="/search" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">search</span>
              <span className="font-label-md text-[14px]">Search Intelligence</span>
            </NavLink>
            <NavLink to="/intelligence" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">lightbulb</span>
              <span className="font-label-md text-[14px]">Executive Intelligence</span>
            </NavLink>
            <NavLink to="/reports" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">description</span>
              <span className="font-label-md text-[14px]">Reports</span>
            </NavLink>
            <NavLink to="/alerts" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 ${isActive ? 'bg-primary text-on-primary shadow-md translate-x-1' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/10'}`}>
              <span className="material-symbols-outlined">notifications_active</span>
              <span className="font-label-md text-[14px]">Alerts</span>
            </NavLink>
          </div>
          <div className="mt-auto pt-8 border-t border-white/20 space-y-2">
            <a className="flex items-center gap-3 text-on-surface-variant hover:text-on-surface px-4 py-3 hover:bg-white/10 rounded-full transition-all duration-300 cursor-pointer">
              <span className="material-symbols-outlined">help</span>
              <span className="font-label-md text-[14px]">Help Center</span>
            </a>
          </div>
        </nav>

        {/* Main Content */}
        <main className="ml-72 flex-1 p-8 min-h-screen">
          <TopNavBar />
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/brands/:brand" element={<BrandDetails />} />
              <Route path="/compare" element={<CompetitorAnalysis />} />
              <Route path="/sentiment" element={<Sentiment />} />
              <Route path="/feed" element={<RawFeed />} />
              <Route path="/topics" element={<Topics />} />
              <Route path="/search" element={<Search />} />
              <Route path="/intelligence" element={<ExecutiveIntelligence />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/alerts" element={<Alerts />} />
            </Routes>
          </div>
        </main>
        <Chatbot />
      </div>
    </Router>
  );
};

export default App;
