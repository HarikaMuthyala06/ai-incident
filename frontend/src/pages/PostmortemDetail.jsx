import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FileText, 
  ArrowLeft, 
  Download, 
  Printer, 
  Edit3, 
  Check, 
  Save, 
  ShieldAlert, 
  Clock, 
  CheckCircle2, 
  BookOpen,
  X
} from 'lucide-react';
import api from '../api/client';

export default function PostmortemDetail() {
  const { id } = useParams();
  const [postmortem, setPostmortem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);

  const fetchPostmortem = async () => {
    try {
      const res = await api.get(`/postmortems/${id}`);
      setPostmortem(res.data);
      setEditForm(res.data);
    } catch (err) {
      console.error('Failed to load postmortem:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPostmortem();
  }, [id]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.patch(`/postmortems/${id}`, {
        title: editForm.title,
        summary: editForm.summary,
        impact: editForm.impact,
        detection: editForm.detection,
        probable_root_cause: editForm.probable_root_cause,
        resolution: editForm.resolution,
        recovery: editForm.recovery,
        status: editForm.status
      });
      setPostmortem(res.data);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update postmortem:', err);
      alert('Error updating postmortem.');
    } finally {
      setSaving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-slate-400">Loading postmortem report...</p>
        </div>
      </div>
    );
  }

  if (!postmortem) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Postmortem not found.</p>
        <Link to="/postmortems" className="text-cyan-400 text-xs mt-2 inline-block">Return to postmortems list</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-20">
      
      {/* Top Action Controls */}
      <div className="flex items-center justify-between gap-4 print:hidden">
        <Link
          to="/postmortems"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Postmortems</span>
        </Link>

        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
            >
              <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Edit Report</span>
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(false)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs font-medium transition"
            >
              <X className="w-3.5 h-3.5" />
              <span>Cancel Edit</span>
            </button>
          )}

          <a
            href={`/api/postmortems/${postmortem.id}/export`}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Export Markdown</span>
          </a>

          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
          >
            <Printer className="w-3.5 h-3.5 text-slate-300" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Main Document Paper Container */}
      <div className="p-8 sm:p-12 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-8 text-slate-200 print:bg-white print:text-black print:p-0 print:border-none print:shadow-none">
        
        {/* Document Header */}
        <div className="border-b border-slate-800 pb-6 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-cyan-400 px-2.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/60 print:border-black print:text-black">
                {postmortem.incident_ref_id}
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 print:bg-gray-200 print:text-black">
                {postmortem.affected_system}
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40 print:border-black print:text-black">
                Status: {postmortem.status}
              </span>
            </div>

            <span className="text-xs text-slate-400 font-mono">
              Published: {new Date(postmortem.created_at).toLocaleDateString()}
            </span>
          </div>

          {!isEditing ? (
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight print:text-black">
              {postmortem.title}
            </h1>
          ) : (
            <input
              type="text"
              value={editForm.title}
              onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
              className="w-full text-xl font-bold p-2 rounded bg-slate-950 border border-slate-700 text-white"
            />
          )}

          <div className="flex flex-wrap gap-4 text-xs text-slate-400 font-mono pt-1">
            <span>Author: <strong className="text-slate-300 print:text-black">{postmortem.author}</strong></span>
            <span>Severity: <strong className="text-rose-400 print:text-black">{postmortem.severity}</strong></span>
            <span>SRE Standard: <strong className="text-slate-300 print:text-black">Blameless Postmortem</strong></span>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-400 font-mono print:text-black">
            1. Executive Summary
          </h2>
          {!isEditing ? (
            <p className="text-sm leading-relaxed text-slate-300 print:text-black">{postmortem.summary}</p>
          ) : (
            <textarea
              rows={3}
              value={editForm.summary}
              onChange={(e) => setEditForm({ ...editForm, summary: e.target.value })}
              className="w-full p-2.5 rounded bg-slate-950 border border-slate-700 text-xs text-slate-200"
            />
          )}
        </section>

        {/* Section 2: Impact & Scope */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-indigo-400 font-mono print:text-black">
            2. Customer & System Impact
          </h2>
          {!isEditing ? (
            <p className="text-sm leading-relaxed text-slate-300 print:text-black">{postmortem.impact}</p>
          ) : (
            <textarea
              rows={2}
              value={editForm.impact}
              onChange={(e) => setEditForm({ ...editForm, impact: e.target.value })}
              className="w-full p-2.5 rounded bg-slate-950 border border-slate-700 text-xs text-slate-200"
            />
          )}
        </section>

        {/* Section 3: Timeline */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-400 font-mono print:text-black">
            3. Chronological Incident Timeline
          </h2>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5 font-mono text-xs print:bg-gray-50 print:border-gray-300">
            {postmortem.timeline && postmortem.timeline.length > 0 ? (
              postmortem.timeline.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <span className="font-bold text-cyan-400 shrink-0 print:text-black">
                    {item.timestamp}
                  </span>
                  <span className="text-slate-300 print:text-black">
                    {item.event}
                  </span>
                  <span className="text-slate-500 text-[10px] ml-auto shrink-0">
                    [{item.source}]
                  </span>
                </div>
              ))
            ) : (
              <p className="text-slate-500">Timeline not reconstructed.</p>
            )}
          </div>
        </section>

        {/* Section 4: Probable Root Cause Hypothesis */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-rose-400 font-mono print:text-black">
            4. Probable Root Cause Hypothesis
          </h2>
          <div className="p-4 rounded-xl bg-gradient-to-r from-slate-950 to-indigo-950/30 border border-indigo-900/40 print:bg-gray-100 print:border-gray-400">
            {!isEditing ? (
              <p className="text-sm font-medium text-slate-200 leading-relaxed print:text-black">
                {postmortem.probable_root_cause}
              </p>
            ) : (
              <textarea
                rows={3}
                value={editForm.probable_root_cause}
                onChange={(e) => setEditForm({ ...editForm, probable_root_cause: e.target.value })}
                className="w-full p-2.5 rounded bg-slate-950 border border-slate-700 text-xs text-slate-200"
              />
            )}
          </div>
        </section>

        {/* Section 5: Supporting Evidence & Contributing Factors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-400 font-mono print:text-black">
              5. Supporting Telemetry Evidence
            </h2>
            <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside print:text-black">
              {postmortem.evidence.map((ev, idx) => (
                <li key={idx}>{ev}</li>
              ))}
            </ul>
          </section>

          <section className="space-y-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-indigo-400 font-mono print:text-black">
              6. Contributing Factors
            </h2>
            <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside print:text-black">
              {postmortem.contributing_factors.map((cf, idx) => (
                <li key={idx}>{cf}</li>
              ))}
            </ul>
          </section>
        </div>

        {/* Section 7: Resolution & Recovery */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-400 font-mono print:text-black">
            7. Resolution & Verification
          </h2>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs print:bg-gray-50 print:border-gray-300">
            <div>
              <span className="font-mono text-emerald-400 block mb-0.5 print:text-black font-bold">Mitigation Applied:</span>
              <p className="text-slate-300 print:text-black">{postmortem.resolution}</p>
            </div>
            <div className="pt-2 border-t border-slate-900 print:border-gray-200">
              <span className="font-mono text-slate-400 block mb-0.5 print:text-black font-bold">Recovery Check:</span>
              <p className="text-slate-300 print:text-black">{postmortem.recovery}</p>
            </div>
          </div>
        </section>

        {/* Section 8: Preventive Actions (Action Items) */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-amber-400 font-mono print:text-black">
            8. Preventive Actions & Action Items
          </h2>
          <div className="space-y-2">
            {postmortem.preventive_actions.map((pa, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start gap-2 print:bg-gray-50 print:border-gray-300 print:text-black">
                <span className="text-cyan-400 font-mono font-bold">[TODO]</span>
                <span>{pa}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 9: Lessons Learned */}
        <section className="space-y-2">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 font-mono print:text-black">
            9. Lessons Learned
          </h2>
          <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside print:text-black">
            {postmortem.lessons_learned.map((ll, idx) => (
              <li key={idx}>{ll}</li>
            ))}
          </ul>
        </section>

        {/* Save button when in edit mode */}
        {isEditing && (
          <div className="pt-4 border-t border-slate-800 flex justify-end gap-3 print:hidden">
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-md shadow-cyan-600/20 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Postmortem Changes'}
            </button>
          </div>
        )}

      </div>

    </div>
  );
}
