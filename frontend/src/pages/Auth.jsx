import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Lock } from 'lucide-react';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const endpoint = isLogin ? "/api/login" : "/api/signup";

      let bodyData;
      let headers;

      if (isLogin) {
        // OAuth2 expects form-urlencoded
        bodyData = new URLSearchParams();
        bodyData.append('username', username);
        bodyData.append('password', password);
        headers = { "Content-Type": "application/x-www-form-urlencoded" };
      } else {
        // Signup expects JSON
        bodyData = JSON.stringify({ username, password });
        headers = { "Content-Type": "application/json" };
      }

      const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: headers,
        body: bodyData
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Authentication Failed");
      }

      login(data.access_token);
      navigate('/chat');

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '85vh' }}>
      <div className="panel glass" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Lock size={48} color="var(--primary)" style={{ marginBottom: '1rem' }} />
          <h2>{isLogin ? "Welcome Back" : "Create Account"}</h2>
        </div>

        {error && <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid var(--accent-red)', padding: '0.8rem', borderRadius: '8px', marginBottom: '1.5rem', color: '#fca5a5', fontSize: '0.9rem' }}>{error}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Username</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.3)', color: 'white', outline: 'none' }}
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.3)', color: 'white', outline: 'none' }}
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" className="btn primary" disabled={loading} style={{ marginTop: '0.5rem', padding: '1rem' }}>
            {loading ? "Processing..." : (isLogin ? "Sign In" : "Register")}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
          </span>
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            style={{ background: 'none', border: 'none', color: 'var(--primary)', fontWeight: 'bold', marginLeft: '0.5rem', cursor: 'pointer' }}
          >
            {isLogin ? "Sign Up" : "Log In"}
          </button>
        </div>
      </div>
    </main>
  );
}
