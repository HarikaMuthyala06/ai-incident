import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Terminal, 
  Sparkles, 
  Server, 
  AlertTriangle, 
  Clock, 
  ArrowRight, 
  Copy, 
  Check, 
  CheckCircle2,
  FileCode,
  Sliders,
  Send
} from 'lucide-react';
import api from '../api/client';

const APPLICATIONS = [
  { id: 'E-commerce', name: 'E-commerce Platform', icon: '🛒', desc: 'Online storefront, payment gateway & checkout' },
  { id: 'Ride Booking', name: 'Ride Booking System', icon: '🚖', desc: 'Real-time driver dispatch & geospatial matching' },
  { id: 'College Portal', name: 'College / Student Portal', icon: '🎓', desc: 'Admissions, exam registrations & hall-tickets' },
  { id: 'Banking', name: 'Core Banking Service', icon: '🏦', desc: 'Ledger settlements, payments & JWT auth' },
  { id: 'Chat Application', name: 'Chat & Messaging App', icon: '💬', desc: 'WebSockets, async queues & push workers' },
  { id: 'Delivery Application', name: 'Food / Parcel Delivery', icon: '📦', desc: 'Dispatch routes, partner apps & tracking' }
];

const INCIDENT_TYPES = [
  { id: 'Database Failure', name: 'Database Failure', desc: 'Pool exhaustion, table locks & timeouts' },
  { id: 'API Failure', name: 'API Failure', desc: 'Cascading 500s, 504 gateway timeouts' },
  { id: 'Authentication Failure', name: 'Authentication Failure', desc: 'JWT expiration, clock drift & JWKS errors' },
  { id: 'Performance Issue', name: 'Performance Issue', desc: 'High latency, missing database indexes' },
  { id: 'Deployment Failure', name: 'Deployment Failure', desc: 'Missing environment variables, OOMKilled' },
  { id: 'Microservice Failure', name: 'Microservice Failure', desc: 'gRPC timeouts & async queue congestion' }
];

export default function IncidentSimulator() {
  const navigate = useNavigate();
  const [selectedApp, setSelectedApp] = useState('E-commerce');
  const [selectedType, setSelectedType] = useState('Database Failure');
  const [generating, setGenerating] = useState(false);
  const [simulatedData, setSimulatedData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await api.post('/simulator/generate', {
        application: selectedApp,
        incident_type: selectedType
      });
      setSimulatedData(res.data);
    } catch (err) {
      console.error('Failed to generate simulation:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveAndInvestigate = async () => {
    if (!simulatedData) return;
    setSaving(true);
    try {
      // 1. Create incident in system
      const res = await api.post('/incidents/', {
        title: simulatedData.title,
        application: simulatedData.application,
        incident_type: simulatedData.incident_type,
        severity: simulatedData.severity,
        description: simulatedData.description,
        logs: simulatedData.logs,
        error_messages: simulatedData.error_messages,
        recent_deployment: simulatedData.recent_deployment,
        metrics: simulatedData.metrics,
        configuration_changes: simulatedData.configuration_changes,
        is_simulated: true
      });

      // 2. Navigate straight to investigation page
      navigate(`/incidents/${res.data.id}`);
    } catch (err) {
      console.error('Failed to save simulated incident:', err);
      alert('Error creating incident. Check backend connection.');
    } finally {
      setSaving(false);
    }
  };

  const copyLogs = () => {
    if (simulatedData?.logs) {
      navigator.clipboard.writeText(simulatedData.logs);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      
      {/* Header Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-6 sm:p-8">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-xs font-mono text-cyan-300 w-fit mb-3">
          <Terminal className="w-3.5 h-3.5" />
          <span>Synthetic Production Incident Generator (6 × 6 Matrix)</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Incident Telemetry Simulator
        </h1>
        <p className="text-sm text-slate-300 max-w-2xl mt-1.5 leading-relaxed">
          Select any application domain and subsystem failure type. The simulator generates realistic, timestamped logs, error traces, deployment diffs, and metrics for live demonstrations without modifying production systems.
        </p>
      </div>

      {/* Simulator Selection Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Step 1: Application Domain Selection */}
        <div className="p-6 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-600 text-white flex items-center justify-center text-xs font-mono">1</span>
              <span>Target Application System</span>
            </h2>
            <span className="text-xs text-slate-400">Choose Domain</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {APPLICATIONS.map((app) => (
              <button
                key={app.id}
                type="button"
                onClick={() => setSelectedApp(app.id)}
                className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                  selectedApp === app.id
                    ? 'bg-cyan-950/40 border-cyan-500 shadow-md shadow-cyan-900/20 ring-1 ring-cyan-500'
                    : 'bg-slate-800/60 border-slate-700/60 hover:bg-slate-800 hover:border-slate-600 text-slate-300'
                }`}
              >
                <div className="flex items-center gap-2.5 mb-1.5">
                  <span className="text-xl">{app.icon}</span>
                  <span className="text-sm font-medium text-white">{app.name}</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{app.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Step 2: Incident Type Selection */}
        <div className="p-6 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-mono">2</span>
              <span>Subsystem Failure Scenario</span>
            </h2>
            <span className="text-xs text-slate-400">Choose Failure</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {INCIDENT_TYPES.map((type) => (
              <button
                key={type.id}
                type="button"
                onClick={() => setSelectedType(type.id)}
                className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                  selectedType === type.id
                    ? 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-900/20 ring-1 ring-indigo-500'
                    : 'bg-slate-800/60 border-slate-700/60 hover:bg-slate-800 hover:border-slate-600 text-slate-300'
                }`}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <AlertTriangle className={`w-4 h-4 ${selectedType === type.id ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span className="text-sm font-medium text-white">{type.name}</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{type.desc}</p>
              </button>
            ))}
          </div>

          {/* Action Button */}
          <div className="pt-2">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-violet-600 hover:opacity-95 text-white font-medium text-sm transition shadow-lg shadow-indigo-600/25 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Synthesizing Telemetry...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Incident Evidence</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>

      {/* Simulated Evidence Output Panel */}
      {simulatedData && (
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 overflow-hidden shadow-xl space-y-6 p-6 sm:p-8 animate-in fade-in duration-300">
          
          {/* Output Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full bg-amber-950/80 text-amber-300 border border-amber-800/60 text-xs font-mono font-medium">
                  SIMULATED INCIDENT
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-rose-950/80 text-rose-300 border border-rose-800/60 text-xs font-mono font-medium">
                  {simulatedData.severity} Severity
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 text-xs font-mono">
                  {simulatedData.application}
                </span>
              </div>
              <h2 className="text-xl font-bold text-white">{simulatedData.title}</h2>
              <p className="text-xs text-slate-300 mt-1">{simulatedData.description}</p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleSaveAndInvestigate}
                disabled={saving}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-sm font-medium transition shadow-lg shadow-cyan-600/20 disabled:opacity-50"
              >
                {saving ? (
                  <span>Initializing RAG Agent...</span>
                ) : (
                  <>
                    <span>Investigate with AI Agent</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Evidence Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Logs Window */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5 font-mono">
                  <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Application & System Logs</span>
                </span>
                <button
                  onClick={copyLogs}
                  className="flex items-center gap-1 hover:text-white transition"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto max-h-56">
                {simulatedData.logs}
              </pre>
            </div>

            {/* Error Message & Stack Trace */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5 font-mono">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Error Messages & Exceptions</span>
                </span>
              </div>
              <pre className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/40 font-mono text-xs text-rose-300 leading-relaxed overflow-x-auto max-h-56">
                {simulatedData.error_messages}
              </pre>
            </div>

            {/* Recent Deployment */}
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-1">
              <span className="text-xs font-mono text-indigo-400 block font-medium">Recent Deployment / Git Commit:</span>
              <p className="text-xs text-slate-200">{simulatedData.recent_deployment}</p>
            </div>

            {/* System Telemetry Metrics */}
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-1">
              <span className="text-xs font-mono text-amber-400 block font-medium">Telemetry & Metrics Anomaly:</span>
              <p className="text-xs text-slate-200">{simulatedData.metrics}</p>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
