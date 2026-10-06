import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  Sparkles, 
  Clock, 
  FileText, 
  BookOpen, 
  History, 
  CheckCircle2, 
  ArrowLeft, 
  Terminal, 
  Layers, 
  ShieldAlert, 
  Search, 
  FileCode,
  Sliders,
  TrendingUp,
  Cpu,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import api from '../api/client';

const SEVERITY_BADGES = {
  Critical: 'bg-rose-950/80 text-rose-300 border-rose-800/60',
  High: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
  Medium: 'bg-yellow-950/80 text-yellow-300 border-yellow-800/60',
  Low: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60',
};

const RELEVANCE_BADGES = {
  High: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60',
  Medium: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
  Low: 'bg-slate-800 text-slate-300 border-slate-700',
};

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingPm, setGeneratingPm] = useState(false);
  const [activeTab, setActiveTab] = useState('evidence'); // evidence, logs, metrics

  const fetchIncident = async () => {
    try {
      const res = await api.get(`/incidents/${id}`);
      setIncident(res.data);
    } catch (err) {
      console.error('Failed to load incident:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleRunInvestigation = async () => {
    setAnalyzing(true);
    try {
      await api.post(`/analysis/${id}/analyze`);
      await fetchIncident();
    } catch (err) {
      console.error('AI investigation failed:', err);
      alert('Investigation failed. Check backend logs.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGeneratePostmortem = async () => {
    setGeneratingPm(true);
    try {
      const res = await api.post(`/postmortems/${id}/generate`);
      navigate(`/postmortems/${res.data.id}`);
    } catch (err) {
      console.error('Postmortem generation failed:', err);
      alert('Please run AI investigation before generating a postmortem.');
    } finally {
      setGeneratingPm(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await api.patch(`/incidents/${id}`, { status: newStatus });
      fetchIncident();
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-slate-400">Loading incident workspace...</p>
        </div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Incident not found.</p>
        <Link to="/incidents" className="text-cyan-400 text-xs mt-2 inline-block">Return to incidents list</Link>
      </div>
    );
  }

  const analysis = incident.analysis;
  const timeline = incident.timeline || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex items-center justify-between gap-4">
        <Link
          to="/incidents"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Incidents</span>
        </Link>

        <div className="flex items-center gap-2">
          {/* Status Selector */}
          <select
            value={incident.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="Open">Status: Open</option>
            <option value="Investigating">Status: Investigating</option>
            <option value="Mitigated">Status: Mitigated</option>
            <option value="Resolved">Status: Resolved</option>
          </select>

          {/* Postmortem Button */}
          {analysis && (
            <button
              onClick={handleGeneratePostmortem}
              disabled={generatingPm}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition shadow-sm disabled:opacity-50"
            >
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>{generatingPm ? 'Generating...' : 'View / Build Postmortem'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Incident Header Card */}
      <div className="p-6 sm:p-7 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-mono font-bold text-cyan-400 px-2.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/60">
            {incident.incident_id}
          </span>
          <span className={`px-2.5 py-0.5 rounded border text-xs font-mono font-medium ${SEVERITY_BADGES[incident.severity] || 'bg-slate-800 text-slate-300'}`}>
            {incident.severity} Severity
          </span>
          <span className="px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 text-xs font-mono">
            {incident.application}
          </span>
          <span className="px-2.5 py-0.5 rounded bg-slate-800 text-slate-400 text-xs font-mono">
            {incident.incident_type}
          </span>
          {incident.is_simulated && (
            <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/60 text-xs font-mono">
              SIMULATED SCENARIO
            </span>
          )}
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">{incident.title}</h1>
        <p className="text-sm text-slate-300 leading-relaxed">{incident.description}</p>

        {/* Investigate CTA */}
        <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 flex items-center gap-2 font-mono">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
          </div>

          <button
            onClick={handleRunInvestigation}
            disabled={analyzing}
            className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-violet-600 hover:opacity-95 text-white text-xs font-semibold tracking-wide uppercase transition shadow-lg shadow-indigo-600/25 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>RAG Retrieval & LLM Hypothesis In Progress...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>{analysis ? 'Re-Run AI Investigation' : 'Run AI RAG Investigation'}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Investigation Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Raw Evidence & Telemetry (1 col) */}
        <div className="space-y-4">
          
          <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <FileCode className="w-4 h-4 text-cyan-400" />
              <span>Incident Telemetry Evidence</span>
            </h2>

            {/* Error Message */}
            {incident.error_messages && (
              <div className="space-y-1">
                <span className="text-[11px] font-mono text-rose-400">Exception / Error Trace:</span>
                <pre className="p-3 rounded-lg bg-rose-950/20 border border-rose-900/40 text-[11px] font-mono text-rose-300 overflow-x-auto max-h-36">
                  {incident.error_messages}
                </pre>
              </div>
            )}

            {/* Application Logs */}
            {incident.logs && (
              <div className="space-y-1">
                <span className="text-[11px] font-mono text-slate-400">Application Logs:</span>
                <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-44">
                  {incident.logs}
                </pre>
              </div>
            )}

            {/* Recent Deployment */}
            {incident.recent_deployment && (
              <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/60 space-y-1">
                <span className="text-[11px] font-mono text-indigo-400 font-medium">Deployment Record:</span>
                <p className="text-xs text-slate-300">{incident.recent_deployment}</p>
              </div>
            )}

            {/* Metrics */}
            {incident.metrics && (
              <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/60 space-y-1">
                <span className="text-[11px] font-mono text-amber-400 font-medium">Telemetry Anomaly:</span>
                <p className="text-xs text-slate-300">{incident.metrics}</p>
              </div>
            )}

            {/* Config Changes */}
            {incident.configuration_changes && (
              <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/60 space-y-1">
                <span className="text-[11px] font-mono text-cyan-400 font-medium">Configuration Diffs:</span>
                <p className="text-xs text-slate-300">{incident.configuration_changes}</p>
              </div>
            )}
          </div>

          {/* Chronological Timeline Card */}
          {timeline.length > 0 && (
            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
              <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-400" />
                <span>Incident Timeline</span>
              </h2>

              <div className="space-y-3 relative before:absolute before:inset-0 before:left-2 before:w-0.5 before:bg-slate-800">
                {timeline.map((item, idx) => (
                  <div key={idx} className="relative pl-6 space-y-0.5">
                    <span className="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-cyan-500 ring-4 ring-slate-900" />
                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] font-mono font-semibold text-cyan-400">
                        {item.timestamp_display}
                      </span>
                      {item.is_inferred && (
                        <span className="text-[9px] px-1 rounded bg-slate-800 text-slate-400 font-mono">
                          Inferred
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300">{item.event}</p>
                    <span className="text-[10px] text-slate-500 font-mono">{item.source}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Right Column: AI Analysis & RAG Knowledge (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          
          {!analysis ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="w-12 h-12 rounded-xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center mx-auto text-indigo-400">
                <Cpu className="w-6 h-6" />
              </div>
              <h2 className="text-base font-semibold text-white">Investigation Not Executed Yet</h2>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                Click <strong>"Run AI RAG Investigation"</strong> above. The system will retrieve relevant runbooks from the vector knowledge base, cross-reference similar past incidents, and formulate a root-cause hypothesis.
              </p>
              <button
                onClick={handleRunInvestigation}
                disabled={analyzing}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium shadow-md shadow-cyan-600/20"
              >
                <Sparkles className="w-4 h-4" />
                <span>Initialize AI Analysis</span>
              </button>
            </div>
          ) : (
            <>
              
              {/* 1. Probable Root Cause Hypothesis Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/50 shadow-xl space-y-4">
                
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                      Root-Cause Hypothesis
                    </span>
                  </div>

                  {/* Confidence Rating Gauge */}
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950 border border-slate-800">
                    <span className="text-[11px] text-slate-400 font-mono">Confidence:</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {Math.round(analysis.confidence_score * 100)}% ({analysis.confidence_rating})
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white leading-snug">
                    {analysis.probable_root_cause}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {analysis.summary}
                  </p>
                </div>

                {/* Safety Guardrail Notice */}
                <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300/90 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Safety Guardrail:</strong> AI produces an evidence-grounded hypothesis, not definitive certainty. Always verify through telemetry before executing remediations.
                  </span>
                </div>

              </div>

              {/* 2. RAG Retrieved Knowledge & Evidence Inspection */}
              <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2 font-mono">
                    <BookOpen className="w-4 h-4 text-cyan-400" />
                    <span>Retrieved Knowledge Evidence (RAG Vector Search)</span>
                  </h3>
                  <span className="text-[11px] text-slate-400 font-mono">Atlas / Cosine Similarity</span>
                </div>

                {analysis.retrieved_knowledge_sources && analysis.retrieved_knowledge_sources.length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {analysis.retrieved_knowledge_sources.map((src, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2 hover:border-slate-700 transition"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded bg-slate-800 text-slate-300 flex items-center justify-center text-[10px] font-mono">
                              {idx + 1}
                            </span>
                            <span className="text-xs font-semibold text-white">{src.title}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <span className={`text-[10px] px-2 py-0.5 rounded border font-mono ${RELEVANCE_BADGES[src.relevance] || 'bg-slate-800 text-slate-300'}`}>
                              Relevance: {src.relevance}
                            </span>
                            {src.score && (
                              <span className="text-[10px] text-slate-400 font-mono">
                                ({src.score})
                              </span>
                            )}
                          </div>
                        </div>

                        {src.snippet && (
                          <p className="text-[11px] text-slate-400 font-mono line-clamp-2 pl-7 border-l border-slate-800">
                            {src.snippet}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No external runbooks retrieved.</p>
                )}
              </div>

              {/* 3. Supporting Evidence & Contributing Factors */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Supporting Evidence */}
                <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono text-cyan-400">
                    Supporting Evidence
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {analysis.supporting_evidence.map((ev, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Contributing Factors */}
                <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono text-indigo-400">
                    Contributing Factors
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {analysis.contributing_factors.map((cf, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0 mt-1.5" />
                        <span>{cf}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>

              {/* 4. Investigation Steps & Recommended Safe Resolution */}
              <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
                
                {/* Recommended Investigation Steps */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-400" />
                    <span>Recommended Investigation Steps (Diagnostics)</span>
                  </h4>
                  <div className="space-y-2">
                    {analysis.recommended_investigation_steps.map((step, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 font-mono text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-cyan-400">$</span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggested Resolution */}
                <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/40 space-y-1">
                  <span className="text-xs font-mono text-emerald-400 font-bold block">
                    Suggested Resolution / Mitigation:
                  </span>
                  <p className="text-xs text-emerald-200 leading-relaxed">
                    {analysis.suggested_resolution}
                  </p>
                </div>

                {/* Long-term Preventive Actions */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-400 font-bold uppercase tracking-wider block">
                    Preventive Actions:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {analysis.preventive_actions.map((act, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-indigo-400 font-bold">•</span>
                        <span>{act}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </>
          )}

        </div>

      </div>

    </div>
  );
}
