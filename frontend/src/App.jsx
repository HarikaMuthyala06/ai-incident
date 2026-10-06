import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import LoginModal from './components/LoginModal';
import Dashboard from './pages/Dashboard';
import IncidentsList from './pages/IncidentsList';
import IncidentDetail from './pages/IncidentDetail';
import IncidentSimulator from './pages/IncidentSimulator';
import KnowledgeBase from './pages/KnowledgeBase';
import PostmortemsList from './pages/PostmortemsList';
import PostmortemDetail from './pages/PostmortemDetail';

export default function App() {
  const [authModalOpen, setAuthModalOpen] = useState(false);

  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
          <Navbar onOpenAuthModal={() => setAuthModalOpen(true)} />
          
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/incidents" element={<IncidentsList />} />
              <Route path="/incidents/:id" element={<IncidentDetail />} />
              <Route path="/simulator" element={<IncidentSimulator />} />
              <Route path="/knowledge" element={<KnowledgeBase />} />
              <Route path="/postmortems" element={<PostmortemsList />} />
              <Route path="/postmortems/:id" element={<PostmortemDetail />} />
            </Routes>
          </main>

          <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-400 font-mono">
            <div className="max-w-7xl mx-auto px-4">
              AI Incident Investigation & Postmortem Agent • Computer Science SRE Portfolio Project
            </div>
          </footer>

          <LoginModal
            isOpen={authModalOpen}
            onClose={() => setAuthModalOpen(false)}
          />
        </div>
      </Router>
    </AuthProvider>
  );
}
