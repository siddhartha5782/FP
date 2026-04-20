import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, Activity, MessageSquare, RefreshCw, Send } from 'lucide-react';
import { marked } from 'marked';
import { useAuth } from '../AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Chat() {
  const [fileUrl, setFileUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [heatmaps, setHeatmaps] = useState({});
  const [historyId, setHistoryId] = useState(null);
  const [insight, setInsight] = useState(null);
  const [activeTab, setActiveTab] = useState('findings');
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatIntensity, setHeatIntensity] = useState(85); // defaults to 85% opacity
  
  const [chatHistory, setChatHistory] = useState([
    { type: 'system', text: 'Hello! I am your AI clinical assistant. Once you upload an image, I can answer specific questions regarding the findings and differential diagnosis.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isChatting, setIsChatting] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
        navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, activeTab]);

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file (PNG/JPG).");
      return;
    }

    setIsAnalyzing(true);
    setPredictions([]);
    setInsight(null);
    setShowHeatmap(false);
    setHistoryId(null);
    setChatHistory([
      { type: 'system', text: 'Hello! I am your AI clinical assistant. Once you upload an image, I can answer specific questions regarding the findings and differential diagnosis.' }
    ]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        },
        body: formData
      });
      const data = await res.json();
      
      if (data.error) {
        alert("Error: " + data.error);
      } else {
        // Backend now returns the raw uploaded image back to us so it's perfectly scaled
        setFileUrl(data.original_image);
        setHistoryId(data.history_id);
        setPredictions(data.predictions);
        setHeatmaps(data.heatmaps);
        setInsight(data.clinical_insight);
        
        if (data.predictions.length > 0 && data.heatmaps[data.predictions[0].condition]) {
            setShowHeatmap(true);
        }
      }
    } catch (err) {
      alert("Network Error: " + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetSession = () => {
    setFileUrl(null);
    setPredictions([]);
    setHeatmaps({});
    setInsight(null);
    setHistoryId(null);
    setShowHeatmap(false);
    setChatHistory([
      { type: 'system', text: 'Hello! I am your AI clinical assistant. Once you upload an image, I can answer specific questions regarding the findings and differential diagnosis.' }
    ]);
  };

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    
    const userText = chatInput;
    setChatHistory(prev => [...prev, { type: 'user', text: userText }]);
    setChatInput('');
    setIsChatting(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ 
          question: userText, 
          context: predictions.map(p => p.condition),
          history_id: historyId
        })
      });
      const data = await res.json();
      
      if (data.error) {
        setChatHistory(prev => [...prev, { type: 'system', text: `Error: ${data.error}` }]);
      } else {
        setChatHistory(prev => [...prev, { type: 'system', isMarkdown: true, text: data.response }]);
      }
    } catch(err) {
      setChatHistory(prev => [...prev, { type: 'system', text: `Network Error: ${err.message}` }]);
    } finally {
      setIsChatting(false);
    }
  };

  const topCondition = predictions.length > 0 ? predictions[0].condition : null;
  const currentHeatmap = topCondition ? heatmaps[topCondition] : null;

  return (
    <main className="container chat-dashboard-container page-fade">
      <section className="panel imaging-panel glass">
        {!fileUrl && !isAnalyzing ? (
          <div 
            className="upload-zone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              accept="image/png, image/jpeg" 
              hidden 
            />
            <div className="upload-content">
              <UploadCloud size={48} />
              <h3>Upload Chest X-Ray</h3>
              <p>Drag & drop or click to browse</p>
            </div>
          </div>
        ) : (
          <div className="viewer-zone">
            <div className="image-wrapper" style={{ position: 'relative' }}>
              {fileUrl && <img src={fileUrl} alt="Uploaded X-Ray" />}
              
              {showHeatmap && currentHeatmap && (
                <img 
                  src={currentHeatmap} 
                  className="heatmap-overlay" 
                  alt="Grad-CAM" 
                  style={{ opacity: heatIntensity / 100, transition: 'none' }} // Zero-latency intensity tuning!
                 />
              )}
              
              {isAnalyzing && (
                <div className="loader-overlay">
                  <div className="spinner"></div>
                  <p>Analyzing morphology & securing data...</p>
                </div>
              )}
            </div>
            
            <div className="viewer-controls" style={{ flexWrap: 'wrap', gap: '1rem' }}>
              <button className="btn secondary" onClick={resetSession}>
                <RefreshCw size={18} /> New Scan
              </button>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(0,0,0,0.3)', padding: '0.5rem 1rem', borderRadius: '8px' }}>
                <span className="label" style={{ fontSize: '0.9rem' }}>Intensity:</span>
                <input 
                    type="range" 
                    min="10" 
                    max="100" 
                    value={heatIntensity} 
                    onChange={(e) => setHeatIntensity(e.target.value)}
                    disabled={!showHeatmap}
                    style={{ cursor: showHeatmap ? 'pointer' : 'not-allowed' }}
                />
                <span style={{ fontSize: '0.8rem', width: '30px' }}>{heatIntensity}%</span>
              </div>

              <div className="switch-layout">
                <span className="label">Overlay:</span>
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={showHeatmap} 
                    disabled={!currentHeatmap || isAnalyzing}
                    onChange={(e) => setShowHeatmap(e.target.checked)} 
                  />
                  <span className="slider round"></span>
                </label>
              </div>
            </div>
          </div>
        )}
      </section>

      <section className="panel intelligence-panel glass">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'findings' ? 'active' : ''}`}
            onClick={() => setActiveTab('findings')}
          >
            <Activity size={16} /> Clinical Findings
          </button>
          <button 
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={16} /> Copilot Chat
          </button>
        </div>

        {activeTab === 'findings' ? (
          <div key="findings" className="tab-content tab-fade" style={{display: 'flex'}}>
            <div className="predictions-box">
              <h3>Identified Pathologies</h3>
              <div className="predictions-list">
                {predictions.length > 0 ? (
                  predictions.map((p, idx) => {
                    const confPercent = (p.confidence * 100).toFixed(1);
                    let barClass = "low";
                    if (p.confidence > 0.7) barClass = "high";
                    else if (p.confidence > 0.3) barClass = "med";
                    
                    return (
                      <div className="prediction-item" key={idx}>
                        <div className="pred-header">
                          <span>{p.condition}</span>
                          <span>{confPercent}%</span>
                        </div>
                        <div className="pred-bar-bg">
                          <div className={`pred-bar ${barClass}`} style={{ width: `${confPercent}%`}}></div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="placeholder-text">
                      {isAnalyzing ? "Scanning..." : fileUrl ? "No significant abnormalities detected." : "Upload a scan to initiate analysis."}
                  </div>
                )}
              </div>
            </div>

            <div className="insight-box">
              <h3>Clinical Overview & Guidance</h3>
              <div className="insight-content markdown-body">
                {insight ? (
                  <div dangerouslySetInnerHTML={{ __html: marked.parse(insight) }} />
                ) : (
                  <p className="placeholder-text">
                      {isAnalyzing ? <span className="spinner" style={{display:'inline-block', width:'15px', height:'15px', borderWidth:'2px'}}></span> : "Awaiting diagnostic targets..."}
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div key="chat" className="tab-content chat-tab tab-fade" style={{display: 'flex'}}>
            <div className="chat-history">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.type}`}>
                  {msg.isMarkdown ? (
                     <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} className="markdown-body" style={{color: 'inherit'}}/>
                  ) : (
                     msg.text
                  )}
                </div>
              ))}
              
              {isChatting && (
                <div className="chat-bubble system">
                  <div className="spinner" style={{width:'15px', height:'15px', borderWidth:'2px', margin: 0}}></div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            
            {/* Suggestion chips — contextual to detected condition */}
            {fileUrl && !isAnalyzing && (
              <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginBottom: '0.2rem' }}>
                {[
                  topCondition ? `Symptoms of ${topCondition}?` : 'What are the symptoms?',
                  topCondition ? `Treatment for ${topCondition}?` : 'What is the treatment?',
                  'Should I be worried?',
                  'What to do next?',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => { setChatInput(suggestion); }}
                    style={{
                      background: 'rgba(59,130,246,0.12)',
                      border: '1px solid rgba(59,130,246,0.35)',
                      borderRadius: '20px',
                      color: 'var(--primary)',
                      padding: '0.15rem 0.55rem',
                      fontSize: '0.7rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      whiteSpace: 'nowrap',
                    }}
                    onMouseEnter={e => e.target.style.background = 'rgba(59,130,246,0.25)'}
                    onMouseLeave={e => e.target.style.background = 'rgba(59,130,246,0.12)'}
                    disabled={isChatting}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
            <div className="chat-input-area">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChat()}
                placeholder="Ask a follow-up question..." 
                disabled={!fileUrl || isAnalyzing}
              />
              <button className="btn primary" onClick={sendChat} disabled={!chatInput.trim() || !fileUrl || isAnalyzing || isChatting}>
                <Send size={18} />
              </button>
            </div>
            <button
              className="btn secondary"
              style={{ marginTop: '0.15rem', width: '100%', justifyContent: 'center', fontSize: '0.75rem', padding: '0.25rem' }}
              disabled={!fileUrl || isAnalyzing}
              onClick={() => setChatHistory([{ type: 'system', text: 'New chat started! Ask me anything about your X-ray.' }])}
            >
              + New Chat
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
