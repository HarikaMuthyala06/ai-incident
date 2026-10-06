import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Upload, 
  Layers, 
  FileText, 
  Search, 
  Eye, 
  Binary, 
  Sparkles, 
  Check, 
  X,
  FileCode,
  ShieldCheck,
  RefreshCw,
  Cpu
} from 'lucide-react';
import api from '../api/client';

export default function KnowledgeBase() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inspectDoc, setInspectDoc] = useState(null);
  const [chunksData, setChunksData] = useState(null);
  const [loadingChunks, setLoadingChunks] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Upload state
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Database');
  const [contentText, setContentText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchDocs = async () => {
    try {
      const res = await api.get('/knowledge/');
      setDocs(res.data);
    } catch (err) {
      console.error('Failed to load knowledge documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleInspectChunks = async (doc) => {
    setInspectDoc(doc);
    setLoadingChunks(true);
    try {
      const res = await api.get(`/knowledge/${doc.id}/chunks`);
      setChunksData(res.data);
    } catch (err) {
      console.error('Failed to inspect chunks:', err);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('category', category);
      if (selectedFile) {
        formData.append('file', selectedFile);
      } else {
        formData.append('content_text', contentText);
      }

      await api.post('/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setShowUploadModal(false);
      setTitle('');
      setContentText('');
      setSelectedFile(null);
      fetchDocs();
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed. Provide a file or paste content text.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      
      {/* Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-6 sm:p-8">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-xs font-mono text-cyan-300 w-fit mb-3">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Manual RAG Pipeline & Vector Database Inspector</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          SRE Troubleshooting Knowledge Base
        </h1>
        <p className="text-sm text-slate-300 max-w-2xl mt-1.5 leading-relaxed">
          Index technical runbooks, architecture specs, and postmortem records. Documents are automatically parsed (PyMuPDF for PDF, python-docx for DOCX), sliced with sliding-window chunk overlap, and embedded as 1536-dimensional vectors.
        </p>
      </div>

      {/* RAG Pipeline Explainer Infographic */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <h2 className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Binary className="w-4 h-4" />
          <span>Under the Hood: How Vector Ingestion & Search Works</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-cyan-400 font-mono font-bold">1. File Extraction</span>
            <p className="text-slate-400 text-[11px]">PyMuPDF for PDFs, python-docx for DOCXs, UTF-8 text parser.</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-indigo-400 font-mono font-bold">2. Cleaning & Chunking</span>
            <p className="text-slate-400 text-[11px]">700 character chunks with 150 character overlap to protect boundary context.</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-violet-400 font-mono font-bold">3. Dense Embeddings</span>
            <p className="text-slate-400 text-[11px]">OpenAI text-embedding-3-small converts text into 1536 float vectors.</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-pink-400 font-mono font-bold">4. Vector Search</span>
            <p className="text-slate-400 text-[11px]">MongoDB Atlas $vectorSearch or Cosine Similarity: (A·B)/(||A|| ||B||).</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-emerald-400 font-mono font-bold">5. Grounded Prompt</span>
            <p className="text-slate-400 text-[11px]">Top K retrieved chunks injected into LLM prompt for grounded analysis.</p>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white">Ingested Runbooks ({docs.length})</h2>
          <p className="text-xs text-slate-400">Guides actively available for AI incident retrieval.</p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-md shadow-cyan-600/20"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document / Guide</span>
        </button>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading knowledge base...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
                    {doc.category}
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">
                    {doc.total_chunks} Chunks
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white line-clamp-1">{doc.title}</h3>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {doc.content_preview}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[10px] font-mono text-slate-500">
                  {doc.source_filename}
                </span>

                <button
                  onClick={() => handleInspectChunks(doc)}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
                >
                  <Binary className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Inspect Chunks</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Vector Chunks Inspector Drawer / Modal */}
      {inspectDoc && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl p-6 space-y-5 shadow-2xl my-8 max-h-[85vh] flex flex-col">
            
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 shrink-0">
              <div>
                <div className="flex items-center gap-2">
                  <Binary className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Chunk Vector Inspector</h3>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Document: <span className="text-cyan-400 font-medium">{inspectDoc.title}</span> ({inspectDoc.total_chunks} vector chunks)
                </p>
              </div>
              <button
                onClick={() => setInspectDoc(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto space-y-4 pr-1">
              {loadingChunks ? (
                <div className="p-8 text-center text-xs text-slate-500">Loading vector segments...</div>
              ) : chunksData?.chunks ? (
                chunksData.chunks.map((chk, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-cyan-400 font-bold">{chk.chunk_id}</span>
                      <span className="text-slate-400">
                        {chk.text_length} chars | {chk.embedding_dimensions} dimensions
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 font-sans leading-relaxed whitespace-pre-wrap">
                      {chk.text}
                    </p>

                    {/* Embedding vector sample */}
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[10px] text-slate-400">
                      <span className="text-indigo-400 block mb-0.5">
                        Embedding Vector Preview [dim 0..5 of {chk.embedding_dimensions}]:
                      </span>
                      <code>[{chk.embedding_sample.map((n) => n.toFixed(6)).join(', ')}, ...]</code>
                    </div>
                  </div>
                ))
              ) : null}
            </div>

            <div className="pt-3 border-t border-slate-800 text-right shrink-0">
              <button
                onClick={() => setInspectDoc(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
              >
                Close Inspector
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Upload Runbook to Vector Store</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Redis Cluster Sentinel Failover Runbook"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Database">Database</option>
                  <option value="API">API</option>
                  <option value="Authentication">Authentication</option>
                  <option value="Deployment">Deployment</option>
                  <option value="Performance">Performance</option>
                  <option value="Microservice">Microservice</option>
                  <option value="General Troubleshooting">General Troubleshooting</option>
                </select>
              </div>

              {/* File Upload Option */}
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Upload File (PDF, DOCX, TXT, LOG, Markdown)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.log,.md,.json"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 file:mr-3 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:bg-slate-800 file:text-cyan-400 hover:file:bg-slate-700"
                />
              </div>

              {/* Or Manual Paste */}
              {!selectedFile && (
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Or Paste Text / Markdown Content
                  </label>
                  <textarea
                    rows={6}
                    placeholder="Paste runbook text, diagnostic instructions, or troubleshooting procedures..."
                    value={contentText}
                    onChange={(e) => setContentText(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-cyan-500"
                  />
                </div>
              )}

              <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-md shadow-cyan-600/20 disabled:opacity-50"
                >
                  {uploading ? 'Processing & Vectorizing...' : 'Index Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
