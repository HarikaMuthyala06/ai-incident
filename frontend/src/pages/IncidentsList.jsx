import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  Plus, 
  Clock, 
  Layers, 
  ArrowRight, 
  Trash2, 
  X,
  FileText,
  Activity,
  CheckCircle2
} from 'lucide-react';
import api from '../api/client';

const SEVERITY_BADGES = {
  Critical: 'bg-rose-950/80 text-rose-300 border-rose-800/60',
  High: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
  Medium: 'bg-yellow-950/80 text-yellow-300 border-yellow-800/60',
  Low: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60',
};

const STATUS_BADGES = {
  Open: 'bg-blue-950/80 text-blue-300 border-blue-800/60',
  Investigating: 'bg-purple-950/80 text-purple-300 border-purple-800/60',
  Mitigated: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
  Resolved: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60',
};

export default function IncidentsList() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedApp, setSelectedApp] = useState('All');
  const [selectedSev, setSelectedSev] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form state for creating incident
  const [newIncident, setNewIncident] = useState({
    title: '',
    application: 'E-commerce',
    incident_type: 'API',
    severity: 'High',
    description: '',
    logs: '',
    error_messages: '',
    recent_deployment: '',
    metrics: '',
    configuration_changes: ''
  });
  const [creating, setCreating] = useState(false);

  const fetchIncidents = async () => {
    try {
      const params = {};
      if (selectedApp !== 'All') params.application = selectedApp;
      if (selectedSev !== 'All') params.severity = selectedSev;
      if (selectedStatus !== 'All') params.status = selectedStatus;
      if (search) params.search = search;

      const res = await api.get('/incidents/', { params });
      setIncidents(res.data);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [selectedApp, selectedSev, selectedStatus]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchIncidents();
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post('/incidents/', newIncident);
      setShowCreateModal(false);
      setNewIncident({
        title: '',
        application: 'E-commerce',
        incident_type: 'API',
        severity: 'High',
        description: '',
        logs: '',
        error_messages: '',
        recent_deployment: '',
        metrics: '',
        configuration_changes: ''
      });
      fetchIncidents();
    } catch (err) {
      console.error('Failed to create incident:', err);
      alert('Error creating incident.');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this incident record?')) return;
    try {
      await api.delete(`/incidents/${id}`);
      fetchIncidents();
    } catch (err) {
      console.error('Failed to delete incident:', err);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Incidents Directory</h1>
          <p className="text-xs text-slate-400 mt-1">Manage, triage, and trigger AI investigations for production outages.</p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/simulator"
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition"
          >
            Launch Simulator
          </Link>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-md shadow-cyan-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Report Incident</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row gap-3 items-center justify-between">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search by ID, title, or error..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>

        {/* Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Application */}
          <select
            value={selectedApp}
            onChange={(e) => setSelectedApp(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Domains</option>
            <option value="E-commerce">E-commerce</option>
            <option value="Ride Booking">Ride Booking</option>
            <option value="College Portal">College Portal</option>
            <option value="Banking">Banking</option>
            <option value="Chat Application">Chat Application</option>
            <option value="Delivery Application">Delivery Application</option>
          </select>

          {/* Severity */}
          <select
            value={selectedSev}
            onChange={(e) => setSelectedSev(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {/* Status */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Mitigated">Mitigated</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>

      </div>

      {/* Incidents Table / Cards */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading incidents...</div>
      ) : incidents.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 space-y-3">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
          <h3 className="text-sm font-semibold text-white">No Incidents Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Try adjusting your search filters or launch the Simulator to synthesize realistic production incidents.
          </p>
          <Link
            to="/simulator"
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
          >
            Generate Simulated Incident
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {incidents.map((inc) => (
            <div
              key={inc.id}
              className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex flex-col md:flex-row md:items-center justify-between gap-4 group"
            >
              <div className="space-y-2 max-w-3xl">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="font-mono text-cyan-400 font-bold">{inc.incident_id}</span>
                  <span className={`px-2 py-0.5 rounded border text-[11px] font-mono font-medium ${SEVERITY_BADGES[inc.severity] || 'bg-slate-800 text-slate-300'}`}>
                    {inc.severity}
                  </span>
                  <span className={`px-2 py-0.5 rounded border text-[11px] font-mono font-medium ${STATUS_BADGES[inc.status] || 'bg-slate-800 text-slate-300'}`}>
                    {inc.status}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] font-mono">
                    {inc.application}
                  </span>
                  {inc.is_simulated && (
                    <span className="px-1.5 py-0.2 rounded bg-amber-950/60 text-amber-400 border border-amber-800/40 text-[10px] font-mono">
                      SIMULATED
                    </span>
                  )}
                </div>

                <Link to={`/incidents/${inc.id}`} className="block">
                  <h3 className="text-base font-semibold text-white group-hover:text-cyan-400 transition">
                    {inc.title}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-0.5">
                    {inc.description}
                  </p>
                </Link>

                {inc.analysis && (
                  <div className="text-xs bg-slate-950/60 border border-slate-800/80 rounded-lg p-2.5 text-slate-300 flex items-start gap-2">
                    <span className="text-cyan-400 font-mono text-[11px] uppercase whitespace-nowrap">Root-Cause Hypothesis:</span>
                    <span className="line-clamp-1 italic text-slate-200">{inc.analysis.probable_root_cause}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2 self-end md:self-center">
                <Link
                  to={`/incidents/${inc.id}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
                >
                  <span>Investigate</span>
                  <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                </Link>
                <button
                  onClick={(e) => handleDelete(inc.id, e)}
                  title="Delete incident"
                  className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-rose-950/60 hover:text-rose-400 text-slate-500 border border-slate-800 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Manual Create Incident Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl p-6 space-y-5 shadow-2xl my-8">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold text-white">Report New Incident</h2>
                <p className="text-xs text-slate-400">Provide title, symptoms, pasted logs, and deployment details.</p>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Incident Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Payment Gateway 504 Timeout during Checkout"
                  value={newIncident.title}
                  onChange={(e) => setNewIncident({ ...newIncident, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Application</label>
                  <select
                    value={newIncident.application}
                    onChange={(e) => setNewIncident({ ...newIncident, application: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="E-commerce">E-commerce</option>
                    <option value="Ride Booking">Ride Booking</option>
                    <option value="College Portal">College Portal</option>
                    <option value="Banking">Banking</option>
                    <option value="Chat Application">Chat Application</option>
                    <option value="Delivery Application">Delivery Application</option>
                    <option value="Other System">Other System</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Incident Type</label>
                  <select
                    value={newIncident.incident_type}
                    onChange={(e) => setNewIncident({ ...newIncident, incident_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="API">API</option>
                    <option value="Database">Database</option>
                    <option value="Authentication">Authentication</option>
                    <option value="Performance">Performance</option>
                    <option value="Deployment">Deployment</option>
                    <option value="Microservice">Microservice</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Severity</label>
                  <select
                    value={newIncident.severity}
                    onChange={(e) => setNewIncident({ ...newIncident, severity: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description / Observed Symptoms *</label>
                <textarea
                  required
                  rows={2}
                  placeholder="Describe user impact, what failed, and when it started..."
                  value={newIncident.description}
                  onChange={(e) => setNewIncident({ ...newIncident, description: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Application / Server Logs</label>
                  <textarea
                    rows={4}
                    placeholder="Paste log output, timestamped log lines..."
                    value={newIncident.logs}
                    onChange={(e) => setNewIncident({ ...newIncident, logs: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Error Messages / Stack Traces</label>
                  <textarea
                    rows={4}
                    placeholder="Paste stack traces, exceptions, HTTP error responses..."
                    value={newIncident.error_messages}
                    onChange={(e) => setNewIncident({ ...newIncident, error_messages: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Recent Deployment / Git Commits</label>
                  <input
                    type="text"
                    placeholder="e.g. Commit a89f1 deployed 20 minutes ago"
                    value={newIncident.recent_deployment}
                    onChange={(e) => setNewIncident({ ...newIncident, recent_deployment: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Telemetry Metrics / Anomaly</label>
                  <input
                    type="text"
                    placeholder="e.g. CPU 98%, p99 latency 14s, 5xx rate 40%"
                    value={newIncident.metrics}
                    onChange={(e) => setNewIncident({ ...newIncident, metrics: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-md shadow-cyan-600/20 disabled:opacity-50"
                >
                  {creating ? 'Saving...' : 'Save Incident'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
