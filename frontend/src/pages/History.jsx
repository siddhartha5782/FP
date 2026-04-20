import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../AuthContext';
import { useNavigate } from 'react-router-dom';
import { Clock, Archive, ChevronRight, X, MessageSquare, Activity } from 'lucide-react';
import { marked } from 'marked';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedScan, setSelectedScan] = useState(null);
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchHistory = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/history", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Failed to fetch history");
        const data = await res.json();
        setHistory(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [isAuthenticated, navigate, token]);

  if (loading) {
     return <div className="container" style={{justifyContent: 'center', alignItems: 'center'}}><div className="spinner"></div></div>;
  }

  return (
    <main className="container page-fade" style={{ flexDirection: 'column', maxWidth: '1000px', margin: '0 auto', paddingTop: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <Archive size={32} color="var(--primary)" />
        <h2>Your Scans Archive</h2>
      </div>

      {error && <div style={{ color: 'var(--accent-red)', marginBottom: '1rem' }}>{error}</div>}

      {history.length === 0 ? (
        <div className="panel glass" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <Clock size={48} color="var(--text-muted)" style={{ marginBottom: '1rem', opacity: 0.5 }} />
          <h3 style={{ color: 'var(--text-muted)' }}>No scans found.</h3>
          <p style={{ marginTop: '0.5rem', color: 'rgba(255,255,255,0.4)' }}>Upload your first chest X-ray in the Dashboard.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {history.map(scan => (
            <div key={scan.id} className="panel glass" style={{ display: 'flex', flexDirection: 'row', gap: '1.25rem', alignItems: 'center', padding: '1rem 1.5rem' }}>

              {/* Thumbnail */}
              <div style={{ width: '90px', height: '90px', borderRadius: '10px', overflow: 'hidden', background: '#000', flexShrink: 0, border: '1px solid rgba(255,255,255,0.08)' }}>
                {scan.original_image && <img src={scan.original_image} alt="Thumbnail" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />}
              </div>

              {/* Text content */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                  {scan.predictions.length > 0 ? scan.predictions[0].condition : 'No significant findings'}
                </h3>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Clock size={12} /> {new Date(scan.timestamp).toLocaleString()}
                </div>
                <p style={{ fontSize: '0.83rem', color: 'rgba(255,255,255,0.55)', lineHeight: 1.5, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                  {scan.chat_log.length > 0 ? scan.chat_log[0].text.substring(0, 160) + '…' : 'No clinical context recorded.'}
                </p>
              </div>

              {/* Action */}
              <div style={{ flexShrink: 0 }}>
                <button className="btn secondary" style={{ padding: '0.5rem 1rem', whiteSpace: 'nowrap' }} onClick={() => setSelectedScan(scan)}>
                  View Details <ChevronRight size={16} />
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

      {selectedScan && createPortal(
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)',
          zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem'
        }}>
          <div className="panel glass modal-animate" style={{
            width: '100%', maxWidth: '900px', maxHeight: '85vh', display: 'flex',
            flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', position: 'relative',
            transform: 'none'
          }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ color: 'var(--primary)' }}>
                Scan from {new Date(selectedScan.timestamp).toLocaleString()}
              </h3>
              <button className="btn secondary" style={{ padding: '0.4rem 0.8rem' }} onClick={() => setSelectedScan(null)}>
                <X size={18} />
              </button>
            </div>

            {/* Image + Predictions side by side */}
            <div style={{ display: 'flex', gap: '1.5rem' }}>
              <div style={{ width: '220px', flexShrink: 0, borderRadius: '10px', overflow: 'hidden', background: '#000', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {selectedScan.original_image && (
                  <img src={selectedScan.original_image} alt="X-Ray" style={{ width: '100%', objectFit: 'contain' }} />
                )}
                {/* Overlay the top-condition heatmap if available */}
                {selectedScan.predictions.length > 0 && selectedScan.heatmaps && selectedScan.heatmaps[selectedScan.predictions[0].condition] && (
                  <img
                    src={selectedScan.heatmaps[selectedScan.predictions[0].condition]}
                    alt="Grad-CAM"
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', opacity: 0.85, mixBlendMode: 'screen' }}
                  />
                )}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--primary)' }}>
                  <Activity size={16} /> <strong>Identified Pathologies</strong>
                </div>
                {selectedScan.predictions.length > 0 ? selectedScan.predictions.map((p, i) => {
                  const conf = (p.confidence * 100).toFixed(1);
                  const barClass = p.confidence > 0.7 ? 'high' : p.confidence > 0.3 ? 'med' : 'low';
                  return (
                    <div key={i} className="prediction-item">
                      <div className="pred-header"><span>{p.condition}</span><span>{conf}%</span></div>
                      <div className="pred-bar-bg"><div className={`pred-bar ${barClass}`} style={{ width: `${conf}%` }}></div></div>
                    </div>
                  );
                }) : <p style={{ color: 'var(--text-muted)' }}>No significant findings.</p>}
              </div>
            </div>

            {/* Chat Log */}
            <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--primary)' }}>
                <MessageSquare size={16} /> <strong>Chat History</strong>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto', maxHeight: '300px', paddingRight: '0.25rem' }}>
                {selectedScan.chat_log.length > 0 ? selectedScan.chat_log.map((msg, i) => (
                  <div key={i} className={`chat-bubble ${msg.type}`} style={{ maxWidth: '100%' }}>
                    {msg.type === 'system' ? (
                      <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} className="markdown-body" style={{ color: 'inherit' }} />
                    ) : msg.text}
                  </div>
                )) : <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No chat messages recorded for this scan.</p>}
              </div>
            </div>
          </div>
        </div>
      , document.body)}
    </main>
  );
}
