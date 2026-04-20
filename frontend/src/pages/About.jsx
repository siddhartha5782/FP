import React from 'react';
import { Database, Network, SearchCode } from 'lucide-react';

export default function About() {
  return (
    <main className="container page-fade" style={{ flexDirection: 'column', maxWidth: '800px', margin: '0 auto', paddingTop: '4rem' }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '2rem', textAlign: 'center', color: 'var(--primary)' }}>About the Architecture</h1>
      
      <div className="panel glass" style={{ marginBottom: '2rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Network size={20}/> Vision Model</h2>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
          The backend relies on a custom trained PyTorch DenseNet121 architecture. It takes standard chest X-rays normalized to 224x224 and extracts features across 121 deep layers. The final classification head is mapped to exactly 14 findings (like Pneumonia, Effusion, etc.) from the NIH standard dataset plus a "No Finding" class.
        </p>
      </div>

      <div className="panel glass" style={{ marginBottom: '2rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Database size={20}/> Retrieval-Augmented Generation</h2>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
          To provide medical insight, the system extracts the vision predictions and uses a fast FAISS vector database to retrieve textbook definitions and treatment guidelines. It utilizes Sentence Transformers (`all-MiniLM-L6-v2`) to embed and match the clinical context instantly.
        </p>
      </div>

      <div className="panel glass">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><SearchCode size={20}/> Large Language Model Copilot</h2>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
          The retrieved DB context and the visual predictions are fused and securely tunneled to the Google Gemini API. This allows the system to synthesize a tailored clinical narrative and empowers the Copilot dashboard to answer complex diagnostic follow-up questions in natural language.
        </p>
      </div>
    </main>
  );
}
