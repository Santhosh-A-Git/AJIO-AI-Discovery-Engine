# AI-Powered Discovery Engine: Phase-Wise Implementation Plan

This document outlines the step-by-step implementation plan for building the AJIO AI-Powered Discovery Engine. The implementation is divided into logical phases based on the system components defined in the architecture and the core objectives in the problem statement. 

All phases prioritize the use of free tier and open-source tools as specified.

---

## Phase 1: Foundation & Data Ingestion 
**Objective:** Set up the core infrastructure and begin collecting raw unstructured user feedback from diverse external platforms.

**Key Tasks:**
1. **Repository Setup:** Initialize the codebase (GitHub/GitLab) and establish a monolithic or microservices folder structure.
2. **Orchestration Configuration:** Setup Apache Airflow (locally) or standard OS Cron Jobs to schedule ingestion tasks.
3. **Scraper Development:** 
   - Develop Python scripts using `BeautifulSoup`/`Scrapy` for fashion forums.
   - Integrate Apify API to scrape subreddits like r/IndianFashionAddicts and Twitter without native rate limits.
   - Integrate YouTube Data API for relevant fashion haul comments.
   - Integrate Google Play Store / Apple App Store review scrapers.
4. **Message Queue Setup:** Deploy RabbitMQ or Redis (local/free tier) to queue the incoming raw data streams asynchronously.
5. **Raw Storage:** Configure AWS S3 (Free Tier) or a local storage directory (`/data/raw/`) as the initial Data Lake.

---

## Phase 2: Data Processing & Normalization
**Objective:** Cleanse, anonymize, and standardize the raw data so it is ready for high-quality AI processing.

**Key Tasks:**
1. **Schema Standardization:** Build a Python pipeline (using Pandas or standard dicts) to map different source formats into a single universal JSON schema (timestamp, source, text, author).
2. **Noise Filtering:** 
   - Implement heuristics to remove URLs, emojis, and duplicate comments.
   - Build a lightweight filter to drop promotional content, spam, and bot-generated text.
3. **Anonymization:** Implement regex or NLP libraries (e.g., `Presidio` or `spaCy`) to scrub Personally Identifiable Information (PII) like names, emails, and phone numbers.
4. **Processed Data Storage:** Output the cleansed data into a separate processed folder (`/data/cleansed/`) or bucket.

---

## Phase 3: AI Engine & Vector DB Integration
**Objective:** Use Large Language Models to extract deep intent, identify specific user frictions, and vectorize the data for semantic clustering.

**Key Tasks:**
1. **Groq API Integration:** Connect to the Groq API (Free Tier) utilizing high-end versatile models like `llama-3.3-70b-versatile`. Implement strict request queueing and token counting to respect Groq's free tier rate limits (RPM and RPD).
2. **Prompt Engineering:** Design system prompts to extract structured JSON containing:
   - **Topic:** (e.g., Size, Fit, Quality)
   - **Problem Statement:** Exact user friction
   - **Intent:** (e.g., High Purchase Intent, Consideration)
   - **Purchase Stage:** (e.g., Pre-purchase evaluation)
3. **Batch Processing & Rate Limiting:** Run the cleansed data through the Groq LLM pipeline using exponential backoff to handle rate limits, and validate the structured outputs.
4. **Vector Embeddings:** 
   - Integrate HuggingFace `SentenceTransformers` (open-source, run locally) to convert the extracted Problem Statements into high-dimensional vectors.
5. **Vector Database Setup:** Spin up ChromaDB (local) or Qdrant (Free Tier) and insert the vectors alongside their metadata.

---

## Phase 4: Analytics, Clustering & Quantification
**Objective:** Group similar problems dynamically, calculate their impact, and compute opportunity scores to prioritize product decisions.

**Key Tasks:**
1. **Relational Database Setup:** Spin up a PostgreSQL instance on a free-tier provider like Supabase or Neon to act as the Insight Data Warehouse.
2. **Dynamic Clustering:** Implement HDBSCAN (via Python's `scikit-learn` or `hdbscan` library) on the vector embeddings to dynamically discover recurring problem themes (e.g., "Inconsistent Sizing Reviews").
3. **Quantification Engine:** 
   - Write SQL/Pandas logic to calculate Prevalence (count), Intent Relevance (ratio of High Purchase Intent), and Segment Reach for each cluster.
4. **Opportunity Scoring:** Implement the mathematical formula to score each cluster: 
   `Opportunity Score = Prevalence × Intent Relevance × Severity × Evidence Strength × Conversion Proximity`
5. **Data Export:** Sync the finalized clusters and their scores into the PostgreSQL warehouse for frontend consumption.

---

## Phase 5: Presentation Layer (Discovery Dashboard)
**Objective:** Deliver actionable, evidence-backed insights to the Product Management team through a visual interface.

**Key Tasks:**
1. **Frontend Foundation:** Initialize a Next.js application styled with Tailwind CSS.
2. **API Layer:** Build Next.js API routes (or a lightweight FastAPI backend) to query PostgreSQL and the Vector DB.
3. **Dashboard Construction:**
   - **Problem Landscape View:** A ranked list of problem clusters sorted by Opportunity Score.
   - **Trend Analysis:** Line charts (using Recharts or Chart.js) showing problem prevalence over time.
   - **Evidence Drill-Down:** A modal or page allowing PMs to view raw user quotes that generated a specific problem cluster.
4. **Metabase Integration (Optional):** Connect Metabase (Open Source version) directly to PostgreSQL for rapid, out-of-the-box BI visualization if custom frontend development takes too long.

---

## Phase 6: Testing, Validation & Handoff
**Objective:** Ensure the system meets the core Product Management requirements and accurately reflects the user problems without relying on monetary incentive hypotheses.

**Key Tasks:**
1. **Pipeline Testing:** Run an end-to-end test with a sample dataset of 1,000 fashion reviews to verify data flows from the scraper to the dashboard.
2. **Accuracy Validation:** Manually review a subset of Groq's LLM outputs to ensure it correctly distinguishes "genuine purchase intent" from "casual bookmarking".
3. **Documentation:** Finalize API documentation, update the architecture diagram if necessary, and write runbooks.
4. **Stakeholder Handoff:** Present the dashboard showing a prioritized list of user problems affecting wishlist-to-purchase conversion.
