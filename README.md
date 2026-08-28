# 🚀 AJIO AI Discovery Engine - Discover The Unmet

An end-to-end Machine Learning pipeline and Full-Stack React/Vite Dashboard built to dynamically extract, cluster, and quantify product friction points, specifically focusing on the **Wishlist to Purchase Conversion** journey.

Built for the **NextLeap Product Management Graduation Project**.

## 🧠 Architecture Overview

The system operates across a seamless pipeline utilizing a **Relevance-First Architecture** and **Retrieval-Augmented Generation (RAG)**:

1. **Scheduled Ingestion Engine:** Scrapes real, unfiltered user reviews across multiple sources (Google Play, Twitter, Reddit, etc.) with deterministic source deduplication.
2. **Relevance Classifier (LLM Gate):** Aggressively filters raw data, discarding "Brand-Generated" or "Irrelevant" data before extraction, ensuring only genuine user friction is processed.
3. **Canonical Evidence Extraction:** For relevant records, the AI extracts a rigorous 11-field **Canonical Evidence Record** (Theme, Intent, Blocker, Segment Clue, etc.).
4. **Semantic Vectorization (RAG):** Converts the AI-distilled problem summaries into dense numerical vectors using `all-MiniLM-L6-v2` and stores them in a local **ChromaDB** vector database for high-precision semantic search.
5. **Machine Learning Clustering (HDBSCAN):** Groups semantically identical problems dynamically. A custom algorithm ranks each cluster using a normalized **6-Component Opportunity Score**.
6. **AI Research Hypotheses Generation:** Uses enterprise LLMs (`qwen/qwen3.8-27b`) to synthesize the raw cluster data into highly actionable, Mad-Libs style research hypotheses for PMs.
7. **Explainable AI Dashboard:** A highly aesthetic frontend and **FastAPI** backend exposes these clustered trends, integrating dynamic filters, RAG-powered querying, and automated PDF reporting.

## 📊 6-Component Opportunity Score

Clusters are no longer arbitrarily ranked. They are quantified using a transparent, weighted formula (Normalized 0-100):
- **Prevalence (25%)**: Absolute volume of evidence.
- **Wishlist-Conversion Relevance (25%)**: Weighting of high-intent behaviors.
- **Evidence Strength (15%)**: Ratio of correctly supported field validations.
- **Severity (15%)**: Qualitative friction impact.
- **Cross-Source Consistency (10%)**: Number of unique independent source categories.
- **Segment Concentration (10%)**: Target demographic specificity.

## 🛡️ Enterprise-Grade Reliability

- **LLM Failover Cascade:** The backend dynamically falls back across tiered enterprise models (e.g., `qwen/qwen3.8-27b`) to seamlessly avoid rate-limit interruptions on Groq.
- **Explainable AI & RAG Filters:** The Vector Database strictly enforces a `where={"relevance_status": {"$in": ["RELEVANT", "POSSIBLY_RELEVANT"]}}` clause so the AI cannot hallucinate on noise.
- **Comprehensive PDF Reporting:** Generates a full 360° snapshot including Funnel metrics, AI Hypotheses, and exact mapped supporting evidence quotes.

## 💻 Tech Stack

- **Backend:** Python, FastAPI, SQLite, ChromaDB, Sentence-Transformers, HDBSCAN, Langchain, Groq API.
- **Frontend:** React, Vite, Tailwind CSS, Recharts, jsPDF.

## 🚀 Running Locally

### 1. Start the Backend (FastAPI)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Start the API server on localhost:8000
uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend (Vite)
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to view the dashboard!

## 🌐 Deployment (Railway)

This repository is strictly configured for instant cloud deployment.
- Connect this repository to Railway.
- Railway will automatically detect the `Procfile` and `requirements.txt` and launch the FastAPI server.
- The `data/warehouse/ajio_warehouse.db` file is committed to the repo so the API serves the pre-calculated ML clusters immediately.

*Frontend is currently integrated and deployed alongside backend via static serving or separate UI hosting.*
