import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Activity, 
  AlertTriangle, 
  Terminal, 
  BookOpen, 
  FileText, 
  Database, 
  Cpu, 
  User, 
  LogOut, 
  LogIn,
  CheckCircle,
  HelpCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function Navbar({ onOpenAuthModal }) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await api.get('/health');
        setHealth(res.data);
      } catch (err) {
        setHealth({ status: 'offline', database: { mode: 'disconnected' } });
      }
    }
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: Activity },
    { name: 'Incidents', path: '/incidents', icon: AlertTriangle },
    { name: 'Simulator', path: '/simulator', icon: Terminal, badge: '6x6' },
    { name: 'Knowledge Base', path: '/knowledge', icon: BookOpen, badge: 'RAG' },
    { name: 'Postmortems', path: '/postmortems', icon: FileText },
  ];

  return (
    <nav className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 via-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-base font-bold text-slate-100 tracking-wide flex items-center gap-2">
                  IncidentAgent <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-mono">AI SRE</span>
                </span>
                <span className="text-xs text-slate-400 block -mt-1">Investigation & Postmortem</span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40 font-mono">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Right Status Badges & User */}
          <div className="flex items-center gap-3">
            
            {/* Database Status */}
            <div 
              title={health?.database?.connected_to_mongo ? "Connected to MongoDB" : "Running on local In-Memory Store (Start MongoDB or configure Atlas in .env)"}
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-xs font-mono"
            >
              <Database className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-300">DB:</span>
              <span className={`w-2 h-2 rounded-full ${health?.database?.connected_to_mongo ? 'bg-emerald-500' : 'bg-amber-400 animate-pulse'}`} />
              <span className="text-slate-300">
                {health?.database?.connected_to_mongo ? 'Mongo' : 'In-Memory'}
              </span>
            </div>

            {/* AI Engine Status */}
            <div 
              title={health?.ai_engine?.openai_configured ? "OpenAI API Active" : "Offline SRE Heuristic Engine (Add OPENAI_API_KEY in .env for GPT-4o)"}
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-xs font-mono"
            >
              <Cpu className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-300">AI:</span>
              <span className={`w-2 h-2 rounded-full ${health?.ai_engine?.openai_configured ? 'bg-emerald-500' : 'bg-cyan-400'}`} />
              <span className="text-slate-300">
                {health?.ai_engine?.openai_configured ? 'GPT-4o' : 'SRE Engine'}
              </span>
            </div>

            {/* Auth / Profile */}
            {user ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-medium text-slate-200">{user.full_name || user.username}</div>
                  <div className="text-[10px] text-cyan-400 font-mono capitalize">{user.role}</div>
                </div>
                <button
                  onClick={logout}
                  title="Log out"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950/60 hover:text-rose-400 text-slate-400 border border-slate-700 transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={onOpenAuthModal}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-md shadow-indigo-600/20"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )}

          </div>

        </div>
      </div>
    </nav>
  );
}
