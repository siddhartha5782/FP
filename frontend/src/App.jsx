import React from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { Activity, LogOut, MessageCircle, Home, Info, Clock } from 'lucide-react';
import { useAuth } from './AuthContext';

import HomePage from './pages/Home';
import AboutPage from './pages/About';
import AuthPage from './pages/Auth';
import ChatPage from './pages/Chat';
import HistoryPage from './pages/History';

// ── Global ambient background (renders behind every page) ──────
const GLOBAL_ORBS = [
  { width: 500, height: 500, top: '-10%', left: '-8%', color: 'rgba(59,130,246,0.22)', duration: '20s', delay: '0s' },
  { width: 380, height: 380, top: '25%', right: '-6%', color: 'rgba(99,102,241,0.18)', duration: '27s', delay: '4s' },
  { width: 280, height: 280, top: '60%', left: '35%', color: 'rgba(59,130,246,0.14)', duration: '23s', delay: '8s' },
  { width: 220, height: 220, top: '-5%', right: '22%', color: 'rgba(239,68,68,0.10)', duration: '19s', delay: '11s' },
];

const GLOBAL_PINGS = [
  { size: 90, top: '18%', left: '12%', delay: '0s', duration: '3s' },
  { size: 65, top: '68%', right: '14%', delay: '1.4s', duration: '3.4s' },
  { size: 50, top: '42%', left: '78%', delay: '2.8s', duration: '3.9s' },
  { size: 80, top: '82%', left: '42%', delay: '0.9s', duration: '3.1s' },
];

const GLOBAL_PARTICLES = Array.from({ length: 40 }, (_, i) => ({
  left: `${(i * 2.5) % 100}%`,
  bottom: `${(i * 7.3) % 60}%`,
  delay: `${(i * 0.47) % 10}s`,
  duration: `${10 + (i * 1.3) % 14}s`,
}));

function GlobalFX() {
  return (
    <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, overflow: 'hidden' }}>
      {GLOBAL_ORBS.map((o, i) => (
        <div key={i} className="home-bg-orb" style={{ width: o.width, height: o.height, top: o.top, left: o.left, right: o.right, background: o.color, animationDuration: o.duration, animationDelay: o.delay }} />
      ))}
      {GLOBAL_PINGS.map((p, i) => (
        <div key={i} className="home-ping" style={{ width: p.size, height: p.size, top: p.top, left: p.left, right: p.right, animationDuration: p.duration, animationDelay: p.delay }} />
      ))}
      {GLOBAL_PARTICLES.map((p, i) => (
        <span key={i} className="home-bg-particle" style={{ left: p.left, bottom: p.bottom, animationDuration: p.duration, animationDelay: p.delay, fontSize: '1.2rem', color: 'rgba(59,130,246,0.4)' }}>✚</span>
      ))}
    </div>
  );
}

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navStyle = (path) => ({
    color: location.pathname === path ? 'var(--primary)' : 'var(--text-main)',
    textDecoration: 'none',
    display: 'flex',
    alignItems: 'center',
    gap: '0.3rem',
    padding: '0.3rem 0.65rem',
    borderRadius: '6px',
    border: location.pathname === path ? '1px solid rgba(59,130,246,0.35)' : '1px solid transparent',
    background: location.pathname === path ? 'rgba(59,130,246,0.08)' : 'transparent',
    transition: 'all 0.2s ease',
  });

  return (
    <header className="glass-header">
      <div className="logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
        <img src="/robologo.png" alt="CXR Logo" style={{ width: '40px', height: '40px', objectFit: 'contain' }} />
        <span>Virtual Healthcare Assistant</span>
      </div>
      <nav style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <Link to="/" className="nav-span" style={navStyle('/')}><Home size={16} /> Home</Link>
        <Link to="/about" className="nav-span" style={navStyle('/about')}><Info size={16} /> About</Link>
        {isAuthenticated ? (
          <>
            <Link to="/chat" className="nav-span" style={{ ...navStyle('/chat'), color: 'var(--primary)', border: '1px solid transparent', background: 'transparent' }}><MessageCircle size={16} /> Chat</Link>
            <Link to="/history" className="nav-span" style={navStyle('/history')}><Clock size={16} /> History</Link>
            <button onClick={handleLogout} className="btn secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.9rem', marginLeft: '0.5rem' }}><LogOut size={16} /> Logout</button>
          </>
        ) : (
          <Link to="/login" className="btn primary" style={{ textDecoration: 'none', marginLeft: '0.5rem' }}>Login</Link>
        )}
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <>
      <GlobalFX />
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
      <footer style={{
        textAlign: 'center',
        padding: '0.85rem 2rem',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        background: 'rgba(15,23,42,0.6)',
        backdropFilter: 'blur(10px)',
        letterSpacing: '0.02em',
      }}>
        Made with <span style={{ color: '#ef4444', fontSize: '0.95rem' }}>♥</span> by <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Team South Dakota</span>
      </footer>
    </>
  );
}
