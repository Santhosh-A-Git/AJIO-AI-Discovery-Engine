# 🚀 AJIO Discovery Engine - Discover The Unmet

An end-to-end Machine Learning pipeline and Full-Stack Next.js Dashboard built to dynamically extract, cluster, and quantify product friction points, specifically focusing on the **Wishlist to Purchase Conversion** journey.

Built for the **NextLeap Product Management Graduation Project**.

## 🧠 Architecture Overview

The system operates across a seamless 5-phase data pipeline:

1. **Scheduled Ingestion Engine:** Automatically scrapes real, unfiltered user reviews from the Google Play Store and various social channels every day at 10:00 PM.
2. **AI Extraction & Filtration:** Uses Large Language Models to distill raw, noisy complaints into structured, actionable problem statements, forcefully rejecting trivial feedback and isolating true Pre-Purchase intent.
3. **Semantic Vectorization:** Converts the distilled AI insights into dense numerical vectors using `all-MiniLM-L6-v2` and stores them in a local **ChromaDB** vector database.
4. **Machine Learning Clustering (HDBSCAN):** Groups semantically identical problems together dynamically and calculates a weighted **Opportunity Score** (`Prevalence` × `Intent Relevance` × `Severity`). The finalized clusters are stored in an **SQLite Data Warehouse**.
5. **Explainable AI Dashboard:** A highly aesthetic **Next.js 16** frontend connects to a **FastAPI** backend to expose these clustered trends and allow PMs to query the AI Engine directly for deep synthesis.

## 📊 The Results & Core Thesis

By filtering exclusively for **Pre-Purchase / Wishlist friction**, the ML pipeline grouped the highest-signal data points into **8 highly-specific Opportunity Themes**.

**Top Discovered Friction Point:**
🚨 **Wishlist Capacity Limits (Score: 92.5)**
The highest-ROI bottleneck preventing conversions is an artificial 70-item cap on user wishlists. Users use the wishlist as a curation tool; when older items are silently deleted to make room for new ones, high-intent purchase opportunities are permanently lost.

**Other Major Bottlenecks:**
- **Comparison Friction (Score: 87.5):** Users abandon wishlists because they cannot confidently compare shortlisted items side-by-side.
- **Unexpected Cost Shock (Score: 86.4):** Users abandon carts when mandatory fees are hidden until the final checkout step.

## 🛡️ Enterprise-Grade Reliability

- **Explainable AI:** The AI Engine is strictly bounded by RAG (Retrieval-Augmented Generation). It does not hallucinate. Every synthesis generates an **11-Parameter Evidence Breakdown** (User Segment Clue, Conversion Blocker, Purchase Status, etc.) proving exactly how the LLM derived its insight from the raw data.
- **Failover Architecture:** The backend features a dynamic LLM cascade (`qwen/qwen3.8-27b` → `openai/gpt-oss-20b` → `allam-2-7b`). If an AI provider experiences rate limits or goes down, the system instantly fails over to a backup model, guaranteeing 100% uptime during evaluation.

## 💻 Tech Stack

- **Backend:** Python, FastAPI, SQLite, ChromaDB, Sentence-Transformers, HDBSCAN, Langchain, Groq API.
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
