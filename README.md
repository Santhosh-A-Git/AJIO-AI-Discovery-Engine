# 🚀 AJIO AI Product Discovery Engine

An end-to-end Machine Learning pipeline and Full-Stack Next.js Dashboard built to dynamically extract, cluster, and quantify product friction points from multi-channel user feedback.

Built for the **NextLeap Product Management Graduation Project**.

## 🧠 Architecture Overview

The system operates across a seamless 5-phase data pipeline:

1. **Ingestion Engine:** Scrapes real, unfiltered user reviews from the Google Play Store and various social channels.
2. **AI Extraction (Groq/LLaMA):** Uses large language models to distill raw, noisy complaints into structured, actionable problem statements, isolating the true user intent and purchase stage.
3. **Semantic Vectorization (HuggingFace):** Converts the distilled AI insights into dense numerical vectors using `all-MiniLM-L6-v2` and stores them in a local **ChromaDB** vector database.
4. **Machine Learning Clustering (HDBSCAN):** Groups semantically identical problems together dynamically and calculates a weighted **Opportunity Score** (`Prevalence` × `Intent Relevance` × `Severity`). The finalized clusters are stored in an **SQLite Data Warehouse**.
5. **Full-Stack Presentation:** A **FastAPI** backend exposes the clustered data via REST, which is consumed by a premium, highly aesthetic **Next.js 15 (App Router)** dashboard built with Tailwind CSS v4 and Recharts.

## 📊 The Results

Out of 1,500+ raw records, the ML pipeline extracted 834 deep insights, filtered out the noise, and grouped the remaining **443 high-signal insights into 12 distinct Problem Clusters.**

**Top Discovered Friction Point:**
🚨 **Delivery & Logistics (Score: 70.4)**
By a massive outlier margin, the AI proved that AJIO's biggest friction point is Delivery. 370 separate complaints were clustered regarding missing packages, late deliveries, and poor courier service with high purchase intent.

## 💻 Tech Stack

- **Backend / AI Engine:** Python, FastAPI, SQLite, ChromaDB, Sentence-Transformers, HDBSCAN, Scikit-learn, Langchain, Groq API.
- **Frontend / Dashboard:** React, Next.js 15 (App Router), Tailwind CSS v4, Recharts, Lucide Icons, Axios.

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
- Add an Environment Variable: `NEXT_PUBLIC_API_URL` pointing to your Railway backend URL + `/api` (e.g., `https://ajio-backend.up.railway.app/api`).
- Deploy!
