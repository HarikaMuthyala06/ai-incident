import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  AlertOctagon, 
  CheckCircle2, 
  Clock, 
  Layers, 
  Server, 
  ArrowRight, 
  PlusCircle,
  Terminal,
  ShieldCheck,
  TrendingDown
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';
import api from '../api/client';

const SEVERITY_COLORS = {
  Critical: '#f43f5e',
  High: '#f97316',
  Medium: '#eab308',
  Low: '#10b981',
};

const CHART_COLORS = ['#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb923c', '#4ade80'];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await api.get('/incidents/stats');
        setStats(res.data);
      } catch (err) {
        console.error('Failed to load incident statistics:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-slate-400">Loading reliability telemetry...</p>
        </div>
      </div>
    );
  }

  const summary = stats?.summary || {
    total_incidents: 0,
    open_incidents: 0,
    resolved_incidents: 0,
    critical_incidents: 0,
    avg_resolution_time_minutes: 0,
  };

  const statCards = [
    {
      label: 'Total Incidents',
      value: summary.total_incidents,
      desc: 'Recorded platform events',
      icon: Layers,
      color: 'text-indigo-400',
      bg: 'bg-indigo-950/40 border-indigo-800/40',
    },
    {
      label: 'Active & Open',
      value: summary.open_incidents,
      desc: 'Under investigation',
      icon: Activity,
      color: 'text-amber-400',
      bg: 'bg-amber-950/40 border-amber-800/40',
    },
    {
      label: 'Critical Priority',
      value: summary.critical_incidents,
      desc: 'High business impact',
      icon: AlertOctagon,
      color: 'text-rose-400',
      bg: 'bg-rose-950/40 border-rose-800/40',
    },
    {
      label: 'Mean Time To Recover',
      value: `${summary.avg_resolution_time_minutes}m`,
      desc: 'Average SLA recovery',
      icon: Clock,
      color: 'text-emerald-400',
      bg: 'bg-emerald-950/40 border-emerald-800/40',
    },
  ];

  return (
    <div className="space-y-8 pb-12">
      
      {/* Top Welcome / Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-6 sm:p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-xs font-mono text-cyan-300 mb-3">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Reliability Engineering & AI Postmortems</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              AI Incident Investigation Center
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl mt-1.5 leading-relaxed">
              Automated multi-system root cause hypothesis generator. Ingests logs, stack traces, and metrics, retrieves relevant technical runbooks via RAG, and produces evidence-grounded postmortems.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/simulator"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition shadow-sm"
            >
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>Run Simulator</span>
            </Link>
            <Link
              to="/incidents"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-sm font-medium transition shadow-lg shadow-cyan-600/20"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Investigate Incident</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-5 rounded-xl border ${card.bg} backdrop-blur-sm transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{card.label}</span>
                <div className={`p-2 rounded-lg bg-slate-900/60 border border-slate-800 ${card.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-2 text-2xl font-bold text-white font-mono">{card.value}</div>
              <div className="mt-1 text-xs text-slate-400">{card.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Visualizations Section with Recharts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Incidents by Failure Type */}
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Incidents by Subsystem Type</h2>
              <p className="text-xs text-slate-400">Distribution across architectural components</p>
            </div>
            <Server className="w-4 h-4 text-slate-500" />
          </div>

          <div className="h-64 w-full">
            {stats?.by_type && stats.by_type.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.by_type} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                  <XAxis 
                    dataKey="type" 
                    stroke="#94a3b8" 
                    fontSize={11} 
                    angle={-20} 
                    textAnchor="end" 
                    tick={{ fill: '#94a3b8' }}
                  />
                  <YAxis stroke="#94a3b8" fontSize={11} tick={{ fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {stats.by_type.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No incidents recorded yet. Generate one in the Simulator!
              </div>
            )}
          </div>
        </div>

        {/* Incidents by Application */}
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Incidents by Application Domain</h2>
              <p className="text-xs text-slate-400">Multi-domain platform tracking</p>
            </div>
            <Layers className="w-4 h-4 text-slate-500" />
          </div>

          <div className="h-64 w-full">
            {stats?.by_application && stats.by_application.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.by_application} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                  <XAxis 
                    dataKey="application" 
                    stroke="#94a3b8" 
                    fontSize={11} 
                    angle={-20} 
                    textAnchor="end"
                    tick={{ fill: '#94a3b8' }}
                  />
                  <YAxis stroke="#94a3b8" fontSize={11} tick={{ fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {stats.by_application.map((entry, index) => (
                      <Cell key={`app-cell-${index}`} fill={CHART_COLORS[(index + 2) % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No application telemetry yet.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Severity Breakdown & Quick Guide */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Severity Pie Chart */}
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <h2 className="text-base font-semibold text-white mb-1">Severity Distribution</h2>
          <p className="text-xs text-slate-400 mb-4">Critical vs High vs Medium vs Low</p>

          <div className="h-52 w-full">
            {stats?.by_severity && stats.by_severity.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.by_severity}
                    dataKey="count"
                    nameKey="severity"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {stats.by_severity.map((entry, index) => (
                      <Cell 
                        key={`sev-cell-${index}`} 
                        fill={SEVERITY_COLORS[entry.severity] || '#94a3b8'} 
                      />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No severity records.
              </div>
            )}
          </div>

          <div className="flex flex-wrap justify-center gap-3 pt-2 text-xs">
            {Object.entries(SEVERITY_COLORS).map(([name, color]) => (
              <div key={name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-slate-300">{name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* How The RAG Agent Works (Educational Callout) */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <span>RAG Incident Investigation Engine</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60">
                  How It Works
                </span>
              </h2>
            </div>
            
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              When an incident is created, our manual RAG engine computes semantic dense vector embeddings, executes Cosine Similarity search over the knowledge base, correlates similar past incidents, and guides the LLM to output a guarded <strong>Probable Root Cause Hypothesis</strong>.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <div className="text-[11px] font-mono text-cyan-400 mb-1">1. Vector Search</div>
                <div className="text-xs text-slate-300">Retrieves relevant troubleshooting runbooks using Cosine distance.</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <div className="text-[11px] font-mono text-indigo-400 mb-1">2. Evidence Fusion</div>
                <div className="text-xs text-slate-300">Correlates error stack traces, log lines, and deployment changes.</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <div className="text-[11px] font-mono text-violet-400 mb-1">3. Safe Postmortem</div>
                <div className="text-xs text-slate-300">Builds verified timeline and blameless postmortem export.</div>
              </div>
            </div>
          </div>

          <div className="pt-5 mt-4 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">Explore pre-seeded incident scenarios:</span>
            <Link
              to="/simulator"
              className="text-xs font-medium text-cyan-400 hover:text-cyan-300 flex items-center gap-1 group"
            >
              <span>Open 6x6 Simulator</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </div>

      </div>

    </div>
  );
}
