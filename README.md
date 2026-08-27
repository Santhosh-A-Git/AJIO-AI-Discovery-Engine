# 🚀 AJIO Discovery Engine - Discover The Unmet

An end-to-end Machine Learning pipeline and Full-Stack Next.js Dashboard built to dynamically extract, cluster, and quantify product friction points, specifically focusing on the **Wishlist to Purchase Conversion** journey.

Built for the **NextLeap Product Management Graduation Project**.

## 🧠 Architecture Overview

The system operates across a seamless 6-phase pipeline utilizing a **Relevance-First Architecture**:

1. **Scheduled Ingestion Engine:** Scrapes real, unfiltered user reviews across multiple sources (Google Play, Twitter, Reddit, etc.) with deterministic source deduplication.
2. **Relevance Classifier (LLM Gate):** Aggressively filters raw data, discarding "Brand-Generated" or "Irrelevant" data before extraction, ensuring only genuine user friction is processed.
3. **Canonical Evidence Extraction:** For relevant records, the AI extracts a rigorous 11-field **Canonical Evidence Record** (Theme, Intent, Blocker, Segment Clue, etc.) alongside field-level validity tracking (Support Status).
4. **Semantic Vectorization:** Converts the AI-distilled `observed_problem_summary` into dense numerical vectors using `all-MiniLM-L6-v2` and stores the 11-field schema as metadata in a local **ChromaDB** database.
5. **Machine Learning Clustering (HDBSCAN):** Groups semantically identical problems dynamically. A custom algorithm ranks each cluster using a normalized **6-Component Opportunity Score**.
6. **Explainable AI Dashboard:** A highly aesthetic **Next.js 16** frontend and **FastAPI** backend exposes these clustered trends, integrating dynamic filters and low-evidence flags.

## 📊 6-Component Opportunity Score

Clusters are no longer arbitrarily ranked. They are quantified using a transparent, weighted formula (Normalized 0-100):
- **Prevalence (25%)**: Absolute volume of evidence.
- **Wishlist-Conversion Relevance (25%)**: Weighting of high-intent behaviors (e.g., *Comparison* vs *Bookmarking*).
- **Evidence Strength (15%)**: Ratio of correctly supported field validations by the LLM.
- **Severity (15%)**: Qualitative friction impact (e.g., *Trust & Price* vs *Styling*).
- **Cross-Source Consistency (10%)**: Number of unique independent source categories reporting the issue.
- **Segment Concentration (10%)**: How strongly the friction targets a specific user segment.

## 🛡️ Enterprise-Grade Reliability

- **Golden Test Suite (CI/CD Ready):** Powered by an assertion-based structured validation suite (pytest) containing 15 diverse wishlist-to-purchase scenarios. This ensures the LLM's categorical extraction exactly matches behavioral intent constraints without byte-for-byte fragility.
- **Explainable AI:** Every synthesis generates an 11-Parameter Evidence Breakdown proving exactly how the LLM derived its insight from the raw data.
- **LLM Failover Cascade:** The backend dynamically falls back across tiered models (`qwen/qwen3.8-27b` → `openai/gpt-oss-20b` → `allam-2-7b`) seamlessly avoiding rate-limit interruptions.

## 💻 Tech Stack

- **Backend:** Python, FastAPI, SQLite, ChromaDB, Sentence-Transformers, HDBSCAN, Langchain, Groq API, Pytest.
- **Frontend:** React, Next.js 16 (App Router), Tailwind CSS v4, Recharts, jsPDF.

## 🚀 Running Locally

### 1. Start the Backend (FastAPI)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Start the API server on localhost:8000
uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` to view the dashboard!

## 🌐 Deployment (Railway & Vercel)

This repository is strictly configured for instant cloud deployment.

### Backend (Railway)
- Connect this repository to Railway.
- Railway will automatically detect the `Procfile` and `requirements.txt` and launch the FastAPI server.
- The `data/warehouse/ajio_warehouse.db` file is committed to the repo so the API serves the pre-calculated ML clusters immediately.

### Frontend (Vercel)
- Connect this repository to Vercel.
- Set the **Root Directory** to `frontend`.
- Add an Environment Variable: `NEXT_PUBLIC_API_URL` pointing to your Railway backend URL + `/api`.

### Pipeline Updates
- Implemented robust LLM fallback cascading to instantly mitigate Groq rate limits, ensuring 100% processing of all 1500+ records.
- Integrated fallback clustering utilizing KMeans for perfectly bounded insights when noise levels are high.
