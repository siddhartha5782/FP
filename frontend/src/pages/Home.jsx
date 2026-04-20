import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ShieldCheck, Zap } from 'lucide-react';
import { useAuth } from '../AuthContext';


export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <main
      className="container page-fade"
      style={{
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        minHeight: '80vh',
        position: 'relative',
        overflow: 'hidden',
      }}
    >

      {/* ── Content (centered, above bg layer) ── */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}>
        <img src="/robologo.png" alt="CXR Assistant" style={{ width: '260px', height: '260px', objectFit: 'contain', marginBottom: '2rem' }} />
        <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: 800 }}>
          Intelligent Chest X-Ray Analysis
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', maxWidth: '600px', marginBottom: '3rem', lineHeight: 1.6 }}>
          Instantly identify pathologies using PyTorch DenseNet architecture and chat with a Google Gemini powered medical assistant.
        </p>

        <div style={{ display: 'flex', gap: '2rem', marginBottom: '4rem' }}>
          <Link to={isAuthenticated ? "/chat" : "/login"} className="btn primary" style={{ fontSize: '1.1rem', padding: '1rem 2rem' }}>
            Get Started
          </Link>
          <Link to="/about" className="btn secondary" style={{ fontSize: '1.1rem', padding: '1rem 2rem' }}>
            Learn More
          </Link>
        </div>

        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <div className="panel glass" style={{ width: '300px', textAlign: 'left' }}>
            <Zap size={32} color="var(--primary)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.5rem' }}>Real-time Heatmaps</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Zero-latency Grad-CAM sliders overlaid directly on your transparent scans.
            </p>
          </div>
          <div className="panel glass" style={{ width: '300px', textAlign: 'left' }}>
            <ShieldCheck size={32} color="var(--accent-green)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.5rem' }}>Secure Storage</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              End-to-End JWT Auth and persistent historical archiving for logged-in users.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
