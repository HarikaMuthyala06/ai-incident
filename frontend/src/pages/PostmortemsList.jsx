import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  ArrowRight, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Download, 
  ExternalLink 
} from 'lucide-react';
import api from '../api/client';

export default function PostmortemsList() {
  const [postmortems, setPostmortems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPMs() {
      try {
        const res = await api.get('/postmortems/');
        setPostmortems(res.data);
      } catch (err) {
        console.error('Failed to load postmortems:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchPMs();
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Postmortem Reports</h1>
          <p className="text-xs text-slate-400 mt-1">
            Blameless engineering incident postmortems, action items, and root-cause analyses.
          </p>
        </div>

        <Link
          to="/incidents"
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
        >
          Generate from Incident
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading postmortems...</div>
      ) : postmortems.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 space-y-3">
          <FileText className="w-8 h-8 text-indigo-400 mx-auto" />
          <h3 className="text-sm font-semibold text-white">No Postmortems Created Yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Run an AI investigation on any open incident and click <strong>"Build Postmortem"</strong> to generate one automatically.
          </p>
          <Link
            to="/incidents"
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
          >
            Go to Incidents
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {postmortems.map((pm) => (
            <div
              key={pm.id}
              className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-cyan-400">
                    {pm.incident_ref_id}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {pm.affected_system}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40 font-medium">
                      {pm.status}
                    </span>
                  </div>
                </div>

                <Link to={`/postmortems/${pm.id}`} className="block">
                  <h3 className="text-base font-semibold text-white group-hover:text-cyan-400 transition">
                    {pm.title}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                    {pm.summary}
                  </p>
                </Link>

                <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60 text-xs text-slate-300">
                  <span className="text-[11px] font-mono text-cyan-400 block mb-0.5">Probable Root Cause:</span>
                  <p className="line-clamp-2 italic text-slate-300">{pm.probable_root_cause}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(pm.created_at).toLocaleDateString()}</span>
                </span>

                <div className="flex items-center gap-2">
                  <a
                    href={`/api/postmortems/${pm.id}/export`}
                    download
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                    title="Download Markdown"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </a>
                  <Link
                    to={`/postmortems/${pm.id}`}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
                  >
                    <span>Read Report</span>
                    <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
