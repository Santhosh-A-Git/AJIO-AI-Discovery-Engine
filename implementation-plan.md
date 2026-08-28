# AI-Powered Discovery Engine: Final Implementation Plan (Executed)

This document outlines the step-by-step implementation plan that was successfully executed to build the AJIO AI-Powered Discovery Engine. 

---

## Phase 1: Foundation & Data Ingestion 
**Objective:** Set up the core infrastructure and collect raw unstructured user feedback from diverse external platforms.

**Key Achievements:**
1. **Repository Setup:** Established a monorepo containing the Python FastAPI backend and the React/Vite frontend.
2. **Scraper Development:** 
   - Integrated Playstore, App Store, YouTube, Twitter, and Web Search data sources.
   - Successfully amassed over 1,400+ raw, unfiltered records.
3. **Data Storage Setup:** Built `ajio_warehouse.db` (SQLite) as the primary relational data lake for raw records.

---

## Phase 2: AI Processing & Relevance Filtering (LLM Gate)
**Objective:** Cleanse, filter, and extract 11-parameter canonical evidence from the raw data using Enterprise AI.

**Key Achievements:**
1. **LLM Relevance Gate:** Implemented a strict AI prompt to evaluate all 1,400 records. Discarded pure noise and isolated records into `RELEVANT` and `POSSIBLY_RELEVANT`.
2. **Canonical Extraction:**
   - Prompt engineered a strict JSON schema output from the LLM.
   - Extracted exact user friction: Intent, Conversion Blocker, Uncertainty, Segment Clue, and Evidence Strength.
3. **Enterprise LLM Integration & Cascading:**
   - Integrated Groq API using `qwen/qwen3.8-27b`.
   - Built a robust fallback/cascade script (`finalize_pipeline.py`) to bypass strict rate limits and ensure 100% of data was processed without dropping records.

---

## Phase 3: RAG & Vector DB Integration
**Objective:** Vectorize the data for semantic clustering and natural language querying.

**Key Achievements:**
1. **Vector Embeddings:** Utilized HuggingFace `all-MiniLM-L6-v2` locally to convert the AI-extracted Problem Statements into dense vectors.
2. **ChromaDB Setup:** Spun up a local ChromaDB instance to store the embeddings alongside the 11-field metadata schemas.
3. **RAG Search Implementation:** Built the `/api/query` endpoint utilizing ChromaDB semantic search, enforcing a strict `where` clause to physically prevent the AI from seeing `NOT_RELEVANT` data.

---

## Phase 4: Analytics, Clustering & Quantification
**Objective:** Group similar problems dynamically, calculate their impact, and generate AI Hypotheses.

**Key Achievements:**
1. **Dynamic Clustering:** Implemented `HDBSCAN` on the vector embeddings to dynamically discover recurring problem themes. Added `KMeans` as a deterministic fallback if noise levels disrupt density clustering.
2. **6-Component Opportunity Scoring:** 
   - Calculated a normalized 0-100 score utilizing: Prevalence, Relevance, Evidence Strength, Severity, Consistency, and Segment Concentration.
3. **AI Research Hypotheses Generation:** 
   - Built an autonomous script (`generate_hypotheses.py`) to synthesize the top clusters into highly actionable, PM-ready research hypotheses explaining the *why* behind the friction.

---

## Phase 5: Presentation Layer (Discovery Dashboard)
**Objective:** Deliver actionable, evidence-backed insights to the Product Management team through a premium UI.

**Key Achievements:**
1. **Frontend Foundation:** Built a stunning React/Vite UI styled with Tailwind CSS, utilizing a modern glassmorphic "Fuchsia & Teal" aesthetic.
2. **Tabs & Workflows:**
   - **Discover:** A RAG-powered natural language search for PMs to ask questions and get AI answers backed by direct quotes.
   - **AI Opportunity Matrix:** Visualizes the HDBSCAN clusters, their opportunity scores, and the AI Research Hypotheses.
   - **Evidence Explorer:** A robust filterable table allowing PMs to view raw user quotes, with Source priority sorting.
3. **PDF Report Generation:** Integrated `jsPDF` and `autoTable` to generate a 360-degree PDF report snapshot encompassing the funnel, the RAG insights, the AI Hypotheses, and the exact supporting evidence quotes.

---

## Phase 6: Testing, Validation & Handoff
**Objective:** Ensure the system meets the core Product Management requirements.

**Key Achievements:**
1. **Pipeline Execution:** Successfully ran the end-to-end pipeline (`run_full_pipeline.py`) processing all 1,453 records without failures.
2. **Accuracy Validation:** Verified that RAG responses dynamically adjust based on query context instead of spitting out generic summaries.
3. **Deployment:** Configured the repo for instant Railway deployment (`Procfile`, `requirements.txt`).
4. **Stakeholder Handoff:** Fully complete. The platform successfully bridges the gap between raw, distributed user feedback and actionable product opportunities related to wishlist-to-purchase conversion.
