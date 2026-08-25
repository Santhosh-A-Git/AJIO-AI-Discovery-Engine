# AI-Powered Discovery Engine: Edge Cases & Corner Scenarios

This document outlines the potential edge cases, anomalies, and corner scenarios that the AJIO AI-Powered Discovery Engine might encounter during data ingestion, processing, and analysis. Mitigation strategies are proposed for each scenario to ensure system resilience and data accuracy.

---

## 1. Data Ingestion & Scraping Scenarios

### 1.1. Free-Tier Rate Limiting & IP Bans
- **Scenario:** Free-tier APIs (Reddit, YouTube) and public scrapers heavily rate-limit requests. Sending too many requests could result in IP bans or suspended API keys.
- **Mitigation:** Implement exponential backoff, jitter, and strict request throttling in Apache Airflow/Cron jobs. Use rotating proxy pools if scraping HTML directly, and respect `Retry-After` headers.

### 1.2. Non-English and "Hinglish" Feedback
- **Scenario:** A significant portion of Indian e-commerce feedback is written in Hinglish (e.g., *"Dress ka material bahut kharab tha, fit nahi aaya"*). 
- **Mitigation:** Ensure the selected high-end LLM (e.g., `llama-3.3-70b-versatile` via Groq) is tested for basic Hinglish understanding. If performance is poor, introduce a lightweight translation layer (e.g., an open-source translation model) before passing text to the AI Engine.

### 1.3. Scraper Breakages due to DOM Changes
- **Scenario:** Forums or App Stores update their HTML structure, causing BeautifulSoup/Scrapy spiders to fail and data pipelines to run dry without throwing obvious application errors.
- **Mitigation:** Implement structural anomaly detection (e.g., alerting if the number of scraped comments drops below a historical 7-day moving average).

### 1.4. Multi-Platform Misattribution
- **Scenario:** A user complains about a competitor (e.g., Myntra or Meesho) in an r/IndianFashionAddicts thread that broadly mentions AJIO.
- **Mitigation:** The prompt engineering for the Groq LLM must explicitly include a rule: *"Ensure the friction or problem is directly attributed to AJIO or the product being evaluated on AJIO. If the complaint targets a competitor, classify it as 'Irrelevant'."*

---

## 2. AI Processing & LLM Corner Cases

### 2.1. Handling Sarcasm
- **Scenario:** A user writes, *"Wow, great job AJIO, I love it when my medium shirt fits like an extra-small."* Standard sentiment analysis might mark this as positive.
- **Mitigation:** Advanced high-end LLMs like `llama-3.3-70b-versatile` generally detect sarcasm better than traditional NLP. The system prompt should explicitly instruct the model to look for sarcasm and extract the literal problem ("Size runs small").

### 2.2. Multi-Topic Complex Reviews
- **Scenario:** A single review contains multiple distinct problems: *"The color didn't match the photo, the zip was broken, and it arrived 3 days late. But I'll still buy it if it goes on sale."*
- **Mitigation:** The AI Engine should be instructed to output an *array* of problem JSON objects rather than a single object. Each distinct problem must be embedded and clustered separately.

### 2.3. Groq API Throttling & Queue Buildup
- **Scenario:** Groq's free tier has strict RPM (Requests Per Minute), RPD (Requests Per Day), and TPD (Tokens Per Day) limits for models like `llama-3.3-70b-versatile`. A sudden influx of data causes the Redis/RabbitMQ queue to build up massively.
- **Mitigation:** Implement strict rate-limiting (e.g., Token Bucket algorithm) and exponential backoff on the queue consumer. Track token usage dynamically. If limits are nearing, pause ingestion of low-priority sources (e.g., YouTube) and prioritize high-value sources (e.g., Reddit, App Store) until quotas reset.

### 2.4. Exceeding LLM Token Limits
- **Scenario:** A user writes a massive, 3,000-word rant about a ruined wedding outfit. This exceeds the max token context for the free-tier LLM API.
- **Mitigation:** The Normalization layer should truncate texts to a safe token limit (e.g., first 1000 and last 500 words) or chunk them into smaller segments before LLM processing.

---

## 3. Clustering & Analytics Anomalies

### 3.1. Contradictory Clusters
- **Scenario:** The system identifies two dense clusters for the exact same brand: *"Sizes run too small"* and *"Sizes run too large"*. 
- **Mitigation:** The Discovery Dashboard should allow PMs to filter by specific garments or product categories. Contradictions often resolve when drilling down from "Brand X" to "Brand X - Winter Jackets".

### 3.2. High Prevalence, Low Intent "Noise"
- **Scenario:** A massive cluster forms around a UI change (e.g., *"I hate the new pink app icon"*). It scores high on prevalence but has zero impact on wishlist-to-purchase conversion.
- **Mitigation:** The Opportunity Scoring formula mathematically penalizes this. Because its `Intent Relevance` score (association with purchase intent) will be near zero, the final Opportunity Score will be suppressed.

### 3.3. HDBSCAN "Noise" Misclassification (The -1 Cluster)
- **Scenario:** HDBSCAN classifies data points that don't fit into dense clusters as "noise" (label -1). A very specific, highly severe problem (e.g., a checkout bug affecting only iOS 17 users) might be too sparse to form a cluster and gets discarded.
- **Mitigation:** Track the "Severity" metric inside the noise cluster. If a data point in the noise cluster is tagged with `Severity: Critical` by the LLM, escalate it to a separate "High-Severity Outliers" view on the dashboard.

### 3.4. Vector Database Storage Limits
- **Scenario:** The Qdrant free tier or local disk fills up after months of generating embeddings.
- **Mitigation:** Implement a TTL (Time To Live) or rolling window approach. For wishlist-to-purchase conversion, problems from 2 years ago are likely stale. Only retain vector embeddings for the last 90-180 days.

---

## 4. Privacy & Compliance Edge Cases

### 4.1. Accidental PII in Problem Extraction
- **Scenario:** A user includes their order ID or phone number in a public tweet, and the PII scrubber misses it. The LLM extracts the order ID into the vector database.
- **Mitigation:** Ensure the prompt strictly instructs the LLM: *"Do NOT include any names, numbers, order IDs, or personal identifiers in the extracted Problem Statement."*

### 4.2. False Positive PII Scrubbing
- **Scenario:** The brand name "John's" or location "India" gets scrubbed by the PII anonymizer, stripping valuable context (e.g., *"This jacket from [REDACTED] is bad"*).
- **Mitigation:** Maintain a whitelist of common fashion brand names and geographic locations to bypass the PII regex/scrubber.
