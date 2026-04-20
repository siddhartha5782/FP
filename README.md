# Virtual Healthcare Assistant: Complete Technical Documentation

Welcome to the master technical documentation for **CXR Intelli-Assist**, a multi-layered AI platform for Chest X-Ray diagnosis. This document provides a transparent, file-by-file breakdown of the entire ecosystem, including the vision models, the RAG-grounded chat system, and the high-fidelity React dashboard.
---

## 🏗️ Core Architectural Philosophy

CXR Intelli-Assist is built on three pillars:
1.  **Expert-Level Vision**: Using standard deep learning (DenseNet) but with medical-specific calibrated thresholds to ensure clinical-grade reliability.
2.  **Visual Transparency**: We don't just provide a label; we use Grad-CAM to show *why* the AI made that choice.
3.  **Grounded Intelligence**: Our AI Copilot isn't just an LLM; it's a RAG system grounded in thousands of clinical facts and peer-reviewed summaries.

---

## 📂 The Master File Inventory

### 📍 Root Directory
The orchestration layer of the application.

- **`main.py`**: The central FastAPI entry point.
    - Manages the REST API endpoints.
    - Orchestrates the "Single-Pass Analysis" (Upload -> Preprocess -> Predict -> Heatmap -> Insight).
    - Stores scan results and chat logs into the SQLite database.
- **`run.bat`**: The one-click launcher.
    - Opens two separate terminal windows.
    - Boots the FastAPI server (backend) and the Vite development server (frontend) simultaneously.
- **`setup.bat`**: Integration & environment initialization.
    - Creates mandatory directories (`data/scans`, `temp`).
    - Initializes the SQLAlchemy database schema.
    - Verifies dependency presence.
- **`requirements.txt`**: The comprehensive list of Python dependencies (PyTorch, FastAPI, FAISS, PIL, etc.).
- **`.env`**: Secrets management (JWT keys, GCP project IDs, Vertex AI credentials).

---

### 🧠 Backend Engine (`/src`)
The "Brains" of the assistant, separated into logical modules.

- **`assistant.py`**: The Vision & Orchestration lead.
    - **Model Loading**: Automatically infers classifier size from `.pth` or `.pt` checkpoints.
    - **Inference**: Applies calibrated thresholds (`THRESHOLDS` dictionary) to raw probabilities.
    - **Grad-CAM**: Generates high-resolution heatmaps using the gradients of the last convolution layer.
- **`rag.py`**: The Knowledge retrieval module.
    - **Vector Search**: Uses FAISS to perform Similarity Search on the internal clinical knowledge base.
    - **Prompt Engineering**: Dynamically constructs RAG prompts by injecting patient findings into a structured hospital protocol.
- **`auth.py`**: The Security layer.
    - Implements JWT (Json Web Token) issuing and verification.
    - Handles password hashing via `bcrypt` for secure storage.
- **`database.py`**: The persistence layer.
    - Defines SQLAlchemy models for `User` and `ScanHistory`.
    - Manages the local `app.db` (SQLite) connection and session lifecycle.

---

### 📂 Data & Knowledge Base (`/data`)
The clinical "Soul" of the project where raw data becomes medical knowledge.

- **`cxr_kb.jsonl`**: The production knowledge base. Thousands of atomic clinical facts used for RAG grounding.
- **`advanced_clinical_docs/`**: A library of 14 curated markdown files (e.g., `atelectasis.md`, `pneumonia.md`).
    - These contain structured Clinical Overviews, Symptoms, and Treatment guidelines sourced from Mayo Clinic protocols.
- **`consolidate_rag.py`**: Data engineering tool.
    - Parses the markdown docs and scraped data.
    - Chunks them into searchable vectors and writes the `cxr_kb.jsonl`.
- **`scrape_clinical_data.py`**: Automated medical research tool.
    - Scrapes high-quality clinical summaries from Wikipedia and medical glossaries.
- **`dump_advanced_clinical.py`**: The source-of-truth generator for the curated markdown summaries.
- **`test_grounding.py`**: A validation script used to test if the RAG system finds the correct context for specific disease triggers.

---

### 📊 Model Training & Eval (`/models`)
The "Scientific Laboratory" of the project.

- **`sol_calib.py`**: Post-training calibration tool.
    - Analyzes validation predictions to find the **Optimal F1-Score Thresholds** for each of the 14 diseases.
- **`sol_metrics_eval.py`**: Validation suite.
    - Calculates AUC-ROC, Precision, Accuracy, and generates per-class classification reports.
- **`test_densenet.py`**: Comprehensive testing script for state-of-the-art DenseNet models.
    - Handles both 14-class and 15-class (No Finding) datasets.
    - Performs sanity forward passes before full evaluation.
- **`densenet_final.pth` / `run1_best.pt`**: Production-ready deep learning weights trained on chest X-ray datasets.

---

### 🖥️ Frontend Dashboard (`/frontend`)
High-fidelity React interface for the clinician end-user.

- **`App.jsx`**: The Layout Engine.
    - Integrates the `GlobalFX` ambient particle background (floating medical-themed objects).
    - Manages top-level routing (Home, History, Chat, Auth).
- **`index.css`**: The Aesthetic Core.
    - Standardizes the **Glassmorphism** panels and primary blue color palette.
    - Contains custom animations like `page-fade` and `tab-fade`.
- **`AuthContext.jsx`**: Global authentication state manager (Login/Logout/Token persistence).
- **`pages/Chat.jsx`**: The command center.
    - Features the Grad-CAM heatmap overlay with real-time intensity slider.
    - Integrates the contextual Copilot suggestions and RAG-based chat bubbles.
- **`pages/History.jsx`**: The archive viewer.
    - Uses **React Portals** to show high-fidelity modal details of past scans without layout shift.
    - Renders compressed scan cards with image previews and findings summaries.

---

## 🧠 The Diagnostic Pipeline

CXR Intelli-Assist follows a strict multi-stage pipeline for every uploaded image:

1.  **Image Prep**: The uploaded image is standardized (resized to 224x224, normalized to ImageNet statistics) and copied to a secure local path.
2.  **Visual Inference**: The DenseNet-121 model predicts probabilities for 14 diseases. These are filtered through **class-specific tuned thresholds** (stored in `assistant.py`) to minimize false positives.
3.  **Heatmap Generation (Grad-CAM)**: For the highest-confidence finding, the backend calculates the gradients of the target class flowing into the final convolutional layer. This produces a Class Activation Map (CAM) showing *where* the AI is looking.
4.  **RAG Contextualization**:
    *   The `rag.py` module takes the top-detected conditions and searches the vector space of `cxr_kb.jsonl`.
    *   It fetches "Advanced Clinical Insights" from the local markdown library.
    *   It combines these with the patient-specific AI findings into a detailed prompt for Gemini.
5.  **Clinical Copilot**: The user receives a detailed markdown overview and can then enter a live chat state where every message is grounded in the retrieved clinical context.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, Lucide Icons, Marked (Markdown) |
| **Backend** | Python 3.10+, FastAPI, PyTorch, OpenCV |
| **Logic** | RAG (FAISS), Gemini 1.5 Pro |
| **Database** | SQLite, SQLAlchemy |
| **Security** | OAuth2, JWT, Bcrypt |

---

## 🔧 Installation & Setup

1. **Backend**: Install `requirements.txt` in a Python 3.10+ venv, run `setup.bat`, then `python main.py`.
2. **Frontend**: Run `npm install` and `npm run dev` in the `/frontend` directory.
3. **Launch**: Use `run.bat` to boot both simultaneously.

---

Developed with ❤️ by **Team South Dakota**.
