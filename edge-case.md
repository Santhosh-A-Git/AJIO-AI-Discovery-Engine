# AI-Powered Discovery Engine: Edge Cases & Corner Scenarios

This document outlines the edge cases, anomalies, and corner scenarios that the AJIO AI-Powered Discovery Engine encounters and explicitly how they are mitigated in the final architecture.

---

## 1. Data Ingestion & Scraping Scenarios

### 1.1. Free-Tier Rate Limiting & IP Bans
- **Scenario:** Free-tier APIs (Reddit, YouTube) and public scrapers heavily rate-limit requests.
- **Mitigation:** Implemented robust retry logic and source deduplication. We successfully scraped and cached over 1,400+ raw records locally to ensure backend processing does not trigger external IP bans.

### 1.2. Multi-Platform Misattribution
- **Scenario:** A user complains about a competitor (e.g., Myntra or Meesho) in a thread that broadly mentions AJIO.
- **Mitigation:** The Relevance Classifier (LLM Gate) explicitly analyzes the context. If the friction is unrelated to the AJIO evaluation journey, it is categorized as `NOT_RELEVANT` and entirely dropped before vectorization.

---

## 2. AI Processing & LLM Corner Cases

### 2.1. Handling Sarcasm
- **Scenario:** A user writes, *"Wow, great job AJIO, I love it when my medium shirt fits like an extra-small."*
- **Mitigation:** Enterprise LLMs like `qwen/qwen3.8-27b` detect sarcasm inherently. The LLM extracts the literal problem ("Size runs small") into the `conversion_blocker` field, bypassing naive sentiment failures.

### 2.2. Groq API Throttling & Rate Limits (The Cascading Fallback)
- **Scenario:** Groq's free tier has strict RPM and TPD limits. Processing 1,400+ records crashes the pipeline with `429 Too Many Requests`.
- **Mitigation:** Implemented a robust **LLM Failover Cascade** (`finalize_pipeline.py`). If the primary model fails, the system automatically catches the exception, pauses with an exponential backoff, and falls back to secondary models, ensuring 100% of data is processed without dropping records.

### 2.3. RAG Hallucinations
- **Scenario:** When a PM queries the system, the LLM hallucinates answers based on irrelevant data or brand noise.
- **Mitigation:** The ChromaDB vector search strictly enforces a `where={"relevance_status": {"$in": ["RELEVANT", "POSSIBLY_RELEVANT"]}}` clause. The AI is physically prevented from seeing noise, guaranteeing that hypotheses are grounded in genuine friction.

---

## 3. Clustering & Analytics Anomalies

### 3.1. HDBSCAN "Noise" Misclassification
- **Scenario:** HDBSCAN classifies data points that don't fit into dense clusters as "noise" (label -1). High noise ratios can suppress cluster generation.
- **Mitigation:** Implemented a **Fallback Clustering Mechanism**. If HDBSCAN fails to find sufficient density (e.g., due to sparse vectors), the pipeline automatically falls back to `KMeans` with a dynamically calculated `k`, ensuring PMs always receive bounded, categorized insights.

### 3.2. Contradictory Clusters
- **Scenario:** The system identifies two dense clusters: *"Sizes run too small"* and *"Sizes run too large"*. 
- **Mitigation:** The Evidence Explorer allows PMs to filter by source and read the raw quotes. The AI Research Hypothesis explicitly synthesizes *why* these contradictions occur (e.g., differences across user segments or brands).

---

## 4. Privacy & Compliance Edge Cases

### 4.1. Accidental PII in Problem Extraction
- **Scenario:** A user includes their order ID or phone number in a public tweet.
- **Mitigation:** The Canonical Evidence Extraction prompt instructs the LLM to synthesize the problem generically into the `problem_statement` field, abstracting away PII while preserving the core behavioral friction.
